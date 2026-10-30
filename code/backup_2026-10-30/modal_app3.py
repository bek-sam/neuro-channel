"""neuro-pipeline: the whole video runs inside Modal. Deploy once (from the Mac sandbox):  modal deploy gpu/modal_app3.py
Start a video from anywhere with one HTTPS call (no Mac needed):
  POST https://<workspace>--neuro-pipeline-start.modal.run   header X-Key: sha256(HF_TOKEN)
  body {"project": "...", "profile": "standard", "budget_usd": 10}
Inputs  : HF dataset work/<project>/scenes.json (+ meta.json with title/thumbnail idea)
Progress: HF dataset work/<project>/status.json      Output: HF dataset videos/<project>/final.mp4, thumbnail.png"""
import modal, os, json, time

HERE = os.path.dirname(__file__)
app = modal.App("neuro-pipeline")
code = lambda img: img.add_local_file(f"{HERE}/models.py", "/root/models.py").add_local_file(
    f"{HERE}/worker.py", "/root/worker.py").add_local_file(f"{HERE}/editor.py", "/root/editor.py")

gpu_image = code(modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg", "git")
    .pip_install("torch", "torchvision", "transformers", "accelerate", "sentencepiece", "ftfy", "imageio", "imageio-ffmpeg",
                 "pillow", "numpy", "huggingface_hub", "hf_transfer")
    .pip_install("git+https://github.com/huggingface/diffusers")
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache/hf"}))
voice_image = code(modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg")
    .pip_install("chatterbox-tts", "huggingface_hub").env({"HF_HOME": "/cache/hf"}))
edit_image = code(modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg", "fonts-dejavu-core", "curl")
    .pip_install("kokoro-onnx", "soundfile", "faster-whisper", "huggingface_hub")
    .run_commands("mkdir -p /models && cd /models && "
                  "curl -sSL -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx && "
                  "curl -sSL -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"))
web_image = code(modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "huggingface_hub"))

cache = modal.Volume.from_name("neuro-model-cache", create_if_missing=True)
SECRET = [modal.Secret.from_name("neuro-hf")]
gpu_kw = dict(image=gpu_image, timeout=6 * 3600, volumes={"/cache": cache}, secrets=SECRET, max_containers=3)


def _stage(stage, model, scenes, idxs, project, thumb=None):
    import sys; sys.path.insert(0, "/root")
    import worker
    try:
        if stage == "images": return worker.images(model, scenes, idxs, project, thumb=thumb)
        return worker.videos(model, scenes, idxs, project)
    finally:
        cache.commit()


@app.function(gpu="A10G", **gpu_kw)
def g_a10g(stage, model, scenes, idxs, project, thumb=None): return _stage(stage, model, scenes, idxs, project, thumb)
@app.function(gpu="A100-40GB", **gpu_kw)
def g_a100_40(stage, model, scenes, idxs, project, thumb=None): return _stage(stage, model, scenes, idxs, project, thumb)
@app.function(gpu="A100-80GB", **gpu_kw)
def g_a100_80(stage, model, scenes, idxs, project, thumb=None): return _stage(stage, model, scenes, idxs, project, thumb)
@app.function(gpu="H100", **gpu_kw)
def g_h100(stage, model, scenes, idxs, project, thumb=None): return _stage(stage, model, scenes, idxs, project, thumb)


@app.function(gpu="A10G", image=voice_image, timeout=2 * 3600, volumes={"/cache": cache}, secrets=SECRET)
def g_voice(scenes, project, cfg=None):
    import sys; sys.path.insert(0, "/root")
    import worker
    try: return worker.voice_chatterbox(scenes, list(range(len(scenes))), project, cfg)
    finally: cache.commit()


@app.function(image=edit_image, cpu=16, memory=16384, timeout=3 * 3600, volumes={"/cache": cache}, secrets=SECRET)
def edit(project, scenes, voice_model, hero_model):
    import sys; sys.path.insert(0, "/root")
    import editor
    try: return editor.edit(project, scenes, voice_model, hero_model)
    finally: cache.commit()


GPU_FN = {"A10G": g_a10g, "A100-40GB": g_a100_40, "A100-80GB": g_a100_80, "H100": g_h100}


@app.function(image=web_image, timeout=8 * 3600, secrets=SECRET)
def controller(project, profile="standard", budget_usd=10.0):
    import sys; sys.path.insert(0, "/root")
    from models import PROFILES, IMAGE, VIDEO, PRICE, FALLBACK, pick_heroes, estimate
    from huggingface_hub import HfApi, hf_hub_download
    REPO = "bekbol446/neuro-channel"; api = HfApi(token=os.environ["HF_TOKEN"]); T0 = time.time()
    log, cost = [], {"usd": 0.0}

    def status(state, **kw):
        log.append(f"{time.strftime('%H:%M:%S')} {state}"); print(log[-1], flush=True)
        api.upload_file(path_or_fileobj=json.dumps(dict(state=state, profile=profile, cost_usd=round(cost["usd"], 2),
                        minutes=round((time.time() - T0) / 60, 1), log=log, **kw), indent=1).encode(),
                        path_in_repo=f"work/{project}/status.json", repo_id=REPO, repo_type="dataset")

    def charge(gpu, seconds): cost["usd"] += seconds / 3600 * PRICE[gpu]

    rd = lambda f: json.load(open(hf_hub_download(REPO, f"work/{project}/{f}", repo_type="dataset", token=os.environ["HF_TOKEN"], force_download=True)))
    scenes = rd("scenes.json")
    try: meta = rd("meta.json")
    except Exception: meta = {}
    channel = {}
    if meta.get("channel"):
        try: channel = json.load(open(hf_hub_download(REPO, f"channels/{meta['channel']}.json", repo_type="dataset", token=os.environ["HF_TOKEN"], force_download=True)))
        except Exception as e: log.append(f"channel settings not found: {e}")
    P = dict(PROFILES[profile]); n = len(scenes)
    if channel.get("voice", {}).get("model"): P["voice"] = channel["voice"]["model"]
    # cost guard: drop hero scenes until the estimate fits the budget
    while P["heroes"] > 0 and estimate_with(P, n) > budget_usd: P["heroes"] -= 1
    heroes = pick_heroes(n, P["heroes"], [i for i, s in enumerate(scenes) if s.get("hero")]) if P["hero_video"] else []
    status("starting", scenes=n, heroes=heroes, estimate_usd=estimate_with(P, n))

    # 1) images: split across up to 3 GPUs
    im = IMAGE[P["image"]]; chunks = [list(range(n))[k::3] for k in range(min(3, n))]
    thumb = {"title": meta.get("thumb_title", ""), "visual": meta.get("thumb_visual", "")} if meta.get("thumb_title") else None
    calls = [GPU_FN[im["gpu"]].spawn("images", P["image"], scenes, c, project, thumb if k == 0 else None) for k, c in enumerate(chunks)]
    voice_call = g_voice.spawn(scenes, project, channel.get("voice")) if P["voice"] == "chatterbox" else None   # voice runs at the same time
    done_imgs = []
    for c in calls:
        r = c.get(); done_imgs += r["done"]; charge(im["gpu"], r["seconds"])
    status("images done", images=len(done_imgs))

    # 2) hero clips: up to 3 GPUs in parallel; failed scenes fall back to the next model, then to stills
    hero_model = P["hero_video"]
    if heroes:
        todo, models_left = list(heroes), [m for m in FALLBACK["video"] if FALLBACK["video"].index(m) >= FALLBACK["video"].index(hero_model)]
        for vm in models_left:
            if not todo or cost["usd"] > budget_usd: break
            v = VIDEO[vm]; parts = [todo[k::3] for k in range(min(3, len(todo)))]
            res = [GPU_FN[v["gpu"]].spawn("videos", vm, scenes, p, project) for p in parts]
            got = []
            for c in res:
                try: r = c.get(); got += r["done"]; charge(v["gpu"], r["seconds"])
                except Exception as e: log.append(f"{vm} chunk failed: {str(e)[:200]}")
            if vm == hero_model: hero_model_used = vm
            todo = [i for i in todo if i not in got]
            status(f"clips with {vm}", clips_done=len(heroes) - len(todo), missing=todo)
            if vm != hero_model and got:  # fallback clips live in their own folder; keep it simple: copy into hero folder
                for i in got:
                    try:
                        f = hf_hub_download(REPO, f"work/{project}/clips_{vm}/clip_{i:03d}.mp4", repo_type="dataset", token=os.environ["HF_TOKEN"])
                        api.upload_file(path_or_fileobj=f, path_in_repo=f"work/{project}/clips_{hero_model}/clip_{i:03d}.mp4", repo_id=REPO, repo_type="dataset")
                    except Exception: pass
    voice_model = P["voice"]
    if voice_call:
        try:
            r = voice_call.get(); charge("A10G", r["seconds"])
            status(f"voice done: chatterbox ({'locked narrator' if r.get('reference') else 'default voice'})")
        except Exception as e: voice_model = "kokoro"; status(f"chatterbox failed, using kokoro: {str(e)[:200]}")

    # 3) edit on a 16-core CPU machine
    status("editing")
    r = edit.remote(project, scenes, voice_model, hero_model if heroes else None)
    charge("CPU", r["seconds"])
    status("done", video=f"videos/{project}/final.mp4", length_s=r["length"], subtitle_lines=r["subtitle_lines"],
           music=r["music"], scene_report=r["scenes"])
    return r


def estimate_with(P, n):
    from models import IMAGE, VIDEO, PRICE
    usd = (n * 2 + 1) * IMAGE[P["image"]]["sec"] / 3600 * PRICE[IMAGE[P["image"]]["gpu"]] + 0.10
    if P["hero_video"]: v = VIDEO[P["hero_video"]]; usd += min(P["heroes"], n) * v["sec"] / 3600 * PRICE[v["gpu"]]
    if P["voice"] == "chatterbox": usd += n * 20 / 3600 * PRICE["A10G"]
    return round(usd, 2)


@app.function(image=web_image, secrets=SECRET)
@modal.fastapi_endpoint(method="POST")
def start(body: dict):
    """Called by Claude cloud over plain HTTPS. body["key"] = sha256 of the HF token (both sides already have it)."""
    import hashlib, hmac
    from fastapi import HTTPException
    want = hashlib.sha256(os.environ["HF_TOKEN"].encode()).hexdigest()
    if not hmac.compare_digest(str(body.get("key", "")), want):
        raise HTTPException(status_code=403, detail="bad key")
    c = controller.spawn(body["project"], body.get("profile", "standard"), float(body.get("budget_usd", 10)))
    return {"call_id": c.object_id, "project": body["project"]}
