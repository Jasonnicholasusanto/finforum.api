from datetime import datetime
import uuid
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Auth.Users table (managed by Supabase)."""

    __tablename__ = "users"
    __table_args__ = {"schema": "auth", "keep_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(max_length=255, nullable=False)


class Identity(SQLModel, table=True):
    """Auth.Identities table (managed by Supabase)."""

    __tablename__ = "identities"
    __table_args__ = {"schema": "auth", "keep_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="auth.users.id", nullable=False, ondelete="CASCADE"
    )
    email: EmailStr = Field(max_length=255, nullable=True)
    identity_data: str = Field(nullable=False)
    provider_id: str = Field(nullable=False)
    provider: str = Field(nullable=False)
    last_sign_in_at: datetime = Field(nullable=True)
    created_at: datetime = Field(nullable=True)
    updated_at: datetime = Field(nullable=True)
