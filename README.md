# Avoided emissions and potential carbon credits of helicopter-to-eVTOL substitution in São Paulo

[![reproducibility](https://github.com/Orbolato/eVTOL-Emissions-Carbon-Credits-Sao-Paulo/actions/workflows/reproducibility.yml/badge.svg)](https://github.com/Orbolato/eVTOL-Emissions-Carbon-Credits-Sao-Paulo/actions/workflows/reproducibility.yml)

Code, public aggregate inputs, and reproducibility materials for:

> Rodrigues, J.F., Carvalho, L.O., Gomes, I.G., Pagani, R.N., Murça, M.C.R., Caldeira, S.S., Guterres, M.X., Pamplona, D.A. (2026). **From avoided emissions to potential credits: A simulation-based case study of helicopter-to-eVTOL substitution in São Paulo.** *Case Studies on Transport Policy*, 25, 101884. https://doi.org/10.1016/j.cstp.2026.101884

Publication page: https://orbolato.github.io/publications/evtol-emissions-carbon-credits/

## Study overview

The study converts simulated helicopter activity in the São Paulo Metropolitan Region (RMSP) into energy use, CO2e emissions, avoided emissions, and **potential** carbon credits, comparing a helicopter fleet-mix baseline with an eVTOL replacement case.

The public analysis package contains three stages:

1. **Aggregated simulation results.** A 146-operation BIMTRA-derived day was simulated over the Helicopter Special Routes (REH) in BlueSky under three settings: no conflict resolution, MVP with 60 s lookahead, and MVP with 120 s lookahead. The repository contains aggregate scenario outputs, not the restricted flight-level BIMTRA records or flight-level BlueSky scenario/log files.
2. **Energy and emissions accounting.** Aggregated 3D distance is converted to helicopter fuel use or eVTOL electricity demand, then to CO2e. The central MVP 60 s case produces approximately 10.27 tCO2e of avoided emissions for full replacement under the study assumptions.
3. **Uncertainty analysis.** A 10,000-iteration Monte Carlo analysis, using seed 42, varies fuel density, helicopter fuel intensity, charging efficiency, eVTOL energy intensity, fixed per-flight eVTOL energy, and the empirical 2023–2024 SIN operating-margin emission factor.

The carbon-credit calculation is an accounting translation of avoided emissions using 1 potential credit = 1 tCO2e. It is **not** a claim of certified, issued, tradable, or registry-eligible credits.

## Reproducibility scope

This repository is intentionally explicit about what can and cannot be reproduced publicly.

| Level | Publicly supported? | Meaning |
|---|---:|---|
| Exact committed-artifact verification | Yes | CI verifies the committed research-data artifacts byte-for-byte using `ARTIFACTS.json`. |
| Downstream emissions/accounting rerun | Yes | `python run_all.py` regenerates the fleet-mix analysis, flight-time summaries, deterministic accounting, Monte Carlo outputs, and annotated figures from the committed aggregate inputs. |
| Raw BIMTRA -> BlueSky reconstruction | No | Flight-level BIMTRA records and flight-level BlueSky scenarios/logs are restricted and are not redistributed. |

See [`PROVENANCE.md`](PROVENANCE.md) for the complete provenance and reproducibility boundary and [`data/README.md`](data/README.md) for the data inventory.

## Repository structure

```text
.
├── README.md
├── CITATION.cff
├── PROVENANCE.md
├── ARTIFACTS.json
├── requirements.txt
├── run_all.py
├── scripts/
│   ├── 01_helicopter_fleet_mix.py
│   ├── 02_flight_time_histograms.py
│   ├── 03_emissions_accounting.py
│   ├── 04_monte_carlo.py
│   ├── 05_annotate_context_map.py
│   └── 06_annotate_bluesky_snapshots.py
├── data/
│   ├── README.md
│   ├── simulation/                 # public aggregate BlueSky-derived inputs
│   ├── grid_emission_factor/       # archived daily SIN factors, 2023-2024
│   └── figure_sources/             # archived base images for figure annotation
├── tests/
└── output/                         # generated; ignored except .gitkeep
```

## Environment

The tested public-analysis environment is Python 3.12 with exact package versions pinned in `requirements.txt`:

```bash
python -m pip install -r requirements.txt
```

The pinned environment is also installed by GitHub Actions before the public downstream analysis is rerun.

## Run the public analysis

From the repository root:

```bash
python run_all.py
```

`run_all.py` performs an input preflight check, executes the six numbered scripts in order, and writes generated results to `output/`.

The scripts can also be run individually in numerical order. Script `03` depends on the generated outputs of scripts `01` and `02`.

## Scripts

| Script | Role |
|---|---|
| `01_helicopter_fleet_mix.py` | Computes fuel intensity for the six most frequent helicopter families and the operation-weighted fleet-mix intensity used by the study. |
| `02_flight_time_histograms.py` | Generates flight-time histograms and summary statistics for the three public aggregate BlueSky scenarios. |
| `03_emissions_accounting.py` | Applies the deterministic activity -> energy -> CO2e -> avoided-emissions accounting for Tables 3–9. |
| `04_monte_carlo.py` | Runs 10,000 seeded Monte Carlo iterations and the Spearman-based correlation sensitivity analysis used for Figs. 8–11 and associated diagnostics. |
| `05_annotate_context_map.py` | Recreates the annotation layer applied to the archived REH/CTR context-map image. |
| `06_annotate_bluesky_snapshots.py` | Recreates the annotation layers applied to the three archived BlueSky screenshots. |

### Sensitivity-analysis terminology

The primary sensitivity diagnostic is Spearman rank correlation. The historical `04_monte_carlo.py` also retains a second normalized column/plot whose legacy comments refer to “Sobol”/“partial correlation,” but its implementation repeats the same absolute Spearman transformation. It should **not** be interpreted as a Sobol index or as an independent partial-correlation estimator. The legacy output is retained for traceability; see `PROVENANCE.md`.

## Article outputs

| Article item | Script | Generated output |
|---|---|---|
| Table 1 | `01` | `output/helicopter_mix_parameters.csv` |
| Tables 3–5 | `03` | `output/operational_metrics.csv` |
| Table 6 | `03` | `output/energy_emissions_central.csv` |
| Table 7 | `03` | `output/evtol_model_sensitivity.csv` |
| Table 8 | `03` | `output/operational_distance_sensitivity.csv` |
| Table 9 | `03` | `output/replacement_share.csv` |
| Fig. 1 | `05` | `output/ctr_annotated.png` / `.pdf` |
| Figs. 2, 4, 6 | `06` | annotated BlueSky screenshot files |
| Figs. 3, 5, 7 | `02` | scenario flight-time histogram PDFs |
| Fig. 8 | `04` | `output/03_emission_reduction_distribution.pdf` |
| Fig. 9 | `04` | `output/01_sensitivity_spearman.pdf` |
| Fig. 10 | `04` | `output/04_efgrid_historical_distribution.pdf` |
| Fig. 11 | `04` | `output/05_parameter_output_correlation.pdf` |

Table 2 contains model/input parameters. The corresponding analysis values are defined near the top of scripts `01`, `03`, and `04`.

## Public data

### Aggregate simulation inputs

`data/simulation/` contains only aggregate/de-identified products used by the downstream analysis:

- `bluesky_scenario_summary.csv`: scenario-level distance, time, safety events, conflict-resolution alerts, and event thresholds;
- `aircraft_flight_times.csv`: scenario label and flight time only, with aircraft identifiers removed;
- `aircraft_type_counts.csv`: aggregate operation counts by aircraft type code.

The original BIMTRA flight-level records and the flight-level BlueSky scenarios/logs are excluded.

Simulation settings represented by the aggregate inputs are conflict resolution off, MVP with 60 s lookahead, and MVP with 120 s lookahead. Event thresholds are LOWC < 500 m horizontally, NMAC < 150 m horizontally and < 30 m vertically, and MAC < 10 m horizontally and < 30 m vertically.

### Grid emission factor

`data/grid_emission_factor/sin_operating_margin_daily_2023_2024.csv` contains 731 daily operating-margin CO2 emission factors for the Brazilian National Interconnected System (SIN), spanning 2023-01-01 through 2024-12-31. The study identifies MCTI/SIRENE as the source. The Monte Carlo analysis samples the empirical daily values with replacement.

No separate license is asserted for this source dataset; source-provider terms remain applicable.

### Figure sources

`data/figure_sources/` contains the archived base images used to create the annotated manuscript figures. The annotation scripts reproduce the added labels and legends; they do not reconstruct the original map or BlueSky states from raw data.

## Automated verification

GitHub Actions runs the following checks on pushes and pull requests:

1. installs the pinned Python 3.12 analysis environment;
2. compiles all Python sources;
3. verifies every artifact listed in `ARTIFACTS.json` byte-for-byte;
4. checks the scenario, fleet-mix, grid-factor, and de-identification data contracts;
5. verifies that common raw BIMTRA and flight-level BlueSky artifacts are absent;
6. reruns `python run_all.py`; and
7. checks key generated numerical results and expected figure/table outputs.

The numerical checks include the 146-operation central scenario, the 127-operation six-family fleet-mix subset, the central 3D distance, and the central helicopter/eVTOL CO2e accounting.

## Citation

If you use this repository, please cite the published article. `CITATION.cff` contains machine-readable repository metadata and the preferred article citation.

```bibtex
@article{Rodrigues2026eVTOL,
  title   = {From avoided emissions to potential credits: A simulation-based case study of helicopter-to-{eVTOL} substitution in S{\~a}o Paulo},
  author  = {Rodrigues, Jaqueline Fonseca and Carvalho, Lucas Orbolato and Gomes, Igor Galhano and Pagani, Regina Negri and Mur{\c{c}}a, Mayara Cond{\'e} Rocha and Caldeira, Samuel da Silva and Guterres, Marcelo Xavier and Pamplona, Daniel Alberto},
  journal = {Case Studies on Transport Policy},
  volume  = {25},
  pages   = {101884},
  year    = {2026},
  doi     = {10.1016/j.cstp.2026.101884}
}
```

## License and third-party terms

No software or data license is granted by this repository unless a separate license file is added in the future. Third-party source terms remain applicable to source data, software, map content, and other external materials.
