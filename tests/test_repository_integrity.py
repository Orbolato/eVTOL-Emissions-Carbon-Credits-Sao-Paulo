from __future__ import annotations

import csv
import hashlib
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


class RepositoryIntegrityTests(unittest.TestCase):
    def test_manifested_artifacts_are_exact(self) -> None:
        manifest = json.loads((ROOT / "ARTIFACTS.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["hash_algorithm"], "git-blob-sha1")
        self.assertGreaterEqual(len(manifest["artifacts"]), 9)

        for item in manifest["artifacts"]:
            path = ROOT / item["path"]
            self.assertTrue(path.is_file(), item["path"])
            data = path.read_bytes()
            self.assertEqual(len(data), item["bytes"], item["path"])
            self.assertEqual(git_blob_sha1(data), item["git_blob_sha1"], item["path"])

    def test_scenario_summary_contract(self) -> None:
        path = ROOT / "data" / "simulation" / "bluesky_scenario_summary.csv"
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        self.assertEqual(
            [row["scenario"] for row in rows],
            ["No conflict resolution", "MVP 60 s", "MVP 120 s"],
        )
        self.assertTrue(all(int(row["n_operations"]) == 146 for row in rows))
        self.assertTrue(all(float(row["simulation_time_s"]) == 90050.0 for row in rows))

        expected_thresholds = {
            "lowc_horizontal_m": 500.0,
            "nmac_horizontal_m": 150.0,
            "nmac_vertical_m": 30.0,
            "mac_horizontal_m": 10.0,
            "mac_vertical_m": 30.0,
        }
        for row in rows:
            for column, expected in expected_thresholds.items():
                self.assertEqual(float(row[column]), expected)

        central = rows[1]
        self.assertAlmostEqual(float(central["total_3d_distance_nm"]), 2130.3684610408354, places=10)
        self.assertEqual(int(central["lowc_events"]), 5)
        self.assertEqual(int(central["nmac_events"]), 0)
        self.assertEqual(int(central["mac_events"]), 0)

    def test_aircraft_type_counts_contract(self) -> None:
        path = ROOT / "data" / "simulation" / "aircraft_type_counts.csv"
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        counts = {row["type_code"]: int(row["operations"]) for row in rows}
        self.assertEqual(sum(counts.values()), 146)
        expected_top_six = {"A109": 39, "B429": 21, "AS50": 20, "EC45": 17, "EC55": 17, "EC35": 13}
        for code, expected in expected_top_six.items():
            self.assertEqual(counts.get(code), expected)
        self.assertEqual(sum(counts[code] for code in expected_top_six), 127)

    def test_flight_time_data_are_deidentified(self) -> None:
        path = ROOT / "data" / "simulation" / "aircraft_flight_times.csv"
        with path.open(newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            self.assertEqual(reader.fieldnames, ["scenario", "flight_time_s"])
            rows = list(reader)

        self.assertGreater(len(rows), 0)
        scenarios = {row["scenario"] for row in rows}
        self.assertEqual(scenarios, {"No conflict resolution", "MVP 60 s", "MVP 120 s"})
        self.assertTrue(all(float(row["flight_time_s"]) >= 0 for row in rows))

    def test_grid_factor_contract(self) -> None:
        path = ROOT / "data" / "grid_emission_factor" / "sin_operating_margin_daily_2023_2024.csv"
        with path.open(newline="", encoding="utf-8") as fh:
            rows = list(csv.DictReader(fh))

        self.assertEqual(len(rows), 731)
        self.assertEqual(rows[0]["date"], "2023-01-01")
        self.assertEqual(rows[-1]["date"], "2024-12-31")
        values = [float(row["ef_grid_kgco2_per_kwh"]) for row in rows]
        self.assertTrue(all(value > 0 for value in values))

    def test_restricted_flight_level_material_is_absent(self) -> None:
        forbidden_exact = {
            ROOT / "data" / "raw" / "bimtra",
            ROOT / "data" / "BIMTRA.csv",
            ROOT / "BIMTRA.csv",
        }
        for path in forbidden_exact:
            self.assertFalse(path.exists(), str(path))

        suspicious_suffixes = {".scn", ".log"}
        suspicious_names = {"bimtra.csv", "bimtra.xlsx", "bimtra.rda", "bimtra.rdata"}
        for path in ROOT.rglob("*"):
            if ".git" in path.parts or not path.is_file():
                continue
            self.assertNotIn(path.name.lower(), suspicious_names, str(path))
            if path.suffix.lower() in suspicious_suffixes:
                self.fail(f"Flight-level simulator artifact should not be public: {path.relative_to(ROOT)}")

    def test_citation_metadata_has_article_and_repository(self) -> None:
        text = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn("10.1016/j.cstp.2026.101884", text)
        self.assertIn("https://github.com/Orbolato/eVTOL-Emissions-Carbon-Credits-Sao-Paulo", text)
        self.assertIn("https://orcid.org/0000-0002-8402-5832", text)


if __name__ == "__main__":
    unittest.main()
