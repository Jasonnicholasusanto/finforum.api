# app/api/v1/endpoints/search_history.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.api.dependencies.profile import get_current_profile
from app.schemas.search_history import SearchHistoryRead, SearchType
from app.services import search_history_service
from app.api.deps import SessionDep
from fastapi import Query


router = APIRouter(prefix="/search-history", tags=["Search History"])


@router.get("/", response_model=List[SearchHistoryRead])
def get_recent_searches(
    db: SessionDep,
    profile=Depends(get_current_profile),
    limit: int = 10,
):
    return search_history_service.list_recent_searches(db, profile.id, limit)


@router.post("/", response_model=SearchHistoryRead, status_code=status.HTTP_201_CREATED)
def create_search_entry(
    db: SessionDep,
    profile=Depends(get_current_profile),
    query: str = Query(..., min_length=1),
    type: SearchType = Query(SearchType.GENERAL),
):
    """
    Record a new search query for the current user.
    Deduplicates by query, updates timestamp if already exists.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    entry = search_history_service.add_search_history(db, profile.id, query, type)
    return entry


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def clear_search_history(
    db: SessionDep,
    profile=Depends(get_current_profile),
):
    """
    Delete all search history for the current user.
    """
    deleted_count = search_history_service.clear_search_history(db, profile.id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="No search history found")
    return None
