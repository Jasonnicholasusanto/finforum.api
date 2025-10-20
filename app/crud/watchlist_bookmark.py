from app.crud.base import CRUDBase
from app.models.watchlist_bookmark import WatchlistBookmark
from sqlmodel import Session, select
from uuid import UUID

from app.schemas.watchlist_bookmark import WatchlistBookmarkBase


class CRUDWatchlistBookmark(CRUDBase[WatchlistBookmark, WatchlistBookmarkBase, WatchlistBookmarkBase]):
    def get_watchlist_bookmark(
        self, session: Session, *, watchlist_id: int, user_id: UUID
    ) -> WatchlistBookmark | None:
        stmt = (
            select(WatchlistBookmark)
            .where(
                WatchlistBookmark.watchlist_id == watchlist_id,
                WatchlistBookmark.user_id == user_id,
            )
            .limit(1)
        )
        return session.exec(stmt).first()
    
    def create(
        self, session: Session, *, obj_in: WatchlistBookmarkBase
    ) -> WatchlistBookmark:        
        db_obj = super().create(session, obj_in=obj_in)

        return db_obj

    def remove(
        self, session: Session, *, id: int
    ) -> bool:
        return super().remove(session, id=id)

    def list_user_bookmarks(
        self, session: Session, *, user_id: UUID, limit: int = 10, offset: int = 0
    ):
        stmt = (
            select(WatchlistBookmark)
            .where(WatchlistBookmark.user_id == user_id)
            .order_by(WatchlistBookmark.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(session.exec(stmt).all())


watchlist_bookmark = CRUDWatchlistBookmark(WatchlistBookmark)
