from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from src.apps.oms.constants import OrderStatus


class OrderBase(SQLModel):
    order_number: str = Field(index=True, unique=True, max_length=60)
    user_id: int = Field(foreign_key="user.id", index=True)
    delivery_address_id: int = Field(foreign_key="customeraddress.id", index=True)
    coupon_id: int | None = Field(default=None, foreign_key="coupon.id")
    payment_transaction_id: int | None = Field(default=None, foreign_key="payment_transactions.id")
    status: OrderStatus = Field(default=OrderStatus.DRAFT)
    subtotal: float = Field(default=0, ge=0)
    tax_amount: float = Field(default=0, ge=0)
    shipping_fee: float = Field(default=0, ge=0)
    discount_amount: float = Field(default=0, ge=0)
    total_amount: float = Field(default=0, ge=0)
    currency: str = Field(default="EUR", max_length=3)
    cancellation_reason: str | None = Field(default=None, max_length=255)
    estimated_delivery: datetime | None = None
    delivered_at: datetime | None = None
    idempotency_key: str = Field(index=True, unique=True, max_length=120)
    snapshot: dict[str, object] = Field(default_factory=dict, sa_column=Column(JSON))


class Order(OrderBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderLineItemBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True)
    product_id: int = Field(foreign_key="product.id", index=True)
    variant_id: int = Field(foreign_key="productvariant.id", index=True)
    product_title: str = Field(max_length=180)
    variant_title: str = Field(default="", max_length=180)
    sku: str = Field(max_length=80)
    quantity: int = Field(ge=1)
    unit_price: float = Field(ge=0)
    line_total: float = Field(ge=0)
    attributes: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))


class OrderLineItem(OrderLineItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OrderMilestoneBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True)
    status: OrderStatus = Field(index=True)
    actor_user_id: int | None = Field(default=None, foreign_key="user.id")
    actor_role: str = Field(default="system", max_length=60)
    notes: str = Field(default="", max_length=500)


class OrderMilestone(OrderMilestoneBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
