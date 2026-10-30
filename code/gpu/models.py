"""Model registry: every image / video / voice model the pipeline can use.
quality: 1-10 (from our own tests)   sec: GPU seconds per item, measured where marked (m), (e) = estimate, not measured yet
gpu: Modal GPU type    gated: accept the license on its Hugging Face page once    fps: the model's native frame rate"""

IMAGE = {
    "sdxl":          dict(repo="stabilityai/stable-diffusion-xl-base-1.0", gpu="A10G",      quality=5, sec=30,  gated=False, note="old, plastic look"),
    "flux2_klein9b": dict(repo="black-forest-labs/FLUX.2-klein-9B",        gpu="A100-40GB", quality=8, sec=15,  gated=True,  note="untested; arena Elo 929, below qwen21"),
    "flux3_klein":   dict(repo="black-forest-labs/flux-3-image-klein",     gpu="A100-40GB", quality=9, sec=8,   gated=True,  note="(e) untested; arena Elo 1043 ~ qwen21; accept licence on HF first"),
    "qwen21":        dict(repo="Qwen/Qwen-Image-2.1",                      gpu="A100-40GB", quality=9, sec=60,  gated=False, note="(m) best anatomy; also renders title text for thumbnails"),
    "qwen21_turbo":  dict(repo="Qwen/Qwen-Image-2.1-Turbo",                gpu="A100-40GB", quality=9, sec=15,  gated=False, note="(e) same model, 8-step distilled"),
}

VIDEO = {  # image-to-video
    "ltx095":     dict(repo="Lightricks/LTX-Video-0.9.5",                                 gpu="A10G",      quality=4, sec=120, fps=24, w=960,  h=544, frames=97,  gated=False, note="(m) weak, melts"),
    "wan22_5b":   dict(repo="Wan-AI/Wan2.2-TI2V-5B-Diffusers",                            gpu="A100-40GB", quality=6, sec=490, fps=24, w=1280, h=704, frames=121, gated=False, note="(m) stable but almost still"),
    "hunyuan15":  dict(repo="hunyuanvideo-community/HunyuanVideo-1.5-Diffusers-720p_i2v", gpu="A100-80GB", quality=8, sec=2800, fps=24, w=1280, h=720, frames=61, gated=False, note="(m) nice glow, far too slow"),
    "ltx25":      dict(repo="Lightricks/LTX-2.5-Diffusers",                               gpu="H100",      quality=8, sec=120, fps=24, w=1280, h=704, frames=121, gated=True,  note="untested; accept licence on HF first"),
    "wan22_a14b": dict(repo="Wan-AI/Wan2.2-I2V-A14B-Diffusers",                           gpu="H100",      quality=9, sec=900, fps=16, w=1280, h=720, frames=81,  gated=False, note="(m) best motion; 81 frames @16fps = 5s"),
    # same model + lightx2v 4-step distill LoRAs (one per expert), no CFG
    "wan22_a14b_4step": dict(repo="Wan-AI/Wan2.2-I2V-A14B-Diffusers", gpu="H100", quality=8, sec=150, fps=16, w=1280, h=720, frames=81, gated=False,
                             steps=4, cfg=1.0, lora="lightx2v/Wan2.2-Distill-Loras",
                             lora_high="wan2.2_i2v_A14b_high_noise_lora_rank64_lightx2v_4step_1022.safetensors",
                             lora_low="wan2.2_i2v_A14b_low_noise_lora_rank64_lightx2v_4step_1022.safetensors", note="(e) ~6x faster"),
}

VOICE = {  # sec = GPU seconds per scene line
    "kokoro":     dict(gpu=None,   sec=0,  quality=6, note="fast, clear, a bit flat; runs on CPU"),
    "chatterbox": dict(gpu="A10G", sec=20, quality=8, note="(m) more natural; ~20s per line"),
    "qwen3tts":   dict(gpu="A10G", sec=10, quality=8, repo="Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice", clone_repo="Qwen/Qwen3-TTS-12Hz-1.7B-Base",
                       note="(e) style set by an instruction; clones a reference voice with the Base model"),
}

MUSIC = {"acestep": dict(repo="ACE-Step/acestep-v15-xl-turbo-diffusers", gpu="A10G", sec=60, note="(e) instrumental bed, looped under the voice")}

# Modal price per GPU-hour (approx.)
PRICE = {"A10G": 1.10, "A100-40GB": 2.10, "A100-80GB": 2.50, "H100": 3.95, "CPU": 0.20}

# Profiles. "hero" scenes get real AI motion; every other scene uses a slow camera move (Ken Burns)
# over the high-quality still images, which costs no GPU and looks like a documentary.
# candidates: images made per scene (best 2 kept)   music: None = assets/music.mp3 if present
PROFILES = {
    "free":     dict(image="qwen21", hero_video=None,         rest_video=None,       heroes=0,  voice="kokoro"),
    "standard": dict(image="qwen21", hero_video="wan22_a14b", rest_video=None,       heroes=4,  voice="chatterbox"),
    "max":      dict(image="qwen21", hero_video="wan22_a14b", rest_video=None,       heroes=10, voice="chatterbox"),
    "max_all":  dict(image="qwen21", hero_video="wan22_a14b", rest_video="wan22_a14b", heroes=10, voice="chatterbox"),
    # research upgrades (Oct 2026): distilled image + video models, new voice, generated music, best of 4 images
    "turbo":    dict(image="qwen21_turbo", hero_video="wan22_a14b_4step", rest_video=None, heroes=15, voice="qwen3tts",
                     candidates=4, music="acestep"),
}
FALLBACK = {"image": ["qwen21_turbo", "qwen21", "sdxl"], "video": ["wan22_a14b_4step", "wan22_a14b", "wan22_5b"],
            "voice": ["qwen3tts", "chatterbox", "kokoro"]}


def pick_heroes(n_scenes, heroes, marked=()):
    """Scenes marked hero:true first, then the first 2 (the hook), then spread evenly."""
    out = list(dict.fromkeys(list(marked) + list(range(min(2, n_scenes)))))
    step = max(1, n_scenes // max(1, heroes))
    for i in range(2, n_scenes, step):
        if len(out) >= heroes: break
        if i not in out: out.append(i)
    return sorted(out[:heroes])


def parts(p, n_scenes):
    """(model, how many items) for every GPU job of one video."""
    out = [(IMAGE[p["image"]], n_scenes * p.get("candidates", 2) + 1)]  # candidates per scene + thumbnail
    h = min(p["heroes"], n_scenes)
    if p["hero_video"]: out.append((VIDEO[p["hero_video"]], h))
    if p["rest_video"]: out.append((VIDEO[p["rest_video"]], n_scenes - h))
    if VOICE[p["voice"]]["gpu"]: out.append((VOICE[p["voice"]], n_scenes))
    if p.get("music"): out.append((MUSIC[p["music"]], 1))
    return out


def estimate_usd(p, n_scenes):
    """Modal dollars for one video with profile dict p (model download not included)."""
    return round(sum(m["sec"] * k / 3600 * PRICE[m["gpu"]] for m, k in parts(p, n_scenes)) + 0.10, 2)  # + editor CPU


def estimate(profile, n_scenes):
    """GPU minutes and Modal dollars for one video."""
    p = PROFILES[profile]
    return round(sum(m["sec"] * k for m, k in parts(p, n_scenes)) / 60), estimate_usd(p, n_scenes)


if __name__ == "__main__":
    for pr in PROFILES:
        mins, usd = estimate(pr, 44)
        print(f"{pr:9} ~{mins:4} GPU-min  ~${usd:5}   {PROFILES[pr]}")
