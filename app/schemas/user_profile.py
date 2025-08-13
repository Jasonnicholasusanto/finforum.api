from typing import Optional
from pydantic import BaseModel
import uuid


# Shared fields for input/output schemas
class UserProfileBase(BaseModel):
    username: str
    phone_number: Optional[str] = None
    full_name: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: bool = True
    is_admin: Optional[bool] = False


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    phone_number: Optional[str] = None
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    is_active: Optional[bool] = True


class UserProfilePublic(UserProfileBase):
    user_id: uuid.UUID
