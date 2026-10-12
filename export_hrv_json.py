import json
import numpy as np
import pandas as pd

def generate_export():
    df = pd.read_csv('fit_health_data.csv', low_memory=False)
    df['datetime'] = pd.to_datetime(df['datetime'])

    # Filter raw renpho stream
    raw_hr = df[df['stream_id'] == 'raw:com.google.heart_rate.bpm:com.renpho.health:health_platform'].copy()
    raw_hr = raw_hr.sort_values('datetime').reset_index(drop=True)

    # Also get Google Fit resting HR stream for comparison
    rhr_stream = df[df['stream_id'] == 'derived:com.google.heart_rate.bpm:com.google.android.gms:resting_heart_rate<-merge_heart_rate_bpm'].copy()
    rhr_stream['date_str'] = pd.to_datetime(rhr_stream['date']).dt.strftime('%Y-%m-%d')
    gfit_rhr_by_date = rhr_stream.groupby('date_str')['value'].agg(['mean', 'min']).to_dict(orient='index')

    # Also get SpO2 for correlation
    spo2 = df[(df['metric'] == 'oxygen_saturation_pct') & (df['source_app'] == 'com.renpho.health')].copy()
    spo2_daily = spo2.groupby('date')['value'].agg(['mean', 'min']).to_dict(orient='index')

    daily_list = []
    telemetry_list = []

    for d, group in raw_hr.groupby('date'):
        vals = group['value'].values
        
        night = group[(group['datetime'].dt.hour < 8) | (group['datetime'].dt.hour >= 22)]
        day = group[(group['datetime'].dt.hour >= 8) & (group['datetime'].dt.hour < 22)]
        
        diffs = np.diff(vals)
        rmssd = float(np.sqrt(np.mean(diffs**2))) if len(diffs) > 0 else None
        
        day_avg = round(float(day['value'].mean()), 1) if not day.empty else None
        night_avg = round(float(night['value'].mean()), 1) if not night.empty else None
        circadian_dip = round(((day_avg - night_avg) / day_avg) * 100, 1) if (day_avg and night_avg) else None
        
        sp_info = spo2_daily.get(d, {})
        spo2_avg = round(float(sp_info.get('mean')), 1) if sp_info.get('mean') is not None else None
        spo2_min = round(float(sp_info.get('min')), 1) if sp_info.get('min') is not None else None
        
        gfit_rhr = gfit_rhr_by_date.get(d, {})
        gfit_rhr_val = round(float(gfit_rhr.get('mean')), 1) if gfit_rhr.get('mean') is not None else None
        
        daily_list.append({
            'date': str(d),
            'readings_count': int(len(vals)),
            'resting_heart_rate_bpm': float(np.min(vals)),
            'average_heart_rate_bpm': round(float(np.mean(vals)), 1),
            'peak_heart_rate_bpm': float(np.max(vals)),
            'hr_variability_std_bpm': round(float(np.std(vals)), 2),
            'inter_sample_rmssd_bpm': round(rmssd, 2) if rmssd else None,
            'daytime_avg_bpm': day_avg,
            'nighttime_avg_bpm': night_avg,
            'circadian_dip_pct': circadian_dip,
            'google_fit_resting_hr_avg': gfit_rhr_val,
            'spo2_avg_pct': spo2_avg,
            'spo2_min_pct': spo2_min
        })
        
        for _, row in group.iterrows():
            hour = row['datetime'].hour
            period = 'Night' if (hour < 8 or hour >= 22) else 'Day'
            telemetry_list.append({
                'timestamp': row['datetime'].strftime('%Y-%m-%d %H:%M:%S'),
                'heart_rate_bpm': float(row['value']),
                'period': period,
                'source': 'Renpho Smart Ring'
            })

    output_data = {
        'title': 'Heart Rate & Heart Rate Variability Telemetry Report',
        'subject': 'Chip Gowan',
        'period': 'Past 3 Months (2026-07-08 to 2026-10-08)',
        'tracking_device': 'Renpho Smart Ring',
        'data_pipeline': 'Renpho Health -> Google Fit / Health Connect API',
        'telemetry_overview': {
            'total_readings': len(telemetry_list),
            'active_monitoring_days': len(daily_list),
            'date_range': f"{daily_list[0]['date']} to {daily_list[-1]['date']}",
            'sampling_cadence': 'Continuous 10-minute interval telemetry (~144 samples/day)',
            'overall_mean_bpm': round(float(np.mean(raw_hr['value'])), 1),
            'overall_resting_nadir_bpm': float(np.min(raw_hr['value'])),
            'overall_peak_active_bpm': float(np.max(raw_hr['value'])),
            'overall_variability_std_bpm': round(float(np.std(raw_hr['value'])), 2),
            'metric_methodology_note': (
                'Renpho Smart Ring syncs continuous 10-minute heart rate (BPM), SpO2, and sleep stages into Google Fit. '
                'Millisecond-level beat-to-beat rMSSD is processed internally by the Renpho Health mobile app and is not '
                'exported via the Google Fit REST API. This dataset includes continuous time-series HR, inter-sample RMSSD '
                'fluctuation proxies, time-domain standard deviation (SDRR), day vs. night circadian dipping, and overnight '
                'resting heart rate nadir (52.0 BPM recovery low).'
            )
        },
        'daily_metrics': daily_list,
        'granular_telemetry': telemetry_list
    }

    with open('hrv_heart_data_past_3_months.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    summary_data = {
        'title': output_data['title'],
        'subject': output_data['subject'],
        'period': output_data['period'],
        'tracking_device': output_data['tracking_device'],
        'data_pipeline': output_data['data_pipeline'],
        'telemetry_overview': output_data['telemetry_overview'],
        'daily_metrics': output_data['daily_metrics']
    }

    with open('hrv_daily_summary_past_3_months.json', 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, indent=2)

    print(f"Export finished successfully!")
    print(f"Full JSON: hrv_heart_data_past_3_months.json ({len(telemetry_list)} data points)")
    print(f"Summary JSON: hrv_daily_summary_past_3_months.json ({len(daily_list)} daily summaries)")

if __name__ == '__main__':
    generate_export()
