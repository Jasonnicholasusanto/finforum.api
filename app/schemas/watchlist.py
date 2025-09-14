from __future__ import annotations

from enum import Enum
from typing import Optional
from uuid import UUID
from datetime import datetime

from pydantic import ConfigDict, Field
from sqlmodel import SQLModel


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


class WatchlistCreate(WatchlistBase):
    # Let clients request default; enforce “one default per user” in DB or service logic.
    is_default: bool = False


class WatchlistUpdate(SQLModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = Field(default=None, max_length=500)
    visibility: Optional[WatchlistVisibility] = None
    is_default: Optional[bool] = None


class WatchlistOut(WatchlistBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    is_default: bool
    created_at: datetime
    updated_at: datetime
