import pandas as pd

df = pd.read_csv('fit_health_data.csv', low_memory=False)

print("=== Renpho SpO2 ===")
spo2 = df[(df['source_app'] == 'com.renpho.health') & (df['metric'] == 'oxygen_saturation_pct')].copy()
spo2['val'] = pd.to_numeric(spo2['value'], errors='coerce')
print(f"Count: {len(spo2)}, Min: {spo2['val'].min():.1f}%, Avg: {spo2['val'].mean():.1f}%, Max: {spo2['val'].max():.1f}%")

print("\n=== Renpho Heart Rate ===")
hr = df[(df['source_app'] == 'com.renpho.health') & (df['metric'] == 'heart_rate_bpm')].copy()
hr['val'] = pd.to_numeric(hr['value'], errors='coerce')
print(f"Count: {len(hr)}, Min: {hr['val'].min():.0f} BPM, Avg: {hr['val'].mean():.1f} BPM, Max: {hr['val'].max():.0f} BPM")

print("\n=== Renpho Daily Calories Burned ===")
cal = df[(df['source_app'] == 'com.renpho.health') & (df['metric'] == 'calories_burned')].copy()
cal['val'] = pd.to_numeric(cal['value'], errors='coerce')
daily_cal = cal.groupby('date')['val'].sum().reset_index()
print(daily_cal)

