from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, JSON
from sqlmodel import Field, Relationship, SQLModel

from src.apps.oms.constants import CouponType, ProductStatus


class CategoryBase(SQLModel):
    name: str = Field(index=True, max_length=120)
    name_en: str = Field(default="", max_length=120)
    name_de: str = Field(default="", max_length=120)
    slug: str = Field(index=True, unique=True, max_length=140)
    description: str = Field(default="", max_length=500)
    description_en: str = Field(default="", max_length=500)
    description_de: str = Field(default="", max_length=500)
    parent_id: int | None = Field(default=None, foreign_key="category.id")
    image_url: str = Field(default="", max_length=500)
    display_order: int = Field(default=0)
    is_active: bool = Field(default=True)


class Category(CategoryBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    products: list["Product"] = Relationship(back_populates="category")


class ProductBase(SQLModel):
    title: str = Field(index=True, max_length=160)
    title_en: str = Field(default="", max_length=160)
    title_de: str = Field(default="", max_length=160)
    slug: str = Field(index=True, unique=True, max_length=180)
    description: str = Field(default="", max_length=4000)
    description_en: str = Field(default="", max_length=4000)
    description_de: str = Field(default="", max_length=4000)
    category_id: int | None = Field(default=None, foreign_key="category.id")
    base_price: float = Field(default=0, ge=0)
    currency: str = Field(default="EUR", max_length=3)
    status: ProductStatus = Field(default=ProductStatus.DRAFT)
    is_available_today: bool = Field(default=True)
    images: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    specifications: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    tags: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_featured: bool = Field(default=False)


class Product(ProductBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    category: Optional["Category"] = Relationship(back_populates="products")
    variants: list["ProductVariant"] = Relationship(back_populates="product")


class ProductVariantBase(SQLModel):
    product_id: int = Field(foreign_key="product.id", index=True)
    sku: str = Field(index=True, unique=True, max_length=80)
    title: str = Field(default="", max_length=160)
    title_en: str = Field(default="", max_length=160)
    title_de: str = Field(default="", max_length=160)
    attributes: dict[str, str] = Field(default_factory=dict, sa_column=Column(JSON))
    price: float = Field(default=0, ge=0)
    compare_at_price: float | None = Field(default=None, ge=0)
    image_url: str = Field(default="", max_length=500)
    is_active: bool = Field(default=True)


class ProductVariant(ProductVariantBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    product: "Product" = Relationship(back_populates="variants")


class CouponBase(SQLModel):
    code: str = Field(index=True, unique=True, max_length=60)
    description: str = Field(default="", max_length=255)
    coupon_type: CouponType = Field(default=CouponType.PERCENTAGE)
    value: float = Field(default=0, ge=0)
    min_order_value: float = Field(default=0, ge=0)
    max_discount_amount: float | None = Field(default=None, ge=0)
    usage_limit: int | None = Field(default=None, ge=1)
    per_customer_limit: int | None = Field(default=None, ge=1)
    active: bool = Field(default=True)
    starts_at: datetime | None = None
    ends_at: datetime | None = None


class Coupon(CouponBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
