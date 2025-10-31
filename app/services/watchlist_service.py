from __future__ import annotations
from typing import Dict, Iterable, List, Union
import uuid
from fastapi import HTTPException, status
from sqlmodel import Session, select
from app.crud.watchlist_item import watchlist_item as watchlist_item_crud
from app.crud.watchlist import watchlist as watchlist_crud
from app.crud.watchlist_share import watchlist_share as watchlist_share_crud
from app.crud.watchlist_bookmark import watchlist_bookmark as watchlist_bookmark_crud
from app.models.watchlist import Watchlist
from app.models.watchlist_bookmark import WatchlistBookmark
from app.models.watchlist_item import WatchlistItem
from app.models.watchlist_share import WatchlistShare
from app.schemas.watchlist import WatchlistCreate, WatchlistForkOut, WatchlistOut, WatchlistUpdate, WatchlistVisibility
from app.schemas.watchlist_bookmark import WatchlistBookmarkBase
from app.schemas.watchlist_item import (
    WatchlistItemCreate,
    WatchlistItemCreateWithoutId,
    WatchlistItemUpdate,
)
from app.schemas.watchlist_share import WatchlistShareCreate


def search_public_watchlists_by_name(
    session: Session, *, name: str, limit: int = 20, offset: int = 0
):
    return watchlist_crud.list_public_by_name(
        session, name=name, limit=limit, offset=offset
    )


def get_all_user_related_watchlists(
    session,
    *,
    user_profile_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> dict:
    """
    Fetch all watchlists associated with a user, including:
      1. Watchlists the user owns,
      2. Watchlists shared with the user,
      3. Watchlists the user bookmarked.

    Returns a categorized dictionary for clarity.
    """

    # 1. Watchlists the user OWNS
    owned_stmt = (
        select(Watchlist)
        .where(Watchlist.user_id == user_profile_id)
        .order_by(Watchlist.created_at.desc())
    )
    owned_watchlists = list(session.exec(owned_stmt).all())

    # 2. Watchlists SHARED with the user
    shared_stmt = (
        select(Watchlist)
        .join(WatchlistShare, WatchlistShare.watchlist_id == Watchlist.id)
        .where(WatchlistShare.user_id == user_profile_id)
        .order_by(Watchlist.created_at.desc())
    )
    shared_watchlists = list(session.exec(shared_stmt).all())

    # 3. Watchlists BOOKMARKED by the user
    bookmarked_stmt = (
        select(Watchlist)
        .join(WatchlistBookmark, WatchlistBookmark.watchlist_id == Watchlist.id)
        .where(WatchlistBookmark.user_id == user_profile_id)
        .order_by(Watchlist.created_at.desc())
    )
    bookmarked_watchlists = list(session.exec(bookmarked_stmt).all())

    # Optionally apply limit/offset across the combined list (to-do)
    if limit:
        owned_watchlists = owned_watchlists[offset : offset + limit]
        shared_watchlists = shared_watchlists[offset : offset + limit]
        bookmarked_watchlists = bookmarked_watchlists[offset : offset + limit]

    # 4. Build Response
    return {
        "owned": [
            WatchlistOut.model_validate(w, from_attributes=True)
            for w in owned_watchlists
        ],
        "shared": [
            WatchlistOut.model_validate(w, from_attributes=True)
            for w in shared_watchlists
        ],
        "bookmarked": [
            WatchlistOut.model_validate(w, from_attributes=True)
            for w in bookmarked_watchlists
        ],
        "counts": {
            "owned": len(owned_watchlists),
            "shared": len(shared_watchlists),
            "bookmarked": len(bookmarked_watchlists),
        },
    }


def get_watchlists_shared_with_user(
    session,
    *,
    user_profile_id: uuid.UUID,
    limit: int = 20,
    offset: int = 0,
) -> List[WatchlistOut]:
    """
    Fetch all watchlists that have been shared with a specific user.
    Includes whether the user has edit permissions.
    """
    stmt = (
        select(Watchlist, WatchlistShare.can_edit)
        .join(WatchlistShare, WatchlistShare.watchlist_id == Watchlist.id)
        .where(WatchlistShare.user_id == user_profile_id)
        .order_by(Watchlist.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    results = session.exec(stmt).all()

    watchlists = []
    for w, can_edit in results:
        watchlist_out = WatchlistOut.model_validate(w, from_attributes=True)
        watchlist_out_dict = watchlist_out.model_dump()
        watchlist_out_dict["can_edit"] = can_edit
        watchlists.append(watchlist_out_dict)

    return watchlists


def watchlist_item_exists(
    session, *, watchlist_id: int, symbol: str, exchange: str
) -> bool:
    """
    Returns True if the given symbol already exists in the watchlist.
    """
    stmt = select(WatchlistItem).where(
        (WatchlistItem.watchlist_id == watchlist_id)
        & (WatchlistItem.symbol == symbol)
        & (WatchlistItem.exchange == exchange)
    )
    existing = session.exec(stmt).first()
    return existing is not None


def load_items_for_watchlists(
    session: Session, watchlist_ids: List[int]
) -> Dict[int, List[WatchlistItem]]:
    """Batch load items for many watchlists to avoid N+1."""
    if not watchlist_ids:
        return {}
    stmt = (
        select(WatchlistItem)
        .where(WatchlistItem.watchlist_id.in_(watchlist_ids))
        .order_by(
            WatchlistItem.watchlist_id.asc(),
            WatchlistItem.position.asc().nulls_last(),
            WatchlistItem.created_at.asc(),
        )
    )
    items_by_wl: Dict[int, list[WatchlistItem]] = {}
    for it in session.exec(stmt).all():
        items_by_wl.setdefault(it.watchlist_id, []).append(it)
    return items_by_wl


def user_can_edit_watchlist(
    session: Session, user_id: uuid.UUID, watchlist_id: int
) -> bool:
    """
    Checks if the given user can edit the specified watchlist.

    A user can edit if:
    1. They own the watchlist (watchlist.user_id == user_id), or
    2. The watchlist is shared with them and can_edit = True.
    """

    # 1. Check if user owns the watchlist
    watchlist = session.exec(
        select(Watchlist).where(Watchlist.id == watchlist_id)
    ).first()
    if not watchlist:
        return False

    if watchlist.user_id == user_id:
        return True

    # 2. Otherwise check shared permissions
    shared_access = session.exec(
        select(WatchlistShare).where(
            (WatchlistShare.watchlist_id == watchlist_id)
            & (WatchlistShare.user_id == user_id)
            & (WatchlistShare.can_edit)
        )
    ).first()

    return shared_access is not None


def create_watchlist_for_user(
    session: Session,
    *,
    user_id: uuid.UUID,
    watchlist_data: WatchlistCreate,
) -> WatchlistOut:
    """
    Create a new watchlist for the given user.
    """
    db_obj = watchlist_crud.create(session, owner_id=user_id, obj_in=watchlist_data)
    return WatchlistOut.model_validate(db_obj, from_attributes=True)


def add_item_to_watchlist(
    session: Session,
    *,
    user_profile_id: uuid.UUID,
    item: WatchlistItemCreate,
) -> WatchlistItem:
    """
    Add a new item to the specified watchlist.
    Uses CRUDWatchlistItem.create() for persistence.
    """
    # 1. Validate edit permissions
    user_access = user_can_edit_watchlist(
        session=session,
        watchlist_id=item.watchlist_id,
        user_id=user_profile_id,
    )

    if not user_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this watchlist.",
        )

    # 2. Prevent duplicate entries
    if watchlist_item_exists(
        session=session,
        watchlist_id=item.watchlist_id,
        symbol=item.symbol,
        exchange=item.exchange,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Symbol '{item.symbol}' already exists in this watchlist.",
        )

    # 3. Create the item
    item_in = WatchlistItemCreate(
        symbol=item.symbol,
        exchange=item.exchange,
        note=item.note,
        position=item.position,
        watchlist_id=item.watchlist_id,
    )

    return watchlist_item_crud.create(
        session=session,
        watchlist_id=item.watchlist_id,
        obj_in=item_in,
    )


def add_many_items_to_watchlist(
    session: Session,
    *,
    watchlist_id: int,
    items: Iterable[Union[WatchlistItemCreate, WatchlistItemCreateWithoutId]],
) -> List[WatchlistItem]:
    """
    Add multiple items to the specified watchlist.
    Uses CRUDWatchlistItem.create_many() for persistence.
    """
    if not items:
        return []

    normalized_items = [
        WatchlistItemCreate(
            watchlist_id=watchlist_id, **item.model_dump(exclude_unset=True)
        )
        for item in items
    ]

    db_items = watchlist_item_crud.create_many(
        session=session,
        watchlist_id=watchlist_id,
        items=normalized_items,
    )

    session.commit()
    for db_item in db_items:
        session.refresh(db_item)

    return db_items


def update_watchlist_item(
    session,
    *,
    item_id: int,
    user_profile_id: uuid.UUID,
    update_data: WatchlistItemUpdate,
):
    """
    Update a watchlist item.
    User must either own the watchlist or have edit access to it.
    """
    db_item = session.get(WatchlistItem, item_id)
    if not db_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    # Check if user can edit this watchlist
    can_edit = user_can_edit_watchlist(
        session=session,
        watchlist_id=db_item.watchlist_id,
        user_id=user_profile_id,
    )

    if not can_edit:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to edit this watchlist item.",
        )

    try:
        updated_item = watchlist_item_crud.update(
            session=session,
            id=item_id,
            obj_in=update_data,
        )

        if not updated_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update item.",
            )

        return updated_item

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update watchlist item: {str(e)}",
        )


def delete_watchlist_item(
    session: Session,
    *,
    item_id: int,
    user_profile_id: uuid.UUID,
) -> WatchlistItem:
    """
    Deletes a watchlist item if the user has edit permission on its parent watchlist.
    """
    # 1. Fetch the item
    item = watchlist_item_crud.get(session, id=item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found.",
        )

    # 2. Check user edit access on the watchlist associated with the item
    has_access = user_can_edit_watchlist(
        session=session,
        watchlist_id=item.watchlist_id,
        user_id=user_profile_id,
    )
    if not has_access:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this item.",
        )

    # 3. Delete the item
    deleted = watchlist_item_crud.remove(session, id=item_id)
    return deleted


def delete_watchlist(
    session: Session,
    *,
    watchlist_id: int,
    user_profile_id: uuid.UUID,
) -> Watchlist:
    """
    Deletes a watchlist if the user owns it.
    (Only owners can delete watchlists — not shared editors.)
    """
    # 1. Fetch the watchlist
    db_watchlist = watchlist_crud.get(session, id=watchlist_id)
    if not db_watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found.",
        )

    # 2. Ensure user is the owner
    if str(db_watchlist.user_id) != str(user_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can delete this watchlist.",
        )

    deleted = watchlist_crud.remove(session, id=watchlist_id)
    return deleted


def share_watchlist_with_user(
    session: Session,
    *,
    watchlist_id: int,
    owner_profile_id: uuid.UUID,
    target_user_id: uuid.UUID,
    can_edit: bool = False,
):
    """
    Share a watchlist with another user.
    Only the owner can share a watchlist.
    """
    # 1. Validate the watchlist exists
    watchlist = watchlist_crud.get(session, id=watchlist_id)
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found.",
        )

    # 2. Ensure the requesting user is the owner
    if str(watchlist.user_id) != str(owner_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can share this watchlist.",
        )

    # 3. Check if share already exists
    existing = watchlist_share_crud.get_share(
        session=session, watchlist_id=watchlist_id, user_id=target_user_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This user is already shared on this watchlist.",
        )

    # 4. Create new share record
    share_data = WatchlistShareCreate(
        watchlist_id=watchlist_id,
        user_id=target_user_id,
        can_edit=can_edit,
    )
    db_obj = watchlist_share_crud.create(
        session=session,
        obj_in=share_data,
    )

    return db_obj


def update_watchlist_share_permission(
    session,
    *,
    watchlist_id: int,
    owner_profile_id: uuid.UUID,
    target_user_id: uuid.UUID,
    can_edit: bool,
):
    """
    Update the 'can_edit' permission for a user on a shared watchlist.
    Only the owner of the watchlist can modify share permissions.
    """
    # 1. Validate watchlist
    watchlist = watchlist_crud.get(session, id=watchlist_id)
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found.",
        )

    # 2. Ensure current user is owner
    if str(watchlist.user_id) != str(owner_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the owner can update share permissions.",
        )

    # 3. Ensure share exists
    db_share = watchlist_share_crud.get_share(
        session=session, watchlist_id=watchlist_id, user_id=target_user_id
    )
    if not db_share:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not currently shared on this watchlist.",
        )

    # 4. Perform update
    updated_share = watchlist_share_crud.update(
        session=session,
        watchlist_id=watchlist_id,
        user_id=target_user_id,
        can_edit=can_edit,
    )

    return updated_share


def update_user_watchlist(
    session,
    *,
    watchlist_id: int,
    owner_profile_id: uuid.UUID,
    update_data: WatchlistUpdate,
):
    """
    Update a user's watchlist.
    Only the owner of the watchlist may perform updates.
    """
    # 1. Fetch existing watchlist
    watchlist = watchlist_crud.get(session, id=watchlist_id)
    if not watchlist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found.",
        )

    # 2. Verify ownership
    if str(watchlist.user_id) != str(owner_profile_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this watchlist.",
        )

    # 3. Apply updates via CRUD
    try:
        updated_watchlist = watchlist_crud.update(
            session=session,
            id=watchlist_id,
            obj_in=update_data,
        )

        if not updated_watchlist:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Failed to update — watchlist not found.",
            )

        return updated_watchlist

    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update watchlist: {str(e)}",
        )


def check_watchlist_bookmarked(
    session, *, watchlist_id: int, user_profile_id: uuid.UUID
) -> bool:
    """
    Check if the given watchlist is bookmarked by the user.
    """
    bookmark = session.exec(
        select(WatchlistBookmark).where(
            (WatchlistBookmark.watchlist_id == watchlist_id)
            & (WatchlistBookmark.user_id == user_profile_id)
        )
    ).first()
    if bookmark:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Watchlist is already bookmarked.",
        )


def check_watchlist_exists(
    session, *, watchlist_id: int, is_public: bool = True
) -> Watchlist:
    """
    Check if the given watchlist exists and is public.
    """
    watchlist = watchlist_crud.get(session, id=watchlist_id)
    if not watchlist or (is_public and watchlist.visibility != "public"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist not found or is not public.",
        )
    return watchlist


def bookmark_watchlist(session, *, watchlist_id: int, user_profile_id: uuid.UUID):
    """
    Bookmark a public watchlist.
    """
    try:
        # 1. Validate watchlist exists and is public
        watchlist = check_watchlist_exists(
            session=session,
            watchlist_id=watchlist_id,
            is_public=True,
        )

        # 2. Check if already bookmarked
        check_watchlist_bookmarked(
            session=session,
            watchlist_id=watchlist.id,
            user_profile_id=user_profile_id,
        )

        # 3. Create bookmark
        obj_in = WatchlistBookmarkBase(
            watchlist_id=watchlist.id,
            user_id=user_profile_id,
        )
        bookmark = watchlist_bookmark_crud.create(
            session=session,
            obj_in=obj_in,
        )
        return bookmark
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to bookmark watchlist: {str(e)}",
        )


def unbookmark_watchlist(session, *, watchlist_id: int, user_profile_id: uuid.UUID):
    """
    Remove a watchlist bookmark.
    """
    try:
        # 1. Validate watchlist exists and is public
        watchlist = check_watchlist_exists(
            session=session,
            watchlist_id=watchlist_id,
            is_public=True,
        )

        # 2. Get watchlist bookmark
        bookmark = watchlist_bookmark_crud.get_watchlist_bookmark(
            session=session,
            watchlist_id=watchlist.id,
            user_id=user_profile_id,
        )
        if not bookmark:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Watchlist Bookmark not found.",
            )

        # 3. Remove bookmark
        watchlist_bookmark_crud.remove(
            session=session,
            id=bookmark.id,
        )
        return {"message": "Bookmark removed successfully."}
    except HTTPException:
        raise
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove bookmark: {str(e)}",
        )


def get_user_bookmarked_watchlists(
    session, *, user_profile_id: uuid.UUID, limit: int = 10, offset: int = 0
):
    """
    Return watchlists bookmarked by the user (with pagination).
    """
    bookmarks = watchlist_bookmark_crud.list_user_bookmarks(
        session=session,
        user_id=user_profile_id,
        limit=limit,
        offset=offset,
    )

    if not bookmarks:
        return []

    watchlist_ids = [b.watchlist_id for b in bookmarks]

    stmt = select(Watchlist).where(Watchlist.id.in_(watchlist_ids))
    return list(session.exec(stmt).all())


def fork_watchlist(
    session: Session,
    *,
    watchlist_id: int,
    user_profile_id: uuid.UUID,
) -> WatchlistForkOut:
    """
    Fork a public watchlist:
      1. Validate existence & visibility
      2. Prevent forking your own list
      3. Clone the watchlist (CRUD layer)
      4. Duplicate its items
      5. Increment fork_count on the original
    """
    # 1. Get the source watchlist
    source = watchlist_crud.get(session, id=watchlist_id)
    if not source:
        raise HTTPException(status_code=404, detail="Original watchlist not found.")
    if source.visibility != WatchlistVisibility.PUBLIC.value:
        raise HTTPException(
            status_code=403, detail="Only public watchlists can be forked."
        )

    # 2. Prevent self-fork
    if str(source.user_id) == str(user_profile_id):
        raise HTTPException(
            status_code=400, detail="You cannot fork your own watchlist."
        )

    # 3. Create forked watchlist (DB insert)
    forked = watchlist_crud.fork(
        session=session,
        source_watchlist=source,
        new_owner_id=user_profile_id,
    )

    # 4. Copy items from original to fork
    items_map = load_items_for_watchlists(session, [source.id])
    original_items = items_map.get(source.id, [])

    forked_items = []
    if original_items:
        items_payload = [
            WatchlistItemCreateWithoutId(
                symbol=i.symbol,
                exchange=i.exchange,
                note=i.note,
                position=i.position,
                percentage=i.percentage,
            )
            for i in original_items
        ]
        forked_items = add_many_items_to_watchlist(
            session=session,
            watchlist_id=forked.id,
            items=items_payload,
        )

    # 5. Increment fork count on source
    source.fork_count = (source.fork_count or 0) + 1
    session.add(source)
    session.commit()
    session.refresh(forked)

    return WatchlistForkOut(
        message="Watchlist forked successfully.",
        forked_watchlist=forked,
        forked_items=forked_items,
    )