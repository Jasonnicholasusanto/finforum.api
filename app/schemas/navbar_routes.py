from typing import List
from pydantic import BaseModel
from sqlmodel import Field


class NavbarRouteBase(BaseModel):
    label: str
    href: str
    parent_id: int | None = None
    order_index: int | None = None
    is_active: bool = True
    is_visible: bool = True

class NavbarRoutes(BaseModel):
    navbar_routes: List[NavbarRouteBase] = Field(default_factory=list)