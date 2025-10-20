from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID
from sqlalchemy import Column, text
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel, Field


class WatchlistBookmark(SQLModel, table=True):
    """
    Association table for users bookmarking watchlists.
    """

    __tablename__ = "watchlist_bookmark"
    __table_args__ = {"schema": "public"}

    id: Optional[int] = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="public.watchlist.id", index=True)
    user_id: UUID = Field(foreign_key="public.user_profile.id", index=True)
    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("timezone('utc'::text, now())"),
        )
    )
