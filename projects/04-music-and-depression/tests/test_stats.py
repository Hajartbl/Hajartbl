"""Unit tests for the statistics toolkit + a smoke test of the pipeline."""

import os
import subprocess
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from stats import bootstrap_ci, cohens_d, one_way_anova, pearson_r, welch_t_test

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_welch_detects_difference():
    rng = np.random.default_rng(0)
    a = rng.normal(0, 1, 200)
    b = rng.normal(1, 1, 200)
    res = welch_t_test(a, b)
    assert res["p_value"] < 0.001
    assert res["n_a"] == 200 and res["n_b"] == 200


def test_welch_no_difference():
    rng = np.random.default_rng(1)
    a = rng.normal(0, 1, 300)
    b = rng.normal(0, 1, 300)
    assert welch_t_test(a, b)["p_value"] > 0.05


def test_cohens_d_sign_and_scale():
    rng = np.random.default_rng(7)
    a = rng.normal(2, 1, 400)
    b = rng.normal(1, 1, 400)
    d = cohens_d(a, b)
    assert d > 0                       # a has the higher mean
    assert abs(d - 1.0) < 0.2          # ~1 SD apart -> d ~ 1
    assert cohens_d(a, a) == 0.0       # no difference -> d = 0


def test_pearson_perfect_correlation():
    x = np.arange(50, dtype=float)
    y = 3 * x + 7
    assert abs(pearson_r(x, y)["r"] - 1.0) < 1e-9


def test_bootstrap_ci_contains_mean():
    rng = np.random.default_rng(3)
    sample = rng.normal(5, 2, 500)
    lo, hi = bootstrap_ci(sample, seed=3)
    assert lo < sample.mean() < hi
    assert lo < hi


def test_anova_detects_group_difference():
    rng = np.random.default_rng(4)
    g1 = rng.normal(0, 1, 100)
    g2 = rng.normal(0, 1, 100)
    g3 = rng.normal(2, 1, 100)
    assert one_way_anova(g1, g2, g3)["p_value"] < 0.001


def test_pipeline_runs_end_to_end():
    """Generate data then run the analysis as a subprocess; expect exit 0."""
    env = dict(os.environ, MPLBACKEND="Agg")
    gen = subprocess.run(
        [sys.executable, "data/generate_data.py"], cwd=ROOT, env=env,
        capture_output=True, text=True,
    )
    assert gen.returncode == 0, gen.stderr
    ana = subprocess.run(
        [sys.executable, "src/analysis.py"], cwd=ROOT, env=env,
        capture_output=True, text=True,
    )
    assert ana.returncode == 0, ana.stderr
    assert "Takeaways" in ana.stdout
