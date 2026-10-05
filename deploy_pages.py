import os
import shutil
import subprocess
import re

DIR = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(DIR, "public")
os.makedirs(public_dir, exist_ok=True)

# Copy files
for src, dst in [("index.html", "index.html"), ("dashboard.html", "dashboard.html")]:
    src_path = os.path.join(DIR, src)
    if os.path.exists(src_path):
        shutil.copy2(src_path, os.path.join(public_dir, dst))

# Read token
toml_path = r"C:\Users\DigitalArthas\AppData\Roaming\xdg.config\.wrangler\config\default.toml"
if os.path.exists(toml_path):
    with open(toml_path, "r", encoding="utf-8") as f:
        m = re.search(r'oauth_token\s*=\s*"([^"]+)"', f.read())
        if m:
            env = os.environ.copy()
            env["CLOUDFLARE_API_TOKEN"] = m.group(1)
            env["CLOUDFLARE_ACCOUNT_ID"] = "887fdd1020fd39e806c54b28e526c6f9"
            cmd = ["npx.cmd", "wrangler", "pages", "deploy", public_dir, "--project-name", "fit-chipgowan", "--commit-dirty=true"]
            print("Deploying fit-chipgowan to Cloudflare Pages...")
            res = subprocess.run(cmd, cwd=DIR, env=env, capture_output=True, encoding="utf-8", errors="replace")
            if res.returncode == 0:
                print("Deployed fit-chipgowan successfully!")
            else:
                print("Deploy error:", res.stderr)
