from typing import Optional
from pydantic import ConfigDict, EmailStr, Field, field_validator
import uuid
from sqlmodel import SQLModel
import re


USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_.]*$")

# Shared base properties
class UserProfileBase(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str = Field(min_length=1, max_length=255)
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=50)
    email_address: EmailStr = Field(max_length=255)


# Properties to receive on user creation
class UserProfileCreate(UserProfileBase):
    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "Username must start with a letter or number and may only contain letters, numbers, underscores, or dots"
            )
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be between 3 and 30 characters")
        return v


# Properties to receive on item update
class UserProfileUpdate(SQLModel):
    model_config = ConfigDict(from_attributes=True)

    username: Optional[str] = None
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    background_picture: Optional[str] = None
    phone_number: Optional[str] = Field(default=None, max_length=50)
    email_address: Optional[str] = Field(default=None, max_length=255)
    is_active: Optional[bool] = None

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not USERNAME_REGEX.match(v):
            raise ValueError(
                "Username must start with a letter or number and may only contain letters, numbers, underscores, or dots"
            )
        if len(v) < 3 or len(v) > 30:
            raise ValueError("Username must be between 3 and 30 characters")
        return v


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
