from typing import Annotated, Optional
from pydantic import ConfigDict, EmailStr, Field
import uuid
from sqlmodel import SQLModel


Username = Annotated[
    str,
    Field(
        strip_whitespace=True, min_length=3, max_length=30, pattern=r"^[a-zA-Z0-9_\.]+$"
    ),
]


# Shared base properties
class UserProfileBase(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    username: Username
    full_name: str = Field(min_length=1, max_length=255)
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=50)
    email_address: EmailStr = Field(max_length=255)


# Properties to receive on user creation
class UserProfileCreate(UserProfileBase):
    pass


# Properties to receive on item update
class UserProfileUpdate(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[Username] = None
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=50)
    email_address: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None


# Properties to return to client
class UserProfilePublic(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    auth_id: uuid.UUID
    username: str
    full_name: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None


class UserProfilesPublic(SQLModel):
    data: list[UserProfilePublic]
    count: int


# Private/me response (richer)
class UserProfileMe(SQLModel):
    model_config = ConfigDict(from_attributes=True)
    id: uuid.UUID
    auth_id: uuid.UUID
    username: str
    full_name: str
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    phone_number: Optional[str] = None
    email_address: str
    is_active: bool
    is_admin: bool = False
