from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel

from src.apps.oms.constants import AddressLabel


class CustomerAddressBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", index=True)
    label: AddressLabel = Field(default=AddressLabel.HOME)
    custom_label: str = Field(default="", max_length=60)
    line1: str = Field(max_length=255)
    line2: str = Field(default="", max_length=255)
    city: str = Field(max_length=100)
    state: str = Field(default="", max_length=100)
    postal_code: str = Field(max_length=30, index=True)
    country: str = Field(default="DE", max_length=2)
    phone: str = Field(default="", max_length=20)
    is_default: bool = Field(default=False)
    is_serviceable: bool = Field(default=True)
    is_archived: bool = Field(default=False)


class CustomerAddress(CustomerAddressBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CartItemBase(SQLModel):
    user_id: int = Field(foreign_key="user.id", index=True)
    variant_id: int = Field(foreign_key="productvariant.id", index=True)
    quantity: int = Field(default=1, ge=1)
    unit_price_snapshot: float = Field(default=0, ge=0)
    currency: str = Field(default="EUR", max_length=3)


class CartItem(CartItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
