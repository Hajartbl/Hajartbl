"""
Image-quality metrics for evaluating the correction.

- PSNR: fidelity of the corrected temperature map vs. ground truth.
- Non-uniformity (NU%): residual fixed-pattern noise on a uniform scene —
  the spatial spread relative to the mean. Lower is better.

BRISQUE (the no-reference perceptual metric used in the original challenge)
is referenced in the README; here we use PSNR + NU% which are reproducible
without a pre-trained perceptual model.
"""

from __future__ import annotations

import numpy as np


def psnr(reference: np.ndarray, test: np.ndarray) -> float:
    """Peak Signal-to-Noise Ratio in dB (higher = closer to reference)."""
    mse = np.nanmean((reference - test) ** 2)
    if mse == 0:
        return float("inf")
    peak = np.nanmax(reference) - np.nanmin(reference)
    return float(20 * np.log10(peak) - 10 * np.log10(mse))


def non_uniformity(frame: np.ndarray) -> float:
    """Spatial non-uniformity (%) of a nominally uniform frame."""
    return float(100.0 * np.nanstd(frame) / np.abs(np.nanmean(frame)))
