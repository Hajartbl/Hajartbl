"""
Simulate a non-uniform infrared focal-plane array (FPA).

Real IR detectors suffer from Fixed Pattern Noise: every pixel has its own gain
(responsivity) and offset, so a perfectly uniform scene still looks grainy. We
model each pixel's raw response to a scene temperature T as:

    raw[i,j] = gain[i,j] * T + offset[i,j] + read_noise      (linear regime)

plus a handful of "bad" pixels (dead / saturated) to exercise outlier handling.
"""

from __future__ import annotations

import numpy as np

RNG = np.random.default_rng(3)


class IRSensor:
    def __init__(self, shape=(96, 128), bad_pixel_frac=0.004):
        self.shape = shape
        # Per-pixel gain ~1.0 with ~5% non-uniformity; offset with spread.
        self.gain = RNG.normal(1.0, 0.05, shape)
        self.offset = RNG.normal(200.0, 25.0, shape)

        # Inject bad pixels: dead (gain~0) and hot (huge offset).
        n_bad = max(1, int(np.prod(shape) * bad_pixel_frac))
        idx = np.unravel_index(
            RNG.choice(np.prod(shape), n_bad, replace=False), shape
        )
        half = n_bad // 2
        self.gain[idx[0][:half], idx[1][:half]] = 0.01          # dead
        self.offset[idx[0][half:], idx[1][half:]] = 4000.0      # hot
        self.bad_pixels = idx

    def capture_uniform(self, temperature: float, read_noise=1.5) -> np.ndarray:
        """Raw frame of a uniform black-body scene at `temperature`."""
        noise = RNG.normal(0, read_noise, self.shape)
        return self.gain * temperature + self.offset + noise

    def capture_scene(self, scene_temp: np.ndarray, read_noise=1.5) -> np.ndarray:
        """Raw frame of an arbitrary scene (per-pixel true temperature map)."""
        noise = RNG.normal(0, read_noise, self.shape)
        return self.gain * scene_temp + self.offset + noise


def make_test_scene(shape=(96, 128)) -> np.ndarray:
    """A synthetic scene: warm disk + gradient background (ground-truth temps)."""
    h, w = shape
    yy, xx = np.mgrid[0:h, 0:w]
    background = 20 + 10 * (xx / w)                     # 20–30 °C gradient
    cy, cx, r = h * 0.4, w * 0.55, min(h, w) * 0.18
    disk = ((yy - cy) ** 2 + (xx - cx) ** 2) < r ** 2
    scene = background.copy()
    scene[disk] = 45.0                                  # warm object
    return scene
