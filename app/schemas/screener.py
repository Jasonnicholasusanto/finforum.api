from typing import List, Optional
from pydantic import BaseModel


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
