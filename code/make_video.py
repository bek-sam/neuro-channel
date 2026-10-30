"""One command: python3 make_video.py <project>   (needs projects/<project>/scenes.json)
scenes.json -> Kaggle GPU (SDXL images, CLIP pick, LTX animation, Real-ESRGAN) -> voice + edit -> Hugging Face"""
import json, os, subprocess, sys, shutil, time
H = os.path.dirname(os.path.abspath(__file__)); P = sys.argv[1]; D = f"{H}/projects/{P}"
USER, HF_REPO = "bekbolsunsamaganov", "bekbol446/video_gen"
def sh(c, **k): print("$", c[:120], flush=True); return subprocess.run(c, shell=True, check=True, text=True, capture_output=True, **k).stdout
for l in open(f"{H}/keys.env"):
    if "=" in l: k, v = l.strip().split("=", 1); os.environ[k] = v
scenes = json.load(open(f"{D}/scenes.json")); print(len(scenes), "scenes")
# 1. scenes -> Kaggle dataset
ds = f"{D}/_ds"; shutil.rmtree(ds, True); os.makedirs(ds); shutil.copy(f"{D}/scenes.json", ds)
json.dump({"title": f"video-gen-{P}", "id": f"{USER}/video-gen-{P}", "licenses": [{"name": "CC0-1.0"}]}, open(f"{ds}/dataset-metadata.json", "w"))
try: sh(f"kaggle datasets create -p {ds}")
except subprocess.CalledProcessError: sh(f"kaggle datasets version -p {ds} -m update")
time.sleep(60)
# 2. render job on Kaggle GPU
k = f"{D}/_k"; shutil.rmtree(k, True); os.makedirs(k); shutil.copy(f"{H}/kR/render.py", k)
json.dump({"id": f"{USER}/render-{P}", "title": f"render-{P}", "code_file": "render.py", "language": "python", "kernel_type": "script",
           "is_private": True, "enable_gpu": True, "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
           "dataset_sources": [f"{USER}/video-gen-{P}"], "competition_sources": [], "kernel_sources": []}, open(f"{k}/kernel-metadata.json", "w"))
print(sh(f"kaggle kernels push -p {k}"))
time.sleep(90)
while True:
    s = sh(f"kaggle kernels status {USER}/render-{P}"); print(time.strftime("%T"), s.strip()[-30:], flush=True)
    if any(x in s for x in ["COMPLETE", "ERROR", "CANCEL"]): break
    time.sleep(120)
# 3. download
sh(f"kaggle kernels output {USER}/render-{P} -p {D}")
# 4. voice + subtitles + edit
print(sh(f"python3 {H}/assemble.py {D}"))
# 5. save to Hugging Face
from huggingface_hub import HfApi
a = HfApi()
a.upload_file(path_or_fileobj=f"{D}/final.mp4", path_in_repo=f"videos/{P}.mp4", repo_id=HF_REPO, repo_type="dataset")
a.upload_folder(folder_path=f"{D}/clips", path_in_repo=f"library/{P}", repo_id=HF_REPO, repo_type="dataset", allow_patterns="clip_*.mp4")
a.upload_file(path_or_fileobj=f"{D}/scenes.json", path_in_repo=f"scripts/{P}.json", repo_id=HF_REPO, repo_type="dataset")
print("DONE ->", f"{D}/final.mp4")
