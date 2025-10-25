from typing import Optional
from pydantic import BaseModel     


class FavouriteStockBase(BaseModel):
    symbol: str
    exchange: str
    note: Optional[str] = None
    company_name: Optional[str] = None


class FavouriteStockCreate(FavouriteStockBase):
    pass


class FavouriteStockUpdate(BaseModel):
    note: Optional[str] = None


class FavouriteStocks(BaseModel):
    favourite_stocks: list[FavouriteStockBase]