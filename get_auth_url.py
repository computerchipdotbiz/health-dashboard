import json
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

flow = InstalledAppFlow.from_client_config(client_config, ALL_SCOPES, redirect_uri='http://localhost:8088/')
auth_url, _ = flow.authorization_url(prompt='consent', access_type='offline')
print(f"AUTH_URL_START:{auth_url}:AUTH_URL_END")
