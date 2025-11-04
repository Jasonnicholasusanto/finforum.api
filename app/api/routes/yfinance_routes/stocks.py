from fastapi import APIRouter, HTTPException, status
from fastapi.params import Query
import yfinance as yf
import requests
from app.api.deps import CurrentUser
from app.core.config import settings
from app.schemas.stocks import TickerFastInfoResponse, TickerInfoResponse, TickersRequest
from app.utils.global_variables import STOCK_INTERVALS, STOCK_PERIODS


router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/av/get-ticker-info/{symbol}")
async def get_alpha_vantage_ticker_data(symbol: str, user: CurrentUser):
    api_key = settings.ALPHA_VANTAGE_API_KEY
    av_url = settings.ALPHA_VANTAGE_BASE_URL
    url = f"{av_url}?function=OVERVIEW&symbol={symbol}&apikey={api_key}"

    try:
        response = requests.get(url)
        data = response.json()
        if "Error Message" in data:
            return {"error": data["Error Message"]}
        return data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-info/{symbol}")
async def get_ticker_info(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        info = ticker_data.get_info()
        return TickerInfoResponse(**info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.post("/get-tickers-info")
async def get_tickers_info(request: TickersRequest, user: CurrentUser):
    try:
        tickers_data = yf.Tickers(" ".join(request.symbols))
        results = {}

        for symbol in request.symbols:
            info = tickers_data.tickers[symbol].get_info()
            results[symbol] = TickerInfoResponse(**info)

        return results
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-fast-info/{symbol}")
async def get_ticker_fast_info(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)

        fast_info = ticker_data.get_fast_info()
        fast_info = TickerFastInfoResponse(symbol=symbol.upper(), **fast_info)
        return fast_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.post("/get-tickers-fast-info")
async def get_tickers_fast_info(request: TickersRequest, user: CurrentUser):
    try:
        tickers_data = yf.Tickers(" ".join(request.symbols))
        results = {}
        for symbol in request.symbols:
            try:
                fi = tickers_data.tickers[symbol].fast_info
                results[symbol] = TickerFastInfoResponse(symbol=symbol.upper(), **fi)
            except Exception as inner_e:
                results[symbol] = {"error": str(inner_e)}

        return {"results": results}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-major-holders/{symbol}")
async def get_ticker_major_holders(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        major_holders = ticker_data.major_holders
        if major_holders is None or len(major_holders) == 0:
            return {"symbol": symbol, "major_holders": {}}
        return {"symbol": symbol, "major_holders": major_holders}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-earnings/{symbol}")
async def get_ticker_earnings(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        earnings = ticker_data.earnings
        if earnings is None or earnings.empty:
            return {"symbol": symbol, "earnings": []}
        earnings = earnings.fillna(0)
        earnings = earnings.reset_index().to_dict(orient="records")
        return earnings
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-earnings-history/{symbol}")
async def get_ticker_earnings_history(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        eh = ticker_data.earnings_history
        if eh is None or len(eh) == 0:
            return {"symbol": symbol, "earnings_history": {}}
        return {"symbol": symbol, "earnings_history": eh}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-earnings-estimate/{symbol}")
async def get_ticker_earnings_estimates(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        ee = ticker_data.earnings_estimate
        if ee is None or ee.empty:
            return {"symbol": symbol, "earnings_estimates": []}
        ee = ee.fillna(0)
        ee = ee.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "earnings_estimates": ee}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-revenue-estimate/{symbol}")
async def get_ticker_revenue_estimates(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        re = ticker_data.revenue_estimate
        if re is None or re.empty:
            return {"symbol": symbol, "revenue_estimate": []}
        re = re.fillna(0)
        re = re.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "revenue_estimate": re}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-growth-estimates/{symbol}")
async def get_ticker_growth_estimates(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        ge = ticker_data.growth_estimates
        if ge is None or ge.empty:
            return {"symbol": symbol, "growth_estimates": []}
        ge = ge.fillna(0)
        ge = ge.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "growth_estimates": ge}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-dividends/{symbol}")
async def get_ticker_dividends(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        dividends = ticker.dividends
        if dividends is None or dividends.empty:
            return {"symbol": symbol, "dividends": []}
        dividends = dividends.fillna(0)
        dividends = ticker.dividends.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "dividends": dividends}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-splits/{symbol}")
async def get_ticker_splits(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        splits = ticker.splits
        if splits is None or splits.empty:
            return {"symbol": symbol, "splits": []}
        splits = splits.fillna(0)
        splits = splits.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "splits": splits}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-balance-sheet/{symbol}")
async def get_balance_sheet(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        bs = ticker.balance_sheet
        if bs is None or bs.empty:
            return {"symbol": symbol, "balance_sheet": []}
        bs = bs.fillna(0)
        bs = bs.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "balance_sheet": bs}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-cashflow/{symbol}")
async def get_cashflow(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        cf = ticker.cashflow
        if cf is None or cf.empty:
            return {"symbol": symbol, "cashflow": []}
        cf = cf.fillna(0)
        cf = cf.reset_index().to_dict(orient="records")
        return {"symbol": symbol, "cashflow": cf}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-financials/{symbol}")
async def get_financials(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        fin = ticker.financials
        if fin is None or len(fin) == 0:
            return {"symbol": symbol, "financials": {}}
        return {"symbol": symbol, "financials": fin}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-sustainability/{symbol}")
async def get_sustainability(symbol: str):
    try:
        ticker = yf.Ticker(symbol)
        sus = ticker.sustainability
        if sus is None or len(sus) == 0:
            return {"symbol": symbol, "sustainability": {}}
        return {"symbol": symbol, "sustainability": sus}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-calendar/{symbol}")
async def get_calendar(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        cal = ticker.calendar
        if not cal or len(cal) == 0:
            return {"symbol": symbol, "calendar": {}}
        return {"symbol": symbol, "calendar": cal}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


@router.get("/get-ticker-analyst-price-targets/{symbol}")
async def get_analyst_price_targets(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        apt = ticker.analyst_price_targets
        if apt is None or len(apt) == 0:
            return {"symbol": symbol, "analyst_price_targets": []}
        return {"symbol": symbol, "analyst_price_targets": apt}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


### Ticker Lookup and Search Endpoints


@router.get("/lookup/{query}")
async def lookup_tickers(
    query: str,
    user: CurrentUser,
    count: int = Query(10, description="Number of results to return"),
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/search/{query}")
async def search_tickers(query: str, user: CurrentUser):
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

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


### News Data Endpoints


@router.get("/get-ticker-news/{symbol}")
async def get_ticker_news(symbol: str, user: CurrentUser):
    try:
        ticker_data = yf.Ticker(symbol)
        news = ticker_data.news
        return news
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


### Analyst Recommendation Data Endpoints


@router.get("/get-ticker-analyst-recommendations/{symbol}")
async def get_analyst_recommendations(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        recs = ticker.recommendations
        if recs is None or recs.empty:
            return {"symbol": symbol, "recommendations": []}
        return {
            "symbol": symbol,
            "recommendations": recs.reset_index().to_dict(orient="records"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


### Analyst Recommendation Summary Endpoint


@router.get("yf/get-ticker-analyst-recommendations-summary/{symbol}")
async def get_analyst_recommendations_summary(symbol: str, user: CurrentUser):
    try:
        ticker = yf.Ticker(symbol)
        ars = ticker.recommendations_summary
        if ars is None or ars.empty:
            return {"symbol": symbol, "recommendations_summary": []}
        return {
            "symbol": symbol,
            "recommendations_summary": ars.reset_index().to_dict(orient="records"),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )


### Stock History Data Endpoints


@router.get(
    "/get-ticker-history/{symbol}",
    description="Get historical market data for a given ticker symbol. Either start/end or period must be provided followed by interval.",
)
async def get_ticker_history(
    symbol: str,
    user: CurrentUser,
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

        if start and end and interval:
            history = ticker_data.history(interval=interval, start=start, end=end)
        elif period and interval:
            history = ticker_data.history(interval=interval, period=period)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either start/end or period must be provided followed by interval.",
            )

        if history.empty:
            return {"symbol": symbol, "history": []}

        history = history.reset_index()
        history_list = history.to_dict(orient="records")

        return {"symbol": symbol, "history": history_list}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch fast info for '{symbol}': {str(e)}",
        )
