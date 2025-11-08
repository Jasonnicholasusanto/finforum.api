from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, desc, delete, func
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.crud.base import CRUDBase
from app.models.search_history import SearchHistory
from app.schemas.search_history import SearchHistoryCreate, SearchHistoryRead


class CRUDSearchHistory(
    CRUDBase[SearchHistory, SearchHistoryCreate, SearchHistoryRead]
):
    """CRUD operations for user search history."""

    # ----- GET -----
    def get_by_id(self, session: Session, *, id: int) -> Optional[SearchHistory]:
        """Fetch a single search history record by ID."""
        return session.get(SearchHistory, id)

    # ----- LIST -----
    def list_by_user(
        self,
        session: Session,
        *,
        user_id: UUID,
        limit: int = 10,
        offset: int = 0,
    ) -> List[SearchHistory]:
        """List the most recent searches for a given user."""
        stmt = (
            select(SearchHistory)
            .where(SearchHistory.user_id == user_id)
            .order_by(desc(SearchHistory.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(session.exec(stmt).scalars().all())

    def list_distinct_queries(
        self,
        session: Session,
        *,
        user_id: UUID,
        limit: int = 10,
    ) -> List[str]:
        """List unique search queries for a user (most recent first)."""
        stmt = (
            select(func.distinct(SearchHistory.query))
            .where(SearchHistory.user_id == user_id)
            .order_by(desc(func.max(SearchHistory.created_at)))
            .limit(limit)
        )
        return [row[0] for row in session.exec(stmt).all()]

    # ----- CREATE -----
    def create(
        self,
        session: Session,
        *,
        user_id: UUID,
        obj_in: SearchHistoryCreate,
    ) -> SearchHistory:
        """
        Create a new search history entry.
        Deduplicates by query for each user: if query exists, update its timestamp instead.
        """
        existing = (
            session.exec(
                select(SearchHistory).where(
                    SearchHistory.user_id == user_id,
                    func.lower(SearchHistory.query)
                    == func.lower(func.trim(obj_in.query)),
                    SearchHistory.type == obj_in.type,
                )
            )
            .scalars()
            .one_or_none()
        )

        if existing:
            # db_obj = super().update(session, id=existing.id, obj_in=obj_in)
            existing.created_at = datetime.now(timezone.utc)
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

        # Otherwise create a new one
        try:
            db_obj = super().create(session, obj_in=obj_in, user_id=user_id)
            return db_obj
        except IntegrityError:
            session.rollback()
            raise ValueError("Failed to insert search history")

    # ----- DELETE -----
    def delete_all_by_user(self, session: Session, *, user_id: UUID) -> int:
        """Delete all search history for a given user. Returns number deleted."""
        stmt = delete(SearchHistory).where(SearchHistory.user_id == user_id)
        result = session.exec(stmt)
        session.commit()
        return result.rowcount or 0


search_history = CRUDSearchHistory(SearchHistory)
