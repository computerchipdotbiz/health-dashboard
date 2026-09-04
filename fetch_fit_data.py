import os
import json
import datetime
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
]

def get_fitness_service():
    creds = None
    token_path = 'token.json'
    cred_path = 'credentials.json'
    
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            with open(cred_path, 'r', encoding='utf-8-sig') as f:
                client_config = json.load(f)
            flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
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
    print("Authentication successful!")
    
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
    }
    
    for src in sources:
        dt_name = src.get('dataType', {}).get('name')
        src_id = src.get('dataStreamId')
        app = src.get('application', {}).get('name', 'unknown')
        
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
                    dt = datetime.datetime.fromtimestamp(start_ns / 1e9)
                    
                    val = None
                    for v in pt.get('value', []):
                        if 'fpVal' in v:
                            val = v['fpVal']
                        elif 'intVal' in v:
                            val = v['intVal']
                    
                    if val is not None:
                        records.append({
                            'datetime': dt.strftime('%Y-%m-%d %H:%M:%S'),
                            'date': dt.strftime('%Y-%m-%d'),
                            'metric': metric_label,
                            'data_type': dt_name,
                            'value': val,
                            'source_app': app,
                            'stream_id': src_id
                        })
            except Exception as e:
                print(f"Error fetching from {src_id}: {e}")
                
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
