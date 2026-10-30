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
    .pip_install("torch", "torchvision", "transformers>=5.17.0", "accelerate", "sentencepiece", "ftfy", "imageio", "imageio-ffmpeg",
                 "pillow", "numpy", "huggingface_hub", "hf_transfer", "peft", "soundfile", "ccvfi", "opencv-python-headless")
    .pip_install("diffusers @ git+https://github.com/huggingface/diffusers@main")  # main: Qwen-Image-2.1-Turbo sigmas, ACE-Step
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache/hf"}))
voice_image = code(modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg")
    .pip_install("chatterbox-tts", "huggingface_hub").env({"HF_HOME": "/cache/hf"}))
qwen_voice_image = code(modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg", "sox")
    .pip_install("qwen-tts", "soundfile", "huggingface_hub").env({"HF_HOME": "/cache/hf"}))
edit_image = code(modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg", "fonts-dejavu-core", "curl")
    .pip_install("kokoro-onnx", "soundfile", "faster-whisper", "huggingface_hub")
    .run_commands("mkdir -p /models && cd /models && "
                  "curl -sSL -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx && "
                  "curl -sSL -O https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin"))
web_image = code(modal.Image.debian_slim(python_version="3.11").pip_install("fastapi[standard]", "huggingface_hub", "anthropic", "pillow"))

cache = modal.Volume.from_name("neuro-model-cache", create_if_missing=True)
SECRET = [modal.Secret.from_name("neuro-hf")]
gpu_kw = dict(image=gpu_image, timeout=6 * 3600, volumes={"/cache": cache}, secrets=SECRET, max_containers=3)


def _stage(stage, model, scenes, idxs, project, thumb=None, candidates=2):
    import sys; sys.path.insert(0, "/root")
    import worker
    try:
        if stage == "images": return worker.images(model, scenes, idxs, project, n_candidates=candidates, thumb=thumb)
        return worker.videos(model, scenes, idxs, project)
    finally:
        cache.commit()


@app.function(gpu="A10G", **gpu_kw)
def g_a10g(stage, model, scenes, idxs, project, thumb=None, candidates=2): return _stage(stage, model, scenes, idxs, project, thumb, candidates)
@app.function(gpu="A100-40GB", **gpu_kw)
def g_a100_40(stage, model, scenes, idxs, project, thumb=None, candidates=2): return _stage(stage, model, scenes, idxs, project, thumb, candidates)
@app.function(gpu="A100-80GB", **gpu_kw)
def g_a100_80(stage, model, scenes, idxs, project, thumb=None, candidates=2): return _stage(stage, model, scenes, idxs, project, thumb, candidates)
@app.function(gpu="H100", **gpu_kw)
def g_h100(stage, model, scenes, idxs, project, thumb=None, candidates=2): return _stage(stage, model, scenes, idxs, project, thumb, candidates)


@app.function(gpu="A10G", image=voice_image, timeout=2 * 3600, volumes={"/cache": cache}, secrets=SECRET)
def g_voice(scenes, project, cfg=None, idxs=None, seed=0):
    import sys; sys.path.insert(0, "/root")
    import worker
    try: return worker.voice_chatterbox(scenes, idxs or list(range(len(scenes))), project, cfg, seed)
    finally: cache.commit()


@app.function(gpu="A10G", image=qwen_voice_image, timeout=2 * 3600, volumes={"/cache": cache}, secrets=SECRET)
def g_voice_qwen(scenes, project, cfg=None, idxs=None, seed=0):
    import sys; sys.path.insert(0, "/root")
    import worker
    try: return worker.voice_qwen3tts(scenes, idxs or list(range(len(scenes))), project, cfg, seed)
    finally: cache.commit()


@app.function(gpu="A10G", **{**gpu_kw, "max_containers": 1})
def g_music(model, project, seconds=180, prompt=None):
    import sys; sys.path.insert(0, "/root")
    import worker
    try: return worker.music(model, project, seconds, prompt)
    finally: cache.commit()


@app.function(image=edit_image, cpu=16, memory=8192, timeout=3600, volumes={"/cache": cache}, secrets=SECRET)
def voice_check(scenes, project, voice_model):
    import sys; sys.path.insert(0, "/root")
    import worker
    try: return worker.voice_check(scenes, project, voice_model)
    finally: cache.commit()


@app.function(image=edit_image, cpu=16, memory=16384, timeout=3 * 3600, volumes={"/cache": cache}, secrets=SECRET)
def edit(project, scenes, voice_model, hero_model):
    import sys; sys.path.insert(0, "/root")
    import editor
    try: return editor.edit(project, scenes, voice_model, hero_model)
    finally: cache.commit()


GPU_FN = {"A10G": g_a10g, "A100-40GB": g_a100_40, "A100-80GB": g_a100_80, "H100": g_h100}
VOICE_FN = {"chatterbox": g_voice, "qwen3tts": g_voice_qwen}


def review_images(project, scenes, log):
    """Claude looks at both kept candidates of every scene and swaps in the 2nd one when it is clearly better.
    Runs only if ANTHROPIC_API_KEY is in the neuro-hf secret. Returns {scene: score} of scenes still below 6."""
    import base64, io, re, tempfile
    import anthropic
    from concurrent.futures import ThreadPoolExecutor
    from PIL import Image
    from huggingface_hub import HfApi, snapshot_download
    REPO = "bekbol446/neuro-channel"; tok = os.environ["HF_TOKEN"]; d = tempfile.mkdtemp()
    snapshot_download(REPO, repo_type="dataset", allow_patterns=[f"work/{project}/imgs/img_*.png"], local_dir=d, token=tok)
    d = f"{d}/work/{project}/imgs"; client = anthropic.Anthropic()

    def jpg(f):
        b = io.BytesIO(); Image.open(f).convert("RGB").resize((768, 432)).save(b, "JPEG", quality=85)
        return {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}}

    def one(i):
        a, b = f"{d}/img_{i:03d}.png", f"{d}/img_{i:03d}_b.png"
        if not os.path.exists(a): return i, None
        imgs = [a] + ([b] if os.path.exists(b) else [])
        content = [jpg(f) for f in imgs] + [{"type": "text", "text":
            f"These are {len(imgs)} candidate images (in order: A{', B' if len(imgs) > 1 else ''}) for one scene of a neuroscience "
            f"explainer video.\nNarration: {scenes[i]['text']}\nImage prompt: {scenes[i]['prompt']}\n"
            "Score each 1-10 for: fits the narration, scientifically plausible, no deformed anatomy, no garbled text or watermarks, "
            'looks cinematic. Reply with JSON only: {"A": score, "B": score, "issue": "main problem of the better one, or empty"}'}]
        try:
            r = client.messages.create(model="claude-opus-5-5", max_tokens=300, messages=[{"role": "user", "content": content}])
            j = json.loads(re.search(r"\{.*\}", next(x.text for x in r.content if x.type == "text"), re.S).group(0))
            return i, j
        except Exception as e: return i, {"error": str(e)[:200]}

    with ThreadPoolExecutor(8) as ex: res = dict(ex.map(one, range(len(scenes))))
    swap, weak = {}, {}
    for i, j in res.items():
        if not j or "A" not in j: continue
        a, b = float(j["A"]), float(j.get("B", 0) or 0)
        if b >= a + 2: swap[i] = (a, b)
        if max(a, b) < 6: weak[i] = max(a, b)
    if swap:  # B becomes the main image (and A the 2nd camera move)
        out = tempfile.mkdtemp()
        for i in swap:
            os.replace(f"{d}/img_{i:03d}.png", f"{out}/img_{i:03d}_b.png"); os.replace(f"{d}/img_{i:03d}_b.png", f"{out}/img_{i:03d}.png")
        HfApi(token=tok).upload_folder(folder_path=out, path_in_repo=f"work/{project}/imgs", repo_id=REPO, repo_type="dataset")
    log.append(f"image review: {len(res)} scenes, swapped {sorted(swap)}, weak {weak}")
    json_out = {str(i): j for i, j in res.items()}
    HfApi(token=tok).upload_file(path_or_fileobj=json.dumps(json_out, indent=1).encode(), path_in_repo=f"work/{project}/image_review.json",
                                 repo_id=REPO, repo_type="dataset")
    return weak


@app.function(image=web_image, timeout=8 * 3600, secrets=SECRET)
def controller(project, profile="standard", budget_usd=10.0):
    import sys; sys.path.insert(0, "/root")
    from models import PROFILES, IMAGE, VIDEO, VOICE, MUSIC, PRICE, FALLBACK, pick_heroes, estimate_usd as estimate_with
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
    calls = [GPU_FN[im["gpu"]].spawn("images", P["image"], scenes, c, project, thumb if k == 0 else None, P.get("candidates", 2))
             for k, c in enumerate(chunks)]
    vfn = VOICE_FN.get(P["voice"])
    voice_call = vfn.spawn(scenes, project, channel.get("voice")) if vfn else None   # voice and music run at the same time
    music_call = g_music.spawn(P["music"], project, 180, meta.get("music_prompt")) if P.get("music") else None
    done_imgs = []
    for c in calls:
        r = c.get(); done_imgs += r["done"]; charge(im["gpu"], r["seconds"])
    status("images done", images=len(done_imgs))
    if os.environ.get("ANTHROPIC_API_KEY"):  # Claude picks the better candidate before any clip is made from it
        try: review_images(project, scenes, log); cost["usd"] += 0.02 * n
        except Exception as e: log.append(f"image review failed: {str(e)[:200]}")
        status("images reviewed")

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
            status(f"voice done: {voice_model} ({'locked narrator' if r.get('reference') else 'default voice'})")
        except Exception as e: status(f"{voice_model} failed, using kokoro: {str(e)[:200]}"); voice_model = "kokoro"
    if voice_model != "kokoro":
        try:  # Whisper listens to every line; lines with skipped / garbled words are made again (2 more takes at most)
            for take in (1, 2):
                bad = voice_check.remote(scenes, project, voice_model); charge("CPU", 60)
                if not bad: status("voice check: all lines clear"); break
                status(f"voice check: redoing {len(bad)} lines", bad_lines=bad)
                r = vfn.remote(scenes, project, channel.get("voice"), sorted(bad), take); charge("A10G", r["seconds"])
            else: status("voice check: after 2 more takes", bad_lines=voice_check.remote(scenes, project, voice_model))
        except Exception as e: log.append(f"voice check failed (keeping the voice as is): {str(e)[:200]}")
    if music_call:
        try: r = music_call.get(); charge(MUSIC[P["music"]]["gpu"], r["seconds"]); status("music done")
        except Exception as e: log.append(f"music failed (using assets/music.mp3 if any): {str(e)[:200]}")

    # 3) edit on a 16-core CPU machine
    status("editing")
    r = edit.remote(project, scenes, voice_model, hero_model if heroes else None)
    charge("CPU", r["seconds"])
    status("done", video=f"videos/{project}/final.mp4", length_s=r["length"], subtitle_lines=r["subtitle_lines"],
           music=r["music"], lufs=r.get("lufs"), scene_report=r["scenes"])
    return r


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
