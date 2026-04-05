from __future__ import annotations

from enum import Enum


class OmsRole(str, Enum):
    CUSTOMER = "customer"
    WAREHOUSE = "warehouse_staff"
    DELIVERY = "delivery_staff"
    OPS = "ops_manager"
    FINANCE = "finance"
    ADMIN = "superadmin"


class AddressLabel(str, Enum):
    HOME = "home"
    WORK = "work"
    CUSTOM = "custom"


class ProductStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class OrderStatus(str, Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    READY_FOR_DISPATCH = "ready_for_dispatch"
    PICKED_UP = "picked_up"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    DELIVERY_FAILED = "delivery_failed"
    RETURN_REQUESTED = "return_requested"
    RETURN_PICKED_UP = "return_picked_up"
    REFUNDED = "refunded"
    RETURNED_TO_WAREHOUSE = "returned_to_warehouse"
    CANCELLED = "cancelled"


class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"
    FREE_SHIPPING = "free_shipping"


class ReservationStatus(str, Enum):
    ACTIVE = "active"
    RELEASED = "released"
    CONSUMED = "consumed"
    EXPIRED = "expired"


class DeliveryAssignmentStatus(str, Enum):
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"
    FAILED = "failed"
    RETURNED = "returned"


class FulfillmentTaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PICKED = "picked"
    PACKED = "packed"
    READY = "ready"


class ReturnStatus(str, Enum):
    REQUESTED = "requested"
    PICKUP_SCHEDULED = "pickup_scheduled"
    PICKED_UP = "picked_up"
    ACCEPTED = "accepted"
    PARTIALLY_ACCEPTED = "partially_accepted"
    REJECTED = "rejected"
    REFUNDED = "refunded"


ORDER_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.DRAFT: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.READY_FOR_DISPATCH, OrderStatus.CANCELLED},
    OrderStatus.READY_FOR_DISPATCH: {OrderStatus.PICKED_UP, OrderStatus.CANCELLED},
    OrderStatus.PICKED_UP: {OrderStatus.OUT_FOR_DELIVERY},
    OrderStatus.OUT_FOR_DELIVERY: {
        OrderStatus.DELIVERED,
        OrderStatus.DELIVERY_FAILED,
        OrderStatus.RETURNED_TO_WAREHOUSE,
    },
    OrderStatus.DELIVERY_FAILED: {
        OrderStatus.OUT_FOR_DELIVERY,
        OrderStatus.RETURNED_TO_WAREHOUSE,
    },
    OrderStatus.DELIVERED: {OrderStatus.RETURN_REQUESTED},
    OrderStatus.RETURN_REQUESTED: {OrderStatus.RETURN_PICKED_UP},
    OrderStatus.RETURN_PICKED_UP: {OrderStatus.REFUNDED},
}
