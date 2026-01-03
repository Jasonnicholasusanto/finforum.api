from typing import List, Optional
from pydantic import BaseModel, Field


class ScreenerCondition(BaseModel):
    field: str
    operator: str
    value: Optional[float | str | int | List[str]]


class ScreenerRequest(BaseModel):
    conditions: List[ScreenerCondition]
    logical_operator: str = "and"
    limit: int = 50
    sort_field: Optional[str] = None
    sort_type: Optional[str] = None


class ScreenTickerInfo(BaseModel):
    symbol: str
    displayName: Optional[str] = Field(None, description="Display Name")
    longName: Optional[str] = Field(None, description="Company Name")
    region: Optional[str] = Field(None, description="Region")
    regularMarketPrice: Optional[float] = Field(None, description="Price")
    currency: Optional[str] = Field(None, description="Currency")
    regularMarketPreviousClose: Optional[float] = Field(
        None, description="Previous Close"
    )
    regularMarketOpen: Optional[float] = Field(None, description="Open")
    regularMarketChange: Optional[float] = Field(None, description="Change")
    regularMarketDayHigh: Optional[float] = Field(None, description="Day High")
    regularMarketDayLow: Optional[float] = Field(None, description="Day Low")
    regularMarketDayRange: Optional[str] = Field(None, description="Day Range")
    fiftyTwoWeekRange: Optional[str] = Field(None, description="52 Week Range")
    fiftyTwoWeekChangePercent: Optional[float] = Field(
        None, description="52 Week Change Percent"
    )
    fiftyTwoWeekHigh: Optional[float] = Field(None, description="52 Week High")
    fiftyTwoWeekLow: Optional[float] = Field(None, description="52 Week Low")
    regularMarketVolume: Optional[int] = Field(None, description="Volume")
    averageDailyVolume3Month: Optional[int] = Field(
        None, description="Avg Volume 3 Month"
    )
    epsTrailingTwelveMonths: Optional[float] = Field(None, description="EPS (TTM)")
    trailingPE: Optional[float] = Field(None, description="Trailing PE Ratio (TTM)")
    bid: Optional[float] = Field(None, description="Bid")
    ask: Optional[float] = Field(None, description="Ask")
    bidSize: Optional[int] = Field(None, description="Bid Size")
    askSize: Optional[int] = Field(None, description="Ask Size")
    marketCap: Optional[float] = Field(None, description="Market Cap")
    averageAnalystRating: Optional[str] = Field(
        None, description="Average Analyst Rating"
    )
    exchange: Optional[str] = Field(None, description="Exchange")
    exchangeTimezoneName: Optional[str] = Field(None, description="Exchange Timezone")
    exchangeTimezoneShortName: Optional[str] = Field(
        None, description="Exchange Timezone Short Name"
    )
    gmtOffSetMilliseconds: Optional[int] = Field(
        None, description="GMT Offset in Milliseconds"
    )
    marketState: Optional[str] = Field(None, description="Market State")