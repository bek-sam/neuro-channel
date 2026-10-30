"""Kaggle batch provider: free T4 x2 GPUs (about 30 h a week). Pushes ONE script kernel that makes many items, polls it,
downloads the results. Inputs travel inside the script (prompts), so no Hugging Face token is ever sent to Kaggle.
  run_images(jobs, out_dir, log)   jobs = [(file_name, prompt, seed)] -> out_dir/<file_name>
Measured on T4: Qwen-Image 20B (offloaded) 29 min/image -> unusable; Z-Image-Turbo 6B: see SEC below."""
import os, json, time, glob, shutil, subprocess, tempfile
USER = os.environ.get("KAGGLE_USER", "bekbolsunsamaganov")
ACC = os.environ.get("KAGGLE_ACC", "NvidiaTeslaT4")  # NvidiaL4 if the account may use it
SEC = {"zimage": 60}  # (e) per image on T4; replaced by the measured value after the first run

IMAGE_SCRIPT = r'''
import subprocess, json, time, os, sys, traceback
subprocess.run("pip install -q -U diffusers transformers accelerate", shell=True)
import torch
from diffusers import ZImagePipeline
JOBS, W, H = json.loads(__JOBS__), __W__, __H__
os.makedirs("/kaggle/working/out", exist_ok=True); t0 = time.time()
gpu = torch.cuda.get_device_name(0); print("gpu", gpu, torch.cuda.device_count(), flush=True)
# Z-Image overflows in fp16 (black images), and a T4 (sm75) has no bf16 flash attention -> one 7 GB attention matrix
# at 1920x1088. Keep bf16 and run attention in chunks of 1024 queries instead (same result, ~0.5 GB at a time).
dt = torch.bfloat16
import torch.nn.functional as F
_sdpa = F.scaled_dot_product_attention
def _chunked(*a, **kw):  # called both positionally and as query=, key=, value=, attn_mask=
    kw.update(zip(("query", "key", "value", "attn_mask", "dropout_p", "is_causal", "scale"), a))
    q, m = kw["query"], kw.get("attn_mask"); L = q.shape[-2]
    if L <= 2048: return _sdpa(**kw)
    out = []
    for s in range(0, L, 1024):
        part = dict(kw, query=q[..., s:s + 1024, :])
        if m is not None and m.dim() >= 2 and m.shape[-2] == L: part["attn_mask"] = m[..., s:s + 1024, :]
        out.append(_sdpa(**part))
    return torch.cat(out, dim=-2)
if torch.cuda.get_device_capability(0)[0] < 8: F.scaled_dot_product_attention = _chunked
try:
    pipe = ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo", torch_dtype=dt, device_map="balanced"); print("balanced", pipe.hf_device_map)
except Exception as e:
    print("balanced failed:", e); pipe = ZImagePipeline.from_pretrained("Tongyi-MAI/Z-Image-Turbo", torch_dtype=dt); pipe.enable_model_cpu_offload()
pipe.vae.enable_tiling()  # the 1080p decode needed 4.5 GB more on the text-encoder GPU
def fp8():  # 12.4 GB of bf16 weights can leave too little room on a 16 GB T4 -> store fp8, compute bf16 (slower)
    pipe.transformer.enable_layerwise_casting(storage_dtype=torch.float8_e4m3fn, compute_dtype=torch.bfloat16)
    torch.cuda.empty_cache(); print("switched to fp8 storage", flush=True)
print("loaded", round(time.time() - t0), "s", flush=True)
def gen(prompt, seed):
    return pipe(prompt=prompt, width=W, height=H, num_inference_steps=9, guidance_scale=0.0,
                generator=torch.Generator("cuda").manual_seed(seed)).images[0]
casted = False
for name, prompt, seed in JOBS:
    t = time.time()
    try:
        try: im = gen(prompt, seed)
        except torch.OutOfMemoryError:
            if casted: raise
            torch.cuda.empty_cache(); fp8(); casted = True; t = time.time(); im = gen(prompt, seed)
        import numpy as np
        if np.asarray(im).mean() < 2: print("black image", name, flush=True); continue
        im.save(f"/kaggle/working/out/{name}")
        print("done", name, round(time.time() - t, 1), "s", flush=True)
    except Exception: traceback.print_exc()
print("total", round(time.time() - t0), "s")
'''


def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)


def _push(slug, code, gpu=True, acc=None):
    d = tempfile.mkdtemp()
    open(f"{d}/job.py", "w").write(code)
    json.dump({"id": f"{USER}/{slug}", "title": slug, "code_file": "job.py", "language": "python", "kernel_type": "script",
               "is_private": True, "enable_gpu": gpu, "enable_internet": True, "dataset_sources": [], "competition_sources": [],
               "kernel_sources": []}, open(f"{d}/kernel-metadata.json", "w"))
    r = sh(f"kaggle kernels push -p {d}" + (f" --accelerator {acc or ACC}" if gpu else ""))
    if "successfully" not in r.stdout.lower() and "pushed" not in r.stdout.lower(): raise RuntimeError(f"kaggle push: {r.stdout[-300:]} {r.stderr[-300:]}")
    return f"{USER}/{slug}"


def _wait(ref, log, timeout=6 * 3600):
    t0 = time.time()
    while time.time() - t0 < timeout:
        time.sleep(30)
        s = sh(f"kaggle kernels status {ref}").stdout
        if "COMPLETE" in s.upper(): return True
        if "ERROR" in s.upper() or "CANCEL" in s.upper(): log("kaggle", ref, time.time() - t0, f"kernel failed: {s.strip()[-200:]}"); return False
    return False


def run_images(jobs, out_dir, log, slug="vg-zimage", acc=None, size=(1440, 816)):
    """Makes every (name, prompt, seed) on one Kaggle T4 x2 kernel. Returns the names that came back."""
    if not jobs: return []
    t0 = time.time()
    code = IMAGE_SCRIPT.replace("__JOBS__", repr(json.dumps(jobs))).replace("__W__", str(size[0])).replace("__H__", str(size[1]))
    ref = _push(slug, code, acc=acc)
    print(f"kaggle: pushed {ref} with {len(jobs)} images", flush=True)
    ok = _wait(ref, log)
    d = tempfile.mkdtemp(); sh(f"kaggle kernels output {ref} -p {d}")
    got = []
    for name, _, _ in jobs:
        f = glob.glob(f"{d}/**/{name}", recursive=True)
        if f: shutil.move(f[0], f"{out_dir}/{name}"); got.append(name)
    logf = glob.glob(f"{d}/*.log")
    if logf:
        import re
        shutil.copy(logf[0], f"{out_dir}/../kaggle_{slug}.log")
        for name, sec in re.findall(r"done (\S+\.png) ([0-9.]+) s", open(logf[0]).read()):
            if name in got: log(f"img {int(name[4:7])}{'_b' if '_b' in name else ''}" if name.startswith("img_") else name, "kaggle_zimage", float(sec))
    log("kaggle batch", "kaggle_zimage", time.time() - t0, None if got else f"no images back (kernel ok={ok})")
    return got
