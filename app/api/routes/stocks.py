from fastapi import APIRouter, HTTPException, status
from fastapi.params import Query
import yfinance as yf
import requests
from app.core.config import settings
from app.models.stocks import TickersRequest
from app.utils.global_variables import STOCK_INTERVALS, STOCK_PERIODS


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


@router.post("/yf/get-tickers-info")
async def get_tickers_info(request: TickersRequest):
    try:
        tickers_data = yf.Tickers(" ".join(request.symbols))
        infos = {
            symbol: tickers_data.tickers[symbol].info for symbol in request.symbols
        }
        return infos
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


@router.post("/yf/get-tickers-fast-info")
async def get_tickers_fast_info(request: TickersRequest):
    try:
        tickers_data = yf.Tickers(" ".join(request.symbols))
        infos = {
            symbol: tickers_data.tickers[symbol].fast_info for symbol in request.symbols
        }
        return infos
    except Exception as e:
        return {"error": str(e)}


@router.get("/yf/get-ticker-earnings/{symbol}")
async def get_ticker_earnings(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        earnings = ticker_data.earnings
        return earnings
    except Exception as e:
        return {"error": str(e)}


@router.get("/yf/get-ticker-growth-estimates/{symbol}")
async def get_ticker_growth_estimates(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        growth_estimates = ticker_data.growth_estimates
        return growth_estimates
    except Exception as e:
        return {"error": str(e)}


### Ticker Lookup and Search Endpoints


@router.get("/yf/lookup/{query}")
async def lookup_tickers(
    query: str, count: int = Query(10, description="Number of results to return")
):
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/yf/search/{query}")
async def search_tickers(query: str):
    try:
        # Create Search object
        search = yf.Search(
            query=query, max_results=10, recommended=10, enable_fuzzy_query=True
        )

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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


### News Data Endpoints


@router.get("/yf/get-ticker-news/{symbol}")
async def get_ticker_news(symbol: str):
    try:
        ticker_data = yf.Ticker(symbol)
        news = ticker_data.news
        return news
    except Exception as e:
        return {"error": str(e)}


### Stock History Data Endpoints

@router.get("/get-ticker-history/{symbol}")
async def get_ticker_history(
    symbol: str,
    interval: str = Query(
        "1d",
        description=f"Valid intervals: {', '.join(list(STOCK_INTERVALS))} (Intraday data cannot extend last 60 days)",
    ),
    start: str = Query(None, description="Start date in YYYY-MM-DD format"),
    end: str = Query(None, description="Ends date in YYYY-MM-DD format"),
    period: str | None = Query(
        "1mo",
        description=f"Alternative to start/end: {', '.join(list(STOCK_INTERVALS))}",
    ),
):
    print(f"Fetching history for {symbol} with interval {interval}, start {start}, end {end}, period {period}")
    if interval not in STOCK_INTERVALS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid interval '{interval}'. Must be one of {sorted(list(STOCK_INTERVALS))}",
        )
    if period and period not in STOCK_PERIODS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid period '{period}'. Must be one of {sorted(list(STOCK_PERIODS))}",
        )
    if not start and not end and not period:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either start/end or period must be provided.",
        )
    try:
        ticker_data = yf.Ticker(symbol)

        if start and end:
            history = ticker_data.history(interval=interval, start=start, end=end)
        elif period:
            history = ticker_data.history(interval=interval, period=period)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either start/end or period must be provided.",
            )

        if history.empty:
            return {"symbol": symbol, "history": []}

        history = history.reset_index()
        history_list = history.to_dict(orient="records")

        return {"symbol": symbol, "history": history_list}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
