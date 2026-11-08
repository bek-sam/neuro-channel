# Run ONCE on your Mac:  pip3 install google-auth-oauthlib && python3 code/yt_auth.py
# Needs keys/client_secret.json (Google Cloud -> YouTube Data API v3 -> OAuth client "Desktop app").
# Writes keys/yt_token.json, which code/youtube_upload.py reads.
import os
from google_auth_oauthlib.flow import InstalledAppFlow
K = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "keys")
f = InstalledAppFlow.from_client_secrets_file(f"{K}/client_secret.json", ["https://www.googleapis.com/auth/youtube.upload"])
open(f"{K}/yt_token.json", "w").write(f.run_local_server(port=0).to_json()); print("saved keys/yt_token.json")
