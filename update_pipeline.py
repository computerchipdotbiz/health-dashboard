import os
import sys
import subprocess
import datetime
import shutil

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def run_step(script_name, description):
    script_path = os.path.join(WORKSPACE_DIR, script_name)
    print(f"\n--- [ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] {description} ---")
    res = subprocess.run([sys.executable, script_path], cwd=WORKSPACE_DIR, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"ERROR running {script_name}:\n{res.stderr}")
        return False
    print(res.stdout)
    return True

def push_to_github():
    print(f"\n--- [ {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ] Syncing to GitHub Pages ---")
    dash_path = os.path.join(WORKSPACE_DIR, 'dashboard.html')
    index_path = os.path.join(WORKSPACE_DIR, 'index.html')
    if os.path.exists(dash_path):
        shutil.copy2(dash_path, index_path)

    res = subprocess.run(['git', 'remote', 'get-url', 'origin'], cwd=WORKSPACE_DIR, capture_output=True, text=True)
    if res.returncode == 0 and res.stdout.strip():
        subprocess.run(['git', 'add', '-A'], cwd=WORKSPACE_DIR)
        now_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        subprocess.run(['git', 'commit', '-m', f'Automated sync & weekly report archive {now_str}'], cwd=WORKSPACE_DIR)
        push_res = subprocess.run(['git', 'push', 'origin', 'main'], cwd=WORKSPACE_DIR, capture_output=True, text=True)
        if push_res.returncode == 0:
            print("[SUCCESS] Pushed latest update to GitHub Pages!")
        else:
            print(f"Git push output: {push_res.stdout}\n{push_res.stderr}")
    else:
        print("[INFO] No git remote configured yet. Local files updated.")

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

    push_to_github()
    print("\n[COMPLETE] All steps completed successfully!")

if __name__ == '__main__':
    main()
