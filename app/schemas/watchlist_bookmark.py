import uuid
from pydantic import BaseModel


class WatchlistBookmarkBase(BaseModel):
    watchlist_id: int
    user_id: uuid.UUID
