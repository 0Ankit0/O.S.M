from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from src.apps.oms.constants import (
    DeliveryAssignmentStatus,
    FulfillmentTaskStatus,
    ReservationStatus,
    ReturnStatus,
)


class WarehouseBase(SQLModel):
    name: str = Field(index=True, max_length=120)
    code: str = Field(index=True, unique=True, max_length=40)
    location: str = Field(default="", max_length=255)
    is_active: bool = Field(default=True)


class Warehouse(WarehouseBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeliveryZoneBase(SQLModel):
    name: str = Field(index=True, max_length=120)
    code: str = Field(index=True, unique=True, max_length=40)
    postal_codes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    delivery_fee: float = Field(default=0, ge=0)
    min_order_value: float = Field(default=0, ge=0)
    sla_hours: int = Field(default=24, ge=1)
    is_active: bool = Field(default=True)


class DeliveryZone(DeliveryZoneBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InventoryItemBase(SQLModel):
    variant_id: int = Field(foreign_key="productvariant.id", index=True)
    warehouse_id: int = Field(foreign_key="warehouse.id", index=True)
    quantity_on_hand: int = Field(default=0, ge=0)
    quantity_reserved: int = Field(default=0, ge=0)
    low_stock_threshold: int = Field(default=5, ge=0)


class InventoryItem(InventoryItemBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class InventoryReservationBase(SQLModel):
    inventory_item_id: int = Field(foreign_key="inventoryitem.id", index=True)
    order_id: int | None = Field(default=None, foreign_key="order.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    quantity: int = Field(ge=1)
    status: ReservationStatus = Field(default=ReservationStatus.ACTIVE)
    expires_at: datetime


class InventoryReservation(InventoryReservationBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FulfillmentTaskBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True, unique=True)
    warehouse_id: int = Field(foreign_key="warehouse.id", index=True)
    assigned_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    status: FulfillmentTaskStatus = Field(default=FulfillmentTaskStatus.PENDING)
    scan_log: list[dict[str, object]] = Field(default_factory=list, sa_column=Column(JSON))
    package_dimensions: dict[str, float] = Field(default_factory=dict, sa_column=Column(JSON))
    package_weight_grams: int = Field(default=0, ge=0)


class FulfillmentTask(FulfillmentTaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DeliveryAssignmentBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True, unique=True)
    delivery_zone_id: int = Field(foreign_key="deliveryzone.id", index=True)
    staff_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    status: DeliveryAssignmentStatus = Field(default=DeliveryAssignmentStatus.ASSIGNED)
    attempt_count: int = Field(default=0, ge=0)
    window_start: datetime | None = None
    window_end: datetime | None = None
    notes: str = Field(default="", max_length=500)
    failure_reasons: list[str] = Field(default_factory=list, sa_column=Column(JSON))


class DeliveryAssignment(DeliveryAssignmentBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProofOfDeliveryBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True, unique=True)
    staff_user_id: int | None = Field(default=None, foreign_key="user.id", index=True)
    signature_path: str = Field(default="", max_length=500)
    photo_paths: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    notes: str = Field(default="", max_length=500)


class ProofOfDelivery(ProofOfDeliveryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReturnRequestBase(SQLModel):
    order_id: int = Field(foreign_key="order.id", index=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    reason_code: str = Field(max_length=80)
    evidence_paths: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    status: ReturnStatus = Field(default=ReturnStatus.REQUESTED)
    inspection_result: str = Field(default="", max_length=80)
    refund_amount: float = Field(default=0, ge=0)
    pickup_staff_user_id: int | None = Field(default=None, foreign_key="user.id")
    inspected_by_user_id: int | None = Field(default=None, foreign_key="user.id")


class ReturnRequest(ReturnRequestBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: datetime | None = None
