"""Runs ONE model on a list of scenes. Reads inputs from / writes outputs to the Hugging Face dataset
(work/<project>/imgs, work/<project>/clips, work/<project>/voice), so no laptop is needed.
Used by modal_app3.py (and can be used on Kaggle)."""
import os, json, time, gc, traceback, glob
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
from models import IMAGE, VIDEO, VOICE, MUSIC
REPO = os.environ.get("HF_REPO") or "bekbol446/video_gen"
STYLE = ", cinematic scientific visualization, photorealistic, dark background, volumetric light, shallow depth of field, ultra detailed"
NEG_I = "text, letters, watermark, logo, cartoon, low quality, blurry, deformed, ugly, jpeg artifacts, frame, border"
NEG_V = "blurry, distorted, morphing, melting, flicker, text, watermark, low quality, static, jittery"


def _hf():
    from huggingface_hub import HfApi
    return HfApi(token=os.environ["HF_TOKEN"])


def _push(local_dir, project, sub):
    _hf().upload_folder(folder_path=local_dir, path_in_repo=f"work/{project}/{sub}", repo_id=REPO, repo_type="dataset")


def _pull(project, sub, dest):
    from huggingface_hub import snapshot_download
    snapshot_download(REPO, repo_type="dataset", allow_patterns=[f"work/{project}/{sub}/*"], local_dir=dest,
                      token=os.environ["HF_TOKEN"])
    return f"{dest}/work/{project}/{sub}"


def _load(cls_name, repo, dtype):
    import diffusers
    return getattr(diffusers, cls_name).from_pretrained(repo, torch_dtype=dtype)


# ---------------------------------------------------------------- images
def images(model, scenes, idxs, project, n_candidates=2, thumb=None):
    import torch
    m = IMAGE[model]; out = "/tmp/imgs"; os.makedirs(out, exist_ok=True); t0 = time.time()
    if model == "sdxl":
        from diffusers import StableDiffusionXLPipeline, AutoencoderKL
        vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
        pipe = StableDiffusionXLPipeline.from_pretrained(m["repo"], vae=vae, torch_dtype=torch.float16, variant="fp16").to("cuda")
        gen = lambda p, s: pipe(p, negative_prompt=NEG_I, width=1344, height=768, num_inference_steps=35, guidance_scale=6.0,
                                generator=torch.Generator("cuda").manual_seed(s)).images[0]
    elif model == "flux2_klein9b":
        pipe = _load("Flux2KleinPipeline", m["repo"], torch.bfloat16); pipe.enable_model_cpu_offload()
        gen = lambda p, s: pipe(prompt=p, width=1360, height=768, generator=torch.Generator("cuda").manual_seed(s)).images[0]
    elif model == "flux3_klein":  # pipeline class read from the repo
        pipe = _load("DiffusionPipeline", m["repo"], torch.bfloat16); pipe.enable_model_cpu_offload()
        gen = lambda p, s: pipe(prompt=p, width=1536, height=864, generator=torch.Generator("cuda").manual_seed(s)).images[0]
    elif model == "qwen21":
        pipe = _load("QwenImage21Pipeline", m["repo"], torch.bfloat16); pipe.enable_model_cpu_offload()
        gen = lambda p, s: pipe(prompt=p, width=1536, height=864, num_inference_steps=30,
                                generator=torch.Generator("cuda").manual_seed(s)).images[0]
    elif model == "qwen21_turbo":  # 8-step schedule is stored in the checkpoint
        pipe = _load("QwenImage21Pipeline", m["repo"], torch.bfloat16); pipe.enable_model_cpu_offload()  # 40 GB is too tight on-GPU
        gen = lambda p, s: pipe(prompt=p, width=1536, height=864, use_kv_cache=True,
                                generator=torch.Generator("cuda").manual_seed(s)).images[0]
    # CLIP picks the best candidate
    from transformers import CLIPModel, CLIPProcessor
    clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.float16).to("cuda")
    cp = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
    picks = {}
    for i in idxs:
        try:
            p = scenes[i]["prompt"] + STYLE
            ims = [gen(p, 1000 * i + c) for c in range(n_candidates)]
            with torch.no_grad():
                x = cp(text=[scenes[i]["prompt"][:300]], images=ims, return_tensors="pt", padding=True, truncation=True).to("cuda")
                x = {k: (v.half() if v.dtype == torch.float32 else v) for k, v in x.items()}
                sc = clip(**x).logits_per_image[:, 0]
            order = [int(k) for k in sc.argsort(descending=True)]
            ims[order[0]].save(f"{out}/img_{i:03d}.png")
            if len(order) > 1: ims[order[1]].save(f"{out}/img_{i:03d}_b.png")
            picks[i] = [round(float(v), 2) for v in sc]
            print("img", i, picks[i], flush=True)
        except Exception: traceback.print_exc()
    if thumb and model.startswith(("qwen21", "flux3")):  # models that can render title text
        try:
            tp = (f'YouTube thumbnail, {thumb["visual"]}, huge bold white sans-serif title text "{thumb["title"]}" '
                  'with thick black outline on the left side, high contrast, dramatic lighting, very sharp, eye-catching')
            gen(tp, 7).resize((1280, 720)).save(f"{out}/thumbnail.png")
        except Exception: traceback.print_exc()
    _push(out, project, "imgs")
    return {"model": model, "done": sorted(int(os.path.basename(f)[4:7]) for f in glob.glob(f"{out}/img_???.png")),
            "seconds": round(time.time() - t0)}


# ---------------------------------------------------------------- video (image -> video)
def videos(model, scenes, idxs, project):
    import torch, numpy as np, subprocess
    from PIL import Image
    from diffusers.utils import export_to_video
    m = VIDEO[model]; src = _pull(project, "imgs", "/tmp/in"); out = "/tmp/clips"; os.makedirs(out, exist_ok=True); t0 = time.time()
    cls = {"ltx095": "LTXImageToVideoPipeline", "wan22_5b": "WanImageToVideoPipeline", "wan22_a14b": "WanImageToVideoPipeline",
           "wan22_a14b_4step": "WanImageToVideoPipeline", "ltx25": "LTX2ImageToVideoPipeline",
           "hunyuan15": "HunyuanVideo15ImageToVideoPipeline"}[model]
    dtype = torch.float16 if model == "ltx095" else torch.bfloat16
    pipe = _load(cls, m["repo"], dtype)
    if m.get("lora"):  # distill LoRA: high-noise expert -> transformer, low-noise expert -> transformer_2
        pipe.load_lora_weights(m["lora"], weight_name=m["lora_high"], adapter_name="hi")
        pipe.load_lora_weights(m["lora"], weight_name=m["lora_low"], adapter_name="lo", load_into_transformer_2=True)
        pipe.fuse_lora(adapter_names=["hi"], lora_scale=1.0, components=["transformer"])
        pipe.fuse_lora(adapter_names=["lo"], lora_scale=1.0, components=["transformer_2"])
        pipe.unload_lora_weights()
    pipe.enable_model_cpu_offload()
    if hasattr(pipe, "vae") and hasattr(pipe.vae, "enable_tiling"): pipe.vae.enable_tiling()
    errors = []
    for i in idxs:
        f = f"{src}/img_{i:03d}.png"
        if not os.path.exists(f): errors.append(f"no image {i}"); continue
        try:
            t = time.time(); s = scenes[i]
            kw = dict(image=Image.open(f).convert("RGB").resize((m["w"], m["h"])),
                      prompt=s.get("motion", "") + ". " + s["prompt"] + ", smooth natural cinematic motion",
                      negative_prompt=NEG_V, width=m["w"], height=m["h"], num_frames=m["frames"],
                      generator=torch.Generator("cuda").manual_seed(i))
            if m.get("steps"): kw.update(num_inference_steps=m["steps"], guidance_scale=m["cfg"], guidance_scale_2=m["cfg"])
            try: r = pipe(**kw)
            except TypeError:  # some pipelines don't take every argument
                for k in ("negative_prompt", "width", "height"): kw.pop(k, None)
                r = pipe(**kw)
            frames, fps = r.frames[0], m.get("fps", 24)
            if fps < 24:  # 16 fps -> 32 fps with RIFE (smoother than the editor repeating frames)
                try: frames = rife2x(frames); fps *= 2
                except Exception: traceback.print_exc()
            export_to_video(frames, f"{out}/raw.mp4", fps=fps)
            # normal-size H.264 (~5 MB) instead of near-lossless
            subprocess.run(f"ffmpeg -loglevel error -y -i {out}/raw.mp4 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p {out}/clip_{i:03d}.mp4", shell=True, check=True)
            os.remove(f"{out}/raw.mp4"); print("clip", i, round(time.time() - t), "s", flush=True)
        except Exception:
            errors.append(traceback.format_exc()[-1500:]); traceback.print_exc(); gc.collect(); torch.cuda.empty_cache()
    if glob.glob(f"{out}/clip_*.mp4"): _push(out, project, f"clips_{model}")
    return {"model": model, "done": sorted(int(f[-7:-4]) for f in glob.glob(f"{out}/clip_*.mp4")),
            "seconds": round(time.time() - t0), "errors": errors}


def rife2x(frames):
    """Doubles the frame rate: one RIFE 4.26 frame between every pair. frames: PIL list or float array 0..1."""
    import numpy as np, cv2
    from ccvfi import AutoModel, ConfigType
    global _RIFE
    if "_RIFE" not in globals(): _RIFE = AutoModel.from_pretrained(pretrained_model_name=ConfigType.RIFE_IFNet_v426_heavy)
    f = [np.asarray(x) for x in frames]
    f = [cv2.cvtColor((x * 255).clip(0, 255).astype(np.uint8) if x.dtype != np.uint8 else x, cv2.COLOR_RGB2BGR) for x in f]
    out = []
    for a, b in zip(f, f[1:]): out += [a, _RIFE.inference_image_list(img_list=[a, b])[0]]
    out.append(f[-1])
    return [cv2.cvtColor(x, cv2.COLOR_BGR2RGB).astype(np.float32) / 255 for x in out]


# ---------------------------------------------------------------- voice
def voice_chatterbox(scenes, idxs, project, cfg=None, seed=0):
    """cfg (from channels/<name>.json "voice"): reference = HF path of a voice clip to copy, exaggeration, cfg_weight."""
    import torch, torchaudio, shutil
    from chatterbox.tts import ChatterboxTTS
    cfg = cfg or {}; out = "/tmp/voice"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out); t0 = time.time()
    torch.manual_seed(seed)  # a retry of a bad line gets a different take
    tts = ChatterboxTTS.from_pretrained(device="cuda")
    ref = None
    if cfg.get("reference"):
        from huggingface_hub import hf_hub_download
        ref = hf_hub_download(REPO, cfg["reference"], repo_type="dataset", token=os.environ["HF_TOKEN"])
    for i in idxs:
        wav = tts.generate(scenes[i]["text"], audio_prompt_path=ref,
                           exaggeration=cfg.get("exaggeration", 0.45), cfg_weight=cfg.get("cfg_weight", 0.5))
        torchaudio.save(f"{out}/a_{i:03d}.wav", wav, tts.sr); print("voice", i, flush=True)
    _push(out, project, "voice_chatterbox")
    return {"model": "chatterbox", "done": list(idxs), "seconds": round(time.time() - t0), "reference": cfg.get("reference")}


def voice_qwen3tts(scenes, idxs, project, cfg=None, seed=0):
    """cfg: speaker (default Aiden), instruct (speaking style), or reference + reference_text = HF path of a voice clip to clone."""
    import torch, soundfile as sf, shutil
    from qwen_tts import Qwen3TTSModel
    from huggingface_hub import hf_hub_download
    cfg = cfg or {}; m = VOICE["qwen3tts"]; out = "/tmp/voice"; shutil.rmtree(out, ignore_errors=True); os.makedirs(out); t0 = time.time()
    torch.manual_seed(seed)
    clone = bool(cfg.get("reference") and cfg.get("reference_text"))
    tts = Qwen3TTSModel.from_pretrained(m["clone_repo"] if clone else m["repo"], device_map="cuda:0", dtype=torch.bfloat16, attn_implementation="sdpa")
    if clone:
        ref = hf_hub_download(REPO, cfg["reference"], repo_type="dataset", token=os.environ["HF_TOKEN"])
        prompt = tts.create_voice_clone_prompt(ref_audio=ref, ref_text=cfg["reference_text"], x_vector_only_mode=False)
    style = cfg.get("instruct", "Calm, warm documentary narrator. Clear, curious and engaging, natural pauses, medium pace.")
    for i in idxs:
        if clone: wavs, sr = tts.generate_voice_clone(text=scenes[i]["text"], language="English", voice_clone_prompt=prompt)
        else: wavs, sr = tts.generate_custom_voice(text=scenes[i]["text"], language="English", speaker=cfg.get("speaker", "Aiden"), instruct=style)
        sf.write(f"{out}/a_{i:03d}.wav", wavs[0], sr); print("voice", i, flush=True)
    _push(out, project, "voice_qwen3tts")
    return {"model": "qwen3tts", "done": list(idxs), "seconds": round(time.time() - t0), "reference": cfg.get("reference")}


def wer(ref, hyp):
    """Word error rate between the script line and what Whisper heard."""
    import re
    a, b = (re.sub(r"[^a-z0-9' ]", " ", x.lower()).split() for x in (ref, hyp))
    d = list(range(len(b) + 1))
    for i, x in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, y in enumerate(b, 1): prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (x != y))
    return d[len(b)] / max(1, len(a))


def voice_check(scenes, project, voice_model, limit=0.2):
    """Transcribes every voice line; returns the lines Whisper heard wrong (skipped words, mumbling, repeats)."""
    from faster_whisper import WhisperModel
    d = _pull(project, f"voice_{voice_model}", "/tmp/vc")
    m = WhisperModel("small.en", device="cpu", compute_type="int8", download_root="/cache/whisper", cpu_threads=16)
    bad = {}
    for i, s in enumerate(scenes):
        segs, _ = m.transcribe(f"{d}/a_{i:03d}.wav", vad_filter=False)
        e = wer(s["text"], " ".join(x.text for x in segs))
        if e > limit: bad[i] = round(e, 2)
    return bad


# ---------------------------------------------------------------- music
def music(model, project, seconds=180, prompt=None):
    """Instrumental bed (looped by the editor under the voice)."""
    import torch, soundfile as sf
    from diffusers import AceStepPipeline
    t0 = time.time(); out = "/tmp/music"; os.makedirs(out, exist_ok=True)
    pipe = AceStepPipeline.from_pretrained(MUSIC[model]["repo"], dtype=torch.bfloat16).to("cuda")
    prompt = prompt or ("calm ambient documentary underscore, soft analog synth pads, gentle felt piano, subtle pulse, "
                        "curious and wondering mood, slow tempo, instrumental, no vocals")
    a = pipe(prompt=prompt, lyrics="[Instrumental]", audio_duration=float(seconds), generator=torch.Generator("cuda").manual_seed(1)).audios
    sf.write(f"{out}/music.wav", a[0].T.cpu().float().numpy(), pipe.sample_rate)
    _push(out, project, "music")
    return {"model": model, "seconds": round(time.time() - t0)}
