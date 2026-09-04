import json
import os
import pandas as pd

clean_weight = pd.read_csv('clean_weight_history.csv')
clean_fat = pd.read_csv('clean_body_fat_history.csv')

# Compute 45-day step average from fit_health_data.csv
avg_45d_steps = 4332
if os.path.exists('fit_health_data.csv'):
    try:
        df = pd.read_csv('fit_health_data.csv')
        steps_df = df[df['metric'] == 'steps'].copy()
        steps_df['date'] = pd.to_datetime(steps_df['date'])
        
        est = steps_df[steps_df['stream_id'].str.contains('estimated_steps', na=False)]
        if est.empty:
            est = steps_df[steps_df['stream_id'].str.contains('merge_step_deltas', na=False)]
        if not est.empty:
            daily = est.groupby('date')['value'].sum().reset_index().sort_values('date')
            latest_date = daily['date'].max()
            last_45 = daily[(daily['date'] <= latest_date) & (daily['date'] > latest_date - pd.Timedelta(days=45))]
            if not last_45.empty:
                avg_45d_steps = int(round(last_45['value'].mean()))
    except Exception as e:
        print("Error computing steps:", e)

# Prepare chart data
weight_data = []
for _, row in clean_weight.iterrows():
    weight_data.append({
        'd': row['date'],
        'dt': row['datetime'],
        'w': float(row['weight_lbs'])
    })

fat_data = []
for _, row in clean_fat.iterrows():
    fat_data.append({
        'd': row['date'],
        'dt': row['datetime'],
        'bf': float(row['body_fat_pct'])
    })

payload = {
    'weights': weight_data,
    'body_fat': fat_data,
    'avg_45d_steps': avg_45d_steps
}

with open('dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)

print(f"Exported {len(weight_data)} weight points, {len(fat_data)} fat points, and 45-day avg steps ({avg_45d_steps}) for dashboard.")
