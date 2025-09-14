from datetime import datetime
from typing import Annotated, Optional
import uuid
from pydantic import ConfigDict
from sqlmodel import Field, SQLModel


NonNegInt = Annotated[int, Field(ge=0)]


# Shared fields for input/output schemas
class UserActivityBase(SQLModel):
    topics_created: NonNegInt = 0
    entries_created: NonNegInt = 0
    comments_created: NonNegInt = 0

    topic_upvotes: NonNegInt = 0
    topic_downvotes: NonNegInt = 0
    entry_upvotes: NonNegInt = 0
    entry_downvotes: NonNegInt = 0
    comment_upvotes: NonNegInt = 0
    comment_downvotes: NonNegInt = 0

    total_points: NonNegInt = 0
    weekly_points: NonNegInt = 0
    monthly_points: NonNegInt = 0


class UserActivityCreate(UserActivityBase):
    model_config = ConfigDict(extra="forbid")


class UserActivityUpdate(SQLModel):
    model_config = ConfigDict(extra="forbid")

    topics_created: Optional[NonNegInt] = None
    entries_created: Optional[NonNegInt] = None
    comments_created: Optional[NonNegInt] = None

    topic_upvotes: Optional[NonNegInt] = None
    topic_downvotes: Optional[NonNegInt] = None
    entry_upvotes: Optional[NonNegInt] = None
    entry_downvotes: Optional[NonNegInt] = None
    comment_upvotes: Optional[NonNegInt] = None
    comment_downvotes: Optional[NonNegInt] = None

    total_points: Optional[NonNegInt] = None
    weekly_points: Optional[NonNegInt] = None
    monthly_points: Optional[NonNegInt] = None

class UserActivityPublic(UserActivityBase):
    model_config = ConfigDict(from_attributes=True)

    user_id: uuid.UUID
    updated_at: datetime

class UserActivityPointsBreakdown(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    total_points: NonNegInt
    weekly_points: NonNegInt
    monthly_points: NonNegInt