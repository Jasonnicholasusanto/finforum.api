import yfinance as yf
from app.utils.global_variables import REGIONS


def load_valid_fields():
    fields = yf.EquityQuery.valid_fields.fget(None)
    values = yf.EquityQuery.valid_values.fget(None)

    values["region"] = sorted(REGIONS)

    return fields, values


def build_equity_query(conditions, logical_operator):
    subqueries = []

    for cond in conditions:
        op = cond.operator.lower()

        if op == "is-in":
            if not isinstance(cond.value, list):
                raise ValueError("is-in operator expects a list value")
            isin_queries = [
                yf.EquityQuery(op, [cond.field, v])
                for v in cond.value
            ]
            if len(isin_queries) == 1:
                subqueries.append(isin_queries[0])
            else:
                subqueries.append(yf.EquityQuery("or", isin_queries))
        elif op == "btwm":
            if not isinstance(cond.value, list) or len(cond.value) != 2:
                raise ValueError("btwm operator expects [min, max]")
            subqueries.append(
                yf.EquityQuery(op, [cond.field, cond.value[0], cond.value[1]])
            )
        else:
            subqueries.append(
                yf.EquityQuery(op, [cond.field, cond.value])
            )

    if len(subqueries) == 1:
        return subqueries[0]

    if logical_operator.lower() not in ("and", "or"):
        raise ValueError("logical_operator must be 'and' or 'or'")

    return yf.EquityQuery(logical_operator.lower(), subqueries)

