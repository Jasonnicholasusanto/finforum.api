from __future__ import annotations

from enum import Enum
from datetime import datetime
from pydantic import BaseModel


class SearchType(str, Enum):
    STOCK = "stock"
    USER = "user"
    FORUM = "forum"
    WATCHLIST = "watchlist"
    GENERAL = "general"


class SearchHistoryCreate(BaseModel):
    query: str
    type: SearchType = SearchType.GENERAL


class SearchHistoryRead(BaseModel):
    id: int
    query: str
    type: SearchType
    created_at: datetime
