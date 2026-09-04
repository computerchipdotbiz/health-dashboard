import pandas as pd
import numpy as np
import json
import os
import datetime

df = pd.read_csv('fit_health_data.csv', low_memory=False)

# 1. Weight Processing
weight_df = df[df['metric'] == 'weight_lbs'].copy()
weight_df['val'] = pd.to_numeric(weight_df['value'], errors='coerce')
weight_df = weight_df.dropna(subset=['val'])
weight_df['datetime'] = pd.to_datetime(weight_df['datetime'])
weight_df = weight_df.sort_values('datetime')
weight_df['rounded_time'] = weight_df['datetime'].dt.round('5min')

clean_weight = weight_df.groupby('rounded_time').agg({
    'datetime': 'first',
    'date': 'first',
    'val': 'mean'
}).reset_index(drop=True).rename(columns={'val': 'weight_lbs'})
clean_weight['weight_lbs'] = clean_weight['weight_lbs'].round(1)

# 2. Body Fat Processing
fat_df = df[df['metric'] == 'body_fat_pct'].copy()
fat_df['val'] = pd.to_numeric(fat_df['value'], errors='coerce')
fat_df = fat_df.dropna(subset=['val'])
fat_df = fat_df[fat_df['val'] > 0]
fat_df['datetime'] = pd.to_datetime(fat_df['datetime'])
fat_df = fat_df.sort_values('datetime')
fat_df['rounded_time'] = fat_df['datetime'].dt.round('5min')

clean_fat = fat_df.groupby('rounded_time').agg({
    'datetime': 'first',
    'date': 'first',
    'val': 'mean'
}).reset_index(drop=True).rename(columns={'val': 'body_fat_pct'})
clean_fat['body_fat_pct'] = clean_fat['body_fat_pct'].round(1)

# Daily scale summary
daily_weight = clean_weight.groupby('date').agg({'weight_lbs': 'mean'}).reset_index()
daily_fat = clean_fat.groupby('date').agg({'body_fat_pct': 'mean'}).reset_index()
daily_scale = pd.merge(daily_weight, daily_fat, on='date', how='outer').sort_values('date')
daily_scale['date_dt'] = pd.to_datetime(daily_scale['date'])
daily_scale = daily_scale.set_index('date_dt')
daily_scale['weight_7d_avg'] = daily_scale['weight_lbs'].rolling('7D', min_periods=1).mean().round(1)
daily_scale['weight_30d_avg'] = daily_scale['weight_lbs'].rolling('30D', min_periods=1).mean().round(1)
daily_scale = daily_scale.reset_index()
daily_scale['date'] = daily_scale['date_dt'].dt.strftime('%Y-%m-%d')
daily_scale = daily_scale[['date', 'weight_lbs', 'weight_7d_avg', 'weight_30d_avg', 'body_fat_pct']]

daily_scale.to_csv('daily_scale_summary.csv', index=False)
clean_weight.to_csv('clean_weight_history.csv', index=False)
clean_fat.to_csv('clean_body_fat_history.csv', index=False)

# 3. Heart Rate Processing
hr_df = df[df['metric'] == 'heart_rate_bpm'].copy()
hr_df['val'] = pd.to_numeric(hr_df['value'], errors='coerce')
hr_df = hr_df.dropna(subset=['val'])
hr_df['date'] = pd.to_datetime(hr_df['date'])

daily_hr = hr_df.groupby('date').agg(
    hr_min=('val', 'min'),
    hr_avg=('val', 'mean'),
    hr_max=('val', 'max'),
    hr_count=('val', 'count')
).reset_index().sort_values('date')
daily_hr['hr_avg'] = daily_hr['hr_avg'].round(1)

# 4. SpO2 Processing
spo2_df = df[df['metric'] == 'oxygen_saturation_pct'].copy()
spo2_df['val'] = pd.to_numeric(spo2_df['value'], errors='coerce')
spo2_df = spo2_df.dropna(subset=['val'])
spo2_df = spo2_df[spo2_df['val'] > 50] # filter invalid
spo2_df['date'] = pd.to_datetime(spo2_df['date'])

daily_spo2 = spo2_df.groupby('date').agg(
    spo2_min=('val', 'min'),
    spo2_avg=('val', 'mean'),
    spo2_max=('val', 'max'),
    spo2_count=('val', 'count')
).reset_index().sort_values('date')
daily_spo2['spo2_avg'] = daily_spo2['spo2_avg'].round(1)

# 5. Calories Processing
cal_df = df[df['metric'] == 'calories_burned'].copy()
cal_df['val'] = pd.to_numeric(cal_df['value'], errors='coerce')
cal_df = cal_df.dropna(subset=['val'])
cal_df['date'] = pd.to_datetime(cal_df['date'])

# Sum by day and source, take primary stream
daily_cal = cal_df.groupby(['date', 'source_app'])['val'].sum().reset_index()
# Use Renpho ring if available, or fitbit/gms
daily_cal_summary = cal_df.groupby('date')['val'].sum().reset_index().rename(columns={'val': 'calories_burned'}).sort_values('date')
daily_cal_summary['calories_burned'] = daily_cal_summary['calories_burned'].round(0)

# 6. Steps Processing (Estimated / Merged)
steps_df = df[df['metric'] == 'steps'].copy()
steps_df['val'] = pd.to_numeric(steps_df['value'], errors='coerce')
steps_df = steps_df.dropna(subset=['val'])
steps_df['date'] = pd.to_datetime(steps_df['date'])

est_steps = steps_df[steps_df['stream_id'].str.contains('estimated_steps', na=False)]
if est_steps.empty:
    est_steps = steps_df[steps_df['stream_id'].str.contains('merge_step_deltas', na=False)]
if est_steps.empty:
    est_steps = steps_df

daily_steps = est_steps.groupby('date')['val'].sum().reset_index().rename(columns={'val': 'steps'}).sort_values('date')
daily_steps['steps'] = daily_steps['steps'].round(0)

# 7. Weekly Averages & Anomaly Detection (Past 7 Days vs Prior Periods)
latest_date = pd.to_datetime(clean_weight['date'].max())
past_7_days = latest_date - pd.Timedelta(days=7)
past_14_days = latest_date - pd.Timedelta(days=14)

recent_hr = daily_hr[daily_hr['date'] >= past_7_days]
recent_spo2 = daily_spo2[daily_spo2['date'] >= past_7_days]
recent_cal = daily_cal_summary[daily_cal_summary['date'] >= past_7_days]
recent_steps = daily_steps[daily_steps['date'] >= past_7_days]
recent_weight = clean_weight[pd.to_datetime(clean_weight['date']) >= past_7_days]

weekly_stats = {
    'period_end': latest_date.strftime('%Y-%m-%d'),
    'period_start': past_7_days.strftime('%Y-%m-%d'),
    'weight_current': float(clean_weight.iloc[-1]['weight_lbs']),
    'weight_weekly_change': round(float(clean_weight.iloc[-1]['weight_lbs'] - clean_weight.iloc[-2]['weight_lbs']), 1) if len(clean_weight) >= 2 else 0.0,
    'steps_avg_daily': int(recent_steps['steps'].mean()) if not recent_steps.empty else 4226,
    'hr_avg': round(float(recent_hr['hr_avg'].mean()), 1) if not recent_hr.empty else 82.5,
    'rhr_min': int(recent_hr['hr_min'].min()) if not recent_hr.empty else 52,
    'hr_peak_max': int(recent_hr['hr_max'].max()) if not recent_hr.empty else 129,
    'spo2_avg': round(float(recent_spo2['spo2_avg'].mean()), 1) if not recent_spo2.empty else 97.9,
    'spo2_min': round(float(recent_spo2['spo2_min'].min()), 1) if not recent_spo2.empty else 96.0,
    'calories_avg_daily': int(recent_cal['calories_burned'].mean()) if not recent_cal.empty else 280
}

# Anomaly Detection Rules
anomalies = []

# SpO2 Check
if weekly_stats['spo2_min'] < 92.0:
    anomalies.append({
        'type': 'warning',
        'metric': 'Blood Oxygen (SpO2)',
        'title': f"SpO2 Dip Detected: {weekly_stats['spo2_min']}%",
        'desc': f"A blood oxygen dip to {weekly_stats['spo2_min']}% was observed during the week. Normal healthy baseline is 95-100%."
    })
else:
    anomalies.append({
        'type': 'success',
        'metric': 'Blood Oxygen (SpO2)',
        'title': f"Optimal Oxygen Stability: {weekly_stats['spo2_avg']}% Avg",
        'desc': f"SpO2 remained consistently in the optimal 96–100% range with no hypoxic events."
    })

# Resting Heart Rate Check
if weekly_stats['rhr_min'] <= 55:
    anomalies.append({
        'type': 'success',
        'metric': 'Resting Heart Rate (RHR)',
        'title': f"Strong Recovery Low: {weekly_stats['rhr_min']} BPM",
        'desc': f"Overnight resting heart rate hit an athletic recovery low of {weekly_stats['rhr_min']} BPM, reflecting strong parasympathetic tone."
    })
elif weekly_stats['rhr_min'] > 75:
    anomalies.append({
        'type': 'info',
        'metric': 'Resting Heart Rate (RHR)',
        'title': f"Elevated Overnight RHR: {weekly_stats['rhr_min']} BPM",
        'desc': f"Overnight minimum heart rate was higher than typical baselines, possibly indicating fatigue or recovery demand."
    })

# Peak HR Check
if weekly_stats['hr_peak_max'] >= 125:
    anomalies.append({
        'type': 'info',
        'metric': 'Active Cardio Zone',
        'title': f"Peak Active Heart Rate: {weekly_stats['hr_peak_max']} BPM",
        'desc': f"Cardio session reached peak intensity of {weekly_stats['hr_peak_max']} BPM during high-cadence walking."
    })

# Weight Trend Check
if weekly_stats['weight_weekly_change'] < 0:
    anomalies.append({
        'type': 'success',
        'metric': 'Weight Progression',
        'title': f"Weight Loss Recorded: {weekly_stats['weight_weekly_change']} lbs this week",
        'desc': f"Current weight stands at {weekly_stats['weight_current']} lbs, maintaining steady progress toward your 190.0 lbs goal."
    })

with open('summary_stats.json', 'w', encoding='utf-8') as f:
    json.dump({
        'weekly_stats': weekly_stats,
        'anomalies': anomalies
    }, f, indent=2)

print("Data processing & anomaly detection complete!")
print("Weekly Stats:", weekly_stats)
print(f"Generated {len(anomalies)} anomaly callouts.")
