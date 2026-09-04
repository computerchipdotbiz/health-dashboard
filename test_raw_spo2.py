from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

creds = Credentials.from_authorized_user_file('token.json')
service = build('fitness', 'v1', credentials=creds)

src_id = 'raw:com.google.oxygen_saturation:com.renpho.health:health_platform'
start_time = int(datetime.datetime(2026, 8, 20).timestamp() * 1e9)
end_time = int(datetime.datetime.now().timestamp() * 1e9)
dataset_id = f"{start_time}-{end_time}"

ds = service.users().dataSources().datasets().get(
    userId='me',
    dataSourceId=src_id,
    datasetId=dataset_id
).execute()

points = ds.get('point', [])
print("Renpho SpO2 Raw Points:", len(points))
if points:
    print("Sample Point 0 values:", points[0].get('value'))
    print("Sample Point 1 values:", points[1].get('value'))
