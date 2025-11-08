from typing import List
from uuid import UUID
from sqlmodel import Session
from app.crud.search_history import search_history as crud_search_history
from app.models.search_history import SearchHistory
from app.schemas.search_history import (
    SearchHistoryCreate,
    SearchHistoryRead,
    SearchType,
)


def add_search_history(
    db: Session,
    user_id: UUID,
    query: str,
    type: SearchType = SearchType.GENERAL,
) -> SearchHistoryRead:
    """Add or update a user search query (deduplicates by query)."""
    obj_in = SearchHistoryCreate(query=query, type=type)
    result = crud_search_history.create(db, user_id=user_id, obj_in=obj_in)
    return SearchHistoryRead.model_validate(result, from_attributes=True)


def list_recent_searches(
    db: Session, user_id: UUID, limit: int = 5
) -> List[SearchHistory]:
    """Return the user's recent searches (most recent first)."""
    return crud_search_history.list_by_user(db, user_id=user_id, limit=limit)


def clear_search_history(db: Session, user_id: UUID) -> int:
    """Delete all search history for a user."""
    return crud_search_history.delete_all_by_user(db, user_id=user_id)
