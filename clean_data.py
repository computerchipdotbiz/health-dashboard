import pandas as pd
import numpy as np
import json
import os

df = pd.read_csv('fit_health_data.csv')

# Weight processing
weight_df = df[df['metric'] == 'weight_lbs'].copy()
weight_df['datetime'] = pd.to_datetime(weight_df['datetime'])
weight_df = weight_df.sort_values('datetime')
weight_df['rounded_time'] = weight_df['datetime'].dt.round('5min')
clean_weight = weight_df.groupby('rounded_time').agg({
    'datetime': 'first',
    'date': 'first',
    'value': 'mean'
}).reset_index(drop=True)
clean_weight = clean_weight.rename(columns={'value': 'weight_lbs'})
clean_weight['weight_lbs'] = clean_weight['weight_lbs'].round(1)

# Body Fat processing
fat_df = df[df['metric'] == 'body_fat_pct'].copy()
fat_df = fat_df[fat_df['value'] > 0]  # Filter out 0.0 glitch readings
fat_df['datetime'] = pd.to_datetime(fat_df['datetime'])
fat_df = fat_df.sort_values('datetime')
fat_df['rounded_time'] = fat_df['datetime'].dt.round('5min')
clean_fat = fat_df.groupby('rounded_time').agg({
    'datetime': 'first',
    'date': 'first',
    'value': 'mean'
}).reset_index(drop=True)
clean_fat = clean_fat.rename(columns={'value': 'body_fat_pct'})
clean_fat['body_fat_pct'] = clean_fat['body_fat_pct'].round(1)

# Merge by date/datetime
merged_scale = pd.merge(clean_weight, clean_fat[['datetime', 'body_fat_pct']], on='datetime', how='left')

# Forward fill body fat if taken at slightly different second or same day
daily_weight = clean_weight.groupby('date').agg({'weight_lbs': 'mean'}).reset_index()
daily_fat = clean_fat.groupby('date').agg({'body_fat_pct': 'mean'}).reset_index()
daily = pd.merge(daily_weight, daily_fat, on='date', how='outer').sort_values('date')
daily['date_dt'] = pd.to_datetime(daily['date'])
daily = daily.set_index('date_dt')

# Rolling averages
daily['weight_7d_avg'] = daily['weight_lbs'].rolling('7D', min_periods=1).mean().round(1)
daily['weight_30d_avg'] = daily['weight_lbs'].rolling('30D', min_periods=1).mean().round(1)

# Daily summary table
daily_reset = daily.reset_index()
daily_reset['date'] = daily_reset['date_dt'].dt.strftime('%Y-%m-%d')
daily_reset = daily_reset[['date', 'weight_lbs', 'weight_7d_avg', 'weight_30d_avg', 'body_fat_pct']]

daily_reset.to_csv('daily_scale_summary.csv', index=False)
clean_weight.to_csv('clean_weight_history.csv', index=False)
clean_fat.to_csv('clean_body_fat_history.csv', index=False)

# Summary stats
latest_weight = clean_weight.iloc[-1]['weight_lbs']
latest_weight_date = clean_weight.iloc[-1]['date']
first_weight = clean_weight.iloc[0]['weight_lbs']
first_weight_date = clean_weight.iloc[0]['date']
max_weight = clean_weight['weight_lbs'].max()
min_weight = clean_weight['weight_lbs'].min()

latest_fat = clean_fat.iloc[-1]['body_fat_pct'] if not clean_fat.empty else None
latest_fat_date = clean_fat.iloc[-1]['date'] if not clean_fat.empty else None

stats = {
    'total_measurements': len(clean_weight),
    'start_date': str(first_weight_date),
    'latest_date': str(latest_weight_date),
    'start_weight': float(first_weight),
    'latest_weight': float(latest_weight),
    'min_weight': float(min_weight),
    'max_weight': float(max_weight),
    'latest_body_fat': float(latest_fat) if latest_fat else None,
    'latest_fat_date': str(latest_fat_date) if latest_fat_date else None
}

with open('summary_stats.json', 'w') as f:
    json.dump(stats, f, indent=2)

print("Data processing complete!")
print(json.dumps(stats, indent=2))
