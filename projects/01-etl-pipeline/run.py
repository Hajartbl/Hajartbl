"""
CLI entry point for the ETL pipeline.

Run:  python run.py
It ingests every sample file in data/, validates against config/schema.yaml,
and loads the result into warehouse.db.
"""

from __future__ import annotations

import glob
import os

from etl import run_pipeline

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    sources = sorted(
        glob.glob(os.path.join(HERE, "data", "orders_batch*.*"))
    )
    if not sources:
        raise SystemExit("No sample data. Run `python data/generate_samples.py` first.")

    report = run_pipeline(
        sources=sources,
        schema_path=os.path.join(HERE, "config", "schema.yaml"),
        db_path=os.path.join(HERE, "warehouse.db"),
        rejects_path=os.path.join(HERE, "data", "rejected_rows.csv"),
    )

    print("Sources ingested:")
    for s in sources:
        print(f"  - {os.path.basename(s)}")
    print("\nRun report:")
    print(f"  {report.summary()}")
    print(f"  db: {report.db_stats}")
    if report.rows_rejected:
        print(f"  {report.rows_rejected} invalid rows -> data/rejected_rows.csv")


if __name__ == "__main__":
    main()
