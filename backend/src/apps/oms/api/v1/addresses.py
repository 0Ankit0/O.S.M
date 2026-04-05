from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.apps.iam.api.deps import get_current_user, get_db
from src.apps.iam.models.user import User
from src.apps.oms.models import CustomerAddress
from src.apps.oms.schemas import AddressCreate, AddressRead
from src.apps.oms.service import ensure_address_belongs_to_user, get_serviceable_zone

router = APIRouter(prefix="/addresses")


@router.get("/", response_model=list[AddressRead])
async def list_addresses(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> list[CustomerAddress]:
    result = await session.execute(
        select(CustomerAddress)
        .where(CustomerAddress.user_id == current_user.id, CustomerAddress.is_archived == False)  # noqa: E712
        .order_by(CustomerAddress.is_default.desc(), CustomerAddress.id.desc())
    )
    return result.scalars().all()


@router.post("/", response_model=AddressRead, status_code=status.HTTP_201_CREATED)
async def create_address(
    payload: AddressCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CustomerAddress:
    if payload.is_default:
        existing_result = await session.execute(
            select(CustomerAddress).where(CustomerAddress.user_id == current_user.id)
        )
        for address in existing_result.scalars().all():
            address.is_default = False

    zone = await get_serviceable_zone(session, payload.postal_code)
    address = CustomerAddress(
        user_id=current_user.id,
        is_serviceable=zone is not None,
        **payload.model_dump(),
    )
    session.add(address)
    await session.commit()
    await session.refresh(address)
    return address


@router.patch("/{address_id}", response_model=AddressRead)
async def update_address(
    address_id: int,
    payload: AddressCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> CustomerAddress:
    address = await ensure_address_belongs_to_user(session, address_id=address_id, user_id=current_user.id)
    for key, value in payload.model_dump().items():
        setattr(address, key, value)
    zone = await get_serviceable_zone(session, address.postal_code)
    address.is_serviceable = zone is not None
    await session.commit()
    await session.refresh(address)
    return address


@router.delete("/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def archive_address(
    address_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    address = await ensure_address_belongs_to_user(session, address_id=address_id, user_id=current_user.id)
    if address.is_default:
        raise HTTPException(status_code=409, detail="Default address cannot be archived directly")
    address.is_archived = True
    await session.commit()
