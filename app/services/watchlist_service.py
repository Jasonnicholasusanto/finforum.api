from __future__ import annotations
from typing import Dict, Iterable, List
import uuid
from sqlmodel import Session, select

from app.crud import watchlist_item
from app.crud.watchlist import watchlist as watchlist_crud
from app.models.watchlist import Watchlist
from app.models.watchlist_item import WatchlistItem
from app.models.watchlist_share import WatchlistShare
from app.schemas.watchlist import WatchlistCreate, WatchlistOut
from app.schemas.watchlist_item import WatchlistItemCreate


def search_public_watchlists_by_name(
    session: Session, *, name: str, limit: int = 20, offset: int = 0
):
    return watchlist_crud.list_public_by_name(
        session, name=name, limit=limit, offset=offset
    )


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
    watchlist_id: int,
    symbol: str,
    exchange: str,
    note: str | None = None,
    position: int | None = None,
) -> WatchlistItem:
    """
    Add a new item to the specified watchlist.
    Uses CRUDWatchlistItem.create() for persistence.
    """
    item_in = WatchlistItemCreate(
        symbol=symbol,
        exchange=exchange,
        note=note,
        position=position,
    )

    return watchlist_item.create(
        session=session,
        watchlist_id=watchlist_id,
        obj_in=item_in,
    )


def add_many_items_to_watchlist(
    session: Session,
    *,
    watchlist_id: int,
    items: Iterable[WatchlistItemCreate],
) -> List[WatchlistItem]:
    """
    Add multiple items to the specified watchlist.
    Uses CRUDWatchlistItem.create_many() for persistence.
    """
    if not items:
        return []

    # Delegate to the CRUD layer
    db_items = watchlist_item.create_many(
        session=session,
        watchlist_id=watchlist_id,
        items=items,
    )

    # Commit once for all items
    session.commit()

    # Refresh all created items to return up-to-date instances
    for db_item in db_items:
        session.refresh(db_item)

    return db_items
