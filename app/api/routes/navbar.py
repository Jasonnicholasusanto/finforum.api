from fastapi import APIRouter
from app.schemas.navbar_routes import NavbarRoutes
from app.api.deps import SessionDep
from app.services.navbar_routes_service import get_navbar_routes


router = APIRouter(prefix="/navbar", tags=["navbar"])

@router.get("/items", response_model=NavbarRoutes)
async def get_navbar_items(db: SessionDep):
    """
    Retrieve a list of navbar items.
    """
    result = get_navbar_routes(db)
    return result
