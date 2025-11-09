from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy import text
from sqlmodel import Column, Field, SQLModel
from sqlalchemy.dialects import postgresql

from app.schemas.search_history import SearchType


class SearchHistory(SQLModel, table=True):
    __tablename__ = "search_history"
    __table_args__ = {"schema": "public"}

    id: int = Field(default=None, nullable=False, primary_key=True)
    user_id: UUID = Field(foreign_key="public.user_profile.id", index=True)
    query: str = Field(index=True, nullable=False)
    type: SearchType = Field(
        sa_column=Column(
            "type",
            postgresql.ENUM(
                SearchType,
                name="search_type",
                schema="public",
                create_type=False,
                values_callable=lambda e: [i.value for i in e],
                validate_strings=True,
            ),
            nullable=False,
            server_default=text("'general'::search_type"),
        )
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            postgresql.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("timezone('utc'::text, now())"),
        ),
    )
