from typing import Optional


def get_regular_market_change(
    last_price: float,
    is_intraday: bool = False,
    prev_close: Optional[float] = None,
) -> tuple[float, float]:
    if is_intraday and prev_close is not None:
        change = last_price - prev_close
        percent = (change / prev_close * 100) if prev_close != 0 else 0

        return change, percent

    if prev_close is None:
        raise ValueError("prev_close must be provided for non-intraday calculations.")
    change = last_price - prev_close
    percent = (change / prev_close * 100) if prev_close != 0 else 0

    return change, percent
