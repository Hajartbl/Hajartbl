"""
Generate a synthetic industrial-equipment sensor dataset for RUL modelling.

Each row is a sensor snapshot of a machine. The target `rul` (Remaining Useful
Life, in operating hours) is a physically-plausible function of the sensor
readings plus noise, so a Random Forest can learn it (target R^2 ~ 0.92).

Run:  python model/generate_data.py
Output: model/equipment.csv
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(11)
N = 6000

FEATURES = [
    "age_hours", "temperature_c", "vibration_mm_s",
    "pressure_bar", "rotational_speed_rpm", "load_percent",
]


def _z(x: np.ndarray) -> np.ndarray:
    return (x - x.mean()) / x.std()


def build() -> pd.DataFrame:
    age_hours = RNG.uniform(0, 20000, N)
    temperature_c = RNG.normal(70, 12, N) + age_hours * 0.0008
    vibration_mm_s = np.abs(RNG.normal(2.5, 1.1, N) + age_hours * 0.00012)
    pressure_bar = RNG.normal(5.0, 0.8, N)
    rotational_speed_rpm = RNG.normal(1500, 220, N)
    load_percent = np.clip(RNG.normal(65, 18, N), 5, 100)

    df = pd.DataFrame({
        "age_hours": age_hours.round(0),
        "temperature_c": temperature_c.round(2),
        "vibration_mm_s": vibration_mm_s.round(3),
        "pressure_bar": pressure_bar.round(2),
        "rotational_speed_rpm": rotational_speed_rpm.round(0),
        "load_percent": load_percent.round(1),
    })

    # Cumulative "stress" drives how much life has been consumed.
    stress = (
        0.45 * _z(df["temperature_c"])
        + 0.45 * _z(df["vibration_mm_s"])
        + 0.15 * _z(df["pressure_bar"])
        + 0.30 * _z(df["load_percent"])
        + 0.60 * (df["age_hours"] / 10000)
    )
    # Irreducible noise sized so a strong model lands around R^2 ~ 0.92,
    # matching real-world sensor unpredictability (no "too perfect" fit).
    noise = RNG.normal(0, 1, N)
    rul = 1500 - 430 * stress + 118 * noise
    df["rul"] = np.clip(rul, 0, None).round(0)
    return df


def main() -> None:
    df = build()
    out = os.path.join(HERE, "equipment.csv")
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} rows to {out}")
    print(f"RUL range: {df['rul'].min():.0f} - {df['rul'].max():.0f} h "
          f"(mean {df['rul'].mean():.0f})")


if __name__ == "__main__":
    main()
