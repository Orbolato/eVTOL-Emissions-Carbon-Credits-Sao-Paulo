"""
Run all scripts in order. Results are written to output/.

Usage (from any directory):
    python run_all.py
"""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "01_helicopter_fleet_mix.py",
    "02_flight_time_histograms.py",
    "03_emissions_accounting.py",
    "04_monte_carlo.py",
    "05_annotate_context_map.py",
    "06_annotate_bluesky_snapshots.py",
]

env = dict(os.environ, PYTHONIOENCODING="utf-8", MPLBACKEND="Agg")
for script in SCRIPTS:
    print(f"\n{'#' * 78}\n# Running: scripts/{script}\n{'#' * 78}\n", flush=True)
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], cwd=ROOT, env=env, check=True)

print("\nAll steps completed. Results are in output/.")
