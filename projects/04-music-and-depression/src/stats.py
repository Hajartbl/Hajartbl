"""
Small, tested statistics toolkit used by the analysis.

Kept dependency-light (numpy + scipy) and pure so every function is unit-tested
in isolation — the kind of rigor a cognitive-science analysis needs when it
reports effect sizes and confidence intervals rather than just p-values.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def welch_t_test(a, b) -> dict:
    """Welch's t-test (unequal variances) between two independent samples."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    t, p = stats.ttest_ind(a, b, equal_var=False)
    return {"t": float(t), "p_value": float(p), "n_a": a.size, "n_b": b.size}


def cohens_d(a, b) -> float:
    """Standardised mean difference (pooled SD). |d|: 0.2 small, 0.5 med, 0.8 large."""
    a, b = np.asarray(a, float), np.asarray(b, float)
    na, nb = a.size, b.size
    pooled_var = ((na - 1) * a.var(ddof=1) + (nb - 1) * b.var(ddof=1)) / (na + nb - 2)
    if pooled_var == 0:
        return 0.0
    return float((a.mean() - b.mean()) / np.sqrt(pooled_var))


def pearson_r(x, y) -> dict:
    """Pearson correlation coefficient with its p-value."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    r, p = stats.pearsonr(x, y)
    return {"r": float(r), "p_value": float(p), "n": x.size}


def bootstrap_ci(sample, statistic=np.mean, n_boot=5000, ci=95, seed=0) -> tuple[float, float]:
    """Percentile bootstrap confidence interval for any statistic."""
    rng = np.random.default_rng(seed)
    sample = np.asarray(sample, float)
    boots = [
        statistic(rng.choice(sample, sample.size, replace=True))
        for _ in range(n_boot)
    ]
    lo = (100 - ci) / 2
    return float(np.percentile(boots, lo)), float(np.percentile(boots, 100 - lo))


def one_way_anova(*groups) -> dict:
    """One-way ANOVA across 2+ groups."""
    f, p = stats.f_oneway(*[np.asarray(g, float) for g in groups])
    return {"F": float(f), "p_value": float(p), "k_groups": len(groups)}
