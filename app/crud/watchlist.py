# app/crud/watchlist.py
from __future__ import annotations

import uuid
from typing import List, Optional

from sqlalchemy import func, update as sa_update
from sqlmodel import Session, select

from app.crud.base import CRUDBase
from app.models.user_profile import UserProfile
from app.models.watchlist import Watchlist
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate, WatchlistVisibility


class CRUDWatchlist(CRUDBase[Watchlist, WatchlistCreate, WatchlistUpdate]):
    # ----- GETs -----
    def get_by_id(self, session: Session, *, id: int) -> Watchlist | None:
        return session.get(Watchlist, id)

    def get_public_by_user_and_name(
        self, session: Session, *, user_id: uuid.UUID, name: str
    ) -> Watchlist | None:
        """Fetch a user's watchlist by name (case-insensitive; trims input)."""
        stmt = (
            select(Watchlist)
            .where(
                Watchlist.user_id == user_id,
                func.lower(Watchlist.name) == func.lower(func.trim(name)),
                Watchlist.visibility == WatchlistVisibility.PUBLIC.value,
            )
            .limit(1)
        )
        return session.exec(stmt).first()

    def get_public_by_username_and_name(
        self,
        session: Session,
        *,
        username: str,
        name: str,
    ) -> Watchlist | None:
        """
        Fetch a watchlist by owner's username and the list name (both case-insensitive).

        Args:
            username: Owner's username (case-insensitive).
            name:     Watchlist name (case-insensitive).
            public_only: If True, only return if the watchlist is PUBLIC,
                         unless current_user_id matches the owner.
            current_user_id: The caller's user id (to allow owner's private lists when public_only=True).

        Returns:
            Watchlist | None
        """
        stmt = (
            select(Watchlist)
            .join(UserProfile, UserProfile.id == Watchlist.user_id)
            .where(
                func.lower(UserProfile.username) == func.lower(func.trim(username)),
                func.lower(Watchlist.name) == func.lower(func.trim(name)),
                Watchlist.visibility == WatchlistVisibility.PUBLIC.value,
            )
            .limit(1)
        )

        return session.exec(stmt).first()

    def list_public_by_name(
        self, session: Session, *, name: str, limit: int = 20, offset: int = 0
    ) -> List[Watchlist]:
        """Case-insensitive partial match on name, public only."""
        n = name.strip()
        stmt = (
            select(Watchlist)
            .where(
                Watchlist.visibility == WatchlistVisibility.PUBLIC.value,
                Watchlist.name.ilike(f"%{n}%"),
            )
            .order_by(Watchlist.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(session.exec(stmt).all())

    def list_by_user(
        self,
        session: Session,
        *,
        user_id: uuid.UUID,
        q: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Watchlist]:
        """
        List watchlists owned by user.
        Optional 'q' filters by name ILIKE '%q%'.
        """
        stmt = select(Watchlist).where(Watchlist.user_id == user_id)
        if q:
            stmt = stmt.where(Watchlist.name.ilike(f"%{q.strip()}%"))
        stmt = (
            stmt.order_by(
                Watchlist.is_default.desc(),  # show default first
                Watchlist.created_at.asc(),
            )
            .limit(limit)
            .offset(offset)
        )
        return list(session.exec(stmt).all())

    def get_default_for_user(
        self, session: Session, *, user_id: uuid.UUID
    ) -> Watchlist | None:
        stmt = (
            select(Watchlist)
            .where(Watchlist.user_id == user_id, Watchlist.is_default.is_(True))
            .limit(1)
        )
        return session.exec(stmt).first()

    # ----- CREATE / UPDATE / DELETE -----
    def create(
        self, session: Session, *, owner_id: uuid.UUID, obj_in: WatchlistCreate
    ) -> Watchlist:
        """
        Create a watchlist for the owner. If obj_in.is_default=True,
        unset other defaults for this user within the same transaction.
        """
        if obj_in.is_default:
            session.exec(
                sa_update(Watchlist)
                .where(Watchlist.user_id == owner_id)
                .values(is_default=False)
            )

        db_obj = Watchlist(**obj_in.model_dump(exclude_unset=True))
        db_obj.user_id = owner_id
        session.add(db_obj)
        session.flush()  # populate db_obj.id
        return db_obj

    def update(
        self, session: Session, *, id: int, obj_in: WatchlistUpdate
    ) -> Watchlist | None:
        """
        Update fields by id. If setting is_default=True, unset other defaults
        for the same user first.
        """
        db_obj = session.get(Watchlist, id)
        if not db_obj:
            return None

        if obj_in.is_default is True:
            session.exec(
                sa_update(Watchlist)
                .where(
                    Watchlist.user_id == db_obj.user_id,
                    Watchlist.id != id,
                )
                .values(is_default=False)
            )

        # delegate to base for partial update semantics
        return super().update(session, id=id, obj_in=obj_in)

    def delete(self, session: Session, *, id: int) -> bool:
        """Delete by id. Returns True if deleted, False if not found."""
        obj = session.get(Watchlist, id)
        if not obj:
            return False
        session.delete(obj)
        # NOTE: if you guarantee at most one default per user, consider
        # auto-promoting another watchlist to default here if you delete the default.
        return True


watchlist = CRUDWatchlist(Watchlist)
