"""
Music & Depression — main analysis.

Loads the survey, runs the statistical tests, prints a readable report, and
saves publication-quality figures to figures/.

Run:  python src/analysis.py
Prereq: data/survey.csv (run data/generate_data.py first).
"""

from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stats import (  # noqa: E402
    bootstrap_ci, cohens_d, one_way_anova, pearson_r, welch_t_test,
)

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "survey.csv")
FIG_DIR = os.path.join(ROOT, "figures")

ACCENT = "#6366f1"   # indigo
GOOD = "#16a34a"     # green
BAD = "#dc2626"      # red
MUTED = "#94a3b8"


def _style():
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        "figure.dpi": 110, "axes.titleweight": "bold",
        "axes.titlesize": 13, "font.size": 10,
    })


def section(title: str):
    print(f"\n{'=' * 66}\n{title}\n{'=' * 66}")


# --------------------------------------------------------------------------- #
# Analyses
# --------------------------------------------------------------------------- #
def overview(df: pd.DataFrame):
    section("1. Sample overview")
    mean = df["depression"].mean()
    lo, hi = bootstrap_ci(df["depression"].to_numpy())
    print(f"N = {len(df)} respondents")
    print(f"Mean depression: {mean:.2f} / 10   (95% bootstrap CI [{lo:.2f}, {hi:.2f}])")
    print(f"Median age: {df['age'].median():.0f}   "
          f"Median listening: {df['hours_per_day'].median():.1f} h/day")


def effect_of_using_music(df: pd.DataFrame):
    section("2. Does using music to regulate mood track lower depression?")
    groups = {k: g["depression"].to_numpy() for k, g in df.groupby("music_effects")}
    anova = one_way_anova(*groups.values())
    print(f"One-way ANOVA across {anova['k_groups']} groups: "
          f"F = {anova['F']:.2f}, p = {anova['p_value']:.2e}")

    improve, none = groups["Improve"], groups["No effect"]
    tt = welch_t_test(improve, none)
    d = cohens_d(improve, none)
    print(f"\n'Improve' (n={tt['n_a']}) vs 'No effect' (n={tt['n_b']}):")
    print(f"  mean {improve.mean():.2f} vs {none.mean():.2f}  "
          f"(Δ = {none.mean() - improve.mean():.2f} points)")
    print(f"  Welch t = {tt['t']:.2f}, p = {tt['p_value']:.2e}, Cohen's d = {d:.2f}")

    # Figure: mean depression per effect group + 95% CI
    order = ["Improve", "No effect", "Worsen"]
    means, los, his = [], [], []
    for k in order:
        g = groups[k]
        means.append(g.mean())
        lo, hi = bootstrap_ci(g)
        los.append(g.mean() - lo)
        his.append(hi - g.mean())
    fig, ax = plt.subplots(figsize=(7.5, 5))
    colors = [GOOD, MUTED, BAD]
    ax.bar(order, means, yerr=[los, his], capsize=6, color=colors, alpha=0.9)
    for i, m in enumerate(means):
        ax.text(i, m + 0.15, f"{m:.2f}", ha="center", fontweight="bold")
    ax.set_ylabel("Mean depression (0–10)")
    ax.set_xlabel("Self-reported effect of music on mental health")
    ax.set_title("Listeners who use music to improve mood report lower depression")
    fig.tight_layout()
    _save(fig, "depression_by_music_effect.png")


def listening_time(df: pd.DataFrame):
    section("3. How does listening time relate to depression?")
    pr = pearson_r(df["hours_per_day"], df["depression"])
    print(f"Linear correlation hours ↔ depression: r = {pr['r']:.3f}, "
          f"p = {pr['p_value']:.2e}")
    print("  (a single linear r masks the relationship — see the U-shape below)")

    bins = [0, 1, 2, 3, 5, 12]
    labels = ["<1h", "1-2h", "2-3h", "3-5h", "5h+"]
    df = df.assign(band=pd.cut(df["hours_per_day"], bins=bins, labels=labels,
                               include_lowest=True))
    by_band = df.groupby("band", observed=True)["depression"].agg(["mean", "count"])
    print("\nMean depression by listening band (U-shaped):")
    print(by_band.round(2).to_string())

    fig, ax = plt.subplots(figsize=(8, 5))
    means = by_band["mean"]
    ax.plot(range(len(means)), means.values, "-o", color=ACCENT, linewidth=2.2,
            markersize=8)
    for i, v in enumerate(means.values):
        ax.text(i, v + 0.06, f"{v:.2f}", ha="center", fontsize=9)
    ax.set_xticks(range(len(means)))
    ax.set_xticklabels(means.index)
    ax.set_xlabel("Daily listening time")
    ax.set_ylabel("Mean depression (0–10)")
    ax.set_title("U-shaped link: moderate listening tracks the lowest depression")
    fig.tight_layout()
    _save(fig, "depression_by_listening_time.png")


def by_genre(df: pd.DataFrame):
    section("4. Depression by favourite genre")
    g = (df.groupby("fav_genre")["depression"]
         .agg(["mean", "count"]).sort_values("mean"))
    print(g.round(2).to_string())

    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    overall = df["depression"].mean()
    colors = [BAD if v > overall else GOOD for v in g["mean"]]
    ax.barh(g.index, g["mean"], color=colors, alpha=0.9)
    ax.axvline(overall, color=MUTED, ls="--", lw=1.3)
    ax.text(overall + 0.03, len(g) - 0.5, f"overall {overall:.2f}",
            color=MUTED, style="italic", fontsize=9)
    ax.set_xlabel("Mean depression (0–10)")
    ax.set_title("Mean depression by favourite genre")
    fig.tight_layout()
    _save(fig, "depression_by_genre.png")


def comorbidity(df: pd.DataFrame):
    section("5. Comorbidity between mental-health dimensions")
    cols = ["anxiety", "depression", "insomnia", "ocd"]
    corr = df[cols].corr()
    print(corr.round(2).to_string())

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="rocket_r", vmin=0, vmax=1,
                square=True, cbar_kws={"label": "Pearson r"}, ax=ax)
    ax.set_title("Mental-health dimensions are positively correlated")
    fig.tight_layout()
    _save(fig, "comorbidity_heatmap.png")


def drivers(df: pd.DataFrame):
    section("6. Standardised drivers of depression (linear model)")
    d = df.copy()
    for col in ["instrumentalist", "exploratory"]:
        d[col] = (d[col] == "Yes").astype(int)
    d["uses_music_to_improve"] = (d["music_effects"] == "Improve").astype(int)

    features = ["hours_per_day", "age", "bpm", "instrumentalist",
                "exploratory", "uses_music_to_improve"]
    X = StandardScaler().fit_transform(d[features])
    y = d["depression"].to_numpy()
    model = LinearRegression().fit(X, y)

    coefs = sorted(zip(features, model.coef_), key=lambda t: abs(t[1]), reverse=True)
    print(f"R² = {model.score(X, y):.3f}")
    print("Standardised coefficients (effect of +1 SD on depression points):")
    for name, c in coefs:
        print(f"  {name:<24} {c:+.3f}")

    fig, ax = plt.subplots(figsize=(8, 5))
    names = [c[0] for c in coefs][::-1]
    vals = [c[1] for c in coefs][::-1]
    colors = [BAD if v > 0 else GOOD for v in vals]
    ax.barh(names, vals, color=colors, alpha=0.9)
    ax.axvline(0, color="black", lw=0.8)
    ax.set_xlabel("Standardised coefficient (→ higher depression)")
    ax.set_title("What moves depression? (standardised linear model)")
    fig.tight_layout()
    _save(fig, "depression_drivers.png")


def _save(fig, name: str):
    path = os.path.join(FIG_DIR, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"  [figure] {os.path.relpath(path, ROOT)}")


def main():
    if not os.path.exists(DATA):
        raise SystemExit("survey.csv missing. Run `python data/generate_data.py` first.")
    os.makedirs(FIG_DIR, exist_ok=True)
    _style()
    df = pd.read_csv(DATA)

    overview(df)
    effect_of_using_music(df)
    listening_time(df)
    by_genre(df)
    comorbidity(df)
    drivers(df)

    section("Takeaways")
    print("• Using music for mood regulation is associated with lower depression.")
    print("• Listening time shows a U-shape — moderate is best, excessive is not.")
    print("• Anxiety / depression / insomnia co-occur (comorbidity).")
    print("• Observational synthetic data: associations, not causal claims.")


if __name__ == "__main__":
    main()
