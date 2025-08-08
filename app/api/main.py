from fastapi import APIRouter

from app.api.routes import user_profile

api_router = APIRouter()
api_router.include_router(user_profile.router)
