# Avoided emissions and potential carbon credits of helicopter-to-eVTOL substitution in São Paulo

Code and data for the article:

> Rodrigues, J.F., Carvalho, L.O., Gomes, I.G., Pagani, R.N., Murça, M.C.R., Caldeira, S.S.,
> Guterres, M.X., Pamplona, D.A. (2026). **From avoided emissions to potential credits: A
> simulation-based case study of helicopter-to-eVTOL substitution in São Paulo.** *Case Studies on
> Transport Policy*, 25, 101884. https://doi.org/10.1016/j.cstp.2026.101884

The study converts simulated helicopter activity in the São Paulo Metropolitan Region (RMSP) into
energy use, CO₂e emissions and potential carbon credits, comparing a helicopter fleet-mix baseline
with an eVTOL replacement case:

1. **Scenario and simulation**: 146 helicopter operations with origin and destination in the RMSP,
   taken from the busiest day in the Brazilian Air Traffic Movement Information Database (BIMTRA),
   routed over the Helicopter Special Routes (REH) and simulated in
   [BlueSky](https://github.com/TUDelft-CNS-ATM/bluesky) without conflict resolution and with MVP
   conflict resolution (60 s and 120 s lookahead). The simulation gives the aggregated 3D flight
   distance *D*<sub>3D</sub>, flight times and safety events.
2. **Accounting**: *D*<sub>3D</sub> → fuel or electricity → CO₂e → avoided emissions and potential
   credits (1 credit = 1 tCO₂e), using a BIMTRA-weighted helicopter fleet mix and the Aurora PAV
   (with a Volocopter benchmark) as the eVTOL.
3. **Uncertainty**: Monte Carlo analysis (10,000 iterations) with Spearman-based sensitivity.

## Repository structure

```
.
├── run_all.py                          # runs all scripts in order
├── requirements.txt
├── scripts/
│   ├── 01_helicopter_fleet_mix.py
│   ├── 02_flight_time_histograms.py
│   ├── 03_emissions_accounting.py
│   ├── 04_monte_carlo.py
│   ├── 05_annotate_context_map.py
│   └── 06_annotate_bluesky_snapshots.py
├── data/
│   ├── simulation/                     # aggregated BlueSky outputs
│   ├── grid_emission_factor/           # daily SIN emission factors 2023-2024
│   └── figure_sources/                 # map and simulator screenshots used in Figs. 1, 2, 4, 6
└── output/                             # created by the scripts
```

## Requirements

Python (≥ 3.10) with the packages in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Tested with Python 3.12 on Windows 10.

## How to run

```bash
python run_all.py
```

All results are written to `output/` in a few seconds. The scripts can also be run one at a time in
numerical order; script `03` uses outputs of `01` and `02`.

## Scripts

| Script | What it does |
|---|---|
| `01_helicopter_fleet_mix.py` | Fuel intensity (capacity / range) of the six most frequent helicopter types and the operation-weighted fleet-mix intensity, 1.1137 L/km (Table 1). |
| `02_flight_time_histograms.py` | Flight-time histograms and summary statistics of the three BlueSky scenarios. |
| `03_emissions_accounting.py` | Applies Eqs. (4)–(12) to the 3D distance of each scenario: operational metrics, fuel and electricity use, CO₂e, avoided emissions and potential credits (Tables 3–9). |
| `04_monte_carlo.py` | Monte Carlo analysis with 10,000 iterations (seed 42) and Spearman sensitivity (Table 10, Figs. 8–11). The summary statistics of Table 10 are printed to the console. |
| `05_annotate_context_map.py` | Adds the label and legend to the REH/CTR context map (Fig. 1). |
| `06_annotate_bluesky_snapshots.py` | Adds labels and legends to the BlueSky screenshots (Figs. 2, 4, 6). |

The short interpretation printed at the end of `04_monte_carlo.py` is in Portuguese.

## Where each figure and table comes from

| Article | Script | Output |
|---|---|---|
| Table 1 | `01` | `output/helicopter_mix_parameters.csv` |
| Tables 3–5 | `03` | `output/operational_metrics.csv` |
| Table 6 | `03` | `output/energy_emissions_central.csv` |
| Table 7 | `03` | `output/evtol_model_sensitivity.csv` |
| Table 8 | `03` | `output/operational_distance_sensitivity.csv` |
| Table 9 | `03` | `output/replacement_share.csv` |
| Table 10 | `04` | console output; input ranges in `output/parameter_correlations.csv` |
| Fig. 1 | `05` | `output/ctr_annotated.png` |
| Figs. 2, 4, 6 | `06` | `output/bluesky_bimtra_mvp_off_annotated.png`, `..._mvp_60_annotated.png`, `..._mvp_120_annotated.png` |
| Figs. 3, 5, 7 | `02` | `output/flight_times_histogram_no_mvp.pdf`, `flight_times_histogram.pdf`, `flight_times_histogram_mvp120.pdf` |
| Fig. 8 | `04` | `output/03_emission_reduction_distribution.pdf` |
| Fig. 9 | `04` | `output/01_sensitivity_spearman.pdf` |
| Fig. 10 | `04` | `output/04_efgrid_historical_distribution.pdf` |
| Fig. 11 | `04` | `output/05_parameter_output_correlation.pdf` |

Table 2 lists the input parameters; they are set at the top of scripts `01`, `03` and `04`.

## Data

### Simulation outputs (`data/simulation/`)

The BlueSky scenario files and the flight-level simulation outputs are not included, because they
contain individual BIMTRA flight records (aircraft registration, type, departure time and route),
which cannot be redistributed. This folder holds the aggregated results of the three runs.

| File | Content |
|---|---|
| `bluesky_scenario_summary.csv` | One row per scenario: number of operations, simulated time, total flight hours, total 3D distance (NM), LOWC/NMAC/MAC event counts, conflict-resolution alerts and the event thresholds |
| `aircraft_flight_times.csv` | Flight time per aircraft (s) in each scenario, without aircraft identifiers and sorted by value |
| `aircraft_type_counts.csv` | Number of operations per aircraft type code in the scenario |

Simulation settings: conflict resolution off, or MVP with a 60 s or 120 s lookahead; protected-zone
radius 500 m. Event thresholds: loss of well-clear (LOWC) < 500 m horizontal; near mid-air
collision (NMAC) < 150 m horizontal and < 30 m vertical; mid-air collision (MAC) < 10 m horizontal
and < 30 m vertical.

### Grid emission factor (`data/grid_emission_factor/`)

`sin_operating_margin_daily_2023_2024.csv`: daily operating-margin CO₂ emission factor of the
Brazilian National Interconnected System (SIN), 2023–2024 (731 days, kgCO₂/kWh), from the
[Ministry of Science, Technology and Innovation (MCTI)](https://www.gov.br/mcti/pt-br/acompanhe-o-mcti/sirene/dados-e-ferramentas/fatores-de-emissao).
It is sampled in the Monte Carlo analysis.

### Figure sources (`data/figure_sources/`)

| File | Content |
|---|---|
| `ctr.png` | Interactive Leaflet map (R) of the REH routes, control zones (CTRs), helipads and aerodromes |
| `aerodrome_red_marker.png` | Aerodrome marker used in the Fig. 1 legend |
| `bluesky_bimtra_mvp_off.jpg`, `bluesky_bimtra_mvp_60.jpg`, `bluesky_bimtra_mvp_120.jpg` | BlueSky screenshots of the three scenarios |

## Citation

If you use this code or data, please cite the article (see also `CITATION.cff`):

```bibtex
@article{Rodrigues2026eVTOL,
  title   = {From avoided emissions to potential credits: A simulation-based case study of
             helicopter-to-{eVTOL} substitution in S{\~a}o Paulo},
  author  = {Rodrigues, Jaqueline Fonseca and Carvalho, Lucas Orbolato and Gomes, Igor Galhano and
             Pagani, Regina Negri and Mur{\c{c}}a, Mayara Cond{\'e} Rocha and Caldeira, Samuel da Silva and
             Guterres, Marcelo Xavier and Pamplona, Daniel Alberto},
  journal = {Case Studies on Transport Policy},
  volume  = {25},
  pages   = {101884},
  year    = {2026},
  doi     = {10.1016/j.cstp.2026.101884}
}
```
