from fastapi import APIRouter

from app.api.routes import auth, me, utils, users, watchlists, stocks

api_router = APIRouter()
api_router.include_router(me.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(auth.router)
api_router.include_router(watchlists.router)
api_router.include_router(stocks.router)
