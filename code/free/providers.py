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
VIDEO = [WanSpace()]
VOICE = {"edge": EdgeTTS(), "qwen3tts": Qwen3TTSSpace()}
MUSIC = [MusicLibrary()]
