from typing import List, Optional
from pydantic import BaseModel

from app.schemas.watchlist import WatchlistPublicOut, WatchlistCreate
from app.schemas.watchlist_item import WatchlistItemBase, WatchlistItemCreateWithoutId


class WatchlistDetail(BaseModel):
    watchlist: WatchlistPublicOut
    watchlist_items: List[WatchlistItemBase] | None


class WatchlistsDetail(BaseModel):
    watchlists: List[WatchlistDetail]


class WatchlistDetailCreateRequest(BaseModel):
    watchlist_data: WatchlistCreate
    items: Optional[List[WatchlistItemCreateWithoutId]] = None
