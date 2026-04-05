from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from httpx import AsyncClient
from jose import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.apps.core import security
from src.apps.core.config import settings
from src.apps.core.security import TokenType
from src.apps.iam.models.token_tracking import TokenTracking
from src.apps.iam.models.user import User
from src.apps.oms.constants import OrderStatus, ReservationStatus
from src.apps.oms.models import DeliveryAssignment, FulfillmentTask, InventoryItem, InventoryReservation, Order, ReturnRequest


async def _create_authenticated_user(db_session: AsyncSession, *, username: str = "omsuser") -> tuple[User, dict[str, str]]:
    user = User(
        username=username,
        email=f"{username}@example.com",
        hashed_password=security.get_password_hash("OmsPass123"),
        is_active=True,
        is_confirmed=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    access_token = security.create_access_token(user.id)
    payload = jwt.decode(access_token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
    db_session.add(
        TokenTracking(
            user_id=user.id,
            token_jti=payload["jti"],
            token_type=TokenType.ACCESS,
            ip_address="127.0.0.1",
            user_agent="pytest",
            expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
        )
    )
    await db_session.commit()
    return user, {"Authorization": f"Bearer {access_token}"}


@pytest.mark.asyncio
async def test_oms_checkout_and_cancel_flow(client: AsyncClient, db_session: AsyncSession) -> None:
    user, headers = await _create_authenticated_user(db_session)

    category_response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Beverages",
            "slug": "beverages",
            "description": "Drinks",
            "display_order": 1,
            "is_active": True,
        },
        headers=headers,
    )
    assert category_response.status_code == 403

    category = await client.post(
        "/api/v1/categories",
        json={
            "name": "Beverages",
            "slug": "beverages",
            "description": "Drinks",
            "display_order": 1,
            "is_active": True,
        },
        headers={},
    )
    assert category.status_code in {401, 403}

    user.is_superuser = True
    db_session.add(user)
    await db_session.commit()

    category_response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Beverages",
            "slug": "beverages",
            "description": "Drinks",
            "display_order": 1,
            "is_active": True,
        },
        headers=headers,
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    product_response = await client.post(
        "/api/v1/products",
        json={
            "title": "Cold Brew",
            "slug": "cold-brew",
            "description": "Smooth bottled coffee",
            "category_id": category_id,
            "base_price": 240,
            "currency": "NPR",
            "status": "active",
            "images": [],
            "specifications": {"size": "250ml"},
            "tags": ["coffee"],
            "is_featured": True,
            "variants": [
                {
                    "sku": "CB-250",
                    "title": "250ml Bottle",
                    "attributes": {"size": "250ml"},
                    "price": 240,
                    "stock_quantity": 8,
                    "weight_grams": 280,
                    "image_url": "",
                    "is_active": True,
                }
            ],
        },
        headers=headers,
    )
    assert product_response.status_code == 201
    variant_id = product_response.json()["variants"][0]["id"]

    coupon_response = await client.post(
        "/api/v1/coupons",
        json={
            "code": "SAVE10",
            "description": "Ten percent off",
            "coupon_type": "percentage",
            "value": 10,
            "min_order_value": 100,
            "active": True,
        },
        headers=headers,
    )
    assert coupon_response.status_code == 201

    address_response = await client.post(
        "/api/v1/addresses/",
        json={
            "label": "home",
            "line1": "Lazimpat 1",
            "line2": "",
            "city": "Kathmandu",
            "state": "Bagmati",
            "postal_code": "44600",
            "country": "NP",
            "phone": "+9779800000000",
            "is_default": True,
        },
        headers=headers,
    )
    assert address_response.status_code == 201
    address_id = address_response.json()["id"]

    add_cart_response = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 2},
        headers=headers,
    )
    assert add_cart_response.status_code == 201
    cart_json = add_cart_response.json()
    assert cart_json["subtotal"] == 480

    cart_with_coupon_response = await client.get(
        "/api/v1/cart/",
        params={"coupon_code": "SAVE10"},
        headers=headers,
    )
    assert cart_with_coupon_response.status_code == 200
    assert cart_with_coupon_response.json()["discount_amount"] == 48

    checkout_response = await client.post(
        "/api/v1/orders/checkout",
        json={"address_id": address_id, "coupon_code": "SAVE10", "payment_provider": "cod"},
        headers={**headers, "Idempotency-Key": "oms-checkout-1"},
    )
    assert checkout_response.status_code == 201
    order_json = checkout_response.json()
    assert order_json["status"] == "confirmed"
    assert order_json["discount_amount"] == 48
    assert len(order_json["line_items"]) == 1
    order_id = order_json["id"]

    inventory_item = (
        await db_session.execute(select(InventoryItem).where(InventoryItem.variant_id == variant_id))
    ).scalars().one()
    assert inventory_item.quantity_reserved == 2

    reservation = (
        await db_session.execute(select(InventoryReservation).where(InventoryReservation.order_id == order_id))
    ).scalars().one()
    assert reservation.status == ReservationStatus.ACTIVE
    assert reservation.expires_at > datetime.now(timezone.utc)

    repeat_checkout_response = await client.post(
        "/api/v1/orders/checkout",
        json={"address_id": address_id, "coupon_code": "SAVE10", "payment_provider": "cod"},
        headers={**headers, "Idempotency-Key": "oms-checkout-1"},
    )
    assert repeat_checkout_response.status_code == 201
    assert repeat_checkout_response.json()["id"] == order_id

    list_orders_response = await client.get("/api/v1/orders/", headers=headers)
    assert list_orders_response.status_code == 200
    assert list_orders_response.json()["items"][0]["id"] == order_id

    cancel_response = await client.patch(
        f"/api/v1/orders/{order_id}/cancel",
        json={"reason": "Changed my mind"},
        headers={**headers, "Idempotency-Key": "oms-cancel-1"},
    )
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    await db_session.refresh(inventory_item)
    assert inventory_item.quantity_reserved == 0

    reservations = (
        await db_session.execute(select(InventoryReservation).where(InventoryReservation.order_id == order_id))
    ).scalars().all()
    assert all(item.status == ReservationStatus.RELEASED for item in reservations)

    order = await db_session.get(Order, order_id)
    assert order is not None
    assert order.status == OrderStatus.CANCELLED


@pytest.mark.asyncio
async def test_oms_fulfillment_delivery_and_return_flow(client: AsyncClient, db_session: AsyncSession) -> None:
    user, headers = await _create_authenticated_user(db_session, username="opsflow")
    user.is_superuser = True
    db_session.add(user)
    await db_session.commit()

    category_response = await client.post(
        "/api/v1/categories",
        json={
            "name": "Signature Rolls",
            "slug": "signature-rolls",
            "description": "Restaurant specials",
            "display_order": 1,
            "is_active": True,
        },
        headers=headers,
    )
    assert category_response.status_code == 201
    category_id = category_response.json()["id"]

    product_response = await client.post(
        "/api/v1/products",
        json={
            "title": "Dragon Roll",
            "slug": "dragon-roll",
            "description": "Avocado, tempura shrimp, eel sauce",
            "category_id": category_id,
            "base_price": 680,
            "currency": "NPR",
            "status": "active",
            "images": [],
            "specifications": {"pieces": "8"},
            "tags": ["featured", "sushi"],
            "is_featured": True,
            "variants": [
                {
                    "sku": "DRAGON-8",
                    "title": "8 Pieces",
                    "attributes": {"pieces": "8"},
                    "price": 680,
                    "stock_quantity": 6,
                    "weight_grams": 320,
                    "image_url": "",
                    "is_active": True,
                }
            ],
        },
        headers=headers,
    )
    assert product_response.status_code == 201
    variant_id = product_response.json()["variants"][0]["id"]

    address_response = await client.post(
        "/api/v1/addresses/",
        json={
            "label": "home",
            "line1": "Maharajgunj 11",
            "line2": "",
            "city": "Kathmandu",
            "state": "Bagmati",
            "postal_code": "44600",
            "country": "NP",
            "phone": "+9779811111111",
            "is_default": True,
        },
        headers=headers,
    )
    assert address_response.status_code == 201
    address_id = address_response.json()["id"]

    add_cart_response = await client.post(
        "/api/v1/cart/items",
        json={"variant_id": variant_id, "quantity": 1},
        headers=headers,
    )
    assert add_cart_response.status_code == 201

    checkout_response = await client.post(
        "/api/v1/orders/checkout",
        json={"address_id": address_id, "payment_provider": "cod"},
        headers={**headers, "Idempotency-Key": "oms-ops-checkout-1"},
    )
    assert checkout_response.status_code == 201
    order_id = checkout_response.json()["id"]

    task = (
        await db_session.execute(select(FulfillmentTask).where(FulfillmentTask.order_id == order_id))
    ).scalars().one()
    assignment = (
        await db_session.execute(select(DeliveryAssignment).where(DeliveryAssignment.order_id == order_id))
    ).scalars().one()

    start_task_response = await client.post(
        f"/api/v1/fulfillment/tasks/{task.id}/start",
        headers=headers,
    )
    assert start_task_response.status_code == 200
    assert start_task_response.json()["status"] == "in_progress"

    scan_response = await client.post(
        f"/api/v1/fulfillment/tasks/{task.id}/scan",
        json={"sku": "DRAGON-8", "quantity": 1},
        headers=headers,
    )
    assert scan_response.status_code == 200
    assert scan_response.json()["status"] == "picked"

    pack_response = await client.post(
        f"/api/v1/fulfillment/tasks/{task.id}/pack",
        json={"length_cm": 25, "width_cm": 18, "height_cm": 6, "weight_grams": 380},
        headers=headers,
    )
    assert pack_response.status_code == 200
    assert pack_response.json()["status"] == "ready"

    order_after_pack = await client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert order_after_pack.status_code == 200
    assert order_after_pack.json()["status"] == "ready_for_dispatch"

    picked_up_response = await client.patch(
        f"/api/v1/deliveries/assignments/{assignment.id}/status",
        json={"status": "picked_up", "notes": "Collected from kitchen handoff"},
        headers=headers,
    )
    assert picked_up_response.status_code == 200
    assert picked_up_response.json()["status"] == "picked_up"

    out_for_delivery_response = await client.patch(
        f"/api/v1/deliveries/assignments/{assignment.id}/status",
        json={"status": "out_for_delivery", "notes": "Courier left the restaurant"},
        headers=headers,
    )
    assert out_for_delivery_response.status_code == 200
    assert out_for_delivery_response.json()["status"] == "out_for_delivery"

    pod_response = await client.post(
        f"/api/v1/deliveries/assignments/{assignment.id}/pod",
        json={
            "signature_path": "/pod/signatures/order-1.png",
            "photo_paths": ["/pod/photos/order-1-dropoff.jpg"],
            "notes": "Handed to customer at front desk",
        },
        headers=headers,
    )
    assert pod_response.status_code == 200

    delivered_response = await client.patch(
        f"/api/v1/deliveries/assignments/{assignment.id}/status",
        json={"status": "delivered", "notes": "Delivered successfully"},
        headers=headers,
    )
    assert delivered_response.status_code == 200
    assert delivered_response.json()["status"] == "delivered"

    order_after_delivery = await client.get(f"/api/v1/orders/{order_id}", headers=headers)
    assert order_after_delivery.status_code == 200
    assert order_after_delivery.json()["status"] == "delivered"

    return_request_response = await client.post(
        f"/api/v1/returns/{order_id}",
        json={"reason_code": "quality_issue", "evidence_paths": ["/returns/order-1.jpg"]},
        headers=headers,
    )
    assert return_request_response.status_code == 201
    return_id = return_request_response.json()["id"]
    assert return_request_response.json()["status"] == "requested"

    review_response = await client.patch(
        f"/api/v1/returns/{return_id}/review",
        json={
            "status": "refunded",
            "inspection_result": "Accepted after kitchen review",
            "refund_amount": 680,
        },
        headers=headers,
    )
    assert review_response.status_code == 200
    assert review_response.json()["status"] == "refunded"

    refreshed_order = await db_session.get(Order, order_id)
    assert refreshed_order is not None
    assert refreshed_order.status == OrderStatus.REFUNDED

    return_request = await db_session.get(ReturnRequest, return_id)
    assert return_request is not None
    assert return_request.status.value == "refunded"
