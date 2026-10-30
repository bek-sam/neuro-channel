"""Deploy once:  modal deploy gpu/modal_app.py
Runs render_core.render() on an A100. Models are cached in a Modal Volume (download once)."""
import modal, os

app = modal.App("video-gen-render")
image = (modal.Image.debian_slim(python_version="3.11")
         .apt_install("ffmpeg", "libgl1", "libglib2.0-0")
         .pip_install("torch", "diffusers", "transformers", "accelerate", "sentencepiece",
                      "imageio", "imageio-ffmpeg", "spandrel", "pillow", "numpy")
         .add_local_file(os.path.join(os.path.dirname(__file__), "render_core.py"), "/root/render_core.py"))
cache = modal.Volume.from_name("video-gen-cache", create_if_missing=True)


@app.function(image=image, gpu="A100-40GB", timeout=6 * 3600, volumes={"/cache": cache},
              secrets=[], max_containers=2)
def render_scenes(scenes: list, idxs: list) -> dict:
    import sys, glob, time
    os.environ["HF_HOME"] = "/cache/hf"
    sys.path.insert(0, "/root")
    from render_core import render
    t = time.time()
    render(scenes, idxs, "/tmp/out")
    cache.commit()
    out = {}
    for f in glob.glob("/tmp/out/clips/clip_*.mp4") + glob.glob("/tmp/out/imgs/img_*.png"):
        out[os.path.basename(f)] = open(f, "rb").read()
    out["_seconds.txt"] = str(round(time.time() - t)).encode()
    return out
