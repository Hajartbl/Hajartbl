"""
Radiometric (non-uniformity) correction.

From a stack of calibration frames captured at known temperatures we estimate,
per pixel, the responsivity (gain) and offset by linear regression:

    raw = responsivity * T + offset

Correcting a new frame then inverts that relation to recover image temperature:

    T_hat = (raw - offset) / responsivity

Bad pixels (near-zero gain, outlier offset) are detected via a robust
MAD threshold and repaired by local median replacement.
"""

from __future__ import annotations

import numpy as np


def calibrate(temps: np.ndarray, frames: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Per-pixel linear regression across calibration temperatures.

    temps  : shape (k,)          calibration temperatures
    frames : shape (k, H, W)     one raw frame per temperature
    returns (responsivity, offset), each shape (H, W).
    """
    temps = np.asarray(temps, dtype=float)
    k = len(temps)
    t_mean = temps.mean()
    y_mean = frames.mean(axis=0)
    dt = (temps - t_mean).reshape(k, 1, 1)
    responsivity = (dt * (frames - y_mean)).sum(axis=0) / (dt.squeeze() ** 2).sum()
    offset = y_mean - responsivity * t_mean
    return responsivity, offset


def detect_bad_pixels(responsivity: np.ndarray, offset: np.ndarray,
                      k_mad: float = 6.0) -> np.ndarray:
    """Flag pixels whose gain or offset is a robust outlier (boolean mask)."""
    def _mad_outliers(a):
        med = np.median(a)
        mad = np.median(np.abs(a - med)) + 1e-9
        return np.abs(a - med) > k_mad * mad

    dead = responsivity < 0.1 * np.median(responsivity)
    return dead | _mad_outliers(responsivity) | _mad_outliers(offset)


def repair(image: np.ndarray, bad_mask: np.ndarray) -> np.ndarray:
    """Replace flagged pixels with the median of their valid 3x3 neighbours."""
    out = image.copy()
    ys, xs = np.where(bad_mask)
    h, w = image.shape
    for y, x in zip(ys, xs):
        y0, y1 = max(0, y - 1), min(h, y + 2)
        x0, x1 = max(0, x - 1), min(w, x + 2)
        patch = image[y0:y1, x0:x1]
        patch_mask = bad_mask[y0:y1, x0:x1]
        good = patch[~patch_mask]
        if good.size:
            out[y, x] = np.median(good)
    return out


def correct(raw: np.ndarray, responsivity: np.ndarray, offset: np.ndarray,
            bad_mask: np.ndarray | None = None) -> np.ndarray:
    """Apply NUC to a raw frame, returning an estimated temperature map."""
    safe_gain = np.where(np.abs(responsivity) < 1e-6, np.nan, responsivity)
    temp = (raw - offset) / safe_gain
    if bad_mask is not None:
        temp = repair(temp, bad_mask | np.isnan(temp))
    return temp
