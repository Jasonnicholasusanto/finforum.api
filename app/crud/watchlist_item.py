from __future__ import annotations
from typing import Iterable, List, Optional
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

    def create(
        self,
        session: Session,
        *,
        watchlist_id: int,
        obj_in: WatchlistItemCreate,
    ) -> WatchlistItem:
        """
        Create a single WatchlistItem for the specified watchlist.
        Delegates to the base CRUD create() for consistent commit/refresh handling.
        """
        # Merge extra field into the base create
        db_obj = super().create(session, obj_in=obj_in, watchlist_id=watchlist_id)
        return db_obj

    def create_many(
        self,
        session: Session,
        *,
        watchlist_id: int,
        items: Iterable[WatchlistItemCreate],
    ) -> List[WatchlistItem]:
        """
        Bulk create WatchlistItems for a given watchlist.
        Uses create() for each to ensure consistent validation and commit behavior.
        Commits once at the end for efficiency.
        """
        db_items: List[WatchlistItem] = []

        for item in items:
            db_obj = self.create(session, watchlist_id=watchlist_id, obj_in=item)
            db_items.append(db_obj)

        # Commit all pending inserts in a single transaction
        session.commit()

        # Refresh instances so they contain DB-generated fields (id, timestamps)
        for db_item in db_items:
            session.refresh(db_item)

        return db_items
    
    def update(
        self, session: Session, *, id: int, obj_in: WatchlistItemUpdate
    ) -> Optional[WatchlistItem]:
        """
        Update an existing WatchlistItem.
        """
        db_obj = session.get(WatchlistItem, id)
        if not db_obj:
            return None

        # Delegate to CRUDBase for patch-style updates
        return super().update(session, id=id, obj_in=obj_in)

    def remove(
        self,
        session: Session,
        *,
        id: int,
    ) -> Optional[WatchlistItem]:
        """
        Delete a WatchlistItem by ID.
        Returns the deleted item if successful, or None if not found.
        """
        db_obj = self.get(session, id=id)
        if not db_obj:
            return None

        # Leverage base remove() for consistency and transaction safety
        return super().remove(session, id=id)


watchlist_item = CRUDWatchlistItem(WatchlistItem)
