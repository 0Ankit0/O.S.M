from __future__ import annotations

import base64
import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.apps.core.cache import RedisCache
from src.apps.iam.models.role import UserRole
from src.apps.oms.constants import (
    DeliveryAssignmentStatus,
    ORDER_TRANSITIONS,
    OrderStatus,
    ReservationStatus,
)
from src.apps.oms.models import (
    CartItem,
    Coupon,
    CustomerAddress,
    DeliveryAssignment,
    DeliveryZone,
    FulfillmentTask,
    InventoryItem,
    InventoryReservation,
    Order,
    OrderLineItem,
    OrderMilestone,
    Product,
    ProductVariant,
    ProofOfDelivery,
    ReturnRequest,
    Warehouse,
)

IDEMPOTENCY_TTL_SECONDS = 60 * 60 * 24

_idempotency_fallback_store: dict[str, dict[str, Any]] = {}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def decode_cursor(cursor: str | None) -> dict[str, Any] | None:
    if not cursor:
        return None
    return json.loads(base64.urlsafe_b64decode(cursor.encode("utf-8")).decode("utf-8"))


async def ensure_admin(user_id: int, session: AsyncSession) -> None:
    role_result = await session.execute(
        select(UserRole).where(UserRole.user_id == user_id)
    )
    role_ids = [row.role_id for row in role_result.scalars().all()]
    if not role_ids:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


async def get_idempotency_value(key: str) -> dict[str, Any] | None:
    cache_key = f"oms:idempotency:{key}"
    cached = await RedisCache.get(cache_key)
    if cached is not None:
        return cached
    return _idempotency_fallback_store.get(cache_key)


async def set_idempotency_value(key: str, value: dict[str, Any]) -> None:
    cache_key = f"oms:idempotency:{key}"
    stored = await RedisCache.set(cache_key, value, ttl=IDEMPOTENCY_TTL_SECONDS)
    if not stored:
        _idempotency_fallback_store[cache_key] = value


def require_transition(current: OrderStatus, nxt: OrderStatus) -> None:
    allowed = ORDER_TRANSITIONS.get(current, set())
    if nxt not in allowed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot transition order from {current.value} to {nxt.value}",
        )


async def record_order_milestone(
    session: AsyncSession,
    *,
    order_id: int,
    status_value: OrderStatus,
    actor_user_id: int | None,
    actor_role: str,
    notes: str = "",
) -> OrderMilestone:
    milestone = OrderMilestone(
        order_id=order_id,
        status=status_value,
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        notes=notes,
    )
    session.add(milestone)
    await session.flush()
    return milestone


async def get_serviceable_zone(session: AsyncSession, postal_code: str) -> DeliveryZone | None:
    result = await session.execute(select(DeliveryZone))
    for zone in result.scalars().all():
        if postal_code in (zone.postal_codes or []):
            return zone
    return None


async def build_cart_summary(
    session: AsyncSession,
    *,
    user_id: int,
    coupon_code: str | None = None,
) -> tuple[list[dict[str, Any]], float, float, float, float, float, str, Coupon | None]:
    result = await session.execute(
        select(CartItem, ProductVariant, Product)
        .join(ProductVariant, ProductVariant.id == CartItem.variant_id)
        .join(Product, Product.id == ProductVariant.product_id)
        .where(CartItem.user_id == user_id)
    )
    rows = result.all()
    currency = rows[0][2].currency if rows else "EUR"
    items: list[dict[str, Any]] = []
    subtotal = 0.0
    for cart_item, variant, product in rows:
        unit_price = float(variant.price or product.base_price)
        line_total = unit_price * cart_item.quantity
        subtotal += line_total
        items.append(
            {
                "id": cart_item.id,
                "variant_id": variant.id,
                "product_id": product.id,
                "product_title": product.title,
                "variant_title": variant.title,
                "sku": variant.sku,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "line_total": line_total,
                "currency": currency,
                "attributes": variant.attributes or {},
                "in_stock": product.is_available_today,
            }
        )
    coupon: Coupon | None = None
    discount = 0.0
    if coupon_code:
        coupon_result = await session.execute(
            select(Coupon).where(Coupon.code == coupon_code.upper(), Coupon.active)
        )
        coupon = coupon_result.scalars().first()
        if coupon and subtotal >= coupon.min_order_value:
            if coupon.coupon_type.value == "percentage":
                discount = subtotal * (coupon.value / 100)
                if coupon.max_discount_amount is not None:
                    discount = min(discount, float(coupon.max_discount_amount))
            elif coupon.coupon_type.value == "fixed":
                discount = min(subtotal, float(coupon.value))
            elif coupon.coupon_type.value == "free_shipping":
                discount = 0.0
        else:
            coupon = None
    tax_amount = round(subtotal * 0.13, 2)
    shipping_fee = 100.0 if subtotal > 0 else 0.0
    if coupon and coupon.coupon_type.value == "free_shipping":
        shipping_fee = 0.0
    total = round(subtotal + tax_amount + shipping_fee - discount, 2)
    return items, round(subtotal, 2), tax_amount, shipping_fee, round(discount, 2), total, currency, coupon


async def validate_availability_for_checkout(
    session: AsyncSession,
    *,
    items: list[dict[str, Any]],
) -> None:
    """Verify all cart items are marked available today before confirming an order."""
    for item in items:
        variant = await session.get(ProductVariant, item["variant_id"])
        if variant is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Variant {item['variant_id']} not found",
            )
        product = await session.get(Product, variant.product_id)
        if product is None or not product.is_available_today:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Variant {item['variant_id']} is not available today",
            )


async def release_inventory_reservations(
    session: AsyncSession,
    *,
    order_id: int,
    next_status: ReservationStatus,
) -> None:
    reservation_result = await session.execute(
        select(InventoryReservation).where(
            InventoryReservation.order_id == order_id,
            InventoryReservation.status == ReservationStatus.ACTIVE,
        )
    )
    reservations = reservation_result.scalars().all()
    for reservation in reservations:
        inventory_item = await session.get(InventoryItem, reservation.inventory_item_id)
        if inventory_item is not None:
            inventory_item.quantity_reserved = max(
                0,
                inventory_item.quantity_reserved - reservation.quantity,
            )
        reservation.status = next_status


async def create_default_warehouse_and_zone(session: AsyncSession, postal_code: str) -> tuple[Warehouse, DeliveryZone]:
    warehouse_result = await session.execute(select(Warehouse).limit(1))
    warehouse = warehouse_result.scalars().first()
    if warehouse is None:
        warehouse = Warehouse(name="Primary Warehouse", code="WH-01", location="Main Fulfillment Center")
        session.add(warehouse)
        await session.flush()
    zone = await get_serviceable_zone(session, postal_code)
    if zone is None:
        zone = DeliveryZone(
            name="Kathmandu Core",
            code="KTM-CORE",
            postal_codes=[postal_code],
            delivery_fee=100,
            min_order_value=0,
            sla_hours=24,
        )
        session.add(zone)
        await session.flush()
    return warehouse, zone


async def bootstrap_order_operations(
    session: AsyncSession,
    *,
    order: Order,
    postal_code: str,
) -> tuple[FulfillmentTask, DeliveryAssignment]:
    warehouse, zone = await create_default_warehouse_and_zone(session, postal_code)
    task = FulfillmentTask(order_id=order.id, warehouse_id=warehouse.id)
    assignment = DeliveryAssignment(order_id=order.id, delivery_zone_id=zone.id)
    session.add(task)
    session.add(assignment)
    await session.flush()
    return task, assignment


async def serialize_order(session: AsyncSession, order: Order) -> dict[str, Any]:
    lines = (
        await session.execute(select(OrderLineItem).where(OrderLineItem.order_id == order.id))
    ).scalars().all()
    milestones = (
        await session.execute(
            select(OrderMilestone).where(OrderMilestone.order_id == order.id).order_by(OrderMilestone.id.asc())
        )
    ).scalars().all()
    return {
        "id": order.id,
        "order_number": order.order_number,
        "status": order.status,
        "subtotal": order.subtotal,
        "tax_amount": order.tax_amount,
        "shipping_fee": order.shipping_fee,
        "discount_amount": order.discount_amount,
        "total_amount": order.total_amount,
        "currency": order.currency,
        "delivery_address_id": order.delivery_address_id,
        "estimated_delivery": order.estimated_delivery,
        "created_at": order.created_at,
        "line_items": [
            {
                "id": line.id,
                "product_id": line.product_id,
                "variant_id": line.variant_id,
                "product_title": line.product_title,
                "variant_title": line.variant_title,
                "sku": line.sku,
                "quantity": line.quantity,
                "unit_price": line.unit_price,
                "line_total": line.line_total,
                "attributes": line.attributes or {},
            }
            for line in lines
        ],
        "milestones": [
            {
                "id": milestone.id,
                "status": milestone.status,
                "actor_user_id": milestone.actor_user_id,
                "actor_role": milestone.actor_role,
                "notes": milestone.notes,
                "recorded_at": milestone.recorded_at,
            }
            for milestone in milestones
        ],
    }


async def ensure_address_belongs_to_user(session: AsyncSession, *, address_id: int, user_id: int) -> CustomerAddress:
    address = await session.get(CustomerAddress, address_id)
    if address is None or address.user_id != user_id or address.is_archived:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    return address


async def ensure_order_belongs_to_user(session: AsyncSession, *, order_id: int, user_id: int) -> Order:
    order = await session.get(Order, order_id)
    if order is None or order.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


async def create_or_update_pod(
    session: AsyncSession,
    *,
    order_id: int,
    staff_user_id: int | None,
    signature_path: str,
    photo_paths: list[str],
    notes: str,
) -> ProofOfDelivery:
    existing_result = await session.execute(
        select(ProofOfDelivery).where(ProofOfDelivery.order_id == order_id)
    )
    pod = existing_result.scalars().first()
    if pod is None:
        pod = ProofOfDelivery(
            order_id=order_id,
            staff_user_id=staff_user_id,
            signature_path=signature_path,
            photo_paths=photo_paths,
            notes=notes,
        )
        session.add(pod)
    else:
        pod.staff_user_id = staff_user_id
        pod.signature_path = signature_path
        pod.photo_paths = photo_paths
        pod.notes = notes
    await session.flush()
    return pod


def map_assignment_status_to_order_status(assignment_status: DeliveryAssignmentStatus) -> OrderStatus:
    mapping = {
        DeliveryAssignmentStatus.PICKED_UP: OrderStatus.PICKED_UP,
        DeliveryAssignmentStatus.OUT_FOR_DELIVERY: OrderStatus.OUT_FOR_DELIVERY,
        DeliveryAssignmentStatus.DELIVERED: OrderStatus.DELIVERED,
        DeliveryAssignmentStatus.FAILED: OrderStatus.DELIVERY_FAILED,
        DeliveryAssignmentStatus.RETURNED: OrderStatus.RETURNED_TO_WAREHOUSE,
    }
    return mapping[assignment_status]
