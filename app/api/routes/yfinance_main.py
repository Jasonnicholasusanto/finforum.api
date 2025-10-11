from fastapi import APIRouter
from app.api.routes.yfinance_routes import market, screen, stocks

router = APIRouter(prefix="/yf", tags=["yfinance endpoints"])

router.include_router(stocks.router)
router.include_router(market.router)
router.include_router(screen.router)
