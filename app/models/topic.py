from sqlmodel import SQLModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime


class Topic(SQLModel, table=True):
    __tablename__ = "topic"

    id: Optional[int] = Field(default=None, primary_key=True)
    slug: str
    name: str
    type: Optional[str] = None
    user_id: Optional[UUID] = Field(foreign_key="auth.users.id")
    is_official: bool = False
    description: Optional[str] = None
    status_id: Optional[int] = Field(foreign_key="topic_status.id")
    created_at: datetime
    updated_at: datetime
