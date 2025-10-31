from __future__ import annotations

from enum import Enum
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel

from app.schemas.watchlist_item import WatchlistItemBase


class WatchlistVisibility(str, Enum):
    # If your DB enum also includes "unlisted", just add it here.
    PRIVATE = "private"
    PUBLIC = "public"
    SHARED = "shared"


# ---------- SCHEMAS (Pydantic/SQLModel) ----------


class WatchlistBase(SQLModel):
    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    visibility: WatchlistVisibility = WatchlistVisibility.PRIVATE.value
    forked_from_id: Optional[int] = None 
    forked_at: Optional[datetime] = None
    original_author_id: Optional[UUID] = None
    fork_count: Optional[int] = 0


class WatchlistCreate(WatchlistBase):
    # Let clients request default; enforce “one default per user” in DB or service logic.
    is_default: bool = False


class WatchlistUpdate(SQLModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_default: Optional[bool] = None
    visibility: Optional[WatchlistVisibility] = None


class WatchlistPublicOut(WatchlistBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class WatchlistOut(WatchlistBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    is_default: bool
    created_at: datetime
    updated_at: datetime


class WatchlistForkOut(SQLModel):
    """
    Response model when a watchlist is forked.
    """
    message: str
    forked_watchlist: WatchlistOut
    forked_items: Optional[List[WatchlistItemBase]] = None


class WatchlistForkListOut(SQLModel):
    """
    Response model listing all forks for a given watchlist.
    """
    message: str
    count: int
    forks: List[WatchlistPublicOut]


class WatchlistLineageOut(SQLModel):
    """
    Shows fork lineage for a watchlist (who forked from whom).
    """
    original_author_id: UUID
    forked_from_id: Optional[int]
    forked_at: Optional[datetime]
    fork_count: int
