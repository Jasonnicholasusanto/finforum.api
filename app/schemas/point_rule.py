from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PointRuleSource(str, Enum):
    topic_posted = "topic_posted"
    entry_posted = "entry_posted"
    comment_posted = "comment_posted"

    vote_received_topic_up = "vote_received_topic_up"
    vote_received_topic_down = "vote_received_topic_down"
    vote_received_entry_up = "vote_received_entry_up"
    vote_received_entry_down = "vote_received_entry_down"
    vote_received_comment_up = "vote_received_comment_up"
    vote_received_comment_down = "vote_received_comment_down"

    topic_archived = "topic_archived"
    entry_deleted = "entry_deleted"
    comment_deleted = "comment_deleted"


# ---------- Base (shared fields) ----------
class PointRuleBase(BaseModel):
    source: PointRuleSource
    # points can be positive or negative
    points: int = Field(..., description="Point delta; may be negative.")


# ---------- Create (client -> server) ----------
class PointRuleCreate(PointRuleBase):
    model_config = ConfigDict(extra="forbid")


# ---------- Update (partial) ----------
class PointRuleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source: Optional[PointRuleSource] = None
    points: Optional[int] = None


# ---------- Public (server -> client) ----------
class PointRulePublic(PointRuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
