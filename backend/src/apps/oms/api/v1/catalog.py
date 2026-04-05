from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import col, select

from src.apps.core.schemas import CursorPage
from src.apps.iam.api.deps import get_current_active_superuser, get_current_user, get_db
from src.apps.iam.models.user import User
from src.apps.oms.models import Category, Coupon, Product, ProductVariant
from src.apps.oms.schemas import (
    AdminOverviewRead,
    CategoryCreate,
    CategoryRead,
    CouponCreate,
    CouponRead,
    ProductCreate,
    ProductAdminUpdate,
    ProductRead,
    ProductVariantRead,
)
from src.apps.oms.service import decode_cursor

router = APIRouter()


@router.get("/categories", response_model=list[CategoryRead])
async def list_categories(
    session: AsyncSession = Depends(get_db),
) -> list[Category]:
    result = await session.execute(select(Category).where(Category.is_active).order_by(col(Category.display_order)))
    return result.scalars().all()


@router.post("/categories", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: CategoryCreate,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> Category:
    del current_user
    category = Category(**payload.model_dump())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@router.get("/products", response_model=CursorPage[ProductRead])
async def list_products(
    cursor: str | None = Query(default=None),
    limit: int = Query(default=12, ge=1, le=50),
    search: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    in_stock: bool | None = Query(default=None),
    sort: str = Query(default="newest"),
    session: AsyncSession = Depends(get_db),
) -> CursorPage[ProductRead]:
    decoded_cursor = decode_cursor(cursor)
    query = select(Product).where(Product.status == "active")
    if category_id is not None:
        query = query.where(Product.category_id == category_id)
    if search:
        like = f"%{search.strip()}%"
        query = query.where((Product.title.ilike(like)) | (Product.description.ilike(like)))
    if decoded_cursor and decoded_cursor.get("id"):
        query = query.where(Product.id < int(decoded_cursor["id"]))

    if sort == "price_asc":
        query = query.order_by(col(Product.base_price).asc(), col(Product.id).desc())
    elif sort == "price_desc":
        query = query.order_by(col(Product.base_price).desc(), col(Product.id).desc())
    else:
        query = query.order_by(col(Product.id).desc())

    result = await session.execute(query.limit(limit + 1))
    products = result.scalars().all()
    has_more = len(products) > limit
    products = products[:limit]

    product_reads: list[ProductRead] = []
    for product in products:
        variants = (
            await session.execute(
                select(ProductVariant).where(
                    ProductVariant.product_id == product.id,
                    ProductVariant.is_active,
                )
            )
        ).scalars().all()
        if in_stock is True and not product.is_available_today:
            continue
        product_reads.append(
            ProductRead(
                **product.model_dump(),
                id=product.id,
                variants=[ProductVariantRead(**variant.model_dump(), id=variant.id, product_id=variant.product_id) for variant in variants],
            )
        )

    next_cursor_value = {"id": products[-1].id} if has_more and products else None
    return CursorPage.from_items(product_reads, next_cursor_value=next_cursor_value, has_more=has_more)


@router.get("/products/{product_id}", response_model=ProductRead)
async def get_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
) -> ProductRead:
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    variants = (
        await session.execute(
            select(ProductVariant).where(ProductVariant.product_id == product.id)
        )
    ).scalars().all()
    return ProductRead(
        **product.model_dump(),
        id=product.id,
        variants=[ProductVariantRead(**variant.model_dump(), id=variant.id, product_id=variant.product_id) for variant in variants],
    )


@router.post("/products", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductCreate,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> ProductRead:
    del current_user
    data = payload.model_dump(exclude={"variants"})
    product = Product(**data)
    session.add(product)
    await session.flush()
    variants: list[ProductVariant] = []
    for variant_payload in payload.variants:
        variant = ProductVariant(product_id=product.id, **variant_payload.model_dump())
        session.add(variant)
        variants.append(variant)
    await session.commit()
    await session.refresh(product)
    for variant in variants:
        await session.refresh(variant)
    return ProductRead(
        **product.model_dump(),
        id=product.id,
        variants=[ProductVariantRead(**variant.model_dump(), id=variant.id, product_id=variant.product_id) for variant in variants],
    )


@router.get("/admin/catalog/products", response_model=list[ProductRead])
async def admin_list_products(
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> list[ProductRead]:
    del current_user
    result = await session.execute(select(Product).order_by(col(Product.id).desc()))
    products = result.scalars().all()
    payload: list[ProductRead] = []
    for product in products:
        variants = (
            await session.execute(select(ProductVariant).where(ProductVariant.product_id == product.id))
        ).scalars().all()
        payload.append(
            ProductRead(
                **product.model_dump(),
                id=product.id,
                variants=[ProductVariantRead(**variant.model_dump(), id=variant.id, product_id=variant.product_id) for variant in variants],
            )
        )
    return payload


@router.patch("/admin/catalog/products/{product_id}", response_model=ProductRead)
async def admin_update_product(
    product_id: int,
    payload: ProductAdminUpdate,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> ProductRead:
    del current_user
    product = await session.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(product, key, value)
    await session.commit()
    await session.refresh(product)
    variants = (
        await session.execute(select(ProductVariant).where(ProductVariant.product_id == product.id))
    ).scalars().all()
    return ProductRead(
        **product.model_dump(),
        id=product.id,
        variants=[ProductVariantRead(**variant.model_dump(), id=variant.id, product_id=variant.product_id) for variant in variants],
    )


@router.post("/coupons", response_model=CouponRead, status_code=status.HTTP_201_CREATED)
async def create_coupon(
    payload: CouponCreate,
    current_user: User = Depends(get_current_active_superuser),
    session: AsyncSession = Depends(get_db),
) -> Coupon:
    del current_user
    coupon = Coupon(**payload.model_dump(), code=payload.code.upper())
    session.add(coupon)
    await session.commit()
    await session.refresh(coupon)
    return coupon


@router.get("/coupons/{code}", response_model=CouponRead)
async def get_coupon(
    code: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> Coupon:
    del current_user
    result = await session.execute(
        select(Coupon).where(Coupon.code == code.upper())
    )
    coupon = result.scalars().first()
    if coupon is None:
        raise HTTPException(status_code=404, detail="Coupon not found")
    return coupon
