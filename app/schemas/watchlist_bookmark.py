import uuid
from sqlmodel import SQLModel


class WatchlistBookmarkBase(SQLModel):
    watchlist_id: int
    user_id: uuid.UUID
    