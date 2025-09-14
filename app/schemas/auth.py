import re
from gotrue import User, UserAttributes
from pydantic import EmailStr, Field, SecretStr, field_validator
from sqlmodel import SQLModel


# Shared properties
class Token(SQLModel):
    access_token: str | None = None
    refresh_token: str | None = None


class UserLogIn(SQLModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)


class UserSignUp(SQLModel):
    email: EmailStr
    password: SecretStr = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_policy(cls, v: SecretStr) -> SecretStr:
        pwd = v.get_secret_value()
        # at least one lowercase, uppercase, digit, and symbol; no spaces
        if not re.search(r"[a-z]", pwd):
            raise ValueError("Password needs a lowercase letter.")
        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Password needs an uppercase letter.")
        if not re.search(r"\d", pwd):
            raise ValueError("Password needs a digit.")
        if not re.search(r"[^\w\s]", pwd):
            raise ValueError("Password needs a symbol.")
        if re.search(r"\s", pwd):
            raise ValueError("Password cannot contain spaces.")
        return v


# request
class UserIn(Token, User):  # type: ignore
    pass


# Properties to receive via API on creation
# in
class UserCreate(SQLModel):
    pass


# Properties to receive via API on update
# in
class UserUpdate(UserAttributes):  # type: ignore
    pass


# response


class UserInDBBase(SQLModel):
    pass


# Properties to return to client via api
# out
class UserOut(Token):
    pass


# Properties properties stored in DB
class UserInDB(User):  # type: ignore
    pass
