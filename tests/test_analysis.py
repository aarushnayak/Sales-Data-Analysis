import sys
import unittest
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "python"))

from analysis import calculate_metrics, validate_dataset


class SalesAnalysisTests(unittest.TestCase):
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

    def test_validation_rejects_empty_data(self):
        with self.assertRaisesRegex(ValueError, "empty"):
            validate_dataset(self.sample_data().iloc[0:0])


if __name__ == "__main__":
    unittest.main()
