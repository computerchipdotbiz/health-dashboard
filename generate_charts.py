import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import shutil
import os

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig_dpi = 150

daily_df = pd.read_csv('daily_scale_summary.csv')
daily_df['date'] = pd.to_datetime(daily_df['date'])
clean_weight = pd.read_csv('clean_weight_history.csv')
clean_weight['datetime'] = pd.to_datetime(clean_weight['datetime'])

artifact_dir = r"C:\Users\DigitalArthas\.gemini\antigravity\brain\1ec6b764-ab9d-477a-bc51-69a33c482e05"
os.makedirs(artifact_dir, exist_ok=True)

# 1. All-Time Weight Journey Chart
fig, ax = plt.subplots(figsize=(12, 6), dpi=fig_dpi)
ax.plot(clean_weight['datetime'], clean_weight['weight_lbs'], 'o', color='#3b82f6', alpha=0.35, markersize=3.5, label='Individual Weigh-in')
ax.plot(daily_df['date'], daily_df['weight_30d_avg'], color='#1d4ed8', linewidth=2.5, label='30-Day Rolling Trend')

# Formatting
ax.set_title('Renpho Health: Complete Weight Journey (2019 - Present)', fontsize=15, fontweight='bold', pad=15)
ax.set_ylabel('Weight (lbs)', fontsize=12, fontweight='semibold')
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
ax.xaxis.set_minor_locator(mdates.MonthLocator(interval=3))
ax.grid(True, linestyle='--', alpha=0.5)

# Annotate all-time high and all-time low
max_row = clean_weight.loc[clean_weight['weight_lbs'].idxmax()]
min_row = clean_weight.loc[clean_weight['weight_lbs'].idxmin()]

ax.annotate(f'Peak: {max_row["weight_lbs"]} lbs\n({max_row["datetime"].strftime("%b %Y")})',
            xy=(max_row['datetime'], max_row['weight_lbs']),
            xytext=(max_row['datetime'], max_row['weight_lbs'] + 12),
            arrowprops=dict(facecolor='#ef4444', shrink=0.08, width=1.5, headwidth=7),
            fontsize=10, fontweight='bold', color='#b91c1c', ha='center')

ax.annotate(f'Lowest / Current: {min_row["weight_lbs"]} lbs\n({min_row["datetime"].strftime("%b %d, %Y")})',
            xy=(min_row['datetime'], min_row['weight_lbs']),
            xytext=(min_row['datetime'], min_row['weight_lbs'] + 22),
            arrowprops=dict(facecolor='#10b981', shrink=0.08, width=1.5, headwidth=7),
            fontsize=10, fontweight='bold', color='#047857', ha='center')

ax.legend(frameon=True, facecolor='white', framealpha=0.9, loc='upper right')
plt.tight_layout()
chart1_path = os.path.join(artifact_dir, 'all_time_weight_trend.png')
plt.savefig(chart1_path)
plt.close()

# 2. Last 12 Months Weight & Rate of Change
last_year_df = clean_weight[clean_weight['datetime'] >= (clean_weight['datetime'].max() - pd.Timedelta(days=365))].copy()
if not last_year_df.empty:
    fig, ax = plt.subplots(figsize=(12, 5), dpi=fig_dpi)
    ax.plot(last_year_df['datetime'], last_year_df['weight_lbs'], 'o-', color='#0284c7', markersize=4, linewidth=1.5, alpha=0.7, label='Weigh-in')
    
    # Trendline
    z = pd.Series(last_year_df['weight_lbs'].values, index=last_year_df['datetime']).rolling('14D', min_periods=1).mean()
    ax.plot(last_year_df['datetime'], z, color='#0369a1', linewidth=2.5, label='14-Day Rolling Avg')
    
    ax.set_title('Past 12 Months Progress & Trend', fontsize=14, fontweight='bold', pad=12)
    ax.set_ylabel('Weight (lbs)', fontsize=11, fontweight='semibold')
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend(loc='upper right')
    plt.tight_layout()
    chart2_path = os.path.join(artifact_dir, 'past_year_trend.png')
    plt.savefig(chart2_path)
    plt.close()

print("Charts successfully generated in artifact directory!")
