"""
Compute a BIMTRA-derived helicopter fleet-mix emissions baseline.

The script reads the aircraft type counts of the BlueSky scenario and computes a
weighted fuel-intensity baseline for the most frequent helicopter families:
A109, B429, AS50, EC45, EC55, and EC35.

Fuel intensity is estimated as usable/standard fuel capacity divided by
published range. This keeps the fleet-mix baseline traceable to public
manufacturer or technical data instead of relying on unsourced hourly burns.
The values are screening assumptions and should be updated if operator-specific
fuel-flow data become available.
"""

from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
COUNTS_PATH = ROOT / "data" / "simulation" / "aircraft_type_counts.csv"
OUTPUT_DIR = ROOT / "output"

D_3D_KM = 3934.90
N_OPS = 146
RHO_FUEL_KG_L = 0.804
EF_TTW_KGCO2_KG_FUEL = 3.16

TOP_TYPES = ("A109", "B429", "AS50", "EC45", "EC55", "EC35")

AIRCRAFT_PARAMETERS = {
    "A109": {
        "family": "Leonardo AW109 GrandNew/Trekker family",
        "fuel_capacity_l": 634.0 / RHO_FUEL_KG_L,
        "range_km": 833.0,
        "note": "Usable fuel mass and range reported for AW109 Trekker/GrandNew-family technical data; range with auxiliary fuel, no reserve.",
        "source": "Leonardo AW109 Trekker brochure",
    },
    "B429": {
        "family": "Bell 429",
        "fuel_capacity_l": 216.9 * 3.785411784,
        "range_km": 761.0,
        "note": "Standard usable fuel and 4,000 ft ISA range at 3,175 kg takeoff weight, no reserve.",
        "source": "Bell 429 Product Specifications, February 2026",
    },
    "AS50": {
        "family": "Airbus H125 / AS350 family",
        "fuel_capacity_l": 425.0 / RHO_FUEL_KG_L,
        "range_km": 630.0,
        "note": "Standard fuel tank mass and max range at fast cruise.",
        "source": "Airbus H125 technical information",
    },
    "EC45": {
        "family": "Airbus H145 / EC145 family",
        "fuel_capacity_l": 723.0 / RHO_FUEL_KG_L,
        "range_km": 650.0,
        "note": "Standard fuel tank mass and sea-level range with standard fuel tanks.",
        "source": "Airbus H145 technical information",
    },
    "EC55": {
        "family": "Airbus H155 / EC155 B1 family",
        "fuel_capacity_l": 1257.0,
        "range_km": 784.0,
        "note": "Standard fuel tanks and maximum range with standard tanks at recommended cruise speed.",
        "source": "Eurocopter EC155 B1 technical data / Airbus Canada brochure",
    },
    "EC35": {
        "family": "Airbus H135 / EC135 family",
        "fuel_capacity_l": 560.0 / RHO_FUEL_KG_L,
        "range_km": 633.0,
        "note": "Standard fuel tank mass and max range with standard fuel tanks. EC35 is the ICAO type designator for the EC135/H135 family.",
        "source": "Airbus H135 technical information / H135 brochure summary",
    },
}


def read_aircraft_types(path: Path) -> Counter[str]:
    # Operations per aircraft type code in the BlueSky scenario (CRE commands)
    df = pd.read_csv(path)
    return Counter(dict(zip(df["type_code"], df["operations"].astype(int))))


def build_parameter_table(counts: Counter[str]) -> pd.DataFrame:
    rows = []
    for type_code in TOP_TYPES:
        params = AIRCRAFT_PARAMETERS[type_code]
        fuel_intensity = params["fuel_capacity_l"] / params["range_km"]
        rows.append(
            {
                "type_code": type_code,
                "family": params["family"],
                "operations": counts.get(type_code, 0),
                "fuel_capacity_l": round(params["fuel_capacity_l"], 2),
                "range_km": params["range_km"],
                "fuel_intensity_l_km": round(fuel_intensity, 4),
                "note": params["note"],
                "source": params["source"],
            }
        )
    return pd.DataFrame(rows)


def compute_results(params_df: pd.DataFrame, total_counts: int) -> dict[str, float | int]:
    represented_ops = int(params_df["operations"].sum())
    weighted_fi = (
        params_df["operations"] * params_df["fuel_intensity_l_km"]
    ).sum() / represented_ops

    total_fuel_l = weighted_fi * D_3D_KM
    total_fuel_t = total_fuel_l * RHO_FUEL_KG_L / 1000.0
    total_co2e_t = total_fuel_l * RHO_FUEL_KG_L * EF_TTW_KGCO2_KG_FUEL / 1000.0

    e_bat_kwh = 0.4659 * D_3D_KM + 7.55 * N_OPS
    e_grid_kwh = e_bat_kwh / 0.90
    evtol_co2e_t = e_grid_kwh * 0.2749 / 1000.0
    avoided_t = total_co2e_t - evtol_co2e_t
    reduction_pct = avoided_t / total_co2e_t * 100.0

    return {
        "total_scenario_operations": total_counts,
        "represented_operations": represented_ops,
        "represented_share": represented_ops / total_counts,
        "weighted_fuel_intensity_l_km": weighted_fi,
        "total_fuel_l": total_fuel_l,
        "total_fuel_t": total_fuel_t,
        "helicopter_co2e_t": total_co2e_t,
        "helicopter_co2e_kg_per_op": total_co2e_t * 1000.0 / N_OPS,
        "evtol_co2e_t": evtol_co2e_t,
        "avoided_co2e_t": avoided_t,
        "relative_reduction_pct": reduction_pct,
    }


def write_counts(counts: Counter[str], output_path: Path) -> None:
    with output_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        writer.writerow(["type_code", "operations"])
        for type_code, operations in counts.most_common():
            writer.writerow([type_code, operations])


def main() -> None:
    counts = read_aircraft_types(COUNTS_PATH)
    params_df = build_parameter_table(counts)
    results = compute_results(params_df, sum(counts.values()))

    OUTPUT_DIR.mkdir(exist_ok=True)
    write_counts(counts, OUTPUT_DIR / "helicopter_mix_counts.csv")
    params_df.to_csv(OUTPUT_DIR / "helicopter_mix_parameters.csv", index=False)
    pd.DataFrame([results]).to_csv(OUTPUT_DIR / "helicopter_mix_baseline_results.csv", index=False)

    print("Aircraft type counts")
    print(pd.Series(counts).sort_values(ascending=False).to_string())
    print()
    print(params_df[["type_code", "operations", "fuel_intensity_l_km"]].to_string(index=False))
    print()
    print("Fleet-mix baseline results")
    for key, value in results.items():
        if isinstance(value, float):
            print(f"{key}: {value:.4f}")
        else:
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
