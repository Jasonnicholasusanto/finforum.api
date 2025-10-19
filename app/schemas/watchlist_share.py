from sqlmodel import SQLModel
from uuid import UUID
from datetime import datetime


class WatchlistShareBase(SQLModel):
    watchlist_id: int
    user_id: UUID
    can_edit: bool = False


class WatchlistShareCreate(WatchlistShareBase):
    pass


class WatchlistShareUpdate(SQLModel):
    can_edit: bool


class WatchlistShareOut(WatchlistShareBase):
    created_at: datetime
