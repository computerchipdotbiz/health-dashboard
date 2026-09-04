import pandas as pd

df = pd.read_csv('fit_health_data.csv')
renpho_hr = df[df['stream_id'].str.contains('renpho', case=False, na=False) & (df['metric'] == 'heart_rate_bpm')].copy()
renpho_hr['datetime'] = pd.to_datetime(renpho_hr['datetime'])
renpho_hr['date'] = pd.to_datetime(renpho_hr['date'])

print("Renpho Ring Heart Rate Data Points:", len(renpho_hr))
print(f"Date range: {renpho_hr['date'].min().strftime('%Y-%m-%d')} to {renpho_hr['date'].max().strftime('%Y-%m-%d')}")
print(f"Min HR: {renpho_hr['value'].min():.0f} BPM, Max HR: {renpho_hr['value'].max():.0f} BPM, Avg: {renpho_hr['value'].mean():.0f} BPM")

daily_hr = renpho_hr.groupby('date').agg({
    'value': ['min', 'mean', 'max', 'count']
})
print("\nDaily HR Breakdown from Renpho Ring:")
print(daily_hr)

