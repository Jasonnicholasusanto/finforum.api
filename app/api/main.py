from fastapi import APIRouter

from app.api.routes import auth, user_profile, utils

api_router = APIRouter()
api_router.include_router(user_profile.router)
api_router.include_router(auth.router)
api_router.include_router(utils.router)
