from typing import Dict, List, Literal, Optional
from pydantic import BaseModel, Field, HttpUrl


class TickersRequest(BaseModel):
    symbols: List[str]


class TickerItem(BaseModel):
    symbol: str
    start_date: str
    end_date: str
    interval: Literal[
        "1m",
        "2m",
        "5m",
        "15m",
        "30m",
        "60m",
        "90m",
        "1h",
        "1d",
        "5d",
        "1wk",
        "1mo",
        "3mo",
    ] = "1m"


class TickerFastInfoResponse(BaseModel):
    symbol: str = Field(..., description="Ticker symbol, e.g., AAPL or BHP.AX")
    currency: str = Field(..., description="Trading currency, e.g., USD or AUD")
    exchange: str = Field(..., description="Stock exchange, e.g., NASDAQ, ASX")
    quoteType: str = Field(
        ..., description="Type of instrument, e.g., EQUITY, ETF, INDEX, CRYPTO"
    )

    lastPrice: Optional[float] = Field(None, description="Most recent traded price")
    open: Optional[float] = Field(
        None, description="Opening price of the current session"
    )
    dayHigh: Optional[float] = Field(
        None, description="Highest price during today’s trading session"
    )
    dayLow: Optional[float] = Field(
        None, description="Lowest price during today’s trading session"
    )
    previousClose: Optional[float] = Field(
        None, description="Previous market session's closing price"
    )
    regularMarketPreviousClose: Optional[float] = Field(
        None, description="Regular market previous close (excludes after-hours)"
    )

    lastVolume: Optional[int] = Field(
        None, description="Latest recorded trading volume"
    )
    tenDayAverageVolume: Optional[int] = Field(
        None, description="Average daily volume over last 10 days"
    )
    threeMonthAverageVolume: Optional[int] = Field(
        None, description="Average daily volume over last 3 months"
    )

    marketCap: Optional[float] = Field(
        None, description="Market capitalization = price * shares outstanding"
    )
    shares: Optional[int] = Field(
        None, description="Total number of shares outstanding"
    )

    fiftyDayAverage: Optional[float] = Field(
        None, description="50-day moving average of closing prices"
    )
    twoHundredDayAverage: Optional[float] = Field(
        None, description="200-day moving average of closing prices"
    )

    yearChange: Optional[float] = Field(
        None, description="Percentage change over the past 12 months"
    )
    yearHigh: Optional[float] = Field(
        None, description="Highest price in the last 52 weeks"
    )
    yearLow: Optional[float] = Field(
        None, description="Lowest price in the last 52 weeks"
    )

    timezone: Optional[str] = Field(
        None, description="Exchange timezone, e.g., Australia/Sydney"
    )


class TickersFastInfoResponse(BaseModel):
    results: Dict[str, TickerFastInfoResponse]


class CompanyOfficer(BaseModel):
    name: str = Field(..., description="Full name of the company officer")
    title: Optional[str] = Field(
        None, description="Title/role of the officer, e.g., CEO, CFO"
    )
    fiscalYear: Optional[int] = Field(
        None, description="Fiscal year of reported compensation"
    )
    totalPay: Optional[float] = Field(
        None, description="Total compensation for the officer"
    )
    exercisedValue: Optional[float] = Field(
        None, description="Value of exercised options"
    )
    unexercisedValue: Optional[float] = Field(
        None, description="Value of unexercised options"
    )
    age: Optional[int] = Field(None, description="Age of the officer (if available)")
    yearBorn: Optional[int] = Field(
        None, description="Birth year of the officer (if available)"
    )


class TickerInfoResponse(BaseModel):
    # Basic company info
    symbol: str = Field(..., description="Ticker symbol, e.g., AAPL or TLS.AX")
    shortName: Optional[str] = Field(None, description="Short company name")
    longName: Optional[str] = Field(None, description="Full registered company name")
    industry: Optional[str] = Field(None, description="Industry category")
    sector: Optional[str] = Field(None, description="Sector category")
    website: Optional[HttpUrl] = Field(None, description="Official company website")
    longBusinessSummary: Optional[str] = Field(
        None, description="Full company description / business summary"
    )

    # Financial position
    enterpriseValue: Optional[float] = Field(
        None, description="Enterprise Value = market cap + debt - cash"
    )
    ebitda: Optional[float] = Field(
        None, description="Earnings before interest, taxes, depreciation, amortization"
    )
    totalCash: Optional[float] = Field(
        None, description="Total cash held by the company"
    )
    totalCashPerShare: Optional[float] = Field(None, description="Cash per share")
    totalDebt: Optional[float] = Field(None, description="Total debt")
    debtToEquity: Optional[float] = Field(None, description="Debt-to-equity ratio")
    quickRatio: Optional[float] = Field(
        None, description="Quick ratio = (cash + receivables) ÷ current liabilities"
    )
    currentRatio: Optional[float] = Field(
        None, description="Current ratio = current assets ÷ current liabilities"
    )

    # Address & contact
    address1: Optional[str] = Field(None, description="Street address line 1")
    address2: Optional[str] = Field(None, description="Street address line 2")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/province/region")
    zip: Optional[str] = Field(None, description="Postal/ZIP code")
    country: Optional[str] = Field(None, description="Country")
    phone: Optional[str] = Field(None, description="Company contact phone number")
    fullTimeEmployees: Optional[int] = Field(
        None, description="Number of full-time employees"
    )

    # Employees & management
    companyOfficers: Optional[List[CompanyOfficer]] = Field(
        None, description="List of company officers and their compensation"
    )

    # Revenue
    totalRevenue: Optional[float] = Field(
        None, description="Total revenue (top line sales)"
    )
    revenuePerShare: Optional[float] = Field(
        None, description="Revenue divided by shares outstanding"
    )
    revenueGrowth: Optional[float] = Field(
        None, description="Year-over-year revenue growth percentage"
    )

    # Margins
    grossMargins: Optional[float] = Field(
        None, description="Gross profit margin = gross profit ÷ revenue"
    )
    ebitdaMargins: Optional[float] = Field(
        None, description="EBITDA margin = EBITDA ÷ revenue"
    )
    operatingMargins: Optional[float] = Field(
        None, description="Operating margin = operating income ÷ revenue"
    )

    # Returns
    returnOnAssets: Optional[float] = Field(
        None, description="Return on Assets (ROA) = profit per dollar of assets"
    )
    returnOnEquity: Optional[float] = Field(
        None, description="Return on Equity (ROE) = profit per dollar of equity"
    )

    # Stock / trading info
    currency: Optional[str] = Field(
        None, description="Trading currency, e.g., USD, AUD"
    )
    exchange: Optional[str] = Field(
        None, description="Stock exchange where the company is listed"
    )
    quoteType: Optional[str] = Field(
        None, description="Type of instrument, e.g., EQUITY, ETF, INDEX"
    )
    market: Optional[str] = Field(None, description="Market identifier")
    marketCap: Optional[float] = Field(None, description="Market capitalization")
    sharesOutstanding: Optional[int] = Field(
        None, description="Total shares outstanding"
    )
    floatShares: Optional[int] = Field(
        None, description="Shares available for public trading (float)"
    )
    beta: Optional[float] = Field(
        None, description="Beta (volatility measure relative to the market)"
    )
    volume: Optional[int] = Field(None, description="Trading volume of latest session")
    averageVolume: Optional[int] = Field(None, description="Average trading volume")
    averageVolume10days: Optional[int] = Field(
        None, description="Average trading volume over last 10 days"
    )
    bid: Optional[float] = Field(None, description="Latest bid price")
    ask: Optional[float] = Field(None, description="Latest ask price")
    exchangeTimezoneName: Optional[str] = Field(
        None, description="Exchange timezone, e.g., America/New_York"
    )
    exchangeTimezoneShortName: Optional[str] = Field(
        None, description="Exchange timezone abbreviation, e.g., EST, AEST"
    )
    gmtOffSetMilliseconds: Optional[int] = Field

    # Governance / risk info
    auditRisk: Optional[int] = Field(None, description="Audit risk score")
    boardRisk: Optional[int] = Field(None, description="Board risk score")
    compensationRisk: Optional[int] = Field(None, description="Compensation risk score")
    shareHolderRightsRisk: Optional[int] = Field(
        None, description="Shareholder rights risk score"
    )
    overallRisk: Optional[int] = Field(
        None, description="Overall governance risk score"
    )
    governanceEpochDate: Optional[int] = Field(
        None, description="Epoch timestamp for governance data"
    )
    compensationAsOfEpochDate: Optional[int] = Field(
        None, description="Epoch timestamp for compensation data"
    )

    # Prices info
    currentPrice: Optional[float] = Field(None, description="Latest traded price")
    previousClose: Optional[float] = Field(None, description="Previous closing price")
    priceHint: Optional[int] = Field(None, description="Price display precision hint")
    open: Optional[float] = Field(
        None, description="Opening price of the current session"
    )
    dayLow: Optional[float] = Field(None, description="Lowest price today")
    dayHigh: Optional[float] = Field(None, description="Highest price today")
    allTimeHigh: Optional[float] = Field(None, description="All-time high price")
    allTimeLow: Optional[float] = Field(None, description="All-time low price")
    fiftyTwoWeekLow: Optional[float] = Field(None, description="52-week low price")
    fiftyTwoWeekHigh: Optional[float] = Field(None, description="52-week high price")
    fiftyDayAverage: Optional[float] = Field(None, description="50-day moving average")
    twoHundredDayAverage: Optional[float] = Field(
        None, description="200-day moving average"
    )
    regularMarketOpen: Optional[float] = Field(
        None, description="Regular market opening price"
    )
    regularMarketDayLow: Optional[float] = Field(
        None, description="Regular market day low"
    )
    regularMarketDayHigh: Optional[float] = Field(
        None, description="Regular market day high"
    )

    # Earnings & valuation
    earningsDate: Optional[List[int]] = Field(
        None, description="Earnings date(s) as epoch timestamps"
    )
    earningsAverage: Optional[float] = Field(
        None, description="Average earnings estimate"
    )
    earningsLow: Optional[float] = Field(None, description="Low earnings estimate")
    earningsHigh: Optional[float] = Field(None, description="High earnings estimate")
    revenueAverage: Optional[float] = Field(
        None, description="Average revenue estimate"
    )
    revenueLow: Optional[float] = Field(None, description="Low revenue estimate")
    revenueHigh: Optional[float] = Field(None, description="High revenue estimate")

    # Dividends
    dividendRate: Optional[float] = Field(None, description="Dividend rate per share")
    dividendYield: Optional[float] = Field(
        None, description="Dividend yield percentage"
    )
    payoutRatio: Optional[float] = Field(
        None, description="Payout ratio of dividends to earnings"
    )
    trailingAnnualDividendRate: Optional[float] = Field(
        None, description="Trailing annual dividend rate"
    )
    trailingAnnualDividendYield: Optional[float] = Field(
        None, description="Trailing annual dividend yield"
    )
    bookValue: Optional[float] = Field(None, description="Book value per share")
    priceToBook: Optional[float] = Field(None, description="Price-to-book ratio")

    # Targets & recommendations
    targetHighPrice: Optional[float] = Field(
        None, description="Highest analyst target price"
    )
    targetLowPrice: Optional[float] = Field(
        None, description="Lowest analyst target price"
    )
    targetMeanPrice: Optional[float] = Field(
        None, description="Mean analyst target price"
    )
    targetMedianPrice: Optional[float] = Field(
        None, description="Median analyst target price"
    )
    recommendationKey: Optional[str] = Field(
        None, description="Consensus recommendation key"
    )
    numberOfAnalystOpinions: Optional[int] = Field(
        None, description="Number of analyst opinions"
    )

    # Timestamps (epoch integers from Yahoo)
    lastFiscalYearEnd: Optional[int] = Field(
        None, description="Last fiscal year end (epoch timestamp)"
    )
    nextFiscalYearEnd: Optional[int] = Field(
        None, description="Next fiscal year end (epoch timestamp)"
    )
    mostRecentQuarter: Optional[int] = Field(
        None, description="Most recent fiscal quarter (epoch timestamp)"
    )


class ScreenTickerInfo(BaseModel):
    symbol: str
    displayName: Optional[str] = Field(None, description="Display Name")
    longName: Optional[str] = Field(None, description="Company Name")
    region: Optional[str] = Field(None, description="Region")
    regularMarketPrice: Optional[float] = Field(None, description="Price")
    currency: Optional[str] = Field(None, description="Currency")
    regularMarketPreviousClose: Optional[float] = Field(None, description="Previous Close")
    regularMarketOpen: Optional[float] = Field(None, description="Open")
    regularMarketChange: Optional[float] = Field(None, description="Change")
    regularMarketDayHigh: Optional[float] = Field(None, description="Day High")
    regularMarketDayLow: Optional[float] = Field(None, description="Day Low")
    regularMarketDayRange: Optional[str] = Field(None, description="Day Range")
    fiftyTwoWeekRange: Optional[str] = Field(None, description="52 Week Range")
    fiftyTwoWeekChangePercent: Optional[float] = Field(None, description="52 Week Change Percent")
    fiftyTwoWeekHigh: Optional[float] = Field(None, description="52 Week High")
    fiftyTwoWeekLow: Optional[float] = Field(None, description="52 Week Low")
    regularMarketVolume: Optional[int] = Field(None, description="Volume")
    averageDailyVolume3Month: Optional[int] = Field(None, description="Avg Volume 3 Month")
    epsTrailingTwelveMonths: Optional[float] = Field(None, description="EPS (TTM)")
    trailingPE: Optional[float] = Field(None, description="Trailing PE Ratio (TTM)")
    bid: Optional[float] = Field(None, description="Bid")
    ask: Optional[float] = Field(None, description="Ask")
    bidSize: Optional[int] = Field(None, description="Bid Size")
    askSize: Optional[int] = Field(None, description="Ask Size")
    marketCap: Optional[float] = Field(None, description="Market Cap")
    averageAnalystRating: Optional[str] = Field(None, description="Average Analyst Rating")
    exchange: Optional[str] = Field(None, description="Exchange")
    exchangeTimezoneName: Optional[str] = Field(None, description="Exchange Timezone")
    exchangeTimezoneShortName: Optional[str] = Field(None, description="Exchange Timezone Short Name")
    gmtOffSetMilliseconds: Optional[int] = Field(None, description="GMT Offset in Milliseconds")
    marketState: Optional[str] = Field(None, description="Market State")