# import uuid
# from pydantic import BaseModel, EmailStr
# from typing import Optional

# class UserSignUp(BaseModel):
#     email: EmailStr
#     password: str
#     username: Optional[str]
#     full_name: Optional[str]
#     phone_number: Optional[str]
#     bio: Optional[str]

# class UserLogin(BaseModel):
#     email: EmailStr
#     password: str

# # Token schemas
# class Token(BaseModel):
#     access_token: Optional[str]
#     refresh_token: Optional[str]

# # Schema representing the current authenticated user
# class UserIn(BaseModel):
#     id: uuid.UUID
#     email: EmailStr
#     username: Optional[str] = None
#     full_name: Optional[str] = None
#     is_active: Optional[bool] = True
#     is_admin: Optional[bool] = False

# # User update schema
# class UserUpdate(BaseModel):
#     username: Optional[str] = None
#     full_name: Optional[str] = None
#     is_active: Optional[bool] = None
#     is_admin: Optional[bool] = None

# # Response schema for API
# class UserOut(Token):
#     user: UserIn

from typing import Optional
from gotrue import User, UserAttributes
from pydantic import BaseModel, EmailStr


# Shared properties
class Token(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None


class UserSignUp(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str]
    full_name: Optional[str]
    phone_number: Optional[str]
    bio: Optional[str]


# request
class UserIn(Token, User):  # type: ignore
    pass


# Properties to receive via API on creation
# in
class UserCreate(BaseModel):
    pass


# Properties to receive via API on update
# in
class UserUpdate(UserAttributes):  # type: ignore
    pass


# response


class UserInDBBase(BaseModel):
    pass


# Properties to return to client via api
# out
class UserOut(Token):
    pass


# Properties properties stored in DB
class UserInDB(User):  # type: ignore
    pass
