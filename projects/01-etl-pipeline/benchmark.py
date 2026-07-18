"""
Performance benchmark — validates the "< 0.5 s for 5 000 rows" target.

Generates a 5 000-row CSV in a temp dir and times a full pipeline run
(extract -> validate -> transform -> load) end to end.

Run:  python benchmark.py
"""

from __future__ import annotations

import os
import tempfile

import numpy as np
import pandas as pd

from etl import run_pipeline

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = os.path.join(HERE, "config", "schema.yaml")
RNG = np.random.default_rng(0)

CATEGORIES = ["Electronics", "Home", "Sports", "Beauty", "Grocery"]
REGIONS = ["North", "South", "East", "West"]


def _make_csv(path: str, n: int) -> None:
    df = pd.DataFrame({
        "order_id": np.arange(n),
        "order_date": pd.to_datetime(
            RNG.integers(0, 300, n), unit="D", origin="2024-01-01"
        ).strftime("%Y-%m-%d"),
        "product": RNG.choice(["A", "B", "C", "D"], n),
        "category": RNG.choice(CATEGORIES, n),
        "region": RNG.choice(REGIONS, n),
        "quantity": RNG.integers(1, 20, n),
        "unit_price": RNG.uniform(5, 400, n).round(2),
    })
    df.to_csv(path, index=False)


def main(n: int = 5000) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        csv_path = os.path.join(tmp, "orders.csv")
        db_path = os.path.join(tmp, "bench.db")
        _make_csv(csv_path, n)
        report = run_pipeline([csv_path], SCHEMA, db_path)

    target = 0.5
    status = "PASS" if report.seconds < target else "SLOW"
    print(f"Rows: {n}")
    print(f"Time: {report.seconds * 1000:.1f} ms  (target < {target * 1000:.0f} ms)")
    print(f"Throughput: {n / report.seconds:,.0f} rows/s")
    print(f"Result: {status}")


if __name__ == "__main__":
    main()
