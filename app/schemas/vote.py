from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class VoteBase(BaseModel):
    """Base schema shared across create/update/read."""

    vote: int = Field(..., description="Allowed values: 1 (upvote) or -1 (downvote)")
    watchlist_id: Optional[int] = None
    topic_id: Optional[int] = None
    entry_id: Optional[int] = None
    comment_id: Optional[int] = None


class VoteCreate(VoteBase):
    """Schema for creating a new vote."""
    pass


class VoteUpdate(BaseModel):
    """Schema for updating an existing vote (toggle or change)."""
    vote: Optional[int] = Field(None, description="Allowed values: 1 or -1")


class VoteOut(VoteBase):
    """Schema for returning a vote with metadata."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: UUID
    created_at: datetime
    updated_at: datetime
