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



# Keep required columns and filter
df = df[['geo', 'Geopolitical entity (reporting)', 'partner',
         'Geopolitical entity (partner)', 'TIME_PERIOD', 'OBS_VALUE']]
focus = ['DK', 'FR', 'DE', 'NO', 'ES']
df = df[df['geo'].isin(focus) & ~df['partner'].isin(['TOTAL', 'NSP'])]
df['OBS_VALUE'] = pd.to_numeric(df['OBS_VALUE'], errors='coerce')

# Latest year
year = df['TIME_PERIOD'].max()
latest = df[df['TIME_PERIOD'] == year]

# Top‑5 exporters per importer
latest_ranked = (latest.groupby(['geo', 'partner'])['OBS_VALUE']
                        .sum()
                        .groupby(level=0, group_keys=False)
                        .nlargest(5)
                        .reset_index())

# Pivot to wide form (importer rows, exporter columns)
pivot = (latest_ranked.pivot(index='geo', columns='partner', values='OBS_VALUE')
                    .fillna(0))

# Sort rows by importer code for consistent order
pivot = pivot.reindex(focus)

# Prepare grouped horizontal bar chart
fig, ax = plt.subplots(figsize=(10, 6))

importers = pivot.index.tolist()
exporters = pivot.columns.tolist()
n_exporters = len(exporters)
bar_height = 0.12
y_positions = np.arange(len(importers))

# Offsets for grouped bars
for i, exp in enumerate(exporters):
    ax.barh(y_positions + (i - n_exporters/2)*bar_height + bar_height/2,
            pivot[exp],
            height=bar_height,
            label=exp)

ax.set_yticks(y_positions)
ax.set_yticklabels(importers)
ax.set_xlabel('Import volume (dataset units)')
ax.set_title(f'Top 5 Gas Exporters to DK, FR, DE, NO, ES in {year} – Grouped Horizontal Bars')
ax.legend(title='Exporter code', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()

