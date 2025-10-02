from typing import List
from sqlmodel import SQLModel

from app.schemas.watchlist import WatchlistBase
from app.schemas.watchlist_item import WatchlistItemBase


class WatchlistDetail(SQLModel):
    watchlist: WatchlistBase
    watchlist_items: List[WatchlistItemBase] | None


class WatchlistsDetail(SQLModel):
    watchlists: List[WatchlistDetail]
