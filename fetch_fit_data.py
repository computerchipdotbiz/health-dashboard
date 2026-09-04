import os
import json
import datetime
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

ALL_SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.body_temperature.read',
    'https://www.googleapis.com/auth/fitness.blood_glucose.read',
    'https://www.googleapis.com/auth/fitness.blood_pressure.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    'https://www.googleapis.com/auth/fitness.oxygen_saturation.read',
    'https://www.googleapis.com/auth/fitness.reproductive_health.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
]

def get_fitness_service():
    creds = None
    token_path = 'token.json'
    cred_path = 'credentials.json'
    
    if os.path.exists(token_path):
        try:
            creds = Credentials.from_authorized_user_file(token_path, ALL_SCOPES)
        except Exception:
            creds = None
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None
        if not creds or not creds.valid:
            with open(cred_path, 'r', encoding='utf-8-sig') as f:
                client_config = json.load(f)
            flow = InstalledAppFlow.from_client_config(client_config, ALL_SCOPES)
            creds = flow.run_local_server(
                port=8088,
                prompt='consent',
                authorization_prompt_message="\n" + "="*70 + "\nAUTH_URL_START:{url}:AUTH_URL_END\n" + "="*70 + "\n",
                open_browser=True
            )
            
        with open(token_path, 'w', encoding='utf-8') as token:
            token.write(creds.to_json())
            
    return build('fitness', 'v1', credentials=creds)

def fetch_data():
    service = get_fitness_service()
    print("Authentication successful with all scopes!")
    
    datasources = service.users().dataSources().list(userId='me').execute()
    sources = datasources.get('dataSource', [])
    print(f"Discovered {len(sources)} data source(s).")
    
    start_time = int(datetime.datetime(2018, 1, 1).timestamp() * 1e9)
    end_time = int(datetime.datetime.now().timestamp() * 1e9)
    dataset_id = f"{start_time}-{end_time}"
    
    records = []
    
    target_types = {
        'com.google.weight': 'weight_kg',
        'com.google.body.fat.percentage': 'body_fat_pct',
        'com.google.height': 'height_m',
        'com.google.heart_rate.bpm': 'heart_rate_bpm',
        'com.google.step_count.delta': 'steps',
        'com.google.sleep.segment': 'sleep_stage',
        'com.google.oxygen_saturation': 'oxygen_saturation_pct',
        'com.google.body.temperature': 'body_temperature_c',
        'com.google.calories.expended': 'calories_burned',
        'com.google.active_minutes': 'active_minutes',
        'com.google.heart_minutes': 'heart_points',
    }
    
    for src in sources:
        dt_name = src.get('dataType', {}).get('name')
        src_id = src.get('dataStreamId')
        app = src.get('application', {}).get('name') or src.get('application', {}).get('packageName', 'unknown')
        
        if dt_name in target_types:
            metric_label = target_types[dt_name]
            try:
                ds = service.users().dataSources().datasets().get(
                    userId='me',
                    dataSourceId=src_id,
                    datasetId=dataset_id
                ).execute()
                
                points = ds.get('point', [])
                if points:
                    print(f"-> Found {len(points)} points for {metric_label} ({dt_name}) from source: {app}")
                for pt in points:
                    start_ns = int(pt.get('startTimeNanos', 0))
                    end_ns = int(pt.get('endTimeNanos', start_ns))
                    dt = datetime.datetime.fromtimestamp(start_ns / 1e9)
                    
                    val = None
                    vals_list = pt.get('value', [])
                    # Extract primary value (fpVal or intVal)
                    for v in vals_list:
                        if 'fpVal' in v:
                            val = v['fpVal']
                            break
                        elif 'intVal' in v:
                            val = v['intVal']
                            break
                    
                    if val is not None:
                        # For sleep segments, duration is important
                        dur_mins = round((end_ns - start_ns) / (1e9 * 60.0), 2)
                        records.append({
                            'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                            'date': dt.strftime('%Y-%m-%d'),
                            'metric': metric_label,
                            'data_type': dt_name,
                            'value': val,
                            'duration_mins': dur_mins,
                            'source_app': app,
                            'stream_id': src_id
                        })
            except Exception as e:
                print(f"Error fetching from {src_id}: {e}")
                
    # Fetch Sessions (Sleep, Workouts, etc.)
    try:
        sessions_res = service.users().sessions().list(userId='me').execute()
        sessions = sessions_res.get('session', [])
        print(f"Fetched {len(sessions)} session(s).")
        for s in sessions:
            st_ms = int(s.get('startTimeMillis', 0))
            et_ms = int(s.get('endTimeMillis', 0))
            dur_hrs = round((et_ms - st_ms) / (1000.0 * 3600.0), 2)
            dt = datetime.datetime.fromtimestamp(st_ms / 1000.0)
            act_type = s.get('activityType', 0)
            act_name = s.get('name', 'Workout')
            
            metric_type = 'sleep_hours' if act_type == 72 or 'sleep' in act_name.lower() else 'workout_session'
            records.append({
                'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                'date': dt.strftime('%Y-%m-%d'),
                'metric': metric_type,
                'data_type': f"session_{act_type}",
                'value': dur_hrs,
                'duration_mins': round(dur_hrs * 60, 1),
                'source_app': s.get('application', {}).get('name') or s.get('application', {}).get('packageName', 'unknown'),
                'stream_id': s.get('id', 'session')
            })
    except Exception as e:
        print(f"Error fetching sessions: {e}")
                
    df = pd.DataFrame(records)
    if not df.empty:
        weight_rows = df[df['metric'] == 'weight_kg'].copy()
        if not weight_rows.empty:
            weight_rows['metric'] = 'weight_lbs'
            weight_rows['value'] = (weight_rows['value'] * 2.20462).round(2)
            df = pd.concat([df, weight_rows], ignore_index=True)
            
        df.to_csv('fit_health_data.csv', index=False)
        print(f"\nSuccessfully saved {len(df)} records to fit_health_data.csv!")
        
        summary = df.groupby(['metric', 'source_app']).size().reset_index(name='count')
        print("\nData Summary:")
        print(summary.to_string(index=False))
    else:
        print("\nNo records found in the specified data sources.")

if __name__ == '__main__':
    fetch_data()
