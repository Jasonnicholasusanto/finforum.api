from fastapi import APIRouter
from app.models.stocks import TickerItem
import yfinance as yf


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.post("/get-ticker-data/")
async def get_ticker_data(tickerItem: TickerItem):
    try:
        ticker_data = yf.Ticker(tickerItem.symbol)
        ticker_data_hist = ticker_data.history(
            start=tickerItem.start_date,
            end=tickerItem.end_date,
            interval=tickerItem.interval,
        )
        return ticker_data_hist.to_dict()
    except Exception as e:
        return {"error": str(e)}
