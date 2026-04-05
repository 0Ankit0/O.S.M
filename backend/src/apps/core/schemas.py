from __future__ import annotations

import base64
import json
from typing import Any, Generic, Sequence, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    skip: int = Field(default=0, ge=0, description="Number of items to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Number of items to return (max 100)")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: Sequence[T]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def create(cls, items: Sequence[T], total: int, skip: int, limit: int):
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=(skip + len(items)) < total
        )


class CursorPage(BaseModel, Generic[T]):
    items: Sequence[T]
    next_cursor: str | None = None
    has_more: bool = False

    @classmethod
    def from_items(
        cls,
        items: Sequence[T],
        *,
        next_cursor_value: dict[str, Any] | None,
        has_more: bool,
    ) -> "CursorPage[T]":
        encoded_cursor: str | None = None
        if next_cursor_value is not None:
            encoded_cursor = base64.urlsafe_b64encode(
                json.dumps(next_cursor_value).encode("utf-8")
            ).decode("utf-8")
        return cls(items=items, next_cursor=encoded_cursor, has_more=has_more)


class APIErrorDetail(BaseModel):
    error: str
    message: str
    details: dict[str, Any] | list[Any] | None = None
    trace_id: str | None = None
