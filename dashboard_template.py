# Builder module
import json
import os

workspace_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(workspace_dir, 'dashboard_data.json')

with open(json_path, 'r', encoding='utf-8') as f_in:
    data = json.load(f_in)

weights_json = json.dumps(data['weights'])
avg_steps = data.get('avg_45d_steps', 4226)
weekly = data.get('weekly_stats', {})
anomalies = data.get('anomalies', [])
past_reports = data.get('past_reports', [])

reports_json = json.dumps(past_reports)
anomalies_json = json.dumps(anomalies)

