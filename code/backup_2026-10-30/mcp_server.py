"""neuro-mcp: remote MCP server so Claude can drive neuro-pipeline. Deploy:  modal deploy gpu/mcp_server.py
Needs neuro-pipeline deployed first (it calls its `controller`). Uses the same `neuro-hf` secret.
Connector URL (paste into claude.ai -> Settings -> Connectors -> Add custom connector, or `claude mcp add`):
  https://<workspace>--neuro-mcp-serve.modal.run/<TOKEN>/mcp
  TOKEN = sha256("mcp:" + HF_TOKEN)   ->  python3 -c 'import hashlib;print(hashlib.sha256(b"mcp:"+b"<HF_TOKEN>").hexdigest())'"""
import modal, os, json

app = modal.App("neuro-mcp")
image = (modal.Image.debian_slim(python_version="3.11").pip_install("mcp>=1.13,<2", "huggingface_hub")
         .add_local_file(f"{os.path.dirname(__file__)}/models.py", "/root/models.py"))
REPO = "bekbol446/neuro-channel"
PROFILES = ["free", "standard", "max", "max_all"]


def build():
    import hashlib, hmac
    from mcp.server.fastmcp import FastMCP
    from mcp.server.transport_security import TransportSecuritySettings
    from huggingface_hub import HfApi, hf_hub_download
    tok = os.environ["HF_TOKEN"]; api = HfApi(token=tok)
    mcp = FastMCP("neuro-channel", stateless_http=True,
                  transport_security=TransportSecuritySettings(enable_dns_rebinding_protection=False))
    rd = lambda path: json.load(open(hf_hub_download(REPO, path, repo_type="dataset", token=tok, force_download=True)))
    put = lambda obj, path: api.upload_file(path_or_fileobj=json.dumps(obj, indent=1).encode(), path_in_repo=path,
                                            repo_id=REPO, repo_type="dataset")

    @mcp.tool()
    def create_video(project: str, scenes: list[dict], profile: str = "standard", budget_usd: float = 10.0,
                     title: str = "", thumb_title: str = "", thumb_visual: str = "", channel: str = "") -> dict:
        """Upload a script and start rendering a video on Modal GPUs.
        scenes: list of {"text": narration, "prompt": image prompt, "motion": camera move, optional "hero": true}.
        profile: free (stills + kokoro voice) | standard | max | max_all. budget_usd caps GPU spend.
        Returns the call id; poll get_status(project) for progress (a video takes roughly 30-120 min)."""
        if profile not in PROFILES: raise ValueError(f"profile must be one of {PROFILES}")
        if not scenes or not all(s.get("text") and s.get("prompt") for s in scenes):
            raise ValueError("every scene needs 'text' and 'prompt'")
        meta = {k: v for k, v in dict(title=title, thumb_title=thumb_title, thumb_visual=thumb_visual, channel=channel).items() if v}
        put(scenes, f"work/{project}/scenes.json"); put(meta, f"work/{project}/meta.json")
        c = modal.Function.from_name("neuro-pipeline", "controller").spawn(project, profile, float(budget_usd))
        return {"project": project, "call_id": c.object_id, "scenes": len(scenes), "profile": profile}

    @mcp.tool()
    def get_status(project: str) -> dict:
        """Progress of a video: state, cost so far, minutes elapsed, log. state == "done" means final.mp4 is ready."""
        try: return rd(f"work/{project}/status.json")
        except Exception: return {"state": "not started (no status.json yet)"}

    @mcp.tool()
    def estimate_cost(n_scenes: int, profile: str = "standard") -> dict:
        """Rough Modal cost in USD for a video with n_scenes at a profile, before starting it."""
        import sys; sys.path.insert(0, "/root")
        from models import PROFILES as PR, IMAGE, VIDEO, PRICE
        P, n = PR[profile], n_scenes  # same formula as estimate_with in modal_app3.py
        usd = (n * 2 + 1) * IMAGE[P["image"]]["sec"] / 3600 * PRICE[IMAGE[P["image"]]["gpu"]] + 0.10
        if P["hero_video"]: v = VIDEO[P["hero_video"]]; usd += min(P["heroes"], n) * v["sec"] / 3600 * PRICE[v["gpu"]]
        if P["voice"] == "chatterbox": usd += n * 20 / 3600 * PRICE["A10G"]
        return {"profile": profile, "scenes": n_scenes, "estimate_usd": round(usd, 2), "note": "standard/max may drop hero clips to fit budget_usd"}

    @mcp.tool()
    def list_projects() -> dict:
        """Projects that have work files and which of them have a finished video."""
        files = api.list_repo_files(REPO, repo_type="dataset")
        work = sorted({f.split("/")[1] for f in files if f.startswith("work/") and f.count("/") >= 2})
        done = sorted({f.split("/")[1] for f in files if f.startswith("videos/") and f.endswith("final.mp4")})
        return {"projects": work, "finished": done}

    @mcp.tool()
    def get_video(project: str) -> dict:
        """Links to the finished video and thumbnail (Hugging Face dataset; needs access to the repo)."""
        base = f"https://huggingface.co/datasets/{REPO}/resolve/main/videos/{project}"
        return {"video": f"{base}/final.mp4", "thumbnail": f"{base}/thumbnail.png"}

    inner = mcp.streamable_http_app()
    want = "/" + hashlib.sha256(b"mcp:" + tok.encode()).hexdigest()

    async def guarded(scope, receive, send):  # secret path segment: /<TOKEN>/mcp -> /mcp
        if scope["type"] == "http":
            path = scope["path"]
            if not (path == want or path.startswith(want + "/")) or not hmac.compare_digest(path[:len(want)], want):
                await send({"type": "http.response.start", "status": 404, "headers": []})
                return await send({"type": "http.response.body", "body": b"not found"})
            scope = dict(scope, path=path[len(want):] or "/", raw_path=None)
        await inner(scope, receive, send)
    return guarded


@app.function(image=image, secrets=[modal.Secret.from_name("neuro-hf")], min_containers=0, timeout=600)
@modal.concurrent(max_inputs=20)
@modal.asgi_app()
def serve():
    return build()
