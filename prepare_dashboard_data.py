import json
import os
import pandas as pd
import datetime

clean_weight = pd.read_csv('clean_weight_history.csv')
clean_fat = pd.read_csv('clean_body_fat_history.csv')
daily_scale = pd.read_csv('daily_scale_summary.csv')

with open('summary_stats.json', 'r', encoding='utf-8') as f:
    stats_data = json.load(f)

# Weight & Fat data for chart
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

# Compute 45-day step average
avg_45d_steps = stats_data['weekly_stats'].get('steps_avg_daily', 4226)
if os.path.exists('fit_health_data.csv'):
    try:
        df = pd.read_csv('fit_health_data.csv', low_memory=False)
        steps_df = df[df['metric'] == 'steps'].copy()
        steps_df['val'] = pd.to_numeric(steps_df['value'], errors='coerce').dropna()
        steps_df['date'] = pd.to_datetime(steps_df['date'])
        
        est = steps_df[steps_df['stream_id'].str.contains('estimated_steps', na=False)]
        if est.empty:
            est = steps_df[steps_df['stream_id'].str.contains('merge_step_deltas', na=False)]
        if est.empty:
            est = steps_df
            
        daily = est.groupby('date')['val'].sum().reset_index().sort_values('date')
        latest_date = daily['date'].max()
        last_45 = daily[(daily['date'] <= latest_date) & (daily['date'] > latest_date - pd.Timedelta(days=45))]
        if not last_45.empty:
            avg_45d_steps = int(round(last_45['val'].mean()))
    except Exception as e:
        print("Error reading steps:", e)

# Maintain Reports Archive Index
os.makedirs('reports', exist_ok=True)
archive_file = 'reports_archive.json'
past_reports = []
if os.path.exists(archive_file):
    try:
        with open(archive_file, 'r', encoding='utf-8') as f:
            past_reports = json.load(f)
    except Exception:
        past_reports = []

# Current report entry
now_str = datetime.datetime.now().strftime('%Y-%m-%d')
report_filename = f"report_{now_str}.html"
current_entry = {
    'date': now_str,
    'filename': report_filename,
    'url': f"reports/{report_filename}",
    'weight': stats_data['weekly_stats']['weight_current'],
    'weekly_change': stats_data['weekly_stats']['weight_weekly_change'],
    'steps_avg': avg_45d_steps,
    'hr_avg': stats_data['weekly_stats']['hr_avg'],
    'rhr_min': stats_data['weekly_stats']['rhr_min'],
    'spo2_avg': stats_data['weekly_stats']['spo2_avg'],
}

# Update or prepend to past_reports (keep unique by date)
past_reports = [r for r in past_reports if r.get('date') != now_str]
past_reports.insert(0, current_entry)

with open(archive_file, 'w', encoding='utf-8') as f:
    json.dump(past_reports, f, indent=2)

payload = {
    'last_updated': datetime.datetime.now().strftime('%b %d, %Y'),
    'weights': weight_data,
    'body_fat': fat_data,
    'avg_45d_steps': avg_45d_steps,
    'weekly_stats': stats_data['weekly_stats'],
    'anomalies': stats_data['anomalies'],
    'past_reports': past_reports
}

with open('dashboard_data.json', 'w', encoding='utf-8') as f:
    json.dump(payload, f, indent=2)

print(f"Prepared dashboard payload with {len(past_reports)} archived reports.")
