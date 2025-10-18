from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.watchlist import WatchlistBase, WatchlistCreate
from app.schemas.watchlist_detail import WatchlistDetail, WatchlistsDetail
from app.schemas.watchlist_item import WatchlistItemBase, WatchlistItemCreate
from app.services.watchlist_service import (
    add_item_to_watchlist,
    add_many_items_to_watchlist,
    create_watchlist_for_user,
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


@router.post("/", status_code=201)
def create_watchlist(
    user: CurrentUser,
    db: SessionDep,
    watchlist_data: WatchlistCreate,
    items: Optional[List[WatchlistItemCreate]] = None,
):
    """
    Create a new watchlist for the authenticated user.
    Optionally accepts a list of initial watchlist items.
    """
    try:
        # 1. Create the new watchlist
        new_watchlist = create_watchlist_for_user(
            db,
            user_id=user.id,
            watchlist_data=watchlist_data,
        )

        # 2. Add items if provided
        new_items = []
        if items:
            new_items = add_many_items_to_watchlist(
                session=db,
                watchlist_id=new_watchlist.id,
                items=items,
            )

        # 3. Return combined response
        return {
            "message": "Watchlist created successfully.",
            "watchlist": new_watchlist,
            "watchlist_items": new_items,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create watchlist: {str(e)}",
        )


@router.post("/{watchlist_id}/items")
def add_watchlist_item(
    watchlist_id: int,
    item: WatchlistItemCreate,
    user: CurrentUser,
    db: SessionDep,
):
    # (optional) check if user can edit this watchlist
    new_item = add_item_to_watchlist(
        session=db,
        watchlist_id=watchlist_id,
        symbol=item.symbol,
        exchange=item.exchange,
        note=item.note,
        position=item.position,
    )
    return {"message": "Item added successfully", "item": new_item}


@router.post("/{watchlist_id}/items/bulk")
def add_bulk_watchlist_items(
    watchlist_id: int,
    items: List[WatchlistItemCreate],
    user: CurrentUser,
    db: SessionDep,
):
    # Optional: validate ownership/edit rights before proceeding
    new_items = add_many_items_to_watchlist(
        session=db,
        watchlist_id=watchlist_id,
        items=items,
    )
    return {"count": len(new_items), "items": new_items}
