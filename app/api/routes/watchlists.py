from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.watchlist import WatchlistBase
from app.schemas.watchlist_detail import WatchlistDetail, WatchlistsDetail
from app.schemas.watchlist_item import WatchlistItemBase
from app.services.watchlist_service import (
    load_items_for_watchlists,
    search_public_watchlists_by_name,
)


router = APIRouter(prefix="/watchlists", tags=["watchlists"])


# Public: Search public watchlists by name (case-insensitive, partial match)
@router.get("/@{name}", response_model=WatchlistsDetail)
def get_watchlists_by_name(
    name: str,
    user: CurrentUser,  # keep if your API requires auth; otherwise remove
    db: SessionDep,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Search PUBLIC watchlists by name (case-insensitive, partial match).
    Returns multiple results.
    """
    if not name.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Name is required."
        )

    watchlists = search_public_watchlists_by_name(
        db, name=name, limit=limit, offset=offset
    )
    if not watchlists:
        return []

    # Batch-load items to avoid N+1
    id_list = [w.id for w in watchlists if w.id is not None]
    items_map = load_items_for_watchlists(db, id_list)

    results = [
        WatchlistDetail(
            watchlist=WatchlistBase.model_validate(w, from_attributes=True),
            watchlist_items=[
                WatchlistItemBase.model_validate(i, from_attributes=True)
                for i in items_map.get(w.id, [])
            ]
            or None,
        )
        for w in watchlists
    ]

    return WatchlistsDetail(watchlists=results)
