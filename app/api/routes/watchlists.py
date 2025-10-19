from typing import List
import uuid
from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import CurrentUser, SessionDep
from app.schemas.watchlist import WatchlistOut, WatchlistPublicOut, WatchlistUpdate
from app.schemas.watchlist_detail import (
    WatchlistDetail,
    WatchlistDetailCreateRequest,
    WatchlistsDetail,
)
from app.schemas.watchlist_item import (
    WatchlistItemBase,
    WatchlistItemCreate,
    WatchlistItemCreateWithoutId,
)
from app.schemas.watchlist_share import (
    WatchlistShareCreate,
    WatchlistShareOut,
    WatchlistShareUpdate,
)
from app.services.user_profile_service import get_user_profile_by_auth
from app.services.watchlist_service import (
    add_item_to_watchlist,
    add_many_items_to_watchlist,
    create_watchlist_for_user,
    delete_watchlist,
    delete_watchlist_item,
    load_items_for_watchlists,
    search_public_watchlists_by_name,
    share_watchlist_with_user,
    update_user_watchlist,
    update_watchlist_share_permission,
    user_can_edit_watchlist,
    watchlist_item_exists,
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
            watchlist=WatchlistPublicOut.model_validate(w, from_attributes=True),
            watchlist_items=[
                WatchlistItemBase.model_validate(i, from_attributes=True)
                for i in items_map.get(w.id, [])
            ]
            or None,
        )
        for w in watchlists
    ]

    return WatchlistsDetail(watchlists=results)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_watchlist(
    user: CurrentUser,
    db: SessionDep,
    payload: WatchlistDetailCreateRequest,
):
    """
    Create a new watchlist for the authenticated user.
    Optionally accepts a list of initial watchlist items.
    """
    try:
        watchlist_data = payload.watchlist_data
        items = payload.items

        # 1. Get user profile
        profile = get_user_profile_by_auth(db, auth_id=user.id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found. Please complete registration.",
            )

        # 2. Create the new watchlist
        new_watchlist = create_watchlist_for_user(
            db,
            user_id=profile.id,
            watchlist_data=watchlist_data,
        )

        # 3. Add items if provided
        new_items = []
        if items:
            new_items = add_many_items_to_watchlist(
                session=db,
                watchlist_id=new_watchlist.id,
                items=items,
            )

        # 4. Return combined response
        return {
            "message": "Watchlist created successfully.",
            "watchlist": new_watchlist,
            "watchlist_items": new_items,
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create watchlist: {str(e)}",
        )


@router.post("/add-item")
def add_watchlist_item(
    item: WatchlistItemCreate,
    user: CurrentUser,
    db: SessionDep,
):
    # 1. Get user profile (not auth user)
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Add the item
    new_item = add_item_to_watchlist(
        session=db,
        item=item,
        user_profile_id=profile.id,
    )
    return {"message": "Item added successfully", "item": new_item}


@router.post("/add-items/{watchlist_id}")
def add_bulk_watchlist_items(
    watchlist_id: int,
    items: List[WatchlistItemCreateWithoutId],
    user: CurrentUser,
    db: SessionDep,
):
    # 1. Get user profile (not auth user)
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Validate edit permissions
    user_access = user_can_edit_watchlist(
        session=db,
        watchlist_id=watchlist_id,
        user_id=profile.id,
    )
    if not user_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this watchlist.",
        )

    # 3. Check for duplicates within the provided items
    watchlist_items_existing_symbols = set()
    for item in items:
        if watchlist_item_exists(
            session=db,
            watchlist_id=watchlist_id,
            symbol=item.symbol,
            exchange=item.exchange,
        ):
            watchlist_items_existing_symbols.add(item.symbol)
    if watchlist_items_existing_symbols:
        symbols_list = ", ".join(sorted(watchlist_items_existing_symbols))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Symbols [{symbols_list}] already exists in this watchlist.",
        )

    # 4. Add the items in bulk
    new_items = add_many_items_to_watchlist(
        session=db,
        watchlist_id=watchlist_id,
        items=items,
    )

    return {"count": len(new_items), "items": new_items}


@router.delete("/item/{item_id}", status_code=status.HTTP_200_OK)
def delete_watchlist_item_route(
    item_id: int,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Delete a specific watchlist item if the user has edit access.
    """
    # 1. Get user profile
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Perform deletion
    deleted_item = delete_watchlist_item(
        session=db,
        item_id=item_id,
        user_profile_id=profile.id,
    )

    if not deleted_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found or already deleted.",
        )

    return {"message": "Item deleted successfully.", "deleted_item": deleted_item}


@router.delete("/{watchlist_id}", status_code=status.HTTP_200_OK)
def delete_watchlist_route(
    watchlist_id: int,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Delete a watchlist owned by the authenticated user.
    All related items and shares will be deleted via ON DELETE CASCADE.
    """
    # 1. Get user profile
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Delete the watchlist (ownership check inside)
    deleted_watchlist = delete_watchlist(
        session=db,
        watchlist_id=watchlist_id,
        user_profile_id=profile.id,
    )

    if not deleted_watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found or already deleted.",
        )

    return {
        "message": "Watchlist deleted successfully.",
        "deleted_watchlist": deleted_watchlist,
    }


@router.post("/share", response_model=WatchlistShareOut)
def share_watchlist(
    share_data: WatchlistShareCreate,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Share a watchlist with another user.
    Only the owner of the watchlist can perform this action.
    """
    # 1. Get owner profile
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Perform the share
    shared = share_watchlist_with_user(
        session=db,
        watchlist_id=share_data.watchlist_id,
        owner_profile_id=profile.id,
        target_user_id=share_data.user_id,
        can_edit=share_data.can_edit,
    )

    return shared


@router.patch(
    "/{watchlist_id}/share/{target_user_id}", response_model=WatchlistShareOut
)
def update_watchlist_share(
    watchlist_id: int,
    target_user_id: uuid.UUID,
    update_data: WatchlistShareUpdate,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Update sharing permissions (can_edit) for a user on a watchlist.
    Only the watchlist owner can perform this action.
    """
    # 1. Get the current user’s profile
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Perform update
    updated_share = update_watchlist_share_permission(
        session=db,
        watchlist_id=watchlist_id,
        owner_profile_id=profile.id,
        target_user_id=target_user_id,
        can_edit=update_data.can_edit,
    )

    return updated_share


@router.patch("/{watchlist_id}", response_model=WatchlistOut)
def update_watchlist(
    watchlist_id: int,
    watchlist_data: WatchlistUpdate,
    user: CurrentUser,
    db: SessionDep,
):
    """
    Update an existing watchlist.
    Only the owner can perform this action.
    """
    # 1. Get user profile (not auth user)
    profile = get_user_profile_by_auth(db, auth_id=user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found.",
        )

    # 2. Perform update
    updated_watchlist = update_user_watchlist(
        session=db,
        watchlist_id=watchlist_id,
        owner_profile_id=profile.id,
        update_data=watchlist_data,
    )

    return updated_watchlist
