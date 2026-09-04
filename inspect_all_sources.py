import json
import os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

creds = Credentials.from_authorized_user_file('token.json')
service = build('fitness', 'v1', credentials=creds)

datasources = service.users().dataSources().list(userId='me').execute()
sources = datasources.get('dataSource', [])

print(f"Total Data Sources: {len(sources)}\n")

by_type = {}
devices = set()

for src in sources:
    dt = src.get('dataType', {}).get('name', 'unknown')
    app = src.get('application', {}).get('name') or src.get('application', {}).get('packageName', 'unknown')
    device = src.get('device', {}).get('model', 'unknown')
    
    if dt not in by_type:
        by_type[dt] = []
    by_type[dt].append({'app': app, 'device': device, 'stream': src.get('dataStreamId')})
    if device != 'unknown':
        devices.add(f"{src.get('device', {}).get('manufacturer', '')} {device}".strip())

print("=== Available Data Types & Connected Apps/Devices ===")
for dt, items in sorted(by_type.items()):
    apps = list(set(i['app'] for i in items))
    devs = list(set(i['device'] for i in items if i['device'] != 'unknown'))
    print(f"\n[DATA TYPE] {dt}")
    print(f"   Streams count: {len(items)}")
    print(f"   Apps: {', '.join(apps)}")
    if devs:
        print(f"   Devices: {', '.join(devs)}")

print("\n=== Connected Devices Detected ===")
for d in sorted(devices):
    print(f"  - {d}")

