"""Reusable data-quality checks for the sales dashboard."""

import pandas as pd


QUALITY_OK = "✅ OK"
PROFIT_EXCEEDS_SALES = "⚠ Profit > Sales"
NEGATIVE_SALES = "⚠ Negative sales"
NEGATIVE_PROFIT = "⚠ Negative profit"


def add_quality_flags(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy of the sales data with a readable quality flag per row.

    The function intentionally flags suspicious records instead of changing
    the underlying Sales or Profit values.
    """
    required_columns = {"Sales", "Profit"}
    missing = required_columns.difference(data.columns)
    if missing:
        raise ValueError(
            f"Missing required columns for quality checks: {', '.join(sorted(missing))}"
        )

    result = data.copy()
    result["Quality_Issue"] = QUALITY_OK
    result.loc[result["Profit"] > result["Sales"], "Quality_Issue"] = (
        PROFIT_EXCEEDS_SALES
    )
    result.loc[result["Sales"] < 0, "Quality_Issue"] = NEGATIVE_SALES
    result.loc[result["Profit"] < 0, "Quality_Issue"] = NEGATIVE_PROFIT
    return result
