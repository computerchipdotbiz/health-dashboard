import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
service = build('fitness', 'v1', credentials=creds)

# 1. Check sessions (Sleep in Google Fit is stored as activityType 72 in Sessions)
try:
    sessions = service.users().sessions().list(userId='me').execute()
    session_list = sessions.get('session', [])
    print(f"Total Logged Sessions: {len(session_list)}")
    
    sleep_sessions = [s for s in session_list if s.get('activityType') == 72 or 'sleep' in s.get('name', '').lower()]
    print(f"Sleep Sessions Found: {len(sleep_sessions)}")
    if sleep_sessions:
        for s in sleep_sessions[-5:]:
            print(f"  - Sleep Session: {s.get('name')} | App: {s.get('application', {}).get('name') or s.get('application', {}).get('packageName')}")
except Exception as e:
    print("Error querying sessions:", e)

# 2. Check for HRV data sources or heart rate variability data types
datasources = service.users().dataSources().list(userId='me').execute()
sources = datasources.get('dataSource', [])

hrv_sources = [s for s in sources if 'variability' in s.get('dataType', {}).get('name', '').lower() or 'rmssd' in s.get('dataType', {}).get('name', '').lower() or 'hrv' in s.get('dataStreamId', '').lower()]
sleep_sources = [s for s in sources if 'sleep' in s.get('dataType', {}).get('name', '').lower() or 'sleep' in s.get('dataStreamId', '').lower()]

print(f"\nHRV Data Sources: {len(hrv_sources)}")
for s in hrv_sources:
    print(f"  - {s.get('dataType', {}).get('name')} | {s.get('dataStreamId')}")

print(f"\nSleep Data Sources: {len(sleep_sources)}")
for s in sleep_sources:
    print(f"  - {s.get('dataType', {}).get('name')} | {s.get('dataStreamId')}")

