from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.apps.iam.api.deps import get_current_user, get_db
from src.apps.iam.models.user import User
from src.apps.oms.models import CartItem, ProductVariant
from src.apps.oms.schemas import CartItemCreate, CartItemUpdate, CartRead
from src.apps.oms.service import build_cart_summary

router = APIRouter(prefix="/cart")


@router.get("/", response_model=CartRead)
async def get_cart(
    coupon_code: str | None = None,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CartRead:
    items, subtotal, tax_amount, shipping_fee, discount_amount, total_amount, currency, coupon = await build_cart_summary(
        session,
        user_id=current_user.id,
        coupon_code=coupon_code,
    )
    return CartRead(
        items=items,
        subtotal=subtotal,
        tax_amount=tax_amount,
        shipping_fee=shipping_fee,
        discount_amount=discount_amount,
        total_amount=total_amount,
        currency=currency,
        coupon_code=coupon.code if coupon else None,
    )


@router.post("/items", response_model=CartRead, status_code=status.HTTP_201_CREATED)
async def add_cart_item(
    payload: CartItemCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CartRead:
    variant = await session.get(ProductVariant, payload.variant_id)
    if variant is None or not variant.is_active:
        raise HTTPException(status_code=404, detail="Variant not found")
    existing_result = await session.execute(
        select(CartItem).where(CartItem.user_id == current_user.id, CartItem.variant_id == payload.variant_id)
    )
    item = existing_result.scalars().first()
    if item is None:
        item = CartItem(
            user_id=current_user.id,
            variant_id=payload.variant_id,
            quantity=payload.quantity,
            unit_price_snapshot=float(variant.price),
            currency=product.currency or "EUR",
        )
        session.add(item)
    else:
        item.quantity += payload.quantity
        item.unit_price_snapshot = float(variant.price)
    await session.commit()
    return await get_cart(current_user=current_user, session=session)


@router.patch("/items/{item_id}", response_model=CartRead)
async def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CartRead:
    item = await session.get(CartItem, item_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    item.quantity = payload.quantity
    await session.commit()
    return await get_cart(current_user=current_user, session=session)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(
    item_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    item = await session.get(CartItem, item_id)
    if item is None or item.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Cart item not found")
    await session.delete(item)
    await session.commit()
