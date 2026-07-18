"""
End-to-end NUC demonstration.

1. Build a non-uniform IR sensor and capture multi-temperature calibration.
2. Reconstruct a *missing* calibration frame with Newton interpolation (deg 3).
3. Calibrate (per-pixel responsivity/offset) + detect/repair bad pixels.
4. Correct a real image and a uniform image; report PSNR and non-uniformity.
5. Save before/after figures to figures/.

Run:  python run.py
"""

from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from nuc.simulate import IRSensor, make_test_image
from nuc.newton import interpolate
from nuc.correction import calibrate, correct, detect_bad_pixels
from nuc.metrics import non_uniformity, psnr

HERE = os.path.dirname(os.path.abspath(__file__))
FIG_DIR = os.path.join(HERE, "figures")
CAL_TEMPS = np.array([10.0, 20.0, 30.0, 40.0, 50.0])


def main() -> None:
    os.makedirs(FIG_DIR, exist_ok=True)
    sensor = IRSensor()

    # 1. Calibration stack -------------------------------------------------
    frames = np.stack([sensor.capture_uniform(t) for t in CAL_TEMPS])

    # 2. Newton reconstruction of a missing calibration frame --------------
    missing_i = 2  # pretend the 30 °C frame is corrupted/missing
    kept = np.delete(np.arange(len(CAL_TEMPS)), missing_i)
    recon = interpolate(CAL_TEMPS[kept], frames[kept], CAL_TEMPS[missing_i], degree=3)
    recon_psnr = psnr(frames[missing_i], recon)
    recon_rmse = float(np.sqrt(np.mean((frames[missing_i] - recon) ** 2)))
    print("Newton reconstruction of missing 30 °C calibration frame:")
    print(f"  PSNR {recon_psnr:.1f} dB | RMSE {recon_rmse:.2f} counts")

    # 3. Calibrate + bad-pixel map ----------------------------------------
    responsivity, offset = calibrate(CAL_TEMPS, frames)
    bad_mask = detect_bad_pixels(responsivity, offset)
    print(f"\nCalibration: {bad_mask.sum()} bad pixels detected "
          f"({100 * bad_mask.mean():.2f}% of the array)")

    # 4a. Correct a real image --------------------------------------------
    truth = make_test_image(sensor.shape)
    raw_image = sensor.capture_image(truth)
    corrected = correct(raw_image, responsivity, offset, bad_mask)
    image_psnr_raw = psnr(truth, raw_image)
    image_psnr_corr = psnr(truth, corrected)
    print("\nImage correction (vs ground-truth temperature):")
    print(f"  PSNR raw {image_psnr_raw:.1f} dB -> corrected {image_psnr_corr:.1f} dB")

    # 4b. Non-uniformity on a fresh uniform image -------------------------
    raw_uniform = sensor.capture_uniform(35.0)
    corr_uniform = correct(raw_uniform, responsivity, offset, bad_mask)
    nu_raw = non_uniformity(raw_uniform)
    nu_corr = non_uniformity(corr_uniform)
    print("\nNon-uniformity on a uniform 35 °C image:")
    print(f"  NU raw {nu_raw:.2f}% -> corrected {nu_corr:.2f}% "
          f"({nu_raw / nu_corr:.0f}x reduction)")

    _save_image_figure(raw_image, corrected, truth)
    _save_uniform_figure(raw_uniform, corr_uniform)
    print(f"\nFigures saved to {os.path.relpath(FIG_DIR, HERE)}/")


def _save_image_figure(raw, corrected, truth):
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for ax, img, title in zip(
        axes,
        [raw, corrected, truth],
        ["Raw (fixed-pattern noise)", "Corrected (NUC)", "Ground truth"],
    ):
        im = ax.imshow(img, cmap="inferno")
        ax.set_title(title, fontweight="bold")
        ax.axis("off")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Radiometric correction of an IR image", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "image_correction.png"), dpi=110)
    plt.close(fig)


def _save_uniform_figure(raw, corrected):
    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    for ax, img, title in zip(
        axes, [raw, corrected], ["Raw uniform image", "Corrected"]
    ):
        im = ax.imshow(img, cmap="viridis")
        ax.set_title(title, fontweight="bold")
        ax.axis("off")
        fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    fig.suptitle("Fixed-pattern noise removed on a uniform target", fontweight="bold")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "uniform_correction.png"), dpi=110)
    plt.close(fig)


if __name__ == "__main__":
    main()
