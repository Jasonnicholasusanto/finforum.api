from datetime import datetime, timezone
import uuid
from sqlmodel import Field, SQLModel


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class UserFollow(SQLModel, table=True):
    """
    Mirrors public.user_follow
    Primary key is id (int, autoincrement).
    follower_id and following_id are FKs to public.user_profile.id
    """

    __tablename__ = "user_follow"
    __table_args__ = {"schema": "public"}

    id: int = Field(default=None, primary_key=True)
    follower_id: uuid.UUID = Field(foreign_key="public.user_profile.id", index=True)
    following_id: uuid.UUID = Field(foreign_key="public.user_profile.id", index=True)
    created_at: datetime = Field(default_factory=utcnow)
