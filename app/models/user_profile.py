import uuid
from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel

from app.models.base import InDBBase


# Shared properties
class UserProfileBase(SQLModel):
    username: str = Field(min_length=1, max_length=50)
    email: str = Field(min_length=1, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=50)
    full_name: str = Field(min_length=1, max_length=255)
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: bool = True
    is_admin: bool = False


# Properties to receive on creation
class UserProfileCreate(UserProfileBase):
    pass


# Properties to receive on update
class UserProfileUpdate(SQLModel):
    username: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(default=None, max_length=50)
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


# Database model
class UserProfile(InDBBase, UserProfileBase, table=True):
    __tablename__ = "user_profile"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# Properties to return via API
class UserProfilePublic(UserProfileBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserProfilesPublic(SQLModel):
    data: list[UserProfilePublic]
    count: int
