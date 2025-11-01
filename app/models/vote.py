from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, CheckConstraint, text
from sqlalchemy.dialects import postgresql
from sqlmodel import SQLModel, Field


class Vote(SQLModel, table=True):
    """
    ORM model for the public.vote table.

    Supports voting on multiple content types:
    - watchlists
    - topics
    - entries
    - comments
    """

    __tablename__ = "vote"
    __table_args__ = (
        CheckConstraint("vote IN (-1, 1)", name="chk_vote_valid_values"),
        {"schema": "public"},
    )

    id: int = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="public.user_profile.id", nullable=False)

    # Polymorphic associations (nullable foreign keys)
    watchlist_id: Optional[int] = Field(foreign_key="public.watchlist.id", default=None)
    topic_id: Optional[int] = Field(foreign_key="public.topic.id", default=None)
    entry_id: Optional[int] = Field(foreign_key="public.entry.id", default=None)
    comment_id: Optional[int] = Field(foreign_key="public.comment.id", default=None)

    # +1 (upvote) or -1 (downvote)
    vote: int = Field(nullable=False, description="Allowed values: 1 or -1")

    created_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("timezone('utc'::text, now())"),
        )
    )
    updated_at: datetime = Field(
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("timezone('utc'::text, now())"),
        )
    )
