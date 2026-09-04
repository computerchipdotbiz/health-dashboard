import json
import os
import urllib.request
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler

with open('credentials.json', 'r', encoding='utf-8-sig') as f:
    client_config = json.load(f)

installed = client_config.get('installed', client_config.get('web', {}))
client_id = installed['client_id']
client_secret = installed['client_secret']
token_uri = installed.get('token_uri', 'https://oauth2.googleapis.com/token')

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

params = {
    'client_id': client_id,
    'redirect_uri': 'http://localhost:8088/',
    'response_type': 'code',
    'scope': ' '.join(ALL_SCOPES),
    'access_type': 'offline',
    'prompt': 'consent'
}

auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urllib.parse.urlencode(params)
print("\n" + "="*70)
print("AUTH_URL:" + auth_url)
print("="*70 + "\n")

class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)
        
        if 'code' in qs:
            code = qs['code'][0]
            # Exchange code for tokens
            post_data = urllib.parse.urlencode({
                'code': code,
                'client_id': client_id,
                'client_secret': client_secret,
                'redirect_uri': 'http://localhost:8088/',
                'grant_type': 'authorization_code'
            }).encode('utf-8')
            
            try:
                req = urllib.request.Request(token_uri, data=post_data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
                with urllib.request.urlopen(req) as response:
                    token_data = json.loads(response.read().decode('utf-8'))
                    
                # Format into google-auth Credentials structure
                token_data['client_id'] = client_id
                token_data['client_secret'] = client_secret
                token_data['scopes'] = ALL_SCOPES
                
                with open('token.json', 'w', encoding='utf-8') as f:
                    json.dump(token_data, f, indent=2)
                    
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(b"<html><body style='font-family:sans-serif;text-align:center;padding:50px;'><h1>&#9989; Successfully Connected!</h1><p>All Google Fit permissions granted. You can close this tab now.</p></body></html>")
                print("\n[SUCCESS] token.json written with ALL scopes!")
            except Exception as e:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(f"Error exchanging token: {e}".encode('utf-8'))
                print("Error exchanging token:", e)
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No code parameter found.")

httpd = HTTPServer(('localhost', 8088), OAuthHandler)
print("Listening on http://localhost:8088/ for authorization...")
httpd.handle_request() # Wait for single auth request
