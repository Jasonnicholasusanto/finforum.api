from fastapi import APIRouter

from app.api.routes import sign_up, user_profile, utils

api_router = APIRouter()
api_router.include_router(user_profile.router)
api_router.include_router(sign_up.router)
api_router.include_router(utils.router)
