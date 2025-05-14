import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# Load the Eurostat filtered dataset
path = 'Data/estat_nrg_ti_gas_filtered_en.csv'
df = pd.read_csv(path)

# Keep relevant columns
df = df[['geo', 'Geopolitical entity (reporting)', 
         'partner', 'Geopolitical entity (partner)', 
         'TIME_PERIOD', 'OBS_VALUE']]

# Filter for the five importing countries
target_codes = ['DK', 'FR', 'DE', 'NO', 'ES']
df = df[df['geo'].isin(target_codes)]

# Exclude 'TOTAL' and 'NSP'
df = df[~df['partner'].isin(['TOTAL', 'NSP'])]

# Ensure numeric for OBS_VALUE
df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')

# Determine the latest year in the dataset
latest_year = df['TIME_PERIOD'].max()

# Filter for the latest year
df_latest = df[df['TIME_PERIOD'] == latest_year]

# Aggregate by reporter and partner
agg_latest = (df_latest.groupby(['geo', 'Geopolitical entity (reporting)', 
                                 'partner', 'Geopolitical entity (partner)'])['OBS_VALUE']
                          .sum()
                          .reset_index())

# Rank within each importer
agg_latest['rank'] = agg_latest.groupby('geo')['OBS_VALUE'].rank(method='first', ascending=False)

# Keep top 5 exporters for each importer
top5_latest = agg_latest[agg_latest['rank'] <= 5].sort_values(['geo', 'rank'])



# ---------- PARAMETERS ----------
importers = ['DK', 'FR', 'DE', 'NO', 'ES', 'IT']  # Added Italy
year = 2023                                     # Year to plot
# ---------------------------------

# Load dataset
path = 'Data/estat_nrg_ti_gas_filtered_en.csv'
df = pd.read_csv(path)

# Filter relevant rows
df = df[df['geo'].isin(importers) & ~df['partner'].isin(['TOTAL', 'NSP'])]
df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')

# Select year
df_year = df[df['TIME_PERIOD'] == year]
if df_year.empty:
    raise ValueError(f"No data available for year {year}.")

# Build top-5 exporters per importer
rows = []
for imp in importers:
    sub = (df_year[df_year['geo'] == imp]
           .groupby('partner', as_index=False)['OBS_VALUE']
           .sum()
           .sort_values('OBS_VALUE', ascending=False)
           .head(5))
    sub['geo'] = imp
    rows.append(sub)

top5_df = pd.concat(rows, ignore_index=True)

# Pivot for plotting
pivot = top5_df.pivot(index='geo', columns='partner', values='OBS_VALUE').fillna(0)
pivot = pivot.reindex(importers)

# Colour map
cmap = plt.get_cmap('tab20')
exporters = pivot.columns.tolist()
color_map = {exp: cmap(i % 20) for i, exp in enumerate(exporters)}

# Plot
fig, ax = plt.subplots(figsize=(11, 6))
bottom = np.zeros(len(pivot))
x = np.arange(len(pivot.index))

for exp in exporters:
    vals = pivot[exp].values
    bars = ax.bar(x, vals, bottom=bottom, color=color_map[exp], label=exp)
    for bar, val in zip(bars, vals):
        if val > 0:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_y() + val/2,
                    f'{int(val):,}\n{exp}',
                    ha='center', va='center', fontsize=7, color='white')
    bottom += vals

ax.set_xticks(x)
ax.set_xticklabels(pivot.index)
ax.set_ylabel('Import volume - million m^3')
importers_str = ", ".join(importers)
ax.set_title(f'Top 5 Gas Exporters to {importers_str} in {year}')
ax.legend(title='Exporter code', bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
plt.tight_layout()
plt.savefig('Figures/Import_by_partner.png')
plt.show()

