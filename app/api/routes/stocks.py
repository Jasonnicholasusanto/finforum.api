from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.params import Query
import yfinance as yf
import requests
from app.core.config import settings


router = APIRouter(prefix="/stocks", tags=["stocks"])

    
@router.get("/av/get-ticker-info/{symbol}")
async def get_alpha_vantage_ticker_data(symbol: str):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    av_url = settings.ALPHA_VANTAGE_BASE_URL
    url = f"{av_url}?function=OVERVIEW&symbol={symbol}&apikey={api_key}"
    
    try:
        response = requests.get(url)
        data = response.json()
        if "Error Message" in data:
            return {"error": data["Error Message"]}
        return data
    except Exception as e:
        return {"error": str(e)}

@router.get("/yf/get-ticker-info/{symbol}")
async def get_ticker_info(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        info = ticker_data.info
        return info
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/yf/get-ticker-fast-info/{symbol}")
async def get_ticker_fast_info(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        fast_info = ticker_data.fast_info
        return fast_info
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/yf/get-ticker-balance-sheet/{symbol}")
async def get_ticker_balance_sheet(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        balance_sheet = ticker_data.balance_sheet
        balance_sheet = balance_sheet.fillna("")
        return balance_sheet.to_dict()
    except Exception as e:
        return {"error": str(e)}
    

@router.get("/lookup/{query}")
async def lookup_tickers(query: str, count: int = Query(10, description="Number of results to return")):
    try:
        # Create Lookup object
        lookup = yf.Lookup(query=query)

        # get_stock returns a Pandas DataFrame
        df = lookup.get_stock(count=count)

        df = df.fillna("")

        if df.empty:
            return {"query": query, "results": []}

        # Convert DataFrame to list of dicts for JSON response
        results = df.to_dict(orient="records")

        return {"query": query, "results": results}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.get("/search/{query}")
async def search_tickers(query: str):
    try:
        # Create Search object
        search = yf.Search(query=query, max_results=10, recommended=10, enable_fuzzy_query=True)

        # Run the search
        search.search()

        # Get quotes (stock results only)
        quotes = search.quotes

        # Clean up output
        results = [
            {
                "symbol": item.get("symbol"),
                "short_name": item.get("shortname"),
                "long_name": item.get("longname"),
                "exchange": item.get("exchange"),
                "exchange_timezone": item.get("exchDisp"),
                "type": item.get("quoteType"),
            }
            for item in quotes
        ]

        return {"query": query, "results": results}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
    
@router.get("/get-ticker-history/{symbol}")
async def get_ticker_history(symbol: str, period: str = "1mo", interval
: str = "1d"):
    try:
        ticker_data = yf.Ticker(symbol)
        history = ticker_data.history(period=period, interval=interval)
        return history.to_dict()
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/get-multiple-tickers-info/")
async def get_multiple_tickers_info(tickers: List[str], start: str, end: str):
    try:
        data = yf.download(tickers, start=start, end=end)
        return data
    except Exception as e:
        return {"error": str(e)}
    
@router.get("/get-ticker-news/{symbol}")
async def get_ticker_news(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        news = ticker_data.news
        return news
    except Exception as e:
        return {"error": str(e)}