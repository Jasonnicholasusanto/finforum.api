import uuid
from typing import Optional
from sqlmodel import Field, SQLModel
# from app.models.base import InDBBase


class UserProfileBase(SQLModel):
    __tablename__ = "user_profile"

    user_id: uuid.UUID = Field(
        primary_key=True, index=True, unique=True, foreign_key="auth.users.id"
    )
    username: str = Field(min_length=1, max_length=50)
    phone_number: Optional[str] = Field(default=None, max_length=50)
    full_name: str = Field(min_length=1, max_length=255)
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: bool = Field(default=True)
    is_admin: Optional[bool] = Field(default=False)


class UserProfile(UserProfileBase, table=True):
    pass


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(UserProfileBase):
    username: Optional[str] | None = Field(default=None, min_length=1, max_length=50)
    phone_number: Optional[str] | None = Field(default=None, max_length=50)
    full_name: Optional[str] | None = Field(default=None, min_length=1, max_length=255)
