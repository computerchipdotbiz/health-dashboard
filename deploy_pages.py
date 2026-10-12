import os
import shutil
import subprocess
import re

DIR = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(DIR, "public")
os.makedirs(public_dir, exist_ok=True)

import sys

# Ensure UTF-8 output on Windows
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Copy core files
for src, dst in [("index.html", "index.html"), ("dashboard.html", "dashboard.html"), ("dashboard_data.json", "dashboard_data.json")]:
    src_path = os.path.join(DIR, src)
    if os.path.exists(src_path):
        shutil.copy2(src_path, os.path.join(public_dir, dst))

# Copy archived weekly reports directory
reports_src = os.path.join(DIR, "reports")
reports_dst = os.path.join(public_dir, "reports")
if os.path.exists(reports_src):
    os.makedirs(reports_dst, exist_ok=True)
    for f in os.listdir(reports_src):
        if f.endswith(".html"):
            shutil.copy2(os.path.join(reports_src, f), os.path.join(reports_dst, f))

# Sync wrangler config to ensure wrangler has valid OAuth credentials
home_wrangler = os.path.join(os.path.expanduser("~"), ".wrangler", "config")
os.makedirs(home_wrangler, exist_ok=True)
home_toml = os.path.join(home_wrangler, "default.toml")

xdg_toml = r"C:\Users\DigitalArthas\AppData\Roaming\xdg.config\.wrangler\config\default.toml"
if not os.path.exists(home_toml) and os.path.exists(xdg_toml):
    shutil.copy2(xdg_toml, home_toml)
elif os.path.exists(home_toml) and os.path.exists(xdg_toml):
    # sync if one is newer
    if os.path.getmtime(home_toml) > os.path.getmtime(xdg_toml):
        shutil.copy2(home_toml, xdg_toml)
    elif os.path.getmtime(xdg_toml) > os.path.getmtime(home_toml):
        shutil.copy2(xdg_toml, home_toml)

cmd = ["npx.cmd", "wrangler", "pages", "deploy", public_dir, "--project-name", "fit-chipgowan", "--commit-dirty=true"]
print("Deploying fit-chipgowan to Cloudflare Pages...")
res = subprocess.run(cmd, cwd=DIR, capture_output=True, text=True, encoding="utf-8", errors="replace")
if res.returncode == 0:
    print("Deployed fit-chipgowan successfully!")
    print(res.stdout)
else:
    print("Deploy error (exit code", res.returncode, "):")
    if res.stdout:
        print(res.stdout)
    if res.stderr:
        print(res.stderr)
    sys.exit(res.returncode)
