import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "python"))

from analysis import calculate_metrics, validate_dataset
from data_quality import (
    INVALID_PRICE,
    INVALID_PROFIT,
    INVALID_QUANTITY,
    INVALID_SALES,
    NEGATIVE_PROFIT,
    NEGATIVE_SALES,
    PROFIT_EXCEEDS_SALES,
    QUALITY_OK,
    add_quality_flags,
)


class SalesAnalysisTests(unittest.TestCase):
    def test_quality_flags_suspicious_profit_without_mutating_source(self):
        source = pd.DataFrame(
            [
                {"Sales": 45000, "Profit": 100000},
                {"Sales": 10000, "Profit": 2500},
            ]
        )

        result = add_quality_flags(source)

        self.assertEqual(result["Quality_Issue"].tolist(), [
            PROFIT_EXCEEDS_SALES, QUALITY_OK
        ])
        self.assertNotIn("Quality_Issue", source.columns)
        self.assertEqual(source.loc[0, "Profit"], 100000)

    def test_quality_flags_negative_sales_and_profit(self):
        source = pd.DataFrame(
            [
                {"Sales": -100, "Profit": 10},
                {"Sales": 100, "Profit": -10},
            ]
        )

        result = add_quality_flags(source)

        self.assertEqual(result["Quality_Issue"].tolist(), [
            f"{PROFIT_EXCEEDS_SALES}; {NEGATIVE_SALES}",
            NEGATIVE_PROFIT,
        ])

    def test_quality_flags_keep_all_matching_issues(self):
        source = pd.DataFrame(
            [
                {"Sales": -100, "Profit": 10},
                {"Sales": -100, "Profit": -10},
                {"Sales": 100, "Profit": -10},
            ]
        )

        result = add_quality_flags(source)

        self.assertEqual(result["Quality_Issue"].tolist(), [
            f"{PROFIT_EXCEEDS_SALES}; {NEGATIVE_SALES}",
            f"{PROFIT_EXCEEDS_SALES}; {NEGATIVE_SALES}; {NEGATIVE_PROFIT}",
            NEGATIVE_PROFIT,
        ])

    def test_quality_flags_missing_and_non_finite_numeric_inputs(self):
        source = pd.DataFrame(
            {
                "Quantity": [None, 2, 3, 4],
                "Price": [10, None, 20, 30],
                "Sales": [100, 100, float("inf"), 100],
                "Profit": [10, 10, 10, float("-inf")],
            }
        )

        result = add_quality_flags(source)

        self.assertEqual(result["Quality_Issue"].tolist(), [
            INVALID_QUANTITY,
            INVALID_PRICE,
            INVALID_SALES,
            INVALID_PROFIT,
        ])

    def test_quality_flags_requires_sales_and_profit(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            add_quality_flags(pd.DataFrame({"Sales": [100]}))

    def sample_data(self):
        return pd.DataFrame(
            [
                {
                    "Order_ID": 1, "Date": "2025-01-01", "Customer": "A",
                    "Product": "Pen", "Category": "Stationery", "Region": "North",
                    "Quantity": 2, "Price": 10, "Sales": 20, "Profit": 5,
                },
                {
                    "Order_ID": 2, "Date": "2025-01-02", "Customer": "B",
                    "Product": "Book", "Category": "Stationery", "Region": "South",
                    "Quantity": 1, "Price": 30, "Sales": 30, "Profit": 10,
                },
            ]
        )

    def test_validation_converts_dates_and_numeric_columns(self):
        result = validate_dataset(self.sample_data())
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result["Date"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(result["Sales"]))

    def test_validation_rejects_missing_columns(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            validate_dataset(self.sample_data().drop(columns=["Profit"]))

    def test_metrics_are_calculated_correctly(self):
        result = calculate_metrics(validate_dataset(self.sample_data()))
        self.assertEqual(result["total_sales"], 50.0)
        self.assertEqual(result["total_profit"], 15.0)
        self.assertEqual(result["orders"], 2)
        self.assertEqual(result["units_sold"], 3)
        self.assertEqual(result["average_order_value"], 25.0)
        self.assertEqual(result["profit_margin_pct"], 30.0)

    def test_validation_rejects_missing_required_values(self):
        source = self.sample_data()
        source.loc[0, "Sales"] = None
        source.loc[1, "Date"] = None

        with self.assertRaises(ValueError) as context:
            validate_dataset(source)

        self.assertIn("Missing values in required columns: Date (1), Sales (1)", str(context.exception))

    def test_validation_rejects_infinite_numeric_values(self):
        source = self.sample_data()
        source["Sales"] = source["Sales"].astype(float)
        source["Price"] = source["Price"].astype(float)
        source.loc[0, "Sales"] = float("inf")
        source.loc[1, "Price"] = float("-inf")

        with self.assertRaises(ValueError) as context:
            validate_dataset(source)

        self.assertIn(
            "Non-finite numeric values in required columns: Price (1), Sales (1)",
            str(context.exception),
        )

    def test_validation_rejects_empty_data(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            validate_dataset(self.sample_data().iloc[0:0])


if __name__ == "__main__":
    unittest.main()
