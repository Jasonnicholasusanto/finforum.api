import yfinance as yf
from app.utils.global_variables import REGIONS

def load_valid_fields():
    fields = yf.EquityQuery.valid_fields.fget(None)
    values = yf.EquityQuery.valid_values.fget(None)

    values['region'] = sorted(REGIONS)

    return fields, values


def build_equity_query(conditions, logical_operator):
    subqueries = []
    for cond in conditions:
        q = yf.EquityQuery(cond.operator.lower(), [cond.field, cond.value])
        subqueries.append(q)

    return yf.EquityQuery(logical_operator.lower(), subqueries)