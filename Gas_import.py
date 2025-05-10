import pandas as pd
import matplotlib.pyplot as plt

# Load the trimmed data
df = pd.read_csv('Data/Gas_import_trimmed.csv')

# Select the five country codes of interest
country_codes = ['DK', 'FR', 'DE', 'NO', 'ES', 'IT', 'GR', 'TR']
df_sel = df[df['reporter'].isin(country_codes)]

# Aggregate import volumes by country code and year
df_group = df_sel.groupby(['reporter', 'year'])['volume_mio_m3'].sum().reset_index()

# Pivot for plotting
pivot = df_group.pivot(index='year', columns='reporter', values='volume_mio_m3')

# Plot
plt.figure(figsize=(8, 5))
for code in pivot.columns:
    plt.plot(pivot.index, pivot[code], label=code)
plt.xlabel('Year')
plt.ylabel('Import Volume (million m³)')
plt.title('Natural Gas Import Volume for DK, FR, DE, NO, ES, IT, GR')
plt.legend(title='Country Code')
#plt.tight_layout()
plt.show()
