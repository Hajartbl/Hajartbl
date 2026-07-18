"""
Transformation layer — de-duplicate, enrich, and aggregate business KPIs.
"""

from __future__ import annotations

import pandas as pd


def deduplicate(df: pd.DataFrame, key: str) -> pd.DataFrame:
    """Drop duplicate rows on the primary key, keeping the last occurrence.

    Keeping the *last* row means a re-sent/corrected record wins over an older
    one — the same intent as the UPSERT on load.
    """
    return df.drop_duplicates(subset=[key], keep="last").reset_index(drop=True)


def enrich(df: pd.DataFrame) -> pd.DataFrame:
    """Add derived business columns."""
    df = df.copy()
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["order_month"] = df["order_date"].str.slice(0, 7)  # YYYY-MM
    return df


def aggregate_kpis(df: pd.DataFrame) -> pd.DataFrame:
    """Compute KPI table: revenue and volume by month / region / category."""
    kpis = (
        df.groupby(["order_month", "region", "category"], as_index=False)
        .agg(
            orders=("order_id", "count"),
            units_sold=("quantity", "sum"),
            revenue=("revenue", "sum"),
        )
        .sort_values(["order_month", "revenue"], ascending=[True, False])
        .reset_index(drop=True)
    )
    kpis["revenue"] = kpis["revenue"].round(2)
    return kpis
