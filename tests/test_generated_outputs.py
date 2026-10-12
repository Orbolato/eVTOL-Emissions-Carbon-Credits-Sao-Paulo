from __future__ import annotations

import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output"


class GeneratedOutputTests(unittest.TestCase):
    def test_expected_outputs_exist(self) -> None:
        expected = [
            "helicopter_mix_parameters.csv",
            "helicopter_mix_baseline_results.csv",
            "flight_times_summary.csv",
            "operational_metrics.csv",
            "energy_emissions_central.csv",
            "evtol_model_sensitivity.csv",
            "operational_distance_sensitivity.csv",
            "replacement_share.csv",
            "sensitivity_analysis_results.csv",
            "parameter_correlations.csv",
            "flight_times_histogram_no_mvp.pdf",
            "flight_times_histogram.pdf",
            "flight_times_histogram_mvp120.pdf",
            "03_emission_reduction_distribution.pdf",
            "01_sensitivity_spearman.pdf",
            "04_efgrid_historical_distribution.pdf",
            "05_parameter_output_correlation.pdf",
            "ctr_annotated.png",
            "bluesky_bimtra_mvp_off_annotated.png",
            "bluesky_bimtra_mvp_60_annotated.png",
            "bluesky_bimtra_mvp_120_annotated.png",
        ]
        for name in expected:
            path = OUTPUT / name
            self.assertTrue(path.is_file(), name)
            self.assertGreater(path.stat().st_size, 0, name)

    def test_fleet_mix_baseline(self) -> None:
        with (OUTPUT / "helicopter_mix_baseline_results.csv").open(newline="", encoding="utf-8") as fh:
            row = next(csv.DictReader(fh))
        self.assertEqual(int(row["total_scenario_operations"]), 146)
        self.assertEqual(int(row["represented_operations"]), 127)
        self.assertAlmostEqual(float(row["weighted_fuel_intensity_l_km"]), 1.1136677165354332, places=10)

    def test_central_accounting_matches_archived_analysis_inputs(self) -> None:
        with (OUTPUT / "operational_metrics.csv").open(newline="", encoding="utf-8") as fh:
            rows = {row["scenario"]: row for row in csv.DictReader(fh)}
        central = rows["MVP 60 s"]
        self.assertEqual(int(float(central["n_operations"])), 146)
        self.assertAlmostEqual(float(central["d3d_km"]), 3945.4423898476275, places=9)

        with (OUTPUT / "energy_emissions_central.csv").open(newline="", encoding="utf-8") as fh:
            energy = {row["alternative"]: row for row in csv.DictReader(fh)}
        heli = energy["Fleet-mix helicopter baseline"]
        evtol = energy["Representative eVTOL"]
        self.assertAlmostEqual(float(heli["co2e_t"]), 11.16334811880312, places=9)
        self.assertAlmostEqual(float(evtol["co2e_t"]), 0.8981537715914549, places=9)

        with (OUTPUT / "replacement_share.csv").open(newline="", encoding="utf-8") as fh:
            replacement = list(csv.DictReader(fh))
        full = replacement[-1]
        self.assertAlmostEqual(float(full["replacement_share"]), 1.0, places=12)
        self.assertAlmostEqual(float(full["avoided_co2e_t"]), 10.265194347211665, places=9)


if __name__ == "__main__":
    unittest.main()
