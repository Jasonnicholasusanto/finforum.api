import yfinance as yf
from app.utils.global_variables import REGIONS


def load_valid_fields():
    fields = yf.EquityQuery.valid_fields.fget(None)
    values = yf.EquityQuery.valid_values.fget(None)

    values["region"] = sorted(REGIONS)

    return fields, values


def build_equity_query(conditions, logical_operator):
    subqueries = [
        yf.EquityQuery(cond.operator.lower(), [cond.field, cond.value])
        for cond in conditions
    ]

    # If only 1 condition → return the condition directly (no AND/OR wrapper)
    if len(subqueries) == 1:
        return subqueries[0]

    # Otherwise wrap in AND / OR
    if logical_operator.lower() not in ("and", "or"):
        raise ValueError("logical_operator must be 'and' or 'or'")

    return yf.EquityQuery(logical_operator.lower(), subqueries)

