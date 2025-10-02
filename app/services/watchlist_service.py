# app/services/watchlist_service.py
from __future__ import annotations
from typing import Dict, List
from sqlmodel import Session, select

from app.crud.watchlist import watchlist as watchlist_crud
from app.models.watchlist_item import WatchlistItem


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
