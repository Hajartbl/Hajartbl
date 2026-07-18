"""Unit + integration tests for the ETL pipeline."""

import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from etl.validate import load_schema, validate
from etl.transform import aggregate_kpis, deduplicate, enrich
from etl import run_pipeline

SCHEMA_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config", "schema.yaml"
)


@pytest.fixture
def schema():
    return load_schema(SCHEMA_PATH)


def _valid_row(**over):
    row = {
        "order_id": 1, "order_date": "2024-03-01", "product": "Laptop",
        "category": "Electronics", "region": "North", "quantity": 3,
        "unit_price": 99.9,
    }
    row.update(over)
    return row


def test_valid_row_passes(schema):
    df = pd.DataFrame([_valid_row()])
    valid, rejected = validate(df, schema)
    assert len(valid) == 1 and rejected.empty


def test_invalid_rows_are_rejected(schema):
    df = pd.DataFrame([
        _valid_row(order_id=1, quantity=-5),          # below min
        _valid_row(order_id=2, category="Toys"),      # not allowed
        _valid_row(order_id=3, order_date="oops"),    # bad date
    ])
    valid, rejected = validate(df, schema)
    assert valid.empty
    assert len(rejected) == 3
    assert "_errors" in rejected.columns


def test_deduplicate_keeps_last():
    df = pd.DataFrame([
        _valid_row(order_id=1, quantity=1),
        _valid_row(order_id=1, quantity=9),
    ])
    out = deduplicate(df, "order_id")
    assert len(out) == 1 and out.iloc[0]["quantity"] == 9


def test_enrich_and_kpis():
    df = enrich(pd.DataFrame([
        _valid_row(order_id=1, quantity=2, unit_price=10.0, region="North"),
        _valid_row(order_id=2, quantity=1, unit_price=50.0, region="North"),
    ]))
    assert df["revenue"].tolist() == [20.0, 50.0]
    kpis = aggregate_kpis(df)
    assert kpis["revenue"].sum() == 70.0
    assert kpis["orders"].sum() == 2


def test_end_to_end(tmp_path):
    csv = tmp_path / "src.csv"
    pd.DataFrame([
        _valid_row(order_id=1),
        _valid_row(order_id=1),          # duplicate
        _valid_row(order_id=2, quantity=-1),  # invalid
    ]).to_csv(csv, index=False)

    report = run_pipeline([str(csv)], SCHEMA_PATH, str(tmp_path / "w.db"))
    assert report.rows_read == 3
    assert report.rows_rejected == 1
    assert report.rows_after_dedup == 1   # two valid rows collapse to one


def test_upsert_is_idempotent(tmp_path):
    csv = tmp_path / "src.csv"
    pd.DataFrame([_valid_row(order_id=1)]).to_csv(csv, index=False)
    db = str(tmp_path / "w.db")
    run_pipeline([str(csv)], SCHEMA_PATH, db)
    report = run_pipeline([str(csv)], SCHEMA_PATH, db)  # run twice
    assert report.db_stats["orders_in_db"] == 1          # no duplication
