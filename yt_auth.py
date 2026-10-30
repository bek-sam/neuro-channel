# Run ONCE on your Mac:  pip3 install google-auth-oauthlib && python3 yt_auth.py
# Needs client_secret.json (Google Cloud -> YouTube Data API v3 -> OAuth client "Desktop app") in this folder.
from google_auth_oauthlib.flow import InstalledAppFlow
f = InstalledAppFlow.from_client_secrets_file("client_secret.json", ["https://www.googleapis.com/auth/youtube.upload"])
open("yt_token.json", "w").write(f.run_local_server(port=0).to_json()); print("saved yt_token.json")
