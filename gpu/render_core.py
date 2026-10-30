import os; os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
import subprocess, json, glob, time, gc, traceback

def render(SCENES, IDXS, W):
    """Make clips for scene numbers IDXS into W/imgs and W/clips. Same code on every GPU provider."""
    import torch
    from diffusers import StableDiffusionXLPipeline, AutoencoderKL, LTXImageToVideoPipeline
    from diffusers.utils import export_to_video
    from transformers import CLIPModel, CLIPProcessor
    os.makedirs(f"{W}/imgs", exist_ok=True); os.makedirs(f"{W}/clips", exist_ok=True)
    STYLE = ", cinematic scientific visualization, photorealistic 3D render, dark background, volumetric light, shallow depth of field, ultra detailed, 8k"
    NEG_I = "text, letters, watermark, logo, cartoon, low quality, blurry, deformed, ugly, jpeg artifacts, frame, border"
    NEG_V = "blurry, distorted, morphing, melting, flicker, text, watermark, low quality, static"
    log = lambda *a: print(*a, flush=True)
    T0 = time.time()

    # ---------- 1. images: SDXL, 2 candidates, CLIP picks best ----------
    vae = AutoencoderKL.from_pretrained("madebyollin/sdxl-vae-fp16-fix", torch_dtype=torch.float16)
    sd = StableDiffusionXLPipeline.from_pretrained("stabilityai/stable-diffusion-xl-base-1.0", vae=vae,
                                                    torch_dtype=torch.float16, variant="fp16").to("cuda")
    clip = CLIPModel.from_pretrained("openai/clip-vit-large-patch14", torch_dtype=torch.float16).to("cuda")
    cp = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
    picks = {}
    for i in IDXS:
        s = SCENES[i]
        try:
            ims = [sd(s["prompt"] + STYLE, negative_prompt=NEG_I, width=1344, height=768, num_inference_steps=35,
                      guidance_scale=6.0, generator=torch.Generator("cuda").manual_seed(1000 * i + c)).images[0] for c in range(2)]
            with torch.no_grad():
                x = cp(text=[s["prompt"][:300]], images=ims, return_tensors="pt", padding=True, truncation=True).to("cuda")
                score = clip(**{k: (v.half() if v.dtype == torch.float32 else v) for k, v in x.items()}).logits_per_image[:, 0]
            best = int(score.argmax()); ims[best].save(f"{W}/imgs/img_{i:03d}.png")
            picks[i] = [round(float(v), 2) for v in score]; log("img", i, picks[i], "->", best)
        except Exception: traceback.print_exc()
    json.dump(picks, open(f"{W}/picks.json", "w"))
    del sd, vae, clip; gc.collect(); torch.cuda.empty_cache()
    log("images done", round(time.time() - T0), "s")

    # ---------- 2. animate: LTX image-to-video ----------
    p = LTXImageToVideoPipeline.from_pretrained("Lightricks/LTX-Video-0.9.5", torch_dtype=torch.float16)
    p.enable_model_cpu_offload(); p.vae.enable_tiling()
    from PIL import Image
    for i in IDXS:
        s = SCENES[i]
        f = f"{W}/imgs/img_{i:03d}.png"
        if not os.path.exists(f): continue
        try:
            t = time.time()
            v = p(image=Image.open(f).resize((960, 544)), prompt=s.get("motion", s["prompt"]) + ", smooth slow cinematic motion",
                  negative_prompt=NEG_V, width=960, height=544, num_frames=97, num_inference_steps=40,
                  generator=torch.Generator("cuda").manual_seed(i)).frames[0]
            export_to_video(v, f"{W}/clips/raw_{i:03d}.mp4", fps=24); log("clip", i, round(time.time() - t), "s")
        except Exception: traceback.print_exc(); gc.collect(); torch.cuda.empty_cache()
    del p; gc.collect(); torch.cuda.empty_cache()
    log("clips done", round(time.time() - T0), "s")

    # ---------- 3. upscale x2: Real-ESRGAN ----------
    try:
        import imageio, numpy as np, urllib.request
        from spandrel import ModelLoader
        urllib.request.urlretrieve("https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x2plus.pth", "/tmp/x2.pth")
        up = ModelLoader().load_from_file("/tmp/x2.pth").cuda().eval().half()
        for f in sorted(glob.glob(f"{W}/clips/raw_*.mp4")):
            t = time.time(); out = f.replace("raw_", "clip_")
            frames = imageio.v3.imread(f)
            res = []
            with torch.no_grad():
                for b in range(0, len(frames), 8):
                    x = torch.from_numpy(frames[b:b + 8]).cuda().half().permute(0, 3, 1, 2) / 255
                    res.append((up(x).clamp(0, 1) * 255).byte().permute(0, 2, 3, 1).cpu().numpy())
            imageio.v3.imwrite(out, np.concatenate(res), fps=24, codec="libx264", quality=9)
            os.remove(f); log("up", os.path.basename(out), round(time.time() - t), "s")
    except Exception:
        traceback.print_exc()
        for f in glob.glob(f"{W}/clips/raw_*.mp4"): os.rename(f, f.replace("raw_", "clip_"))
    log("ALL DONE", round(time.time() - T0), "s")
