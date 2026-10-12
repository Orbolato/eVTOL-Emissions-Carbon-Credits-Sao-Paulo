"""
Generate flight-time histograms from the BlueSky aircraft flight times.

The script writes the three histograms used in the article:
  - output/flight_times_histogram_no_mvp.pdf  (no conflict resolution)
  - output/flight_times_histogram.pdf         (MVP 60 s)
  - output/flight_times_histogram_mvp120.pdf  (MVP 120 s)

It also writes a combined comparison plot and a summary table.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
FLIGHT_TIMES_PATH = ROOT / "data" / "simulation" / "aircraft_flight_times.csv"
REV_DIR = ROOT / "output"

plt.rcParams.update(
    {
        "font.size": 12,
        "axes.labelsize": 13,
        "xtick.labelsize": 12,
        "ytick.labelsize": 12,
        "legend.fontsize": 11,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "font.family": "DejaVu Sans",
    }
)

SCENARIOS = {
    "No conflict resolution": {
        "pdf": REV_DIR / "flight_times_histogram_no_mvp.pdf",
        "png": REV_DIR / "flight_times_histogram_no_mvp.png",
        "color": "#2f6f9f",
    },
    "MVP 60 s": {
        "pdf": REV_DIR / "flight_times_histogram.pdf",
        "png": REV_DIR / "flight_times_histogram.png",
        "color": "#3c8f5a",
    },
    "MVP 120 s": {
        "pdf": REV_DIR / "flight_times_histogram_mvp120.pdf",
        "png": REV_DIR / "flight_times_histogram_mvp120.png",
        "color": "#b45f32",
    },
}


def load_flight_times(scenario: str) -> pd.Series:
    # Flight time per aircraft (s) from the BlueSky UAM metrics output, without aircraft IDs
    df = pd.read_csv(FLIGHT_TIMES_PATH)
    values = df.loc[df["scenario"] == scenario, "flight_time_s"].astype("float64").reset_index(drop=True)
    values = values[values > 0.0] / 60.0  # seconds to minutes
    values.name = "flight_time_min"
    return values


def describe(label: str, times: pd.Series) -> dict[str, float | int | str]:
    return {
        "scenario": label,
        "n_aircraft": int(times.shape[0]),
        "mean_min": round(float(times.mean()), 2),
        "median_min": round(float(times.median()), 2),
        "std_min": round(float(times.std(ddof=1)), 2),
        "min_min": round(float(times.min()), 2),
        "max_min": round(float(times.max()), 2),
    }


def plot_single(label: str, times: pd.Series, out_pdf: Path, out_png: Path, color: str) -> None:
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    bins = range(0, int(times.max()) + 6, 2)
    ax.hist(times, bins=bins, color=color, edgecolor="white", linewidth=0.8, alpha=0.88)
    ax.axvline(times.mean(), color="#222222", linestyle="--", linewidth=1.4, label=f"Mean = {times.mean():.1f} min")
    ax.axvline(times.median(), color="#555555", linestyle=":", linewidth=1.4, label=f"Median = {times.median():.1f} min")
    ax.set_xlabel("Flight time (min)")
    ax.set_ylabel("Number of aircraft")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(out_pdf, bbox_inches="tight")
    fig.savefig(out_png, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_comparison(all_times: dict[str, pd.Series]) -> None:
    fig, ax = plt.subplots(figsize=(7.8, 4.8))
    max_time = max(float(times.max()) for times in all_times.values())
    bins = range(0, int(max_time) + 6, 2)

    for label, times in all_times.items():
        ax.hist(
            times,
            bins=bins,
            histtype="step",
            linewidth=1.8,
            label=f"{label} (mean {times.mean():.1f} min)",
        )

    ax.set_xlabel("Flight time (min)")
    ax.set_ylabel("Number of aircraft")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(REV_DIR / "flight_times_histogram_comparison.pdf", bbox_inches="tight")
    fig.savefig(REV_DIR / "flight_times_histogram_comparison.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    all_times: dict[str, pd.Series] = {}
    summaries = []
    REV_DIR.mkdir(exist_ok=True)

    for label, cfg in SCENARIOS.items():
        times = load_flight_times(label)
        all_times[label] = times
        summaries.append(describe(label, times))
        plot_single(label, times, cfg["pdf"], cfg["png"], cfg["color"])
        print(f"Saved {cfg['pdf'].name} and {cfg['png'].name}")

    plot_comparison(all_times)
    summary = pd.DataFrame(summaries)
    summary.to_csv(REV_DIR / "flight_times_summary.csv", index=False)
    print("Saved flight_times_histogram_comparison.pdf/.png")
    print("Saved flight_times_summary.csv")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
