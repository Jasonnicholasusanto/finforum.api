from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profile"

    user_profile_id: Optional[int] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="auth.users.id", unique=True)
    username: str = Field(index=True, max_length=50, unique=True)
    email: str = Field(index=True, unique=True)
    phone_number: Optional[str] = Field(
        default=None, index=True, max_length=50, unique=True
    )
    full_name: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    updated_at: datetime
