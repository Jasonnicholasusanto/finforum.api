from typing import Literal
from pydantic import BaseModel


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
