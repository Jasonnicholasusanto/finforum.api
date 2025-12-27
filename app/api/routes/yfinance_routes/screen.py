from fastapi import APIRouter, Depends
import yfinance as yf
from fastapi import HTTPException

from app.api.dependencies.profile import get_current_profile
from app.schemas.screener import ScreenerRequest
from app.schemas.stocks import ScreenTickerInfo
from app.utils.global_variables import SCREENER_LOGICAL_OPERATORS
from app.utils.screener import build_equity_query, load_valid_fields


router = APIRouter(prefix="/screen", tags=["screener"])


@router.get("/predefined-queries")
async def get_predefined_queries(user=Depends(get_current_profile)):
    """
    Retrieve a list of predefined screener queries available in yfinance.
    """
    psq = yf.PREDEFINED_SCREENER_QUERIES
    psq_list = set(psq.keys())
    psq_dict = {key.replace("_", " ").title(): key for key in psq_list}

    return {"predefined_queries_list": psq_dict, "predefined_queries": psq}


@router.get("/equity-valid-inputs")
async def get_equity_screener_valid_fields(user=Depends(get_current_profile)):
    """
    Retrieve a list of valid fields and valid values for the EquityQuery API.
    """
    valid_fields, valid_values = load_valid_fields()

    return {
        "equity_screener_valid_fields": valid_fields,
        "equity_screener_valid_values": valid_values,
    }


@router.get("/predefined-queries-result/{category}")
async def get_results_by_pre_defined_queries(
    category: str,
    limit: int = 25,
    user=Depends(get_current_profile),
):
    """
    Fetch trending stocks by category using Yahoo Finance screener.
    Categories include: day_gainers, day_losers, most_actives, undervalued_growth_stocks, etc.
    """
    predefined = yf.PREDEFINED_SCREENER_QUERIES.keys()

    if category not in predefined:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Valid options: {', '.join(predefined)}",
        )

    try:
        data = yf.screen(category, count=limit)
        quotes = data.get("quotes", [])
        total = data.get("count", 0)

        return {
            "category": category,
            "count": total,
            "results": [ScreenTickerInfo(**quote) for quote in quotes],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch data: {str(e)}")


@router.post("/custom-equity-query-results")
async def custom_equity_query(request: ScreenerRequest, user=Depends(get_current_profile)):
    """
    Run a custom equity query based on user-defined conditions.
    """

    if request.logical_operator.lower() not in {"and", "or"}:
        raise HTTPException(
            status_code=400,
            detail="Invalid logical operator. Must be 'and' or 'or'.",
        )
    for i in request.conditions:
        if i.operator.lower() not in SCREENER_LOGICAL_OPERATORS.values():
            raise HTTPException(
                status_code=400,
                detail=f"Invalid operator: {i.operator}",
            )

    # Build query
    query = build_equity_query(request.conditions, request.logical_operator)

    print(query)

    # Run query
    results = yf.screen(
        query, size=request.limit, sortField=request.sort_field, sortAsc=True
    )

    quotes = results.get("quotes", [])

    return {"query": request, "results": [ScreenTickerInfo(**quote) for quote in quotes]}
