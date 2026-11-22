"""Reusable data-quality checks for the sales dashboard."""

import pandas as pd


QUALITY_OK = "✅ OK"
PROFIT_EXCEEDS_SALES = "⚠ Profit > Sales"
NEGATIVE_SALES = "⚠ Negative sales"
NEGATIVE_PROFIT = "⚠ Negative profit"
INVALID_QUANTITY = "⚠ Invalid quantity"
INVALID_PRICE = "⚠ Invalid price"
INVALID_SALES = "⚠ Invalid sales"
INVALID_PROFIT = "⚠ Invalid profit"


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
    # Keep every matching rule so one anomaly cannot hide another.
    row_issues = [[] for _ in range(len(result))]
    checks = [
        (result["Profit"] > result["Sales"], PROFIT_EXCEEDS_SALES),
        (result["Sales"] < 0, NEGATIVE_SALES),
        (result["Profit"] < 0, NEGATIVE_PROFIT),
    ]
    invalid_numeric_labels = {
        "Quantity": INVALID_QUANTITY,
        "Price": INVALID_PRICE,
        "Sales": INVALID_SALES,
        "Profit": INVALID_PROFIT,
    }
    for column, label in invalid_numeric_labels.items():
        if column in result.columns:
            values = result[column]
            invalid = values.isna() | values.isin([float("inf"), float("-inf")])
            checks.append((invalid, label))

    for mask, label in checks:
        for position, matches in enumerate(mask.fillna(False).to_numpy()):
            if matches:
                row_issues[position].append(label)

    result["Quality_Issue"] = [
        "; ".join(issues) if issues else QUALITY_OK for issues in row_issues
    ]
    return result
