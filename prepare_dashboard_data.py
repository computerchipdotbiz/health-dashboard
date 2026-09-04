import json
import pandas as pd

clean_weight = pd.read_csv('clean_weight_history.csv')
clean_fat = pd.read_csv('clean_body_fat_history.csv')

# Prepare chart data
weight_data = []
for _, row in clean_weight.iterrows():
    weight_data.append({
        'd': row['date'],
        'dt': row['datetime'],
        'w': float(row['weight_lbs'])
    })

fat_data = []
for _, row in clean_fat.iterrows():
    fat_data.append({
        'd': row['date'],
        'dt': row['datetime'],
        'bf': float(row['body_fat_pct'])
    })

with open('dashboard_data.json', 'w') as f:
    json.dump({'weights': weight_data, 'body_fat': fat_data}, f)

print(f"Exported {len(weight_data)} weight points and {len(fat_data)} body fat points for dashboard.")
