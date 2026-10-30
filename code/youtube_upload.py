"""Upload a video to YouTube (PRIVATE by default, AI content disclosed).
Usage: python3 youtube_upload.py <video.mp4> "<title>" "<description>" [tags,comma,separated] [thumbnail.jpg]
Needs keys/yt_token.json (made once with yt_auth.py on your Mac)."""
import sys, os
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
H = os.path.dirname(os.path.abspath(__file__))
creds = Credentials.from_authorized_user_file(f"{H}/yt_token.json", ["https://www.googleapis.com/auth/youtube.upload"])
yt = build("youtube", "v3", credentials=creds)
video, title, desc = sys.argv[1], sys.argv[2], sys.argv[3]
tags = sys.argv[4].split(",") if len(sys.argv) > 4 else []
body = {"snippet": {"title": title[:100], "description": desc, "tags": tags, "categoryId": "28"},  # 28 = Science & Technology
        "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False, "containsSyntheticMedia": True}}
r = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(video, chunksize=8 << 20, resumable=True))
resp = None
while resp is None:
    st, resp = r.next_chunk()
    if st: print(f"uploaded {int(st.progress() * 100)}%", flush=True)
vid = resp["id"]; print("VIDEO ID:", vid, "-> https://youtu.be/" + vid, "(private)")
if len(sys.argv) > 5:
    yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(sys.argv[5])).execute(); print("thumbnail set")
