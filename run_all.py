"""Run the public downstream analysis in the documented order.

This runner starts from the committed aggregate/public inputs. It does not
reconstruct the restricted BIMTRA-to-BlueSky upstream simulation stage.

Usage (from any directory):
    python run_all.py
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

SCRIPTS = [
    "01_helicopter_fleet_mix.py",
    "02_flight_time_histograms.py",
    "03_emissions_accounting.py",
    "04_monte_carlo.py",
    "05_annotate_context_map.py",
    "06_annotate_bluesky_snapshots.py",
]

REQUIRED_INPUTS = [
    ROOT / "data" / "simulation" / "aircraft_flight_times.csv",
    ROOT / "data" / "simulation" / "aircraft_type_counts.csv",
    ROOT / "data" / "simulation" / "bluesky_scenario_summary.csv",
    ROOT / "data" / "grid_emission_factor" / "sin_operating_margin_daily_2023_2024.csv",
    ROOT / "data" / "figure_sources" / "ctr.png",
    ROOT / "data" / "figure_sources" / "aerodrome_red_marker.png",
    ROOT / "data" / "figure_sources" / "bluesky_bimtra_mvp_off.jpg",
    ROOT / "data" / "figure_sources" / "bluesky_bimtra_mvp_60.jpg",
    ROOT / "data" / "figure_sources" / "bluesky_bimtra_mvp_120.jpg",
]


def preflight() -> None:
    if sys.version_info < (3, 10):
        raise RuntimeError("Python 3.10 or newer is required; Python 3.12 is the tested environment.")

    missing = [path.relative_to(ROOT) for path in REQUIRED_INPUTS if not path.is_file()]
    if missing:
        formatted = "\n".join(f"  - {path}" for path in missing)
        raise FileNotFoundError(f"Missing required public analysis inputs:\n{formatted}")

    missing_scripts = [ROOT / "scripts" / name for name in SCRIPTS if not (ROOT / "scripts" / name).is_file()]
    if missing_scripts:
        formatted = "\n".join(f"  - {path.relative_to(ROOT)}" for path in missing_scripts)
        raise FileNotFoundError(f"Missing analysis scripts:\n{formatted}")

    OUTPUT_DIR.mkdir(exist_ok=True)


def main() -> None:
    preflight()
    env = dict(os.environ, PYTHONIOENCODING="utf-8", MPLBACKEND="Agg")

    print(f"Repository root: {ROOT}")
    print(f"Python: {sys.version.split()[0]}")
    print("Public input preflight: OK")

    for script in SCRIPTS:
        relative = Path("scripts") / script
        print(f"\n{'#' * 78}\n# Running: {relative.as_posix()}\n{'#' * 78}\n", flush=True)
        subprocess.run(
            [sys.executable, str(ROOT / relative)],
            cwd=ROOT,
            env=env,
            check=True,
        )

    print("\nAll public downstream analysis steps completed. Results are in output/.")


if __name__ == "__main__":
    main()
