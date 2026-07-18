"""
Generate heterogeneous sample sources (CSV, Excel, JSON, XML) for the pipeline.

The output deliberately contains a few duplicate order_ids and a few invalid
rows so the validation + de-duplication stages have something real to do.

Run:  python data/generate_samples.py
"""

from __future__ import annotations

import json
import os
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(7)

CATEGORIES = ["Electronics", "Home", "Sports", "Beauty", "Grocery"]
REGIONS = ["North", "South", "East", "West"]
PRODUCTS = {
    "Electronics": ["Laptop", "Headphones", "Monitor", "Keyboard"],
    "Home": ["Lamp", "Cushion", "Blender", "Towel Set"],
    "Sports": ["Yoga Mat", "Dumbbell", "Running Shoes", "Bottle"],
    "Beauty": ["Serum", "Lipstick", "Perfume", "Cream"],
    "Grocery": ["Coffee", "Olive Oil", "Pasta", "Tea"],
}


def _make_rows(n: int, start_id: int) -> pd.DataFrame:
    cats = RNG.choice(CATEGORIES, n)
    rows = {
        "order_id": np.arange(start_id, start_id + n),
        "order_date": pd.to_datetime(
            RNG.integers(0, 180, n), unit="D", origin="2024-01-01"
        ).strftime("%Y-%m-%d"),
        "product": [RNG.choice(PRODUCTS[c]) for c in cats],
        "category": cats,
        "region": RNG.choice(REGIONS, n),
        "quantity": RNG.integers(1, 12, n),
        "unit_price": (RNG.uniform(5, 400, n)).round(2),
    }
    return pd.DataFrame(rows)


def main() -> None:
    df = _make_rows(400, start_id=1000)

    # CSV (first 120 rows)
    df.iloc[:120].to_csv(os.path.join(HERE, "orders_batch1.csv"), index=False)

    # Excel (next 120 rows) — with 5 duplicated order_ids from the CSV batch
    excel_part = df.iloc[120:240].copy()
    dup = df.iloc[:5].copy()
    dup["quantity"] = dup["quantity"] + 1  # a corrected re-send
    excel_part = pd.concat([excel_part, dup], ignore_index=True)
    excel_part.to_excel(os.path.join(HERE, "orders_batch2.xlsx"), index=False)

    # JSON (next 80 rows) — inject 3 invalid rows
    json_part = df.iloc[240:320].copy()
    bad = json_part.iloc[:3].copy()
    bad["quantity"] = [-2, 0, 5000]          # violate min/max
    bad["category"] = ["Toys", "Home", "Games"]  # 2 not in allowed set
    json_part = pd.concat([json_part, bad], ignore_index=True)
    json_part.to_json(
        os.path.join(HERE, "orders_batch3.json"), orient="records", indent=2
    )

    # XML (last 80 rows)
    _write_xml(df.iloc[320:400], os.path.join(HERE, "orders_batch4.xml"))

    print("Generated: orders_batch1.csv, orders_batch2.xlsx, "
          "orders_batch3.json, orders_batch4.xml")


def _write_xml(df: pd.DataFrame, path: str) -> None:
    root = ET.Element("records")
    for _, row in df.iterrows():
        rec = ET.SubElement(root, "record")
        for col, val in row.items():
            ET.SubElement(rec, col).text = str(val)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    main()
