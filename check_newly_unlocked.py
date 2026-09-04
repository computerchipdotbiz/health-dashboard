import pandas as pd

df = pd.read_csv('fit_health_data.csv', low_memory=False)
renpho = df[df['source_app'] == 'com.renpho.health']

print("=== Renpho Smart Ring Unlocked Metrics ===")
for m, g in renpho.groupby('metric'):
    vals = pd.to_numeric(g['value'], errors='coerce').dropna()
    print(f"\nMetric: {m} ({len(g)} records)")
    print(f"  Range: {g['date'].min()} to {g['date'].max()}")
    if not vals.empty:
        print(f"  Min: {vals.min():.1f}, Avg: {vals.mean():.1f}, Max: {vals.max():.1f}")

print("\n=== Sleep Stages Across Sources ===")
sleep_df = df[df['metric'] == 'sleep_stage'].copy()
if not sleep_df.empty:
    print(f"Total Sleep Stage Records: {len(sleep_df)}")
    print("Sources:", sleep_df['source_app'].value_counts().to_dict())

