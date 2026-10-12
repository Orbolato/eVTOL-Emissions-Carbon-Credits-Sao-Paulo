# Data inventory

This directory contains the **public analysis boundary** for the article. It intentionally excludes restricted flight-level BIMTRA records and the BlueSky scenario/log files constructed from them. See [`../PROVENANCE.md`](../PROVENANCE.md) for the full provenance statement and [`../ARTIFACTS.json`](../ARTIFACTS.json) for exact committed artifact identities.

## `simulation/`

### `bluesky_scenario_summary.csv`

One aggregate row per analyzed BlueSky scenario. The three scenarios are:

- `No conflict resolution`
- `MVP 60 s`
- `MVP 120 s`

Columns include the number of operations, simulation time, total flight hours, total 3D distance, safety-event counts, conflict-resolution alert counts, and the LOWC/NMAC/MAC thresholds. All three scenarios contain 146 operations.

### `aircraft_flight_times.csv`

Scenario label plus flight-time value in seconds. Aircraft identifiers are removed. The analysis discards non-positive values when producing flight-time summaries and histograms.

### `aircraft_type_counts.csv`

Aggregate operation counts by aircraft type code. Counts sum to 146 operations. The six most frequent families used in the fleet-mix baseline are A109, B429, AS50, EC45, EC55, and EC35.

These files are **derived aggregate products**. They do not enable reconstruction of individual BIMTRA records or the original flight-level BlueSky scenarios.

## `grid_emission_factor/`

### `sin_operating_margin_daily_2023_2024.csv`

Archived daily operating-margin CO2 emission factors for the Brazilian National Interconnected System (SIN), 2023–2024, in kgCO2/kWh. The study identifies MCTI/SIRENE as the source. The Monte Carlo analysis samples this empirical daily distribution with replacement.

No separate data license is asserted by this repository; the source provider’s applicable terms remain controlling.

## `figure_sources/`

Base images used by the annotation scripts:

- `ctr.png`: exported RMSP/REH/CTR context map used as the base for Fig. 1;
- `aerodrome_red_marker.png`: marker image used in the Fig. 1 legend;
- `bluesky_bimtra_mvp_off.jpg`: BlueSky screenshot for the no-conflict-resolution scenario;
- `bluesky_bimtra_mvp_60.jpg`: BlueSky screenshot for the MVP 60 s scenario;
- `bluesky_bimtra_mvp_120.jpg`: BlueSky screenshot for the MVP 120 s scenario.

The scripts reproduce the **annotation layer** from these archived base images. They do not regenerate the underlying map or BlueSky simulator screenshots from raw operational inputs.

## Excluded data

Do not add the following to the public repository:

- raw BIMTRA flight-level extracts;
- aircraft-registration-level tables;
- flight-level route/departure-time records derived from BIMTRA;
- BlueSky scenario files containing those records; or
- flight-level simulator logs containing identifying operational fields.

The aggregate files already committed under `simulation/` are the intended public interface to the downstream analysis.
