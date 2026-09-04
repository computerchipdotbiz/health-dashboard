import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

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

with open('credentials.json', 'r', encoding='utf-8-sig') as f:
    client_config = json.load(f)

flow = InstalledAppFlow.from_client_config(client_config, ALL_SCOPES)
creds = flow.run_local_server(
    port=8088,
    prompt='consent',
    timeout_seconds=300,
    open_browser=True
)

with open('token.json', 'w', encoding='utf-8') as token:
    token.write(creds.to_json())

print("SUCCESS: token.json created with all permissions!")
