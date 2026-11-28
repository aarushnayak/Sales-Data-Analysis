import sqlite3
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR / "python"))

from tenant_data import get_sales_for_user, initialize_tenant_schema


class TenantSalesAccessTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        initialize_tenant_schema(self.connection)
        self.connection.executemany(
            "INSERT INTO users (id) VALUES (?)",
            [("user-a",), ("user-b",), ("user-without-memberships",)],
        )
        self.connection.executemany(
            "INSERT INTO businesses (id, name) VALUES (?, ?)",
            [("business-a", "A"), ("business-b", "B"), ("business-c", "C")],
        )
        self.connection.executemany(
            """
            INSERT INTO business_memberships (user_id, business_id, role)
            VALUES (?, ?, ?)
            """,
            [
                ("user-a", "business-a", "owner"),
                ("user-a", "business-c", "analyst"),
                ("user-b", "business-a", "viewer"),
                ("user-b", "business-b", "owner"),
            ],
        )
        self.connection.executemany(
            """
            INSERT INTO sales_records (
                business_id, Order_ID, Date, Customer, Product, Category,
                Region, Quantity, Price, Sales, Profit
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    "business-a", "A-001", "2026-01-01", "Customer A",
                    "Pen", "Office", "North", 2, 10, 20, 5,
                ),
                (
                    "business-a", "A-002", "2026-01-02", "Customer B",
                    "Book", "Office", "South", 1, 30, 30, 10,
                ),
                (
                    "business-b", "B-001", "2026-01-03", "Customer C",
                    "Bag", "Travel", "West", 1, 50, 50, 12,
                ),
                (
                    "business-c", "C-001", "2026-01-04", "Customer D",
                    "Cup", "Home", "East", 3, 5, 15, 4,
                ),
            ],
        )

    def tearDown(self):
        self.connection.close()

    def test_user_sees_only_sales_for_member_businesses(self):
        result = get_sales_for_user(self.connection, authenticated_user_id="user-a")
        self.assertEqual(set(result["Order_ID"]), {"A-001", "A-002", "C-001"})
        self.assertNotIn("B-001", set(result["Order_ID"]))

    def test_membership_allows_shared_business_and_multiple_businesses(self):
        result = get_sales_for_user(self.connection, authenticated_user_id="user-b")
        self.assertEqual(set(result["Order_ID"]), {"A-001", "A-002", "B-001"})
        self.assertNotIn("C-001", set(result["Order_ID"]))

    def test_user_without_memberships_gets_empty_result(self):
        result = get_sales_for_user(
            self.connection, authenticated_user_id="user-without-memberships"
        )
        self.assertTrue(result.empty)
        self.assertEqual(
            list(result.columns),
            [
                "Order_ID", "Date", "Customer", "Product", "Category",
                "Region", "Quantity", "Price", "Sales", "Profit",
            ],
        )

    def test_missing_or_blank_identity_is_rejected(self):
        for identity in (None, "", "   "):
            with self.subTest(identity=identity):
                with self.assertRaisesRegex(
                    ValueError, "non-empty verified identity"
                ):
                    get_sales_for_user(
                        self.connection, authenticated_user_id=identity
                    )

    def test_identity_is_bound_as_a_sql_parameter(self):
        malicious_identity = "' OR 1=1 --"
        result = get_sales_for_user(
            self.connection, authenticated_user_id=malicious_identity
        )
        self.assertTrue(result.empty)
        self.assertEqual(
            len(
                get_sales_for_user(
                    self.connection, authenticated_user_id="user-a"
                )
            ),
            3,
        )

    def test_schema_initialization_is_idempotent(self):
        initialize_tenant_schema(self.connection)
        result = get_sales_for_user(self.connection, authenticated_user_id="user-a")
        self.assertEqual(len(result), 3)


if __name__ == "__main__":
    unittest.main()
