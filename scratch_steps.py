import pandas as pd

df = pd.read_csv('fit_health_data.csv')
steps_df = df[df['metric'] == 'steps'].copy()
steps_df['datetime'] = pd.to_datetime(steps_df['datetime'])
steps_df['date'] = pd.to_datetime(steps_df['date'])

# Print all unique stream IDs
for s in steps_df['stream_id'].unique():
    print(s)

# Use estimated_steps stream if available, or merge_step_deltas
est = steps_df[steps_df['stream_id'].str.contains('estimated_steps', na=False)]
if est.empty:
    est = steps_df[steps_df['stream_id'].str.contains('merge_step_deltas', na=False)]

print("\n--- Estimated/Merged Daily Steps ---")
daily = est.groupby('date')['value'].sum().reset_index().sort_values('date')
print(f"Total days: {len(daily)}")
print(f"Date range: {daily['date'].min().strftime('%Y-%m-%d')} to {daily['date'].max().strftime('%Y-%m-%d')}")

latest = daily['date'].max()
last_7 = daily[daily['date'] >= (latest - pd.Timedelta(days=7))]
last_30 = daily[daily['date'] >= (latest - pd.Timedelta(days=30))]
last_90 = daily[daily['date'] >= (latest - pd.Timedelta(days=90))]
last_180 = daily[daily['date'] >= (latest - pd.Timedelta(days=180))]

print(f"\nAverage Daily Steps:")
print(f"  • Last 7 Days:   {int(last_7['value'].mean()):,} steps/day")
print(f"  • Last 30 Days:  {int(last_30['value'].mean()):,} steps/day")
print(f"  • Last 90 Days:  {int(last_90['value'].mean()):,} steps/day")
print(f"  • Last 180 Days (6 Mo): {int(last_180['value'].mean()):,} steps/day")

print("\nLast 14 Days Detail:")
for _, r in daily.tail(14).iterrows():
    print(f"  {r['date'].strftime('%Y-%m-%d (%a)')}: {int(r['value']):,} steps")
