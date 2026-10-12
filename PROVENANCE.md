# Provenance and reproducibility boundaries

This repository accompanies the 2026 *Case Studies on Transport Policy* article **“From avoided emissions to potential credits: A simulation-based case study of helicopter-to-eVTOL substitution in São Paulo.”** Its purpose is to make the downstream analysis auditable and rerunnable without redistributing restricted flight-level operational records.

## What is public here

The committed public package contains:

- aggregated BlueSky scenario summaries for three conflict-resolution settings;
- de-identified, sorted flight-time values by scenario;
- aggregate aircraft-type operation counts used to construct the helicopter fleet mix;
- the archived daily Brazilian SIN operating-margin emission-factor series used by the Monte Carlo analysis;
- author-produced figure-source images used for annotation; and
- the Python analysis scripts that convert those inputs into the article’s accounting tables, uncertainty analysis, and figures.

`ARTIFACTS.json` records the exact Git-blob identity and byte size of every committed research-data artifact. CI verifies those identities on each change.

## Restricted upstream operational records

The original BIMTRA flight-level records are **not** included. They contain individual operational information such as aircraft registrations, types, departure times, and routes and are not redistributed by this repository. The original BlueSky scenario files/logs built from those records are also excluded.

Accordingly, this repository does **not** claim public end-to-end reconstruction of the 146-operation scenario from the raw BIMTRA source. Instead, the three committed aggregate simulation datasets are the public boundary between the restricted upstream simulation stage and the reproducible downstream emissions/accounting stage.

The repository’s `.gitignore` intentionally blocks common locations and names for raw BIMTRA material and BlueSky flight-level logs/scenarios.

## BlueSky-derived aggregate inputs

`data/simulation/bluesky_scenario_summary.csv` contains one row for each of the three analyzed scenarios:

- no conflict resolution;
- MVP with 60 s lookahead; and
- MVP with 120 s lookahead.

Each scenario represents 146 operations. The aggregate table records total simulated 3D distance, flight hours, safety-event counts, conflict-resolution alerts, and the thresholds used to classify LOWC, NMAC, and MAC events.

`data/simulation/aircraft_flight_times.csv` contains only scenario labels and flight-time values. Aircraft identifiers are absent. `data/simulation/aircraft_type_counts.csv` contains operation counts by aircraft type code only.

These files support rerunning the public downstream analysis but do not substitute for the restricted flight-level source records.

## Grid-emission-factor input

`data/grid_emission_factor/sin_operating_margin_daily_2023_2024.csv` is the archived daily operating-margin CO2 emission-factor series for the Brazilian National Interconnected System (SIN) used in the study. The source identified by the study is the Brazilian Ministry of Science, Technology and Innovation (MCTI/SIRENE).

The repository preserves the exact analysis input used by the code. No separate license is asserted for this source dataset; users remain responsible for the source provider’s applicable terms.

## Figure-source images

`data/figure_sources/` contains the map export and BlueSky screenshots used as the base images for the manuscript figures. The annotation scripts add labels and legends; they do not reconstruct the original map or simulator state from raw geospatial/flight-level inputs.

These source images are preserved as research artifacts. Their inclusion in this repository does not imply a separate license grant for third-party software, map layers, or other underlying content.

## Reproducibility levels

The repository supports three distinct levels of reproducibility:

1. **Exact public-artifact verification.** CI verifies the committed data artifacts byte-for-byte using Git-blob identities and validates their schemas and key study invariants.
2. **Downstream analysis rerun.** `python run_all.py` reruns the fleet-mix calculation, flight-time summaries, deterministic emissions accounting, Monte Carlo analysis, and figure annotation from the committed public inputs.
3. **Upstream simulation reconstruction.** Not publicly reproducible from this repository because the raw BIMTRA records and derived flight-level BlueSky scenarios/logs are intentionally excluded.

The repository therefore should not be described as reproducing the original BIMTRA-to-BlueSky pipeline from first principles.

## Interpretation of potential carbon credits

The article converts avoided emissions into **potential** credits using the accounting convention 1 credit = 1 tCO2e. The repository does not claim that the calculated quantities are certified, issued, tradable, or eligible under any particular carbon-credit standard or methodology. Additionality, baseline approval, monitoring, leakage, permanence, verification, registry rules, and other program-specific requirements are outside this computational package.

## Monte Carlo sensitivity terminology

The published analysis uses Spearman rank correlations as a correlation-based sensitivity diagnostic. The historical script also contains a second normalized column/plot that repeats the same absolute Spearman transformation; despite legacy variable names/comments, it is **not** a Sobol index and it is **not** a statistically distinct partial-correlation analysis. The hardening pass retains the legacy output for traceability while documenting this limitation explicitly. It is not used as an independent sensitivity estimator.

## Licensing

No software or data license is granted by this repository unless a separate license file is added in the future. Third-party source terms remain applicable.
