"""
Load layer — persist clean data with an idempotent UPSERT.

Uses SQLite by default (zero-config, runs anywhere), but the UPSERT statement
(`INSERT ... ON CONFLICT ... DO UPDATE`) is written in the SQL-standard syntax
that PostgreSQL uses too, so the same code path targets Postgres in production
by swapping the connection.
"""

from __future__ import annotations

import sqlite3

import pandas as pd

CREATE_ORDERS = """
CREATE TABLE IF NOT EXISTS sales_orders (
    order_id    INTEGER PRIMARY KEY,
    order_date  TEXT    NOT NULL,
    product     TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    region      TEXT    NOT NULL,
    quantity    INTEGER NOT NULL,
    unit_price  REAL    NOT NULL,
    revenue     REAL    NOT NULL,
    order_month TEXT    NOT NULL
);
"""

CREATE_KPIS = """
CREATE TABLE IF NOT EXISTS sales_kpis (
    order_month TEXT    NOT NULL,
    region      TEXT    NOT NULL,
    category    TEXT    NOT NULL,
    orders      INTEGER NOT NULL,
    units_sold  INTEGER NOT NULL,
    revenue     REAL    NOT NULL,
    PRIMARY KEY (order_month, region, category)
);
"""

_ORDER_COLS = [
    "order_id", "order_date", "product", "category", "region",
    "quantity", "unit_price", "revenue", "order_month",
]
_KPI_COLS = ["order_month", "region", "category", "orders", "units_sold", "revenue"]


def _upsert(conn, table: str, columns: list[str], key_cols: list[str], rows: list[tuple]):
    placeholders = ", ".join(["?"] * len(columns))
    updates = ", ".join(
        f"{c}=excluded.{c}" for c in columns if c not in key_cols
    )
    sql = (
        f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders}) "
        f"ON CONFLICT ({', '.join(key_cols)}) DO UPDATE SET {updates}"
    )
    conn.executemany(sql, rows)


def load(orders: pd.DataFrame, kpis: pd.DataFrame, db_path: str) -> dict:
    """Create tables if needed and UPSERT both the fact rows and the KPI rows."""
    conn = sqlite3.connect(db_path)
    try:
        conn.execute(CREATE_ORDERS)
        conn.execute(CREATE_KPIS)
        _upsert(
            conn, "sales_orders", _ORDER_COLS, ["order_id"],
            list(orders[_ORDER_COLS].itertuples(index=False, name=None)),
        )
        _upsert(
            conn, "sales_kpis", _KPI_COLS, ["order_month", "region", "category"],
            list(kpis[_KPI_COLS].itertuples(index=False, name=None)),
        )
        conn.commit()
        n_orders = conn.execute("SELECT COUNT(*) FROM sales_orders").fetchone()[0]
        n_kpis = conn.execute("SELECT COUNT(*) FROM sales_kpis").fetchone()[0]
    finally:
        conn.close()
    return {"orders_in_db": n_orders, "kpis_in_db": n_kpis}
