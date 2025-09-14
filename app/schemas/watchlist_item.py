from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel


class WatchlistItemBase(SQLModel):
    symbol: str = Field(min_length=1)
    exchange: str = Field(min_length=1)
    note: Optional[str] = Field(default=None, max_length=1000)
    position: Optional[int] = Field(default=None, ge=0)


class WatchlistItemCreate(WatchlistItemBase):
    watchlist_id: int


class WatchlistItemUpdate(SQLModel):
    symbol: Optional[str] = Field(default=None, min_length=1)
    exchange: Optional[str] = Field(default=None, min_length=1)
    note: Optional[str] = Field(default=None, max_length=1000)
    position: Optional[int] = Field(default=None, ge=0)


class WatchlistItemOut(WatchlistItemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    watchlist_id: int
    created_at: datetime
    updated_at: datetime
