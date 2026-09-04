import pandas as pd
import json

df = pd.read_csv('fit_health_data.csv', low_memory=False)

print("Unique metrics in dataset:")
print(df['metric'].value_counts())

print("\n--- SpO2 Sample ---")
spo2 = df[df['metric'] == 'oxygen_saturation_pct']
print(spo2[['datetime', 'value', 'source_app']].head(5))
vals = pd.to_numeric(spo2['value'], errors='coerce').dropna()
print(f"SpO2 range: {vals.min()} to {vals.max()}")

print("\n--- Heart Rate Sample ---")
hr = df[df['metric'] == 'heart_rate_bpm']
print(hr[['datetime', 'value', 'source_app']].head(5))

print("\n--- Sleep Sample ---")
sleep = df[df['metric'] == 'sleep_stage']
print(sleep[['datetime', 'value', 'source_app']].head(5))
print("Sleep stage values:", sleep['value'].value_counts())

print("\n--- Calories Sample ---")
cal = df[df['metric'] == 'calories_burned']
print(cal[['datetime', 'value', 'source_app']].head(5))

