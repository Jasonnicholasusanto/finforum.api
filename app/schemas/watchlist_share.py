from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class WatchlistShareBase(BaseModel):
    watchlist_id: int
    user_id: UUID
    can_edit: bool = False


class WatchlistShareCreate(WatchlistShareBase):
    pass


class WatchlistShareUpdate(BaseModel):
    can_edit: bool


class WatchlistShareOut(WatchlistShareBase):
    created_at: datetime
