from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from src.apps.core.schemas import CursorPage
from src.apps.oms.constants import (
    AddressLabel,
    CouponType,
    DeliveryAssignmentStatus,
    FulfillmentTaskStatus,
    OrderStatus,
    ProductStatus,
    ReturnStatus,
)


class CategoryCreate(BaseModel):
    name: str
    name_en: str = ""
    name_de: str = ""
    slug: str
    description: str = ""
    description_en: str = ""
    description_de: str = ""
    parent_id: int | None = None
    image_url: str = ""
    display_order: int = 0
    is_active: bool = True


class CategoryRead(CategoryCreate):
    id: int


class ProductVariantCreate(BaseModel):
    sku: str
    title: str = ""
    title_en: str = ""
    title_de: str = ""
    attributes: dict[str, str] = Field(default_factory=dict)
    price: float
    compare_at_price: float | None = None
    image_url: str = ""
    is_active: bool = True


class ProductCreate(BaseModel):
    title: str
    title_en: str = ""
    title_de: str = ""
    slug: str
    description: str = ""
    description_en: str = ""
    description_de: str = ""
    category_id: int | None = None
    base_price: float = 0
    currency: str = "EUR"
    status: ProductStatus = ProductStatus.ACTIVE
    is_available_today: bool = True
    images: list[str] = Field(default_factory=list)
    specifications: dict[str, str] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)
    is_featured: bool = False
    variants: list[ProductVariantCreate] = Field(default_factory=list)


class ProductVariantRead(ProductVariantCreate):
    id: int
    product_id: int


class ProductRead(ProductCreate):
    id: int
    variants: list[ProductVariantRead]


class CouponCreate(BaseModel):
    code: str
    description: str = ""
    coupon_type: CouponType = CouponType.PERCENTAGE
    value: float = 0
    min_order_value: float = 0
    max_discount_amount: float | None = None
    usage_limit: int | None = None
    per_customer_limit: int | None = None
    active: bool = True
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class CouponRead(CouponCreate):
    id: int


class ProductAdminUpdate(BaseModel):
    title: str | None = None
    title_en: str | None = None
    title_de: str | None = None
    description: str | None = None
    description_en: str | None = None
    description_de: str | None = None
    base_price: float | None = Field(default=None, ge=0)
    status: ProductStatus | None = None
    is_featured: bool | None = None
    is_available_today: bool | None = None
    tags: list[str] | None = None


class AddressCreate(BaseModel):
    label: AddressLabel = AddressLabel.HOME
    custom_label: str = ""
    line1: str
    line2: str = ""
    city: str
    state: str = ""
    postal_code: str
    country: str = "DE"
    phone: str = ""
    is_default: bool = False


class AddressRead(AddressCreate):
    id: int
    is_serviceable: bool
    is_archived: bool


class CartItemCreate(BaseModel):
    variant_id: int
    quantity: int = Field(ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartLineRead(BaseModel):
    id: int
    variant_id: int
    product_id: int
    product_title: str
    variant_title: str
    sku: str
    quantity: int
    unit_price: float
    line_total: float
    currency: str
    attributes: dict[str, str] = Field(default_factory=dict)
    in_stock: bool = True


class CartRead(BaseModel):
    items: list[CartLineRead]
    subtotal: float
    tax_amount: float
    shipping_fee: float
    discount_amount: float
    total_amount: float
    currency: str
    coupon_code: str | None = None


class CheckoutRequest(BaseModel):
    address_id: int
    coupon_code: str | None = None
    payment_provider: str = "cod"


class OrderLineRead(BaseModel):
    id: int
    product_id: int
    variant_id: int
    product_title: str
    variant_title: str
    sku: str
    quantity: int
    unit_price: float
    line_total: float
    attributes: dict[str, str] = Field(default_factory=dict)


class OrderMilestoneRead(BaseModel):
    id: int
    status: OrderStatus
    actor_user_id: int | None = None
    actor_role: str
    notes: str
    recorded_at: datetime


class OrderRead(BaseModel):
    id: int
    order_number: str
    status: OrderStatus
    subtotal: float
    tax_amount: float
    shipping_fee: float
    discount_amount: float
    total_amount: float
    currency: str
    delivery_address_id: int
    estimated_delivery: datetime | None = None
    created_at: datetime
    line_items: list[OrderLineRead]
    milestones: list[OrderMilestoneRead]


class CancelOrderRequest(BaseModel):
    reason: str = Field(min_length=3, max_length=255)


class UpdateOrderAddressRequest(BaseModel):
    address_id: int


class WarehouseCreate(BaseModel):
    name: str
    code: str
    location: str = ""
    is_active: bool = True


class WarehouseRead(WarehouseCreate):
    id: int


class InventoryItemRead(BaseModel):
    id: int
    variant_id: int
    warehouse_id: int
    quantity_on_hand: int
    quantity_reserved: int
    low_stock_threshold: int


class DeliveryZoneCreate(BaseModel):
    name: str
    code: str
    postal_codes: list[str] = Field(default_factory=list)
    delivery_fee: float = 0
    min_order_value: float = 0
    sla_hours: int = 24
    is_active: bool = True


class DeliveryZoneRead(DeliveryZoneCreate):
    id: int


class FulfillmentTaskRead(BaseModel):
    id: int
    order_id: int
    warehouse_id: int
    assigned_user_id: int | None
    status: FulfillmentTaskStatus
    scan_log: list[dict[str, Any]]
    package_dimensions: dict[str, float]
    package_weight_grams: int


class FulfillmentScanRequest(BaseModel):
    sku: str
    quantity: int = Field(ge=1)


class FulfillmentPackRequest(BaseModel):
    length_cm: float = Field(ge=0)
    width_cm: float = Field(ge=0)
    height_cm: float = Field(ge=0)
    weight_grams: int = Field(ge=0)


class DeliveryAssignmentRead(BaseModel):
    id: int
    order_id: int
    delivery_zone_id: int
    staff_user_id: int | None
    status: DeliveryAssignmentStatus
    attempt_count: int
    notes: str
    failure_reasons: list[str]


class DeliveryStatusUpdateRequest(BaseModel):
    status: DeliveryAssignmentStatus
    notes: str = ""


class DeliveryFailureRequest(BaseModel):
    reason: str = Field(min_length=2, max_length=80)


class PodSubmitRequest(BaseModel):
    signature_path: str = ""
    photo_paths: list[str] = Field(default_factory=list)
    notes: str = ""


class ReturnRequestCreate(BaseModel):
    reason_code: str
    evidence_paths: list[str] = Field(default_factory=list)


class ReturnRequestRead(BaseModel):
    id: int
    order_id: int
    user_id: int
    reason_code: str
    evidence_paths: list[str]
    status: ReturnStatus
    inspection_result: str
    refund_amount: float
    created_at: datetime


class ReturnReviewRequest(BaseModel):
    status: ReturnStatus
    inspection_result: str = ""
    refund_amount: float = Field(default=0, ge=0)


class AdminOverviewRead(BaseModel):
    total_orders: int
    active_orders: int
    delivered_orders: int
    cancelled_orders: int
    return_requests: int
    low_stock_items: int
    active_fulfillment_tasks: int
    active_delivery_assignments: int
    featured_products: int
    top_category_names: list[str] = Field(default_factory=list)


OmsProductPage = CursorPage[ProductRead]
OmsOrderPage = CursorPage[OrderRead]
