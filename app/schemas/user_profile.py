from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserProfileBase(BaseModel):
    username: str = Field(max_length=50)
    full_name: str
    email: str
    phone_number: str
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: bool


class UserProfileCreate(UserProfileBase):
    user_id: UUID


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: Optional[bool] = None


class UserProfileRead(UserProfileBase):
    user_profile_id: int
    user_id: UUID
    is_admin: bool
    created_at: datetime
    updated_at: datetime
