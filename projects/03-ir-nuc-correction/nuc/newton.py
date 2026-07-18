"""
Newton polynomial interpolation via divided differences.

Vectorised so it interpolates a whole image at once: the y-nodes may be scalars
or N-D arrays (one calibration *frame* per node). Used to reconstruct a missing
calibration temperature from the surrounding ones.
"""

from __future__ import annotations

import numpy as np


def divided_differences(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    """
    Compute Newton divided-difference coefficients.

    x : shape (n,)         interpolation nodes (e.g. calibration temperatures)
    y : shape (n, ...)     values at each node (scalar or a full frame per node)
    returns coefficients of shape (n, ...).
    """
    x = np.asarray(x, dtype=float)
    coef = np.array(y, dtype=float)
    n = len(x)
    for level in range(1, n):
        # coef[j] <- (coef[j] - coef[j-1]) / (x[j] - x[j-level])
        denom = (x[level:] - x[: n - level]).reshape(
            (-1,) + (1,) * (coef.ndim - 1)
        )
        coef[level:] = (coef[level:] - coef[level - 1 : -1]) / denom
    return coef


def newton_eval(x: np.ndarray, coef: np.ndarray, x_eval: float) -> np.ndarray:
    """Evaluate the Newton polynomial (Horner-style) at a single point x_eval."""
    x = np.asarray(x, dtype=float)
    n = len(x)
    result = np.array(coef[n - 1])
    for k in range(n - 2, -1, -1):
        result = result * (x_eval - x[k]) + coef[k]
    return result


def interpolate(x: np.ndarray, y: np.ndarray, x_eval: float, degree: int = 3) -> np.ndarray:
    """
    Interpolate y(x_eval) using a Newton polynomial of the given degree.

    The `degree + 1` nodes closest to x_eval are used (local interpolation),
    which is more stable than fitting a global high-degree polynomial.
    """
    x = np.asarray(x, dtype=float)
    order = np.argsort(np.abs(x - x_eval))[: degree + 1]
    order = order[np.argsort(x[order])]  # keep nodes sorted
    coef = divided_differences(x[order], np.asarray(y)[order])
    return newton_eval(x[order], coef, x_eval)
