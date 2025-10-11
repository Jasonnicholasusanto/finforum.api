from fastapi import APIRouter
import yfinance as yf
from fastapi import HTTPException

from app.api.deps import CurrentUser


router = APIRouter(prefix="/screen", tags=["screener"])

@router.get("/predefined-queries")
async def get_predefined_queries():
    """
    Retrieve a list of predefined screener queries available in yfinance.
    """
    psq = yf.PREDEFINED_SCREENER_QUERIES
    psq_list = set(psq.keys())
    psq_dict = {key.replace('_', ' ').title(): key for key in psq_list}

    return {"predefined_queries_list": psq_dict, "predefined_queries": psq}

@router.get("/trending/{category}")
async def get_trending_stocks(category: str, limit: int = 25):
    """
    Fetch trending stocks by category using Yahoo Finance screener.
    Categories include: day_gainers, day_losers, most_actives, undervalued_growth_stocks, etc.
    """
    predefined = yf.PREDEFINED_SCREENER_QUERIES.keys()

    if category not in predefined:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Valid options: {', '.join(predefined)}"
        )

    try:
        data = yf.screen(category, count=limit)
        quotes = data.get("quotes", [])
        total = data.get("count", 0)

        return {
            "category": category,
            "count": total,
            "results": [
                {
                    "symbol": q.get("symbol"),
                    "name": q.get("shortName"),
                    "price": q.get("regularMarketPrice"),
                    "change_percent": q.get("regularMarketChangePercent"),
                    "volume": q.get("regularMarketVolume"),
                    "market_cap": q.get("marketCap"),
                    "sector": q.get("sector"),
                    "exchange": q.get("fullExchangeName"),
                }
                for q in quotes
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")
