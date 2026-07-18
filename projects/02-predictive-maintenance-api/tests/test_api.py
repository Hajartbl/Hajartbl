"""Tests for the predictive-maintenance API (no trained model required)."""

import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "model"))

from app.api import create_app
from features import classify_risk, feature_columns


class _StubModel:
    """Deterministic stand-in so API tests don't depend on a trained .pkl."""
    def predict(self, X):
        return np.full(len(X), 300.0)


def _client(bundle):
    return create_app(bundle=bundle).test_client()


def _valid_payload(**over):
    p = {
        "age_hours": 12000, "temperature_c": 88, "vibration_mm_s": 4.1,
        "pressure_bar": 5.2, "rotational_speed_rpm": 1480, "load_percent": 82,
    }
    p.update(over)
    return p


def test_classify_risk_bands():
    assert classify_risk(100) == "HIGH"
    assert classify_risk(400) == "MEDIUM"
    assert classify_risk(900) == "LOW"


def test_health_ok():
    resp = _client(None).get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_predict_without_model_returns_503():
    resp = _client(None).post("/predict", json=_valid_payload())
    assert resp.status_code == 503


def test_predict_single():
    bundle = {"model": _StubModel(), "features": feature_columns()}
    resp = _client(bundle).post("/predict", json=_valid_payload())
    assert resp.status_code == 200
    body = resp.get_json()
    assert body["predicted_rul_hours"] == 300.0
    assert body["risk"] == "MEDIUM"


def test_predict_batch():
    bundle = {"model": _StubModel(), "features": feature_columns()}
    resp = _client(bundle).post("/predict", json=[_valid_payload(), _valid_payload()])
    assert resp.status_code == 200
    assert len(resp.get_json()) == 2


def test_predict_missing_feature_returns_400():
    bundle = {"model": _StubModel(), "features": feature_columns()}
    bad = _valid_payload()
    del bad["temperature_c"]
    resp = _client(bundle).post("/predict", json=bad)
    assert resp.status_code == 400
    assert "temperature_c" in resp.get_json()["fields"]
