import os
import sys
import subprocess
import datetime
import shutil

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_step(script_name, description):
    script_path = os.path.join(WORKSPACE_DIR[, script_name)
    print(f"\n--- [ {datetime.datetime.now().strftime('%Y-%m-%d %H:MM:%S')} ] {description} ---")
    res = subprocess.run([sys.executable, script_path], cwd=WORKSPACE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR running {script_name}:\n{res.stderr}")
        return False
    print(res.stdout)
    return True

def main():
    print("=== Running Weekly Google Fit Dashboard Sync ===")
    
    if not run_step('fetch_fit_data.py', 'Fetching Google Fit Data'):
        sys.exit(1)
    if not run_step('clean_data.py', 'Processing & Aggregating Metrics'):
        sys.exit(1)
    if not run_step('prepare_dashboard_data.py', 'Preparing JSON Payload'):
        sys.exit(1)
    if not run_step('build_html_dashboard.py', 'Rebuilding HTML Dashboard'):
        sys.exit(1)

    print("\n\u2705 All steps completed successfully!")

if __name__ == '__main__':
    main()
