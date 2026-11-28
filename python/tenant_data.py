"""SQLite starter schema and user-scoped sales read boundary.

This module does not authenticate users. Callers must pass an immutable user
subject obtained from a trusted, server-side authentication layer.
"""

import sqlite3

import pandas as pd


TENANT_SCHEMA_STATEMENTS = (
    """CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS businesses (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )""",
    """CREATE TABLE IF NOT EXISTS business_memberships (
        user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
        role TEXT NOT NULL CHECK (role IN ('owner', 'admin', 'analyst', 'viewer')),
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (user_id, business_id)
    )""",
    """CREATE INDEX IF NOT EXISTS idx_memberships_business_user
        ON business_memberships (business_id, user_id)""",
    """CREATE TABLE IF NOT EXISTS sales_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        business_id TEXT NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
        Order_ID TEXT NOT NULL,
        Date TEXT NOT NULL,
        Customer TEXT NOT NULL,
        Product TEXT NOT NULL,
        Category TEXT NOT NULL,
        Region TEXT NOT NULL,
        Quantity REAL NOT NULL,
        Price REAL NOT NULL,
        Sales REAL NOT NULL,
        Profit REAL NOT NULL,
        UNIQUE (business_id, Order_ID)
    )""",
    """CREATE INDEX IF NOT EXISTS idx_sales_records_business_date
        ON sales_records (business_id, Date)""",
)


SALES_COLUMNS = (
    "Order_ID", "Date", "Customer", "Product", "Category",
    "Region", "Quantity", "Price", "Sales", "Profit",
)


def initialize_tenant_schema(connection: sqlite3.Connection) -> None:
    """Create the starter tenant tables in an explicitly supplied SQLite DB.

    This is a local/prototype schema initializer, not a production migration
    system. It never imports or alters the existing sample CSV.
    """
    connection.execute("PRAGMA foreign_keys = ON")
    for statement in TENANT_SCHEMA_STATEMENTS:
        connection.execute(statement)


def get_sales_for_user(
    connection: sqlite3.Connection, *, authenticated_user_id: str
) -> pd.DataFrame:
    """Return sales belonging only to businesses the verified user belongs to.

    authenticated_user_id must come from a server-verified identity, never
    from a query parameter, form field, or client-editable session value.
    Membership is checked in SQL for every read; values are parameter-bound.
    """
    if not isinstance(authenticated_user_id, str) or not authenticated_user_id.strip():
        raise ValueError("authenticated_user_id must be a non-empty verified identity.")

    columns = ", ".join(f"sales_records.{column}" for column in SALES_COLUMNS)
    query = f"""
        SELECT {columns}
        FROM sales_records
        WHERE EXISTS (
            SELECT 1
            FROM business_memberships
            WHERE business_memberships.business_id = sales_records.business_id
              AND business_memberships.user_id = ?
        )
        ORDER BY sales_records.Date DESC, sales_records.Order_ID
    """
    return pd.read_sql_query(query, connection, params=(authenticated_user_id,))
