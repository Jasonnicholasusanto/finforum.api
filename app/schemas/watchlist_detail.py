from typing import List, Optional
from sqlmodel import SQLModel

from app.schemas.watchlist import WatchlistPublicOut, WatchlistCreate
from app.schemas.watchlist_item import WatchlistItemBase, WatchlistItemCreateWithoutId


class WatchlistDetail(SQLModel):
    watchlist: WatchlistPublicOut
    watchlist_items: List[WatchlistItemBase] | None


class WatchlistsDetail(SQLModel):
    watchlists: List[WatchlistDetail]


class WatchlistDetailCreateRequest(SQLModel):
    watchlist_data: WatchlistCreate
    items: Optional[List[WatchlistItemCreateWithoutId]] = None
