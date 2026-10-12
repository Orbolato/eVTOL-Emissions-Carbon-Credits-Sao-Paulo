"""
Sensitivity Analysis for Monte Carlo Simulation
Contribution of parameters to total emission variability
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
from pathlib import Path
import sys

# Suppress warnings about constant input to correlation functions
warnings.filterwarnings('ignore', category=stats.ConstantInputWarning)
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# 0. LOAD HISTORICAL EF_GRID
# ============================================================================

root_dir = Path(__file__).resolve().parents[1]
rev_dir = root_dir / "output"
rev_dir.mkdir(exist_ok=True)
csv_path = root_dir / "data" / "grid_emission_factor" / "sin_operating_margin_daily_2023_2024.csv"

# Load EF_grid historical values (daily SIN operating-margin factors, 2023-2024)
df_efgrid = pd.read_csv(csv_path)
df_efgrid = df_efgrid.rename(columns={'date': 'data_ref',
                                      'ef_grid_kgco2_per_kwh': 'EFgrid_operation_margin_kgCO2_per_kWh'})
df_efgrid = df_efgrid.dropna()

# Calculate statistics from historical data
EF_grid_mean = df_efgrid['EFgrid_operation_margin_kgCO2_per_kWh'].mean()
EF_grid_std = df_efgrid['EFgrid_operation_margin_kgCO2_per_kWh'].std()
EF_grid_min = df_efgrid['EFgrid_operation_margin_kgCO2_per_kWh'].min()
EF_grid_max = df_efgrid['EFgrid_operation_margin_kgCO2_per_kWh'].max()

print(f"Historical EF_grid Statistics (from {len(df_efgrid)} days in 2023-2024):")
print(f"  Mean: {EF_grid_mean:.4f} kgCO2e/kWh")
print(f"  Std Dev: {EF_grid_std:.4f}")
print(f"  Min: {EF_grid_min:.4f}")
print(f"  Max: {EF_grid_max:.4f}")
print()

# ============================================================================
# 1. DEFINE PARAMETER DISTRIBUTIONS
# ============================================================================

n_iterations = 10000

# Parameter ranges (min, max) as per paper. Range-based parameters are sampled
# from uniform distributions across the stated bounds.
param_ranges = {
    'D_3D': (3945.44, 3945.44),  # km, BIMTRA-derived BlueSky scenario with MVP 60 s conflict resolution
    'rho_fuel': (0.7713, 0.8366),  # kg/L
    'FI_h': (0.8391, 1.6033),  # L/km (range among frequent BIMTRA fleet-mix types)
    'eta_charge': (0.88, 0.95),  # dimensionless
    'EI_e': (0.1643, 0.4659),  # kWh/km
    'E_0': (3.61, 7.61),  # kWh/flight
}

# Constants (held constant)
EF_TTW = 3.16  # kgCO2e/kg fuel
N_ops = 146  # filtered BIMTRA-derived intra-RMSP operations

# ============================================================================
# 2. GENERATE PARAMETER SAMPLES
# ============================================================================

parameters = {}

for param_name, (param_min, param_max) in param_ranges.items():
    # Check if parameter is constant (min == max)
    if param_min == param_max:
        # Create constant array
        samples = np.full(n_iterations, param_min)
        print(f"  {param_name}: CONSTANT = {param_min:.2f}")
    else:
        samples = np.random.uniform(param_min, param_max, n_iterations)
        print(
            f"  {param_name}: uniform range=[{param_min:.2f}, {param_max:.2f}]"
        )
    
    parameters[param_name] = samples

# Add EF_grid as parameter sampled from historical data
# Resample with replacement from historical values
parameters['EF_grid'] = np.random.choice(
    df_efgrid['EFgrid_operation_margin_kgCO2_per_kWh'].values, 
    size=n_iterations, 
    replace=True
)

# Convert to DataFrame for easier manipulation
df_params = pd.DataFrame(parameters)

# ============================================================================
# 3. CALCULATE EMISSIONS FOR EACH ITERATION
# ============================================================================

# Helicopter baseline (BIMTRA-derived fleet mix)
M_fuel_ec135 = df_params['FI_h'] * df_params['D_3D'] * df_params['rho_fuel']
CO2e_heli = M_fuel_ec135 * EF_TTW

# eVTOL (using historical EF_grid)
E_bat = df_params['EI_e'] * df_params['D_3D'] + df_params['E_0'] * N_ops
E_grid = E_bat / df_params['eta_charge']
CO2e_evtol = E_grid * df_params['EF_grid']

# Avoided emissions
avoided_emissions = CO2e_heli - CO2e_evtol
relative_reduction = (avoided_emissions / CO2e_heli) * 100

# ============================================================================
# 4. SENSITIVITY ANALYSIS
# ============================================================================

# Method: Correlation-based sensitivity (Spearman rank correlation)
# This shows the monotonic relationship between each parameter and output

sensitivities = {}
for param_name in df_params.columns:
    # Check if parameter is constant (no variance) - use tolerance for floating point
    if df_params[param_name].std() < 1e-7:
        # Constant parameters have no sensitivity
        sensitivities[param_name] = 0
    else:
        # Calculate Spearman correlation
        corr, p_value = stats.spearmanr(df_params[param_name], relative_reduction)
        # Handle NaN correlation (shouldn't happen, but just in case)
        if np.isnan(corr):
            sensitivities[param_name] = 0
        else:
            sensitivities[param_name] = abs(corr)  # Use absolute value

# Normalize to percentages (so they sum to 100%)
# Only count non-zero sensitivities
total_sensitivity = sum(sensitivities.values())
if total_sensitivity > 0:
    sensitivities_pct = {k: (v / total_sensitivity) * 100 for k, v in sensitivities.items()}
else:
    sensitivities_pct = {k: 0 for k in sensitivities.keys()}

# ============================================================================
# 5. LEGACY DUPLICATE SPEARMAN DIAGNOSTIC (NOT SOBOL / NOT PARTIAL CORRELATION)
# ============================================================================

# Historical compatibility output: this repeats the absolute Spearman
# transformation above. It is retained for traceability, but it is not a
# Sobol index and not a statistically distinct partial-correlation estimate.
partial_correlations = {}

for param_name in df_params.columns:
    # Check if parameter is constant (no variance) - use tolerance for floating point
    if df_params[param_name].std() < 1e-7:
        # Constant parameters have no sensitivity
        partial_correlations[param_name] = 0
    else:
        # Correlation between parameter and output
        corr_output = stats.spearmanr(df_params[param_name], relative_reduction)[0]
        # Handle NaN correlation
        if np.isnan(corr_output):
            partial_correlations[param_name] = 0
        else:
            # Legacy duplicate of the absolute Spearman diagnostic.
            # Do not interpret this as an independent partial correlation.
            partial_correlations[param_name] = abs(corr_output)

# Normalize
total_partial = sum(partial_correlations.values())
if total_partial > 0:
    partial_contributions_pct = {
        k: (v / total_partial) * 100 for k, v in partial_correlations.items()
    }
else:
    partial_contributions_pct = {k: 0 for k in partial_correlations.keys()}

# ============================================================================
# 6. CREATE VISUALIZATIONS - SEPARATE PLOTS
# ============================================================================

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7.5)
plt.rcParams['font.size'] = 20
plt.rcParams['axes.labelsize'] = 22
plt.rcParams['axes.titlesize'] = 23
plt.rcParams['xtick.labelsize'] = 20
plt.rcParams['ytick.labelsize'] = 20
plt.rcParams['legend.fontsize'] = 19
plt.rcParams['pdf.fonttype'] = 42
plt.rcParams['ps.fonttype'] = 42
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['mathtext.fontset'] = 'dejavusans'

# Plot 1: Spearman Correlation-based Sensitivity (Separate)
plt.figure(figsize=(12, 7))
params_sorted_1 = sorted(sensitivities_pct.items(), key=lambda x: x[1], reverse=True)
# Filter out parameters with 0 contribution (constants)
params_sorted_1 = [(k, v) for k, v in params_sorted_1 if v > 0]
names_1, values_1 = zip(*params_sorted_1) if params_sorted_1 else ([], [])

if len(values_1) > 0:
    colors_1 = plt.cm.viridis(np.linspace(0.2, 0.9, len(names_1)))
    bars_1 = plt.barh(names_1, values_1, color=colors_1, edgecolor='black', linewidth=1.5)
    plt.xlabel('Relative contribution (%)')
    plt.title('Parameter Sensitivity: Contribution to Emission Variability\n(Spearman Correlation Method)', 
              fontsize=23)
    plt.xlim(0, max(values_1) * 1.15)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars_1, values_1)):
        plt.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=19)
else:
    plt.text(0.5, 0.5, 'No variable parameters', ha='center', va='center', fontsize=21)
    plt.axis('off')

plt.tight_layout()
plt.savefig(rev_dir / '01_sensitivity_spearman.pdf', bbox_inches='tight')
print("Saved: 01_sensitivity_spearman.pdf")
plt.close()

# Plot 2: legacy duplicate Spearman diagnostic (retained for traceability)
plt.figure(figsize=(12, 7))
params_sorted_2 = sorted(partial_contributions_pct.items(), key=lambda x: x[1], reverse=True)
# Filter out parameters with 0 contribution (constants)
params_sorted_2 = [(k, v) for k, v in params_sorted_2 if v > 0]
names_2, values_2 = zip(*params_sorted_2) if params_sorted_2 else ([], [])

if len(values_2) > 0:
    colors_2 = plt.cm.plasma(np.linspace(0.2, 0.9, len(names_2)))
    bars_2 = plt.barh(names_2, values_2, color=colors_2, edgecolor='black', linewidth=1.5)
    plt.xlabel('Relative contribution (%)')
    plt.title('Legacy Sensitivity Diagnostic: Normalized Absolute Spearman\n(Not an independent partial-correlation method)', 
              fontsize=23)
    plt.xlim(0, max(values_2) * 1.15)
    
    # Add value labels
    for i, (bar, val) in enumerate(zip(bars_2, values_2)):
        plt.text(val + 1, i, f'{val:.1f}%', va='center', fontsize=19)
else:
    plt.text(0.5, 0.5, 'No variable parameters', ha='center', va='center', fontsize=21)
    plt.axis('off')

plt.tight_layout()
plt.savefig(rev_dir / '02_sensitivity_partial_correlation.pdf', bbox_inches='tight')
print("Saved: 02_sensitivity_partial_correlation.pdf")
plt.close()

# Plot 3: Distribution of Emission Reduction % (Separate)
plt.figure(figsize=(12, 7))
plt.hist(relative_reduction, bins=50, color='steelblue', edgecolor='black', alpha=0.7, linewidth=1.2)
plt.axvline(np.mean(relative_reduction), color='red', linestyle='--', linewidth=2.5, 
            label=f'Mean: {np.mean(relative_reduction):.2f}%')
plt.axvline(np.median(relative_reduction), color='green', linestyle='--', linewidth=2.5, 
            label=f'Median: {np.median(relative_reduction):.2f}%')
plt.xlabel('Relative emission reduction (%)')
plt.ylabel('Frequency')
plt.title('Distribution of Model Output: Relative Emission Reduction\n(10,000 Monte Carlo Iterations)', 
          fontsize=23)
plt.legend(loc='upper left')
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(rev_dir / '03_emission_reduction_distribution.pdf', bbox_inches='tight')
print("Saved: 03_emission_reduction_distribution.pdf")
plt.close()

# Plot 4: EF_grid Historical Distribution (Separate)
plt.figure(figsize=(12, 7))
plt.hist(df_efgrid['EFgrid_operation_margin_kgCO2_per_kWh'].values, bins=40, 
         color='coral', edgecolor='black', alpha=0.7, linewidth=1.2, label='Historical Data')
plt.axvline(EF_grid_mean, color='darkred', linestyle='--', linewidth=2.5, 
            label=f'Mean: {EF_grid_mean:.4f} kgCO2e/kWh')
plt.xlabel(r'$EF_{\mathrm{grid}}$ (kgCO$_2$e/kWh)')
plt.ylabel('Frequency (days)')
plt.title('Historical EF_grid Distribution (Grid Emission Factor)\n2023-2024 Daily Values', 
          fontsize=23)
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.savefig(rev_dir / '04_efgrid_historical_distribution.pdf', bbox_inches='tight')
print("Saved: 04_efgrid_historical_distribution.pdf")
plt.close()

# Plot 5: Correlation between Each Parameter and Output (Separate)
plt.figure(figsize=(12, 7))
param_names = list(df_params.columns)
correlations_with_output = []
param_names_filtered = []

for param_name in param_names:
    if df_params[param_name].std() < 1e-7:
        # Skip constant parameters
        continue
    corr, _ = stats.spearmanr(df_params[param_name], relative_reduction)
    correlations_with_output.append(corr)
    param_names_filtered.append(param_name)

if len(correlations_with_output) > 0:
    # Sort by absolute correlation
    sorted_indices = np.argsort(np.abs(correlations_with_output))[::-1]
    sorted_names = [param_names_filtered[i] for i in sorted_indices]
    sorted_corrs = [correlations_with_output[i] for i in sorted_indices]
    
    # Color by positive/negative correlation
    colors = ['green' if c > 0 else 'red' for c in sorted_corrs]
    bars = plt.barh(sorted_names, sorted_corrs, color=colors, edgecolor='black', linewidth=1.5, alpha=0.7)
    
    plt.xlabel(r'Spearman correlation coefficient ($\rho$)')
    plt.title('Parameter Correlation with Emission Reduction\n(Positive = increases reduction, Negative = decreases reduction)', 
              fontsize=23)
    plt.axvline(0, color='black', linestyle='-', linewidth=0.8)
    plt.xlim(-1, 1)
    
    # Add value labels (only for finite values)
    for i, val in enumerate(sorted_corrs):
        if np.isfinite(val):
            x_pos = val + (0.01 if val > 0 else -0.01)
            ha = 'left' if val > 0 else 'right'
            plt.text(x_pos, i, f'{val:.3f}', va='center', ha=ha, fontsize=19)
else:
    plt.text(0.5, 0.5, 'No variable parameters', ha='center', va='center', fontsize=21)
    plt.axis('off')

plt.tight_layout()
plt.savefig(rev_dir / '05_parameter_output_correlation.pdf', bbox_inches='tight')
print("Saved: 05_parameter_output_correlation.pdf")
plt.close()

print("\nAll plots saved successfully!")

# ============================================================================
# 7. DETAILED RESULTS TABLE
# ============================================================================

# Create detailed results table
results_df = pd.DataFrame({
    'Parameter': list(sensitivities_pct.keys()),
    'Spearman Correlation (%)': list(sensitivities_pct.values()),
    'Legacy Duplicate Spearman (%)': list(partial_contributions_pct.values())
})

# Calculate average contribution
results_df['Average Contribution (%)'] = (results_df['Spearman Correlation (%)'] + 
                                          results_df['Legacy Duplicate Spearman (%)']) / 2

# Sort by average contribution and filter out constant parameters (0 contribution)
results_df = results_df[results_df['Average Contribution (%)'] > 0].sort_values('Average Contribution (%)', ascending=False)

print("\n" + "="*70)
print("SENSITIVITY ANALYSIS RESULTS")
print("="*70)
print(results_df.to_string(index=False))

# ============================================================================
# 8. PARAMETER-OUTPUT CORRELATIONS
# ============================================================================

print("\n" + "="*70)
print("PARAMETER STATISTICS AND CORRELATIONS WITH OUTPUT")
print("="*70)

correlations_summary = []
for param_name in df_params.columns:
    # Skip constant parameters
    if df_params[param_name].std() < 1e-7:
        continue
    
    param_data = df_params[param_name]
    corr_spearman, _ = stats.spearmanr(param_data, relative_reduction)
    corr_pearson, _ = stats.pearsonr(param_data, relative_reduction)
    
    correlations_summary.append({
        'Parameter': param_name,
        'Mean': param_data.mean(),
        'Std': param_data.std(),
        'Min': param_data.min(),
        'Max': param_data.max(),
        'Spearman ρ': corr_spearman,
        'Pearson r': corr_pearson
    })

corr_df = pd.DataFrame(correlations_summary)
print(corr_df.to_string(index=False))

# ============================================================================
# 9. EXPORT RESULTS
# ============================================================================

results_df.to_csv(rev_dir / 'sensitivity_analysis_results.csv', index=False)
corr_df.to_csv(rev_dir / 'parameter_correlations.csv', index=False)

print("\n" + "="*70)
print("EXPORT COMPLETED")
print("="*70)
print("Saved: sensitivity_analysis_results.csv")
print("Saved: parameter_correlations.csv")
print("\n")

# ============================================================================
# 10. INTERPRETATION
# ============================================================================

print("="*70)
print("INTERPRETATION")
print("="*70)
print(f"""
A variabilidade total nas emissões é governada principalmente por:

1. Parâmetros com MAIOR contribuição:
""")

for idx, row in results_df.head(3).iterrows():
    print(f"   - {row['Parameter']}: {row['Average Contribution (%)']:.1f}%")

print(f"""
2. Parâmetros com MENOR contribuição:
""")

for idx, row in results_df.tail(3).iterrows():
    print(f"   - {row['Parameter']}: {row['Average Contribution (%)']:.1f}%")

print(f"""
3. Estatísticas da redução de emissões:
   - Média: {np.mean(relative_reduction):.2f}%
   - Desvio padrão: {np.std(relative_reduction):.2f}%
   - Intervalo: {np.min(relative_reduction):.2f}% a {np.max(relative_reduction):.2f}%
   - Coeficiente de Variação: {(np.std(relative_reduction) / np.mean(relative_reduction)) * 100:.2f}%

4. Dados do EF_grid histórico (2023-2024):
   - {len(df_efgrid)} observações diárias
   - Média: {EF_grid_mean:.4f} kgCO2e/kWh
   - Desvio padrão: {EF_grid_std:.4f}
   - Intervalo: {EF_grid_min:.4f} a {EF_grid_max:.4f}

Esta análise mostra que a variabilidade nas emissões é principalmente
determinada por poucos parâmetros-chave, indicando que o modelo é robusto
a variações em outros parâmetros. O uso de dados históricos de EF_grid
representa melhor a incerteza relacionada às emissões da matriz elétrica.
""")
