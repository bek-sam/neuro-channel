"""Multi-GPU manager.
  python3 manager.py start  <project>   split scenes across available providers and submit
  python3 manager.py poll   <project>   check jobs, collect results, retry failed scenes elsewhere
  python3 manager.py finish <project>   voice + edit + save to Hugging Face (runs when all jobs are done)
  python3 manager.py status <project>
State is saved in projects/<project>/state.json, so it survives restarts."""
import os, sys, json, time, subprocess
H = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, f"{H}/gpu")
for l in open(f"{H}/keys.env"):
    if "=" in l: k, v = l.strip().split("=", 1); os.environ[k] = v
from providers import ALL
HF_REPO = "bekbol446/neuro-channel"
cmd, P = sys.argv[1], sys.argv[2]; D = f"{H}/projects/{P}"; SF = f"{D}/state.json"
load = lambda: json.load(open(SF)) if os.path.exists(SF) else {"jobs": [], "tried": {}, "done": []}
save = lambda s: json.dump(s, open(SF, "w"), indent=1)
PROV = {p.name: p for p in ALL}
HOOK = 3  # first scenes are most important -> fastest provider


def split(idxs, provs):
    """Give each provider a share by speed so they all finish at about the same time. Hook scenes go to the fastest."""
    speed = {p.name: 1 / p.sec_per_scene for p in provs}; tot = sum(speed.values())
    out = {p.name: [] for p in provs}
    hook, rest = [i for i in idxs if i < HOOK], [i for i in idxs if i >= HOOK]
    out[provs[0].name] += hook
    for i in rest:  # greedy: put scene where projected finish time is lowest
        best = min(provs, key=lambda p: (len(out[p.name]) + 1) * p.sec_per_scene)
        out[best.name].append(i)
    return {k: v for k, v in out.items() if v}


def submit(st, idxs, exclude=()):
    provs = [p for p in ALL if p.available() and p.name not in exclude]
    if not provs: print("no provider left for", idxs); return
    for name, part in split(idxs, provs).items():
        try:
            job = PROV[name].submit(P, D, part); st["jobs"].append(job)
            for i in part: st["tried"].setdefault(str(i), []).append(name)
            print(f"-> {name}: {len(part)} scenes  ~{len(part) * PROV[name].sec_per_scene / 60:.0f} min")
        except Exception as e:
            print(f"{name} submit failed: {e}"); submit(st, part, exclude=tuple(exclude) + (name,))


def log_usage(job):
    secs = job.get("gpu_seconds") or (time.time() - job["t0"])
    u_f = f"{H}/usage.json"; u = json.load(open(u_f)) if os.path.exists(u_f) else []
    u.append({"provider": job["provider"], "project": P, "scenes": len(job["idxs"]), "hours": round(secs / 3600, 2),
              "cost_usd": round(secs / 3600 * PROV[job["provider"]].cost_per_hr, 2), "date": time.strftime("%F")})
    json.dump(u, open(u_f, "w"), indent=1)


scenes = json.load(open(f"{D}/scenes.json")); st = load()
if cmd == "start":
    print("providers available:", [p.name for p in ALL if p.available()])
    submit(st, list(range(len(scenes)))); save(st)

elif cmd == "poll":
    for job in [j for j in st["jobs"] if j.get("state") not in ("collected", "failed")]:
        s = PROV[job["provider"]].poll(job); print(job["provider"], job["ref"], s)
        if s == "done":
            PROV[job["provider"]].fetch(job, D); job["state"] = "collected"; log_usage(job)
        elif s == "failed":
            job["state"] = "failed"
    have = {int(f[5:8]) for f in os.listdir(f"{D}/clips")} if os.path.isdir(f"{D}/clips") else set()
    busy = {i for j in st["jobs"] if j.get("state") not in ("collected", "failed") for i in j["idxs"]}
    missing = [i for i in range(len(scenes)) if i not in have and i not in busy]
    retry = [i for i in missing if len(st["tried"].get(str(i), [])) < 2]
    if retry:  # failed scenes go to a provider that hasn't tried them
        tried = set(sum((st["tried"][str(i)] for i in retry), []))
        print("retrying", retry, "excluding", tried); submit(st, retry, exclude=tried)
    save(st)
    left = [j for j in st["jobs"] if j.get("state") not in ("collected", "failed")]
    print(f"clips: {len(have)}/{len(scenes)}  jobs running: {len(left)}")
    print("READY" if not left else "WAITING")

elif cmd == "finish":
    subprocess.run(f"python3 {H}/assemble.py {D}", shell=True, check=True)
    from huggingface_hub import HfApi
    a = HfApi()
    a.upload_file(path_or_fileobj=f"{D}/final.mp4", path_in_repo=f"videos/{P}.mp4", repo_id=HF_REPO, repo_type="dataset")
    if os.path.isdir(f"{D}/clips"):
        a.upload_folder(folder_path=f"{D}/clips", path_in_repo=f"library/{P}", repo_id=HF_REPO, repo_type="dataset", allow_patterns="clip_*.mp4")
    for f, dst in ((f"{D}/scenes.json", f"scripts/{P}.json"), (f"{H}/usage.json", "usage.json")):
        if os.path.exists(f): a.upload_file(path_or_fileobj=f, path_in_repo=dst, repo_id=HF_REPO, repo_type="dataset")
    print("DONE ->", f"{D}/final.mp4")

elif cmd == "status":
    for j in st["jobs"]: print(j["provider"], j["ref"], len(j["idxs"]), "scenes", j.get("state", "submitted"))
