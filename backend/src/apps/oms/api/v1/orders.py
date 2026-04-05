from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from src.apps.core.schemas import CursorPage
from src.apps.iam.api.deps import get_current_user, get_db
from src.apps.iam.models.user import User
from src.apps.oms.constants import OrderStatus, ReservationStatus
from src.apps.oms.models import CartItem, InventoryReservation, Order, OrderLineItem
from src.apps.oms.schemas import (
    CancelOrderRequest,
    CheckoutRequest,
    OrderRead,
    UpdateOrderAddressRequest,
)
from src.apps.oms.service import (
    bootstrap_order_operations,
    build_cart_summary,
    decode_cursor,
    ensure_address_belongs_to_user,
    ensure_order_belongs_to_user,
    get_idempotency_value,
    release_inventory_reservations,
    record_order_milestone,
    validate_availability_for_checkout,
    serialize_order,
    set_idempotency_value,
    utcnow,
)

router = APIRouter(prefix="/orders")


@router.post("/checkout", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
async def checkout_order(
    payload: CheckoutRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> OrderRead:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")

    cached = await get_idempotency_value(idempotency_key)
    if cached is not None:
        return OrderRead(**cached)

    address = await ensure_address_belongs_to_user(session, address_id=payload.address_id, user_id=current_user.id)
    if not address.is_serviceable:
        raise HTTPException(status_code=409, detail="Selected address is outside active delivery zones")

    items, subtotal, tax_amount, shipping_fee, discount_amount, total_amount, currency, coupon = await build_cart_summary(
        session,
        user_id=current_user.id,
        coupon_code=payload.coupon_code,
    )
    if not items:
        raise HTTPException(status_code=400, detail="Cart is empty")
    if not all(item["in_stock"] for item in items):
        raise HTTPException(status_code=409, detail="One or more cart items are unavailable")

    order = Order(
        order_number=f"OMS-{utcnow().strftime('%Y%m%d')}-{current_user.id:04d}-{len(items):02d}",
        user_id=current_user.id,
        delivery_address_id=address.id,
        coupon_id=coupon.id if coupon else None,
        status=OrderStatus.CONFIRMED,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        total_amount=total_amount,
        currency=currency,
        estimated_delivery=utcnow() + timedelta(hours=24),
        idempotency_key=idempotency_key,
        snapshot={"cart_items": items, "payment_provider": payload.payment_provider},
    )
    session.add(order)
    await session.flush()

    for item in items:
        session.add(
            OrderLineItem(
                order_id=order.id,
                product_id=item["product_id"],
                variant_id=item["variant_id"],
                product_title=item["product_title"],
                variant_title=item["variant_title"],
                sku=item["sku"],
                quantity=item["quantity"],
                unit_price=item["unit_price"],
                line_total=item["line_total"],
                attributes=item["attributes"],
            )
        )

    await validate_availability_for_checkout(session, items=items)
    await record_order_milestone(
        session,
        order_id=order.id,
        status_value=OrderStatus.CONFIRMED,
        actor_user_id=current_user.id,
        actor_role="customer",
        notes="Checkout completed",
    )
    await bootstrap_order_operations(session, order=order, postal_code=address.postal_code)

    cart_result = await session.execute(select(CartItem).where(CartItem.user_id == current_user.id))
    for cart_item in cart_result.scalars().all():
        await session.delete(cart_item)

    await session.commit()
    await session.refresh(order)
    serialized = await serialize_order(session, order)
    await set_idempotency_value(idempotency_key, serialized)
    return OrderRead(**serialized)


@router.get("/", response_model=CursorPage[OrderRead])
async def list_orders(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=10, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CursorPage[OrderRead]:
    decoded_cursor = decode_cursor(cursor)
    query = select(Order).where(Order.user_id == current_user.id)
    if decoded_cursor and decoded_cursor.get("id"):
        query = query.where(Order.id < int(decoded_cursor["id"]))
    query = query.order_by(col(Order.id).desc()).limit(limit + 1)
    result = await session.execute(query)
    orders = result.scalars().all()
    has_more = len(orders) > limit
    orders = orders[:limit]
    items = [OrderRead(**await serialize_order(session, order)) for order in orders]
    next_cursor_value = {"id": orders[-1].id} if has_more and orders else None
    return CursorPage.from_items(items, next_cursor_value=next_cursor_value, has_more=has_more)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> OrderRead:
    order = await ensure_order_belongs_to_user(session, order_id=order_id, user_id=current_user.id)
    return OrderRead(**await serialize_order(session, order))


@router.patch("/{order_id}/cancel", response_model=OrderRead)
async def cancel_order(
    order_id: int,
    payload: CancelOrderRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> OrderRead:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    order = await ensure_order_belongs_to_user(session, order_id=order_id, user_id=current_user.id)
    if order.status not in {OrderStatus.CONFIRMED, OrderStatus.READY_FOR_DISPATCH}:
        raise HTTPException(status_code=409, detail="Order can no longer be cancelled")
    order.status = OrderStatus.CANCELLED
    order.cancellation_reason = payload.reason
    await release_inventory_reservations(
        session,
        order_id=order.id,
        next_status=ReservationStatus.RELEASED,
    )
    await record_order_milestone(
        session,
        order_id=order.id,
        status_value=OrderStatus.CANCELLED,
        actor_user_id=current_user.id,
        actor_role="customer",
        notes=payload.reason,
    )
    await session.commit()
    await session.refresh(order)
    serialized = await serialize_order(session, order)
    await set_idempotency_value(idempotency_key, serialized)
    return OrderRead(**serialized)


@router.patch("/{order_id}/address", response_model=OrderRead)
async def update_order_address(
    order_id: int,
    payload: UpdateOrderAddressRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> OrderRead:
    if not idempotency_key:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required")
    order = await ensure_order_belongs_to_user(session, order_id=order_id, user_id=current_user.id)
    if order.status not in {OrderStatus.CONFIRMED, OrderStatus.READY_FOR_DISPATCH}:
        raise HTTPException(status_code=409, detail="Order address can no longer be changed")
    address = await ensure_address_belongs_to_user(session, address_id=payload.address_id, user_id=current_user.id)
    if not address.is_serviceable:
        raise HTTPException(status_code=409, detail="Address is not serviceable")
    order.delivery_address_id = address.id
    await record_order_milestone(
        session,
        order_id=order.id,
        status_value=order.status,
        actor_user_id=current_user.id,
        actor_role="customer",
        notes=f"Delivery address updated to {address.line1}",
    )
    await session.commit()
    await session.refresh(order)
    serialized = await serialize_order(session, order)
    await set_idempotency_value(idempotency_key, serialized)
    return OrderRead(**serialized)
