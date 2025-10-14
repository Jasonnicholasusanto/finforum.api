from __future__ import annotations
from datetime import datetime
import uuid
from sqlmodel import SQLModel, Field

from app.utils.functions import utcnow


class UserActivity(SQLModel, table=True):
    """
    Mirrors public.user_activity
    Primary key is user_id (FK to public.user_profile.id).
    """

    __tablename__ = "user_activity"
    __table_args__ = {"schema": "public"}

    user_id: uuid.UUID = Field(
        primary_key=True,
        foreign_key="public.user_profile.id",
        nullable=False,
    )

    topics_created: int = Field(default=0, nullable=False)
    entries_created: int = Field(default=0, nullable=False)
    comments_created: int = Field(default=0, nullable=False)

    topic_upvotes: int = Field(default=0, nullable=False)
    topic_downvotes: int = Field(default=0, nullable=False)
    entry_upvotes: int = Field(default=0, nullable=False)
    entry_downvotes: int = Field(default=0, nullable=False)
    comment_upvotes: int = Field(default=0, nullable=False)
    comment_downvotes: int = Field(default=0, nullable=False)

    total_points: int = Field(default=0, nullable=False)
    weekly_points: int = Field(default=0, nullable=False)
    monthly_points: int = Field(default=0, nullable=False)

    # App-side default; DB also has DEFAULT now()
    updated_at: datetime = Field(default_factory=utcnow, nullable=False)
