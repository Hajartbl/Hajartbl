"""
Flask REST API serving the RUL model.

Endpoints
---------
GET  /health           liveness + whether the model is loaded
POST /predict          single or batch prediction of RUL + risk band

Example
-------
curl -X POST localhost:8000/predict -H 'Content-Type: application/json' -d '{
  "age_hours": 12000, "temperature_c": 88, "vibration_mm_s": 4.1,
  "pressure_bar": 5.2, "rotational_speed_rpm": 1480, "load_percent": 82
}'
"""

from __future__ import annotations

import os
import pickle
import sys

import pandas as pd
from flask import Flask, jsonify, request

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model"))
from features import RAW_FEATURES, build_features, classify_risk  # noqa: E402

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "model", "rul_model.pkl"
)


def load_model(path: str = MODEL_PATH):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return pickle.load(f)


_UNSET = object()


def create_app(bundle=_UNSET) -> Flask:
    # bundle omitted -> load from disk; bundle=None -> explicitly no model (tests).
    app = Flask(__name__)
    app.config["BUNDLE"] = load_model() if bundle is _UNSET else bundle

    @app.get("/health")
    def health():
        return jsonify(status="ok", model_loaded=app.config["BUNDLE"] is not None)

    @app.post("/predict")
    def predict():
        bundle = app.config["BUNDLE"]
        if bundle is None:
            return jsonify(error="model not trained; run model/train.py"), 503

        payload = request.get_json(silent=True)
        if payload is None:
            return jsonify(error="invalid or missing JSON body"), 400

        records = payload if isinstance(payload, list) else [payload]
        missing = [
            f for r in records for f in RAW_FEATURES if f not in r
        ]
        if missing:
            return jsonify(error="missing features", fields=sorted(set(missing))), 400

        feats = build_features(pd.DataFrame(records))[bundle["features"]]
        preds = bundle["model"].predict(feats)

        results = [
            {"predicted_rul_hours": round(float(p), 1), "risk": classify_risk(p)}
            for p in preds
        ]
        return jsonify(results if isinstance(payload, list) else results[0])

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
