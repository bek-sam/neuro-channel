"""GPU providers. Each one: available() -> bool, submit(P, D, idxs) -> job dict, poll(job) -> 'running'|'done'|'failed', fetch(job, D)."""
import os, json, shutil, subprocess, time, glob
H = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE = open(f"{H}/gpu/render_core.py").read()
PIP = "diffusers transformers accelerate sentencepiece imageio imageio-ffmpeg spandrel"

def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)


class Kaggle:
    name, sec_per_scene, cost_per_hr = "kaggle", 330, 0.0       # T4: ~5.5 min per scene (measured)
    user = "bekbolsunsamaganov"
    def available(self): return bool(os.environ.get("KAGGLE_API_TOKEN"))
    def submit(self, P, D, idxs):
        tag = f"{P}-{int(time.time()) % 100000}"
        ds, k = f"{D}/_kds_{tag}", f"{D}/_kk_{tag}"
        for d in (ds, k): shutil.rmtree(d, True); os.makedirs(d)
        shutil.copy(f"{D}/scenes.json", ds); json.dump(idxs, open(f"{ds}/idxs.json", "w"))
        json.dump({"title": f"nd-{tag}", "id": f"{self.user}/nd-{tag}", "licenses": [{"name": "CC0-1.0"}]}, open(f"{ds}/dataset-metadata.json", "w"))
        r = sh(f"kaggle datasets create -p {ds}"); print(r.stdout[-150:], r.stderr[-150:])
        time.sleep(60)
        main = (f'subprocess.run("pip install -q -U {PIP}", shell=True)\n'
                'sj = glob.glob("/kaggle/input/**/scenes.json", recursive=True)[0]\n'
                'render(json.load(open(sj)), json.load(open(sj.replace("scenes.json", "idxs.json"))), "/kaggle/working")\n')
        open(f"{k}/job.py", "w").write(CORE + "\n" + main)
        json.dump({"id": f"{self.user}/nk-{tag}", "title": f"nk-{tag}", "code_file": "job.py", "language": "python",
                   "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_internet": True,
                   "machine_shape": "NvidiaTeslaT4", "dataset_sources": [f"{self.user}/nd-{tag}"],
                   "competition_sources": [], "kernel_sources": []}, open(f"{k}/kernel-metadata.json", "w"))
        r = sh(f"kaggle kernels push -p {k}"); print(r.stdout[-200:], r.stderr[-200:])
        if "successfully" not in r.stdout: raise RuntimeError("kaggle push failed")
        return {"provider": self.name, "ref": f"{self.user}/nk-{tag}", "idxs": idxs, "t0": time.time()}
    def poll(self, job):
        s = sh(f"kaggle kernels status {job['ref']}").stdout
        return "done" if "COMPLETE" in s else "failed" if ("ERROR" in s or "CANCEL" in s) else "running"
    def fetch(self, job, D):
        tmp = f"{D}/_out_{job['ref'].split('/')[-1]}"; shutil.rmtree(tmp, True); os.makedirs(tmp)
        sh(f"kaggle kernels output {job['ref']} -p {tmp}")
        _collect(tmp, D)


class Modal:
    name, sec_per_scene, cost_per_hr = "modal", 45, 2.50       # A100: estimate, measured after first run
    def available(self): return bool(os.environ.get("MODAL_TOKEN_ID") and os.environ.get("MODAL_TOKEN_SECRET"))
    def submit(self, P, D, idxs):
        import modal
        fn = modal.Function.from_name("neuro-render", "render_scenes")
        call = fn.spawn(json.load(open(f"{D}/scenes.json")), idxs)
        return {"provider": self.name, "ref": call.object_id, "idxs": idxs, "t0": time.time()}
    def poll(self, job):
        import modal
        try:
            modal.FunctionCall.from_id(job["ref"]).get(timeout=0); return "done"
        except TimeoutError: return "running"
        except Exception as e: print("modal error:", e); return "failed"
    def fetch(self, job, D):
        import modal
        files = modal.FunctionCall.from_id(job["ref"]).get(timeout=60)
        for name, data in files.items():
            if name.startswith("_"): job["gpu_seconds"] = int(data.decode()); continue
            sub = "clips" if name.endswith(".mp4") else "imgs"
            os.makedirs(f"{D}/{sub}", exist_ok=True); open(f"{D}/{sub}/{name}", "wb").write(data)


class Lightning:
    """Untested until a Lightning API key is added. Runs the same job on a Lightning T4 machine."""
    name, sec_per_scene, cost_per_hr = "lightning", 330, 0.0
    def available(self): return bool(os.environ.get("LIGHTNING_API_KEY") and os.environ.get("LIGHTNING_USER_ID"))
    def submit(self, P, D, idxs):
        from lightning_sdk import Job, Machine
        os.makedirs(f"{D}/_lt", exist_ok=True)
        open(f"{D}/_lt/job.py", "w").write(CORE + f'\nimport json\nrender(json.load(open("scenes.json")), {idxs}, "out")\n')
        shutil.copy(f"{D}/scenes.json", f"{D}/_lt/")
        j = Job.run(name=f"neuro-{P}-{int(time.time())}", machine=Machine.T4,
                    command=f"pip install -q {PIP} && python job.py")
        return {"provider": self.name, "ref": j.name, "idxs": idxs, "t0": time.time()}
    def poll(self, job):
        from lightning_sdk import Job
        st = str(Job(job["ref"]).status).lower()
        return "done" if "complete" in st else "failed" if ("fail" in st or "stop" in st) else "running"
    def fetch(self, job, D):
        from lightning_sdk import Job
        Job(job["ref"]).download_artifacts(f"{D}/_lt_out"); _collect(f"{D}/_lt_out", D)


def _collect(src, D):
    for sub, pat in (("clips", "clip_*.mp4"), ("imgs", "img_*.png")):
        os.makedirs(f"{D}/{sub}", exist_ok=True)
        for f in glob.glob(f"{src}/**/{pat}", recursive=True): shutil.copy(f, f"{D}/{sub}/")


# priority order: fastest first
ALL = [Modal(), Kaggle(), Lightning()]
