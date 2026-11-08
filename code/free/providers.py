"""Free providers. Each one makes ONE item into a local file:
  image(prompt, seed, out_png)   clip(image_png, prompt, seed, out_mp4)   voice(text, out_wav)   music(prompt, seconds, out_wav)
A provider that runs out of free quota raises QuotaError; the router then skips it for the rest of the run.
quality: 1-10 (our own tests)   sec: wall seconds per item, measured where marked (m)   limit: parallel calls"""
import os, time, json, shutil, asyncio, threading, subprocess, urllib.parse, urllib.request

HF = lambda: os.environ.get("HF_TOKEN")


class QuotaError(Exception): pass


def ffmpeg(args):
    r = subprocess.run(f"ffmpeg -loglevel error -y {args}", shell=True, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[-500:])


# ------------------------------------------------------------- Hugging Face ZeroGPU Spaces (free daily GPU quota per account)
_clients, _lock = {}, threading.Lock()


def _space(sid):
    from gradio_client import Client
    key = (sid, threading.get_ident())
    with _lock:
        if key not in _clients: _clients[key] = Client(sid, token=HF(), verbose=False)
    return _clients[key]


def _call(sid, api, **kw):
    try: return _space(sid).predict(api_name=api, **kw)
    except Exception as e:
        m = str(e).lower()
        if any(k in m for k in ("quota", "exceeded", "zerogpu", "too many requests", "rate limit")): raise QuotaError(f"{sid}: {str(e)[:200]}")
        raise


def _file(r):
    """First file path inside a gradio result (str, dict with path/image/video, or nested list)."""
    x = r
    while isinstance(x, (list, tuple)): x = x[0]
    while isinstance(x, dict): x = x.get("image") or x.get("video") or x.get("path") or x.get("value")
    return x


class ZImage:  # Tongyi-MAI Z-Image-Turbo, Apache-2.0, 8 steps
    name, kind, quality, sec, limit, space = "zg_zimage", "image", 9, 18, 2, "Tongyi-MAI/Z-Image-Turbo"  # (m) 2048x1152 in 18 s
    def available(self): return bool(HF())
    def image(self, prompt, seed, out, size="2048x1152 ( 16:9 )"):
        r = _call(self.space, "/generate", prompt=prompt, resolution=size, seed=seed, steps=8, shift=3.0, random_seed=False,
                  gallery_images=[])
        shutil.copy(_file(r), out)


class Flux2Klein:  # black-forest-labs FLUX.2 [klein] 9B, 4 steps (non-commercial licence; channel is research)
    name, kind, quality, sec, limit, space = "zg_flux2klein", "image", 8, 15, 2, "black-forest-labs/FLUX.2-klein-9B"
    def available(self): return bool(HF())
    def image(self, prompt, seed, out):
        r = _call(self.space, "/generate", prompt=prompt, input_images=[], mode_choice="Distilled (4 steps)", seed=seed,
                  randomize_seed=False, width=1920, height=1088, num_inference_steps=4, guidance_scale=1.0, prompt_upsampling=False)
        shutil.copy(_file(r), out)


class WanSpace:  # Wan2.2-I2V-A14B fp8 + lightning LoRA, 6 steps, 832x480 @16 fps
    name, kind, quality, sec, limit, space = "zg_wan22", "video", 8, 60, 1, "zerogpu-aoti/wan2-2-fp8da-aoti-faster"  # (m) 57 s
    def available(self): return bool(HF())
    def clip(self, image, prompt, seed, out):
        from gradio_client import handle_file
        r = _call(self.space, "/generate_video", input_image=handle_file(image), prompt=prompt, steps=6, duration_seconds=5.0,
                  guidance_scale=1, guidance_scale_2=1, seed=seed, randomize_seed=False)
        shutil.copy(_file(r), out)


class WanSpaceR3gm(WanSpace):  # a second Wan2.2 14B fp8 Space (same model, different owner): used when the first is down
    name, space = "zg_wan22_r3gm", "r3gm/wan2-2-fp8da-aoti-preview"
    def clip(self, image, prompt, seed, out):
        from gradio_client import handle_file
        r = _call(self.space, "/generate_video", input_image=handle_file(image), last_image=None, prompt=prompt, steps=6,
                  duration_seconds=5.0, guidance_scale=1, guidance_scale_2=1, seed=seed, randomize_seed=False)
        shutil.copy(_file(r), out)  # returns ({video, subtitles}, file, seed); _file picks the video


class LtxSpace:  # Lightricks' own LTX-2.3 Space (distilled): a different model family, so it still works if Wan Spaces break
    name, kind, quality, sec, limit, space = "zg_ltx23", "video", 7, 45, 1, "Lightricks/LTX-2-3"
    def available(self): return bool(HF())
    def clip(self, image, prompt, seed, out):
        from gradio_client import handle_file
        r = _call(self.space, "/generate_video", input_image=handle_file(image), prompt=prompt, duration=5.0, enhance_prompt=False,
                  seed=seed, randomize_seed=False, height=704, width=1280)
        shutil.copy(_file(r), out)


# ------------------------------------------------------------- spending caps for the providers that can cost money
# One ledger per month on the HF dataset (budget/<YYYY-MM>.json -> {"modal": usd, "muapi": usd}), shared by every runner.
_blk = threading.Lock()
CAPS = {"modal": float(os.environ.get("MODAL_MONTHLY_USD") or 25),   # Modal gives $30 free each month; keep $5 spare
        "muapi": float(os.environ.get("MUAPI_MONTHLY_USD") or 5)}    # Muapi is real money; 0 turns it off


def _ledger_path(): return f"budget/{time.strftime('%Y-%m', time.gmtime())}.json"


def _ledger():
    from huggingface_hub import hf_hub_download
    try: return json.load(open(hf_hub_download(os.environ["HF_REPO"], _ledger_path(), repo_type="dataset", token=HF(), force_download=True)))
    except Exception: return {}


def budget_left(who):
    with _blk: return CAPS[who] - float(_ledger().get(who, 0))


def budget_spend(who, usd):
    """Adds usd to this month's ledger. Read-modify-write under a lock: exact within one runner, close enough across two."""
    from huggingface_hub import HfApi
    with _blk:
        led = _ledger(); led[who] = round(float(led.get(who, 0)) + usd, 4)
        HfApi(token=HF()).upload_file(path_or_fileobj=json.dumps(led, indent=1).encode(), path_in_repo=_ledger_path(),
                                      repo_id=os.environ["HF_REPO"], repo_type="dataset", commit_message=f"budget: {who} +${usd:.3f}")


class ModalWan:  # Wan2.2-I2V-A14B + 4-step lightx2v LoRAs on a Modal H100, 1280x720 @16 fps (code/free/modal_clip.py)
    """Uses the $30/month Modal credit. Cost is counted conservatively: wall time of the call (cold start included) at
    the H100 rate, plus 30 s for the idle minute before the container stops. Over the cap -> QuotaError."""
    name, kind, quality, sec, limit = "modal_wan22", "video", 9, 150, 1
    USD_PER_SEC = 3.95 / 3600  # Modal H100, on-demand
    def available(self):
        if not (os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET") and HF() and CAPS["modal"] > 0): return False
        try: import modal  # noqa: F401
        except ImportError: return False
        return True
    def clip(self, image, prompt, seed, out):
        if budget_left("modal") < 0.6: raise QuotaError(f"modal: monthly cap ${CAPS['modal']:.0f} reached")
        import modal
        t = time.time()
        try: data = modal.Cls.from_name("neuro-clip", "Wan")().clip.remote(open(image, "rb").read(), prompt, int(seed))
        finally: budget_spend("modal", (time.time() - t + 30) * self.USD_PER_SEC)
        open(out, "wb").write(data)


class Muapi:  # paid API for closed models (Kling, Veo, Seedance, Hailuo...): last resort, under MUAPI_MONTHLY_USD
    """MUAPI_API_KEY + optional MUAPI_MODEL (any image-to-video endpoint on muapi.ai, default Kling 2.5 Turbo Std, $0.28/5 s).
    Upload the still -> submit -> poll /predictions/<id>/result. The charge comes back in the response and goes in the ledger."""
    name, kind, quality, sec, limit = "muapi", "video", 9, 120, 2
    BASE = "https://api.muapi.ai/api/v1"
    MODEL = os.environ.get("MUAPI_MODEL") or "kling-v2.5-turbo-std-i2v"
    PRICE = float(os.environ.get("MUAPI_CLIP_USD") or 0.6)  # used only when Muapi does not report the charge (worst-case guess)
    def available(self): return bool(os.environ.get("MUAPI_API_KEY")) and CAPS["muapi"] > 0
    def _http(self):
        import httpx
        return httpx.Client(base_url=self.BASE, headers={"x-api-key": os.environ["MUAPI_API_KEY"]}, timeout=120)
    def payload(self, image_url, prompt):
        m = self.MODEL
        p = {"prompt": prompt[:1500]}
        if m.startswith(("seedance-2", "seedance-v2")): p["images_list"] = [image_url]; p.update(aspect_ratio="16:9", resolution="720p")
        else: p["image_url"] = image_url
        if "veo" in m: p.update(aspect_ratio="16:9", resolution="720p")  # Veo clips are 8 s; the editor cuts them to the scene
        else: p["duration"] = 5
        return p
    @staticmethod
    def _check(r):
        if r.status_code in (402, 429) or "insufficient" in r.text.lower(): raise QuotaError(f"muapi {r.status_code}: {r.text[:150]}")
        r.raise_for_status(); return r.json()
    def clip(self, image, prompt, seed, out):
        left = budget_left("muapi")
        if left < self.PRICE: raise QuotaError(f"muapi: monthly cap ${CAPS['muapi']:.2f} reached (${left:.2f} left)")
        with self._http() as c:
            with open(image, "rb") as f: up = self._check(c.post("/upload_file", files={"file": (os.path.basename(image), f, "image/png")}))
            url = up.get("url") or up.get("file_url") or (up.get("data") or {}).get("url")
            if not url: raise RuntimeError(f"muapi upload: no url in {str(up)[:200]}")
            sub = self._check(c.post(f"/{self.MODEL}", json=self.payload(url, prompt)))
            rid = sub.get("request_id") or sub.get("id") or (sub.get("data") or {}).get("request_id")
            if not rid: raise RuntimeError(f"muapi submit: no request_id in {str(sub)[:200]}")
            charged = False
            try:
                for _ in range(180):  # 15 min
                    time.sleep(5)
                    r = c.get(f"/predictions/{rid}/result")
                    if r.status_code >= 500 or r.status_code == 429: continue  # busy / polling too fast: ask again
                    res = self._check(r); st = str(res.get("status") or (res.get("data") or {}).get("status") or "").lower()
                    if st in ("failed", "error", "cancelled", "canceled"): raise RuntimeError(f"muapi {rid}: {str(res)[:200]}")
                    if st in ("completed", "succeeded", "success"):
                        cost = (res.get("cost") or sub.get("cost") or {}).get("amount_usd")
                        budget_spend("muapi", float(cost) if cost is not None else self.PRICE); charged = True
                        o = res.get("outputs") or (res.get("data") or {}).get("outputs") or []
                        vurl = (o[0] if o else None) or res.get("url") or (res.get("output") or {}).get("url")
                        if not vurl: raise RuntimeError(f"muapi {rid}: no video url")
                        with c.stream("GET", vurl) as v, open(out, "wb") as f:
                            for b in v.iter_bytes(): f.write(b)
                        return
                raise RuntimeError(f"muapi {rid}: timed out")
            finally:
                if not charged: budget_spend("muapi", self.PRICE)  # submitted but no result: count it, the job may still bill


class Qwen3TTSSpace:
    name, kind, quality, sec, limit, space = "zg_qwen3tts", "voice", 8, 10, 2, "Qwen/Qwen3-TTS"
    def available(self): return bool(HF())
    def voice(self, text, out, speaker="Aiden",
              instruct="Calm, warm documentary narrator. Clear, curious and engaging, natural pauses, medium pace."):
        r = _call(self.space, "/generate_custom_voice", text=text, language="English", speaker=speaker, instruct=instruct, model_size="1.7B")
        ffmpeg(f"-i '{_file(r)}' -ac 1 -ar 24000 '{out}'")


# ------------------------------------------------------------- no GPU, no key
class EdgeTTS:  # Microsoft Edge read-aloud neural voices; unlimited, ~1 s per line
    name, kind, quality, sec, limit = "edge", "voice", 7, 2, 4
    VOICE = os.environ.get("EDGE_VOICE", "en-US-AndrewMultilingualNeural")
    def available(self): return True
    def voice(self, text, out, rate="+0%"):
        import edge_tts
        mp3 = out[:-4] + ".mp3"
        for k in range(3):  # the service sometimes drops a request
            try: asyncio.run(edge_tts.Communicate(text, self.VOICE, rate=rate).save(mp3)); break
            except Exception:
                if k == 2: raise
                time.sleep(2)
        ffmpeg(f"-i '{mp3}' -ac 1 -ar 24000 '{out}'"); os.remove(mp3)


class Pollinations:  # last resort: blurry, 1024x576, watermark (m)
    name, kind, quality, sec, limit = "pollinations", "image", 3, 6, 1
    def available(self): return True
    def image(self, prompt, seed, out):
        u = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt[:900])}?width=1920&height=1080&model=flux&nologo=true&seed={seed}"
        with urllib.request.urlopen(u, timeout=180) as r:
            if r.status == 429: raise QuotaError("pollinations rate limit")
            data = r.read()
        from PIL import Image; import io
        Image.open(io.BytesIO(data)).convert("RGB").save(out)


class MusicLibrary:  # a bed we already made (ACE-Step on Modal) or the user's assets/music.mp3 on the HF dataset
    name, kind, quality, sec, limit = "library", "music", 6, 5, 1
    FILES = ("assets/music.mp3", "work/test_turbo_1030/music/music.wav")
    def available(self): return bool(HF())
    def music(self, prompt, seconds, out):
        from huggingface_hub import hf_hub_download
        repo = os.environ.get("HF_REPO") or "bekbol446/video_gen"
        for f in self.FILES:
            try: src = hf_hub_download(repo, f, repo_type="dataset", token=HF()); break
            except Exception: src = None
        if not src: raise RuntimeError("no music in the library")
        ffmpeg(f"-i '{src}' -ac 2 -ar 48000 '{out}'")


# ------------------------------------------------------------- optional: keys the user can add for more free quota
class GeminiImage:  # needs GEMINI_API_KEY from a project WITHOUT billing (free tier); prepaid projects return 402
    name, kind, quality, sec, limit = "gemini_image", "image", 9, 12, 2
    MODEL = "gemini-3.1-flash-image"
    def available(self): return bool(os.environ.get("GEMINI_API_KEY"))
    def image(self, prompt, seed, out):
        from google import genai
        from google.genai import types
        try:
            r = genai.Client(api_key=os.environ["GEMINI_API_KEY"]).models.generate_content(model=self.MODEL, contents=prompt,
                config=types.GenerateContentConfig(response_modalities=["IMAGE"], image_config=types.ImageConfig(aspect_ratio="16:9"), seed=seed))
        except Exception as e:
            if any(k in str(e) for k in ("402", "429", "RESOURCE_EXHAUSTED")): raise QuotaError(f"gemini: {str(e)[:150]}")
            raise
        part = next(p for p in r.candidates[0].content.parts if p.inline_data)
        open(out, "wb").write(part.inline_data.data)


class CloudflareImage:  # needs CF_ACCOUNT_ID + CF_API_TOKEN (Workers AI free daily allowance)
    name, kind, quality, sec, limit = "cf_flux", "image", 7, 6, 2
    MODEL = "@cf/black-forest-labs/flux-1-schnell"
    def available(self): return bool(os.environ.get("CF_ACCOUNT_ID") and os.environ.get("CF_API_TOKEN"))
    def image(self, prompt, seed, out):
        import base64
        req = urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{os.environ['CF_ACCOUNT_ID']}/ai/run/{self.MODEL}",
                                     data=json.dumps({"prompt": prompt[:2000], "steps": 8, "seed": seed}).encode(),
                                     headers={"Authorization": f"Bearer {os.environ['CF_API_TOKEN']}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as r: res = json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429, 402): raise QuotaError(f"cloudflare {e.code}")
            raise
        open(out, "wb").write(base64.b64decode(res["result"]["image"]))


# best first. The router keeps ONE image model and ONE voice per video when it can (consistent look and narrator).
IMAGE = [ZImage(), GeminiImage(), Flux2Klein(), CloudflareImage(), Pollinations()]
# clips: free ZeroGPU first (one daily quota per HF account, shared by all three Spaces; the 2nd and 3rd are for when a
# Space is down), then the Modal free credit, then paid Muapi. Each paid one stops at its monthly cap.
VIDEO = [WanSpace(), WanSpaceR3gm(), LtxSpace(), ModalWan(), Muapi()]
VOICE = {"edge": EdgeTTS(), "qwen3tts": Qwen3TTSSpace()}
MUSIC = [MusicLibrary()]
