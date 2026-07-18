"""
Feature engineering shared by training and serving.

Keeping this in one place guarantees the API computes features exactly the way
the model was trained — the classic source of train/serve skew.
"""

from __future__ import annotations

import pandas as pd

RAW_FEATURES = [
    "age_hours", "temperature_c", "vibration_mm_s",
    "pressure_bar", "rotational_speed_rpm", "load_percent",
]

# Risk thresholds on predicted RUL (operating hours).
RISK_HIGH = 250
RISK_MEDIUM = 650


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered interaction/ratio features on top of the raw sensors."""
    df = df.copy()
    df["thermal_load"] = df["temperature_c"] * df["load_percent"] / 100
    df["vibration_per_krpm"] = df["vibration_mm_s"] / (df["rotational_speed_rpm"] / 1000 + 1e-6)
    df["age_khours"] = df["age_hours"] / 1000
    return df


def feature_columns() -> list[str]:
    return RAW_FEATURES + ["thermal_load", "vibration_per_krpm", "age_khours"]


def classify_risk(rul: float) -> str:
    """Map a predicted RUL to an operational risk band."""
    if rul < RISK_HIGH:
        return "HIGH"
    if rul < RISK_MEDIUM:
        return "MEDIUM"
    return "LOW"
