"""After Kaggle render finishes: python3 finish.py <project>  -> download, edit, save to HF"""
import os, sys, subprocess
H = os.path.dirname(os.path.abspath(__file__)); P = sys.argv[1]; D = f"{H}/projects/{P}"
USER, HF_REPO = "bekbolsunsamaganov", "bekbol446/neuro-channel"
for l in open(f"{H}/keys.env"):
    if "=" in l: k, v = l.strip().split("=", 1); os.environ[k] = v
s = subprocess.run(f"kaggle kernels status {USER}/render-{P}", shell=True, capture_output=True, text=True).stdout
print(s.strip())
if "COMPLETE" not in s and "ERROR" not in s: sys.exit("not finished yet")
subprocess.run(f"kaggle kernels output {USER}/render-{P} -p {D}", shell=True, check=True, capture_output=True)
print("clips:", len([f for f in os.listdir(f"{D}/clips") if f.startswith("clip_")]) if os.path.isdir(f"{D}/clips") else 0)
subprocess.run(f"python3 {H}/assemble.py {D}", shell=True, check=True)
from huggingface_hub import HfApi
a = HfApi()
a.upload_file(path_or_fileobj=f"{D}/final.mp4", path_in_repo=f"videos/{P}.mp4", repo_id=HF_REPO, repo_type="dataset")
if os.path.isdir(f"{D}/clips"):
    a.upload_folder(folder_path=f"{D}/clips", path_in_repo=f"library/{P}", repo_id=HF_REPO, repo_type="dataset", allow_patterns="clip_*.mp4")
a.upload_file(path_or_fileobj=f"{D}/scenes.json", path_in_repo=f"scripts/{P}.json", repo_id=HF_REPO, repo_type="dataset")
print("DONE ->", f"{D}/final.mp4")
