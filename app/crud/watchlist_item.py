from __future__ import annotations
from typing import Iterable, List
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.watchlist_item import WatchlistItem
from app.schemas.watchlist_item import WatchlistItemCreate, WatchlistItemUpdate


class CRUDWatchlistItem(
    CRUDBase[WatchlistItem, WatchlistItemCreate, WatchlistItemUpdate]
):
    def list_by_watchlist(
        self, session: Session, *, watchlist_id: int
    ) -> List[WatchlistItem]:
        stmt = (
            select(WatchlistItem)
            .where(WatchlistItem.watchlist_id == watchlist_id)
            .order_by(
                WatchlistItem.position.asc().nulls_last(),
                WatchlistItem.created_at.asc(),
            )
        )
        return list(session.exec(stmt).all())

    def create_many(
        self,
        session: Session,
        *,
        watchlist_id: int,
        items: Iterable[WatchlistItemCreate],
    ) -> List[WatchlistItem]:
        out: List[WatchlistItem] = []
        for it in items:
            db_obj = WatchlistItem(
                **{**it.model_dump(exclude_unset=True), "watchlist_id": watchlist_id}
            )
            session.add(db_obj)
            out.append(db_obj)
        session.flush()
        return out

    def delete_one(self, session: Session, *, id: int) -> bool:
        obj = session.get(WatchlistItem, id)
        if not obj:
            return False
        session.delete(obj)
        return True


watchlist_item = CRUDWatchlistItem(WatchlistItem)
