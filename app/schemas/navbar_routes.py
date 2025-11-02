from __future__ import annotations  # this enables self-referencing types
from typing import List, Optional
from pydantic import BaseModel, Field


class NavbarRouteBase(BaseModel):
    id: int
    label: str
    href: str
    parent_id: int | None = None
    order_index: int | None = None
    is_active: bool = True
    is_visible: bool = True
    children: Optional[List[NavbarRouteBase]] = None


class NavbarRoutes(BaseModel):
    navbar_routes: List[NavbarRouteBase] = Field(default_factory=list)
