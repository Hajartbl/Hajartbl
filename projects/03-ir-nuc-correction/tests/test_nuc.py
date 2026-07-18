"""Tests for the NUC correction pipeline."""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nuc.newton import interpolate, divided_differences, newton_eval
from nuc.correction import calibrate, correct, detect_bad_pixels
from nuc.metrics import non_uniformity, psnr
from nuc.simulate import IRSensor, make_test_scene

CAL_TEMPS = np.array([10.0, 20.0, 30.0, 40.0, 50.0])


def test_newton_recovers_cubic_exactly():
    # Degree-3 Newton must reproduce a cubic at machine precision.
    x = np.array([0.0, 1.0, 2.0, 3.0, 4.0])
    f = lambda t: 2 * t**3 - 5 * t**2 + t - 7
    y = f(x)
    assert np.isclose(interpolate(x, y, 2.5, degree=3), f(2.5))


def test_newton_vectorised_frames():
    # Interpolate a stack of frames (linear in T -> exact).
    temps = CAL_TEMPS
    gain = np.array([[1.0, 2.0], [0.5, 3.0]])
    frames = np.stack([gain * t + 10 for t in temps])
    out = interpolate(temps, frames, 25.0, degree=3)
    assert np.allclose(out, gain * 25.0 + 10)


def test_calibration_recovers_gain_offset():
    sensor = IRSensor(shape=(32, 32), bad_pixel_frac=0.0)
    frames = np.stack([sensor.capture_uniform(t, read_noise=0.0) for t in CAL_TEMPS])
    resp, off = calibrate(CAL_TEMPS, frames)
    assert np.allclose(resp, sensor.gain, atol=1e-6)
    assert np.allclose(off, sensor.offset, atol=1e-6)


def test_correction_improves_psnr():
    sensor = IRSensor(shape=(48, 64))
    frames = np.stack([sensor.capture_uniform(t) for t in CAL_TEMPS])
    resp, off = calibrate(CAL_TEMPS, frames)
    bad = detect_bad_pixels(resp, off)
    scene = make_test_scene(sensor.shape)
    raw = sensor.capture_scene(scene)
    corrected = correct(raw, resp, off, bad)
    assert psnr(scene, corrected) > psnr(scene, raw) + 10  # big improvement


def test_non_uniformity_drops():
    sensor = IRSensor(shape=(48, 64))
    frames = np.stack([sensor.capture_uniform(t) for t in CAL_TEMPS])
    resp, off = calibrate(CAL_TEMPS, frames)
    bad = detect_bad_pixels(resp, off)
    raw_u = sensor.capture_uniform(35.0)
    corr_u = correct(raw_u, resp, off, bad)
    assert non_uniformity(corr_u) < non_uniformity(raw_u)


def test_bad_pixels_detected():
    sensor = IRSensor(shape=(64, 64), bad_pixel_frac=0.01)
    frames = np.stack([sensor.capture_uniform(t) for t in CAL_TEMPS])
    resp, off = calibrate(CAL_TEMPS, frames)
    assert detect_bad_pixels(resp, off).sum() > 0
