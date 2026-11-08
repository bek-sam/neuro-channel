"""One motion clip per call on a Modal H100: Wan2.2-I2V-A14B + lightx2v 4-step LoRAs, 1280x720, 81 frames @16 fps (5 s).
Used by providers.ModalWan, after the free ZeroGPU quota runs out. Weights are cached on the same volume as code/gpu.
    modal deploy code/free/modal_clip.py          (once, and after any change here)
The container stays warm for 2 minutes after a call, so clips in a row pay the ~3 min model load once."""
import modal

app = modal.App("neuro-clip")
image = (modal.Image.debian_slim(python_version="3.11").apt_install("ffmpeg", "git")
         .pip_install("torch", "transformers", "accelerate", "sentencepiece", "ftfy", "imageio", "imageio-ffmpeg", "pillow",
                      "numpy", "huggingface_hub", "hf_transfer", "peft")
         .pip_install("diffusers @ git+https://github.com/huggingface/diffusers@main")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache/hf", "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True"}))
cache = modal.Volume.from_name("video-gen-cache", create_if_missing=True)

REPO, W, H, FRAMES, FPS, STEPS = "Wan-AI/Wan2.2-I2V-A14B-Diffusers", 1280, 720, 81, 16, 4
LORA = "lightx2v/Wan2.2-Distill-Loras"
LORA_HI = "wan2.2_i2v_A14b_high_noise_lora_rank64_lightx2v_4step_1022.safetensors"
LORA_LO = "wan2.2_i2v_A14b_low_noise_lora_rank64_lightx2v_4step_1022.safetensors"
NEG = "blurry, distorted, morphing, melting, flicker, text, watermark, low quality, static, jittery"


@app.cls(gpu="H100", image=image, volumes={"/cache": cache}, timeout=1800, scaledown_window=120, max_containers=1)
class Wan:
    @modal.enter()
    def load(self):
        import torch
        from diffusers import WanImageToVideoPipeline
        pipe = WanImageToVideoPipeline.from_pretrained(REPO, torch_dtype=torch.bfloat16)
        # distill LoRAs: high-noise expert -> transformer, low-noise expert -> transformer_2, then fused (no LoRA cost per step)
        pipe.load_lora_weights(LORA, weight_name=LORA_HI, adapter_name="hi")
        pipe.load_lora_weights(LORA, weight_name=LORA_LO, adapter_name="lo", load_into_transformer_2=True)
        pipe.fuse_lora(adapter_names=["hi"], lora_scale=1.0, components=["transformer"])
        pipe.fuse_lora(adapter_names=["lo"], lora_scale=1.0, components=["transformer_2"])
        pipe.unload_lora_weights()
        pipe.enable_model_cpu_offload()  # two 14B experts + the text encoder do not fit in 80 GB together with 720p activations
        pipe.vae.enable_tiling()
        self.pipe = pipe
        cache.commit()  # first run: keep the downloaded weights for the next container

    @modal.method()
    def clip(self, image_png: bytes, prompt: str, seed: int) -> bytes:
        import io, os, subprocess, tempfile, torch
        from PIL import Image
        from diffusers.utils import export_to_video
        im = Image.open(io.BytesIO(image_png)).convert("RGB").resize((W, H))
        frames = self.pipe(image=im, prompt=prompt, negative_prompt=NEG, width=W, height=H, num_frames=FRAMES,
                           num_inference_steps=STEPS, guidance_scale=1.0, guidance_scale_2=1.0,
                           generator=torch.Generator("cuda").manual_seed(seed)).frames[0]
        d = tempfile.mkdtemp()
        export_to_video(frames, f"{d}/raw.mp4", fps=FPS)
        subprocess.run(f"ffmpeg -loglevel error -y -i {d}/raw.mp4 -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p {d}/clip.mp4",
                       shell=True, check=True)
        data = open(f"{d}/clip.mp4", "rb").read()
        os.remove(f"{d}/raw.mp4"); os.remove(f"{d}/clip.mp4")
        return data
