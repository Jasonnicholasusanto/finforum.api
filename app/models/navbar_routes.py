from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

from app.utils.functions import utcnow


class NavbarRoute(SQLModel, table=True):
    __tablename__ = "navbar_routes"
    __table_args__ = {"schema": "public"}

    id: int = Field(default=None, nullable=False, primary_key=True)
    parent_id: Optional[int] = Field(
        default=None, nullable=True, foreign_key="public.navbar_routes.id"
    )
    label: str = Field(..., nullable=False, description="Display name for the route")
    href: str = Field(..., nullable=False, description="Path or URL for the route")
    order_index: Optional[int] = Field(
        default=None, nullable=True, description="Display order for the route"
    )
    is_active: bool = Field(
        default=True, nullable=False, description="Whether the route is active/visible"
    )
    is_visible: bool = Field(
        default=True,
        nullable=False,
        description="Whether the route is visible in the navbar",
    )
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    updated_at: Optional[datetime] = Field(default_factory=utcnow, nullable=True)
