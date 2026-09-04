import pandas as pd

df = pd.read_csv('fit_health_data.csv')
steps_df = df[df['metric'] == 'steps'].copy()
steps_df['datetime'] = pd.to_datetime(steps_df['datetime'])
steps_df['date'] = pd.to_datetime(steps_df['date'])

est = steps_df[steps_df['stream_id'].str.contains('estimated_steps', na=False)]
if est.empty:
    est = steps_df[steps_df['stream_id'].str.contains('merge_step_deltas', na=False)]

daily = est.groupby('date')['value'].sum().reset_index().sort_values('date')

# Exclude today if incomplete (Sep 4)
latest_complete_date = pd.to_datetime('2026-09-03')
last_45 = daily[(daily['date'] <= latest_complete_date) & (daily['date'] > latest_complete_date - pd.Timedelta(days=45))]

avg_45 = last_45['value'].mean()
print(f"45-day step average (2026-07-21 to 2026-09-03): {round(avg_45):,} steps/day ({len(last_45)} days)")
print(f"Min: {int(last_45['value'].min()):,}, Max: {int(last_45['value'].max()):,}")

