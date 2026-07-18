"""
Generate a synthetic "Music & Mental Health" (MxMH-style) survey dataset.

Each row is a respondent: their music-listening habits and self-reported
mental-health scores (0–10). The data is synthetic but built from relationships
grounded in the mood-regulation literature, so the analysis surfaces genuine,
interpretable patterns:

  - Using music deliberately to regulate mood ("Improve") is associated with
    LOWER depression (mood-regulation hypothesis).
  - Listening time has a U-shaped link with depression: moderate listening
    tracks the lowest scores, very heavy listening slightly higher (escapism /
    rumination).
  - Playing an instrument (active musical engagement) tracks slightly lower
    depression.
  - Anxiety, insomnia and depression are positively correlated (comorbidity).

NB: this is observational, synthetic data — associations are not causal.

Run:  python data/generate_data.py
Output: data/survey.csv
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
RNG = np.random.default_rng(2024)
N = 736

GENRES = [
    "Pop", "Rock", "Classical", "Hip hop", "EDM",
    "R&B", "Jazz", "Metal", "Folk", "Lo-fi",
]
# Typical tempo (BPM) centre per genre — used to synthesise a plausible bpm.
GENRE_BPM = {
    "Pop": 118, "Rock": 128, "Classical": 90, "Hip hop": 95, "EDM": 132,
    "R&B": 100, "Jazz": 110, "Metal": 140, "Folk": 104, "Lo-fi": 78,
}
# Small fixed per-genre association with depression (demonstrative, modest).
GENRE_DEP = {
    "Pop": -0.1, "Rock": 0.0, "Classical": -0.3, "Hip hop": 0.2, "EDM": 0.1,
    "R&B": 0.0, "Jazz": -0.2, "Metal": 0.3, "Folk": -0.1, "Lo-fi": -0.2,
}


def build() -> pd.DataFrame:
    age = np.clip(RNG.normal(25, 9, N).round(), 13, 72).astype(int)
    hours_per_day = np.clip(RNG.exponential(2.6, N), 0, 12).round(1)
    while_working = RNG.choice(["Yes", "No"], N, p=[0.72, 0.28])
    instrumentalist = RNG.choice(["Yes", "No"], N, p=[0.32, 0.68])
    composer = RNG.choice(["Yes", "No"], N, p=[0.12, 0.88])
    exploratory = RNG.choice(["Yes", "No"], N, p=[0.63, 0.37])
    fav_genre = RNG.choice(GENRES, N)
    bpm = np.array([
        int(np.clip(RNG.normal(GENRE_BPM[g], 12), 50, 200)) for g in fav_genre
    ])

    # Latent vulnerability trait -> drives the correlated MH scores.
    z = RNG.normal(0, 1, N)

    # music_effects: most listeners report "Improve"; a few "No effect"/"Worsen".
    effect = RNG.choice(
        ["Improve", "No effect", "Worsen"], N, p=[0.74, 0.21, 0.05]
    )
    effect_shift = np.select(
        [effect == "Improve", effect == "Worsen"],
        [-1.2, 0.9],
        default=0.0,
    )

    genre_shift = np.array([GENRE_DEP[g] for g in fav_genre])

    depression = (
        5.0
        + 1.8 * z
        + effect_shift
        + 0.13 * (hours_per_day - 3.0) ** 2        # U-shape: min around ~3h/day
        - 0.5 * (instrumentalist == "Yes")
        - 0.02 * (age - 25)
        + genre_shift
        + RNG.normal(0, 0.8, N)
    )
    anxiety = 5.0 + 1.6 * z + 0.4 * (effect == "Worsen") + RNG.normal(0, 1.1, N)
    insomnia = 4.2 + 1.3 * z + RNG.normal(0, 1.3, N)
    ocd = 3.0 + 1.0 * z + RNG.normal(0, 1.4, N)

    df = pd.DataFrame({
        "age": age,
        "hours_per_day": hours_per_day,
        "while_working": while_working,
        "instrumentalist": instrumentalist,
        "composer": composer,
        "exploratory": exploratory,
        "fav_genre": fav_genre,
        "bpm": bpm,
        "music_effects": effect,
        "anxiety": _score(anxiety),
        "depression": _score(depression),
        "insomnia": _score(insomnia),
        "ocd": _score(ocd),
    })
    return df


def _score(x: np.ndarray) -> np.ndarray:
    """Clip a latent value to the survey's 0–10 integer scale."""
    return np.clip(np.rint(x), 0, 10).astype(int)


def main() -> None:
    df = build()
    out = os.path.join(HERE, "survey.csv")
    df.to_csv(out, index=False)
    print(f"Wrote {len(df)} respondents to {out}")
    print(f"Mean depression: {df['depression'].mean():.2f} / 10")
    print("By music_effects:")
    print(df.groupby("music_effects")["depression"].mean().round(2).to_string())


if __name__ == "__main__":
    main()
