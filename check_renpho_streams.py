import pandas as pd

df = pd.read_csv('fit_health_data.csv')
renpho_df = df[df['stream_id'].str.contains('renpho', case=False, na=False) | df['source_app'].str.contains('renpho', case=False, na=False)]

print("=== Renpho Data Streams ===")
print("Total rows:", len(renpho_df))
for metric, group in renpho_df.groupby('metric'):
    print(f"\nMetric: {metric}")
    print(f"  Count: {len(group)}")
    print(f"  Date range: {group['date'].min()} to {group['date'].max()}")
    print(f"  Sample streams: {group['stream_id'].unique()[:3]}")

