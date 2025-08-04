import datetime
from typing import Optional
import uuid
from sqlmodel import Field, SQLModel


class UserProfile(SQLModel, table=True):
    user_profile_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(index=True, nullable=False, unique=True)
    username: str = Field(max_length=50, nullable=False, unique=True)
    full_name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)