"""Deploy:  modal deploy gpu/modal_app2.py      (needs Modal secret "video-gen-hf" with HF_TOKEN)
One function per GPU size. Each can run any model from models.py. Results go straight to Hugging Face."""
import modal, os

HERE = os.path.dirname(__file__)
app = modal.App("video-gen-render2")
# video/image image: no voice packages (avoids torch version clashes)
image = (modal.Image.debian_slim(python_version="3.11")
         .apt_install("ffmpeg", "git")
         .pip_install("torch", "torchvision", "transformers", "accelerate", "sentencepiece", "ftfy",
                      "imageio", "imageio-ffmpeg", "pillow", "numpy", "huggingface_hub", "hf_transfer")
         .pip_install("git+https://github.com/huggingface/diffusers")
         .env({"HF_HUB_ENABLE_HF_TRANSFER": "1", "HF_HOME": "/cache/hf"})
         .add_local_file(f"{HERE}/models.py", "/root/models.py")
         .add_local_file(f"{HERE}/worker.py", "/root/worker.py"))
# voice image: chatterbox brings its own torch version
voice_image = (modal.Image.debian_slim(python_version="3.11")
               .apt_install("ffmpeg")
               .pip_install("chatterbox-tts", "huggingface_hub")
               .env({"HF_HOME": "/cache/hf"})
               .add_local_file(f"{HERE}/models.py", "/root/models.py")
               .add_local_file(f"{HERE}/worker.py", "/root/worker.py"))
cache = modal.Volume.from_name("video-gen-cache", create_if_missing=True)
common = dict(image=image, timeout=6 * 3600, volumes={"/cache": cache},
              secrets=[modal.Secret.from_name("video-gen-hf")], max_containers=3)


def _run(stage, model, scenes, idxs, project):
    import sys; sys.path.insert(0, "/root")
    import worker
    try:
        if stage == "images": r = worker.images(model, scenes, idxs, project)
        elif stage == "videos": r = worker.videos(model, scenes, idxs, project)
        elif stage == "voice": r = worker.voice_chatterbox(scenes, idxs, project)
        else: raise ValueError(stage)
    finally:
        cache.commit()
    return r


@app.function(gpu="A10G", **common)
def run_a10g(stage, model, scenes, idxs, project): return _run(stage, model, scenes, idxs, project)

@app.function(gpu="A100-40GB", **common)
def run_a100_40(stage, model, scenes, idxs, project): return _run(stage, model, scenes, idxs, project)

@app.function(gpu="A100-80GB", **common)
def run_a100_80(stage, model, scenes, idxs, project): return _run(stage, model, scenes, idxs, project)

@app.function(gpu="H100", **common)
def run_h100(stage, model, scenes, idxs, project): return _run(stage, model, scenes, idxs, project)

@app.function(gpu="A10G", image=voice_image, timeout=2 * 3600, volumes={"/cache": cache},
              secrets=[modal.Secret.from_name("video-gen-hf")], max_containers=2)
def run_voice(scenes, idxs, project): return _run("voice", "chatterbox", scenes, idxs, project)

FN = {"A10G": "run_a10g", "A100-40GB": "run_a100_40", "A100-80GB": "run_a100_80", "H100": "run_h100", "voice": "run_voice"}
