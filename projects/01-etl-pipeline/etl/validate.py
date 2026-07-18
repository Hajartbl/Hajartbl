"""
Validation layer — enforce the YAML schema on incoming data.

Rows that violate the schema are separated out (never silently loaded) so the
pipeline can report data-quality issues instead of corrupting the target table.
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd
import yaml

_CASTERS = {
    "int": int,
    "float": float,
    "str": str,
}


def load_schema(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _check_cell(value, rule: dict) -> tuple[object, str | None]:
    """Return (coerced_value, error). error is None when the cell is valid."""
    if value is None or (isinstance(value, float) and pd.isna(value)) or value == "":
        if rule.get("required", False):
            return value, "missing required value"
        return None, None

    dtype = rule["type"]
    try:
        if dtype == "date":
            coerced = datetime.strptime(str(value), rule.get("format", "%Y-%m-%d")).date()
            coerced = coerced.isoformat()
        else:
            coerced = _CASTERS[dtype](value)
    except (ValueError, TypeError):
        return value, f"cannot cast {value!r} to {dtype}"

    if "allowed" in rule and coerced not in rule["allowed"]:
        return coerced, f"{coerced!r} not in allowed set"
    if "min" in rule and coerced < rule["min"]:
        return coerced, f"{coerced} < min {rule['min']}"
    if "max" in rule and coerced > rule["max"]:
        return coerced, f"{coerced} > max {rule['max']}"
    if "max_length" in rule and len(str(coerced)) > rule["max_length"]:
        return coerced, f"length > {rule['max_length']}"
    return coerced, None


def validate(df: pd.DataFrame, schema: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split df into (valid_rows, rejected_rows).

    Valid rows are returned with values coerced to the schema's types.
    Rejected rows carry an extra `_errors` column describing what failed.
    """
    columns = schema["columns"]
    valid_records, rejected_records = [], []

    for _, row in df.iterrows():
        coerced, errors = {}, []
        for col, rule in columns.items():
            value = row.get(col)
            new_value, err = _check_cell(value, rule)
            coerced[col] = new_value
            if err:
                errors.append(f"{col}: {err}")
        if errors:
            bad = dict(row)
            bad["_errors"] = "; ".join(errors)
            rejected_records.append(bad)
        else:
            valid_records.append(coerced)

    valid = pd.DataFrame(valid_records, columns=list(columns))
    rejected = pd.DataFrame(rejected_records)
    return valid, rejected
