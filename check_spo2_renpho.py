import pandas as pd

df = pd.read_csv('fit_health_data.csv', low_memory=False)
renpho_spo2 = df[(df['source_app'] == 'com.renpho.health') & (df['metric'] == 'oxygen_saturation_pct')]
print(renpho_spo2[['datetime', 'value', 'data_type']].head(10))

