from typing import Optional, List
from sqlmodel import Session, select
from app.crud.base import CRUDBase
from app.models.watchlist_share import WatchlistShare
from app.schemas.watchlist_share import WatchlistShareCreate


class CRUDWatchlistShare(
    CRUDBase[WatchlistShare, WatchlistShareCreate, WatchlistShareCreate]
):
    def get_share(
        self, session: Session, *, watchlist_id: int, user_id: str
    ) -> Optional[WatchlistShare]:
        stmt = select(WatchlistShare).where(
            WatchlistShare.watchlist_id == watchlist_id,
            WatchlistShare.user_id == user_id,
        )
        return session.exec(stmt).first()

    def list_shared_users(
        self, session: Session, *, watchlist_id: int
    ) -> List[WatchlistShare]:
        stmt = select(WatchlistShare).where(WatchlistShare.watchlist_id == watchlist_id)
        return list(session.exec(stmt).all())

    def create(self, session, *, obj_in, **extra_fields):
        return super().create(session, obj_in=obj_in, **extra_fields)

    def update(
        self,
        session: Session,
        *,
        watchlist_id: int,
        user_id: str,
        can_edit: bool,
    ) -> Optional[WatchlistShare]:
        """
        Update the can_edit permission for an existing share record.
        """
        db_share = self.get_share(session, watchlist_id=watchlist_id, user_id=user_id)
        if not db_share:
            return None

        db_share.can_edit = can_edit
        session.add(db_share)
        session.commit()
        session.refresh(db_share)
        return db_share


watchlist_share = CRUDWatchlistShare(WatchlistShare)
