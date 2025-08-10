import uuid
from pydantic import EmailStr
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """Auth.Users table (managed by Supabase).
    ⚠️ Do not run Alembic migrations on this table.
    """

    __tablename__ = "users"
    __table_args__ = {"schema": "auth", "keep_existing": True}

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    email: EmailStr = Field(max_length=255, nullable=False)
