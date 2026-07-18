"""
Train the Remaining-Useful-Life (RUL) model.

Random Forest regressor on the engineered features. Reports R^2 / MAE on a
held-out test set and serialises the fitted model to model/rul_model.pkl.

Run:  python model/train.py
"""

from __future__ import annotations

import json
import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from features import build_features, feature_columns

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "equipment.csv")
MODEL_PATH = os.path.join(HERE, "rul_model.pkl")
METRICS_PATH = os.path.join(HERE, "metrics.json")


def main() -> None:
    if not os.path.exists(DATA):
        raise SystemExit("equipment.csv missing. Run `python model/generate_data.py` first.")

    df = build_features(pd.read_csv(DATA))
    cols = feature_columns()
    X, y = df[cols], df["rul"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = RandomForestRegressor(
        n_estimators=300, max_depth=16, min_samples_leaf=3,
        n_jobs=-1, random_state=42,
    )
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    metrics = {
        "r2": round(float(r2_score(y_test, pred)), 4),
        "mae_hours": round(float(mean_absolute_error(y_test, pred)), 1),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }

    with open(MODEL_PATH, "wb") as f:
        pickle.dump({"model": model, "features": cols}, f)
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)

    print(f"Test R^2 : {metrics['r2']}")
    print(f"Test MAE : {metrics['mae_hours']} h")
    print(f"Saved model -> {os.path.relpath(MODEL_PATH, HERE)}")

    print("\nTop feature importances:")
    importances = sorted(
        zip(cols, model.feature_importances_), key=lambda t: t[1], reverse=True
    )
    for name, imp in importances[:5]:
        print(f"  {name:<22} {imp:.3f}")


if __name__ == "__main__":
    main()
