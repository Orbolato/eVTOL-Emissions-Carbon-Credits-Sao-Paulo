"""
Deterministic activity -> energy -> CO2e -> potential credits accounting.

Applies Eqs. (4)-(12) of the article to the aggregated 3D distance (D_3D) of the
three BlueSky scenarios and writes the operational metrics and accounting
tables of the Results section:
  - output/operational_metrics.csv          (Tables 3-5)
  - output/energy_emissions_central.csv     (Table 6, MVP 60 s)
  - output/evtol_model_sensitivity.csv      (Table 7)
  - output/operational_distance_sensitivity.csv  (Table 8)
  - output/replacement_share.csv            (Table 9)

Run 01_helicopter_fleet_mix.py and 02_flight_time_histograms.py first.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = ROOT / "data" / "simulation" / "bluesky_scenario_summary.csv"
OUTPUT_DIR = ROOT / "output"
FLEET_MIX_PATH = OUTPUT_DIR / "helicopter_mix_parameters.csv"
FLIGHT_TIMES_PATH = OUTPUT_DIR / "flight_times_summary.csv"

NM_TO_KM = 1.852
CENTRAL_SCENARIO = "MVP 60 s"
BASE_SCENARIO = "No conflict resolution"

# Helicopter baseline (Jet A-1/QAV-1, tank-to-wake)
RHO_FUEL_KG_L = 0.804
EF_TTW_KGCO2_KG_FUEL = 3.16

# eVTOL (grid electricity, SIN operating margin 2024)
ETA_CHARGE = 0.90
EF_GRID_KGCO2_KWH = 0.2749
EVTOL_CASES = {
    "Aurora PAV (central)": {"ei_e_kwh_km": 0.4659, "e0_kwh_op": 7.55},
    "Volocopter benchmark": {"ei_e_kwh_km": 0.1643, "e0_kwh_op": 3.61},
}
CENTRAL_EVTOL = "Aurora PAV (central)"

REPLACEMENT_SHARES = (0.25, 0.50, 0.75, 1.00)


def fleet_mix_fuel_intensity(path: Path) -> float:
    """Operation-weighted fuel intensity of the six most frequent types (Eq. 5)."""
    df = pd.read_csv(path)
    return float((df["operations"] * df["fuel_intensity_l_km"]).sum() / df["operations"].sum())


def helicopter(d3d_km: float, fi_mix: float) -> dict[str, float]:
    """Fuel use and CO2e of the helicopter fleet-mix baseline (Eqs. 6 and 9)."""
    fuel_l = fi_mix * d3d_km
    fuel_kg = fuel_l * RHO_FUEL_KG_L
    return {"fuel_l": fuel_l, "fuel_t": fuel_kg / 1000.0, "co2e_t": fuel_kg * EF_TTW_KGCO2_KG_FUEL / 1000.0}


def evtol(d3d_km: float, n_ops: int, ei_e_kwh_km: float, e0_kwh_op: float) -> dict[str, float]:
    """Battery and grid energy and CO2e of the eVTOL replacement (Eqs. 7, 8 and 10)."""
    e_bat_kwh = ei_e_kwh_km * d3d_km + e0_kwh_op * n_ops
    e_grid_kwh = e_bat_kwh / ETA_CHARGE
    return {"e_bat_mwh": e_bat_kwh / 1000.0, "e_grid_mwh": e_grid_kwh / 1000.0,
            "co2e_t": e_grid_kwh * EF_GRID_KGCO2_KWH / 1000.0}


def credits(heli_co2e_t: float, evtol_co2e_t: float) -> float:
    """Avoided emissions as potential credits, 1 credit = 1 tCO2e (Eq. 11)."""
    return max(0.0, heli_co2e_t - evtol_co2e_t)


def main() -> None:
    summary = pd.read_csv(SUMMARY_PATH).set_index("scenario")
    flight_times = pd.read_csv(FLIGHT_TIMES_PATH).set_index("scenario")
    fi_mix = fleet_mix_fuel_intensity(FLEET_MIX_PATH)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # ---------- Tables 3-5: operational metrics ----------
    base = summary.loc[BASE_SCENARIO]
    base_time = flight_times.loc[BASE_SCENARIO, "mean_min"]
    rows = []
    for scenario, s in summary.iterrows():
        d3d_km = s["total_3d_distance_nm"] * NM_TO_KM
        mean_time = flight_times.loc[scenario, "mean_min"]
        rows.append({
            "scenario": scenario,
            "n_operations": int(s["n_operations"]),
            "d3d_nm": s["total_3d_distance_nm"],
            "d3d_km": d3d_km,
            "avg_distance_per_op_km": d3d_km / s["n_operations"],
            "mean_flight_time_min": mean_time,
            "lowc": int(s["lowc_events"]),
            "nmac": int(s["nmac_events"]),
            "mac": int(s["mac_events"]),
            "distance_variation_pct": (s["total_3d_distance_nm"] / base["total_3d_distance_nm"] - 1.0) * 100.0,
            "time_variation_pct": (mean_time / base_time - 1.0) * 100.0,
        })
    ops = pd.DataFrame(rows)
    ops.to_csv(OUTPUT_DIR / "operational_metrics.csv", index=False)

    # ---------- Table 6: central scenario, fleet mix vs representative eVTOL ----------
    central = ops.set_index("scenario").loc[CENTRAL_SCENARIO]
    n_ops = int(central["n_operations"])
    heli = helicopter(central["d3d_km"], fi_mix)
    pav = evtol(central["d3d_km"], n_ops, **EVTOL_CASES[CENTRAL_EVTOL])
    table6 = pd.DataFrame([
        {"alternative": "Fleet-mix helicopter baseline", "fuel_l": heli["fuel_l"], "fuel_t": heli["fuel_t"],
         "e_bat_mwh": None, "e_grid_mwh": None, "co2e_t": heli["co2e_t"],
         "co2e_kg_per_op": heli["co2e_t"] * 1000.0 / n_ops, "boundary": "TTW (combustion)"},
        {"alternative": "Representative eVTOL", "fuel_l": None, "fuel_t": None,
         "e_bat_mwh": pav["e_bat_mwh"], "e_grid_mwh": pav["e_grid_mwh"], "co2e_t": pav["co2e_t"],
         "co2e_kg_per_op": pav["co2e_t"] * 1000.0 / n_ops, "boundary": "Grid electricity"},
    ])
    table6.to_csv(OUTPUT_DIR / "energy_emissions_central.csv", index=False)

    # ---------- Table 7: eVTOL model sensitivity (central scenario) ----------
    table7 = []
    for case, p in EVTOL_CASES.items():
        e = evtol(central["d3d_km"], n_ops, **p)
        table7.append({"evtol_case": case, "ei_e_kwh_km": p["ei_e_kwh_km"], "e0_kwh_op": p["e0_kwh_op"],
                       "e_grid_mwh": e["e_grid_mwh"], "evtol_co2e_t": e["co2e_t"],
                       "avoided_co2e_t": credits(heli["co2e_t"], e["co2e_t"])})
    table7 = pd.DataFrame(table7)
    table7.to_csv(OUTPUT_DIR / "evtol_model_sensitivity.csv", index=False)

    # ---------- Table 8: operational-distance sensitivity ----------
    table8 = []
    for _, r in ops.iterrows():
        h = helicopter(r["d3d_km"], fi_mix)
        e = evtol(r["d3d_km"], int(r["n_operations"]), **EVTOL_CASES[CENTRAL_EVTOL])
        avoided = credits(h["co2e_t"], e["co2e_t"])
        table8.append({"scenario": r["scenario"], "d3d_km": r["d3d_km"], "helicopter_co2e_t": h["co2e_t"],
                       "evtol_co2e_t": e["co2e_t"], "avoided_co2e_t": avoided,
                       "reduction_pct": avoided / h["co2e_t"] * 100.0})
    table8 = pd.DataFrame(table8)
    table8.to_csv(OUTPUT_DIR / "operational_distance_sensitivity.csv", index=False)

    # ---------- Table 9: replacement share (central scenario) ----------
    avoided_central = credits(heli["co2e_t"], pav["co2e_t"])
    table9 = pd.DataFrame({"replacement_share": REPLACEMENT_SHARES,
                           "avoided_co2e_t": [s * avoided_central for s in REPLACEMENT_SHARES]})
    table9.to_csv(OUTPUT_DIR / "replacement_share.csv", index=False)

    pd.set_option("display.width", 160)
    print(f"Fleet-mix fuel intensity FI_mix = {fi_mix:.4f} L/km\n")
    print("Tables 3-5: operational metrics")
    print(ops.round(2).to_string(index=False), "\n")
    print(f"Table 6: energy and emissions, {CENTRAL_SCENARIO}")
    print(table6.round(2).to_string(index=False), "\n")
    print("Table 7: eVTOL model sensitivity")
    print(table7.round(2).to_string(index=False), "\n")
    print("Table 8: operational-distance sensitivity")
    print(table8.round(2).to_string(index=False), "\n")
    print("Table 9: avoided emissions by replacement share")
    print(table9.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
