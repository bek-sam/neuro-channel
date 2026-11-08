"""MCP server for the free video pipeline: Claude writes the scenes, this starts the render on free GPUs.

Local (Claude Code / Claude Desktop, stdio):
    python server/mcp_server.py
Cloud (any host: Hugging Face Space, Oracle Always Free VM, Modal...), streamable HTTP:
    python server/mcp_server.py --http --port 7860
    connector URL: https://<host>/<MCP_TOKEN>/mcp   (or https://<host>/mcp with "Authorization: Bearer <MCP_TOKEN>")

Env: HF_TOKEN (write access to HF_REPO), HF_REPO (dataset that holds scripts, state and videos),
     GH_DISPATCH_TOKEN + GH_REPO (optional: a fine-grained token with Actions read/write on the repo, so a new video
     starts at once; without it the video is queued and the 6-hourly cron starts it), MCP_TOKEN (required for --http).
The render itself runs in GitHub Actions (.github/workflows/video.yml -> code/free/run.py) on Kaggle, ZeroGPU and edge-tts.
"""
import os, re, sys, json, hmac, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if os.path.exists(f"{ROOT}/keys/keys.env"):  # local run: same keys file as the pipeline
    for l in open(f"{ROOT}/keys/keys.env"):
        if "=" in l and not l.startswith("#"):
            k, v = l.strip().split("=", 1); os.environ.setdefault(k, v.strip("'\""))

from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings
from huggingface_hub import HfApi, hf_hub_download

REPO = os.environ.get("HF_REPO") or "bekbol446/neuro-channel"
GH_REPO = os.environ.get("GH_REPO") or "bek-sam/neuro-channel"
VOICES = ["edge", "qwen3tts"]
GUIDE = """How to write scenes for this pipeline.

A video is a list of scenes. Each scene is one narration line over one picture:
  {"text": "...", "prompt": "...", "motion": "...", "hero": true}
- text: what the narrator says, 1-3 short spoken sentences (about 6-15 s). Write numbers the way they are spoken.
- prompt: the image to draw for that line. Concrete subject, setting, light, camera. End every prompt with the same
  style words so the whole video matches, e.g. "cinematic, dark background, bioluminescent blue and warm gold light,
  ultra detailed, 16:9, no text". Never ask for text or letters in the image.
- motion: how the picture moves, e.g. "slow push in", "signals racing along the fibers", "camera orbits the brain".
- hero (optional): true for the shots that most deserve a real motion clip (Wan2.2). The rest get a slow camera move.
  About 1 hero per 2-3 scenes. Free ZeroGPU clips are about 5 a day; after that clips come from the Modal free credit
  and then Muapi (paid), each up to its monthly cap, and the rest wait for the next day's free quota.

Good videos: a hook in the first scene, one idea per scene, 20-60 scenes for 4-12 minutes.
Output: 1920x1080 MP4 with narration, music bed, burned-in subtitles, plus a thumbnail when thumb_title is set.
"""


def hf(): return HfApi(token=os.environ["HF_TOKEN"])


def read(path):
    return json.load(open(hf_hub_download(REPO, path, repo_type="dataset", token=os.environ["HF_TOKEN"], force_download=True)))


def put(obj, path):
    hf().upload_file(path_or_fileobj=json.dumps(obj, indent=1, ensure_ascii=False).encode(), path_in_repo=path,
                     repo_id=REPO, repo_type="dataset", commit_message=f"mcp: {path}")


def dispatch(project, args):
    """Starts the GitHub Actions workflow now. Returns None on success, or why it could not."""
    tok = os.environ.get("GH_DISPATCH_TOKEN")
    if not tok: return "no GH_DISPATCH_TOKEN"
    import urllib.request
    req = urllib.request.Request(f"https://api.github.com/repos/{GH_REPO}/actions/workflows/video.yml/dispatches", method="POST",
                                 data=json.dumps({"ref": "main", "inputs": {"project": project, "args": args}}).encode(),
                                 headers={"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json",
                                          "User-Agent": "neuro-channel-mcp"})
    try: urllib.request.urlopen(req, timeout=20); return None
    except Exception as e: return f"dispatch failed: {str(e)[:200]}"


mcp = FastMCP("free-video-generator", stateless_http=True,  # the token check below guards HTTP; any host name
              transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))


@mcp.tool()
def how_to_write_scenes() -> str:
    """Read this before create_video: the scene format and what makes a good script for this pipeline."""
    return GUIDE


@mcp.tool()
def create_video(project: str, scenes: list[dict], title: str = "", thumb_title: str = "",
                 voice: str = "edge", heroes: int = 15) -> dict:
    """Save a script and start rendering it on free GPUs (Kaggle images, ZeroGPU Wan2.2 clips, edge-tts voice).
    project: short id, lower-case letters, digits, '-' or '_' (e.g. "dopamine-scroll").
    scenes: [{"text": narration, "prompt": image prompt, "motion": camera move, "hero": optional bool}], see how_to_write_scenes.
    voice: "edge" (fast, default) or "qwen3tts". heroes: max scenes that get a real motion clip.
    Then poll get_status(project). Images take about 1-2 h; motion clips are added as the free quota allows."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{1,60}", project): raise ValueError("project: lower-case letters, digits, '-' or '_'")
    if voice not in VOICES: raise ValueError(f"voice must be one of {VOICES}")
    if not scenes or not all(isinstance(s, dict) and s.get("text") and s.get("prompt") for s in scenes):
        raise ValueError("every scene needs 'text' and 'prompt'")
    try:
        st = read(f"work/{project}/status.json")
        if st.get("state") not in ("done", "failed") and not st["state"].startswith("waiting") and st["state"] != "queued":
            raise ValueError(f"project '{project}' is running ({st['state']}); pick another name")
    except ValueError: raise
    except Exception: pass
    clean = [{k: s[k] for k in ("text", "prompt", "motion", "hero") if k in s} for s in scenes]
    meta = {k: v for k, v in dict(title=title, thumb_title=thumb_title).items() if v}
    args = ["--voice", voice, "--heroes", str(int(heroes))]
    put(clean, f"work/{project}/scenes.json"); put(meta, f"work/{project}/meta.json")
    put({"state": "queued", "args": args, "attempts": 0, "scenes": len(clean)}, f"work/{project}/status.json")
    why = dispatch(project, " ".join(args))
    return {"project": project, "scenes": len(clean),
            "started": why is None,
            "note": "rendering started in GitHub Actions" if why is None else
                    f"queued ({why}); the cron starts it within 6 hours",
            "runs": f"https://github.com/{GH_REPO}/actions/workflows/video.yml"}


@mcp.tool()
def get_status(project: str) -> dict:
    """Progress of one video: state (queued, starting, images, waiting..., done, failed), minutes, scenes, clips."""
    try: st = read(f"work/{project}/status.json")
    except Exception: return {"project": project, "state": "unknown (no such project)"}
    return {k: v for k, v in st.items() if k not in ("items",)}


@mcp.tool()
def list_videos() -> dict:
    """Every project in the dataset and which ones have a finished video."""
    files = hf().list_repo_files(REPO, repo_type="dataset")
    work = sorted({f.split("/")[1] for f in files if f.startswith("work/") and f.count("/") >= 2})
    done = sorted({f.split("/")[1] for f in files if f.startswith("videos/") and f.endswith("/final.mp4")})
    return {"projects": work, "finished": done}


@mcp.tool()
def get_video(project: str, download: bool = False) -> dict:
    """Links to the finished video and thumbnail. download=true (local server only) saves them to ~/Downloads/<project>/."""
    base = f"videos/{project}"
    files = [f for f in hf().list_repo_files(REPO, repo_type="dataset") if f.startswith(base + "/")]
    if f"{base}/final.mp4" not in files: return {"project": project, "ready": False, "hint": "check get_status"}
    out = {"project": project, "ready": True,
           "links": {os.path.basename(f): f"https://huggingface.co/datasets/{REPO}/resolve/main/{f}" for f in files}}
    if download:
        if os.environ.get("MCP_HTTP"): return {**out, "download": "only when the server runs on your machine"}
        dest = os.path.expanduser(f"~/Downloads/{project}"); os.makedirs(dest, exist_ok=True)
        for f in files:
            hf_hub_download(REPO, f, repo_type="dataset", token=os.environ["HF_TOKEN"], local_dir=dest + "/_hf")
            os.replace(f"{dest}/_hf/{f}", f"{dest}/{os.path.basename(f)}")
        import shutil; shutil.rmtree(dest + "/_hf", ignore_errors=True)
        out["saved_to"] = dest
    return out


def http_app():
    """Streamable HTTP app behind MCP_TOKEN: /<token>/mcp, or /mcp with a Bearer header. /health is open."""
    token = os.environ.get("MCP_TOKEN", "")
    if len(token) < 24: sys.exit("set MCP_TOKEN (24+ random characters) before serving over HTTP")
    inner, prefix = mcp.streamable_http_app(), "/" + token

    async def app(scope, receive, send):
        if scope["type"] == "http":
            path = scope["path"]
            if path == "/health":
                await send({"type": "http.response.start", "status": 200, "headers": [(b"content-type", b"application/json")]})
                return await send({"type": "http.response.body", "body": b'{"ok":true}'})
            auth = dict(scope.get("headers") or []).get(b"authorization", b"").decode()
            if path.startswith(prefix + "/") and hmac.compare_digest(path[:len(prefix)], prefix):
                scope = dict(scope, path=path[len(prefix):], raw_path=None)
            elif not hmac.compare_digest(auth, f"Bearer {token}"):
                await send({"type": "http.response.start", "status": 404, "headers": []})
                return await send({"type": "http.response.body", "body": b"not found"})
        await inner(scope, receive, send)
    return app


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--http", action="store_true", help="serve over streamable HTTP instead of stdio")
    ap.add_argument("--host", default="0.0.0.0"); ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", 7860)))
    a = ap.parse_args()
    if not os.environ.get("HF_TOKEN"): sys.exit("set HF_TOKEN (keys/keys.env locally, a secret in the cloud)")
    if a.http:
        os.environ["MCP_HTTP"] = "1"
        import uvicorn; uvicorn.run(http_app(), host=a.host, port=a.port, log_level="info")
    else:
        mcp.run()
