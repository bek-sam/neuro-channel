"""Free-first orchestrator: makes a whole video with free GPUs (Hugging Face ZeroGPU Spaces, Kaggle) and free services.
Runs in the cloud (GitHub Actions, .github/workflows/video.yml) or anywhere with Python + ffmpeg. Nothing here costs money.
  python code/free/run.py <project> [--voice edge|qwen3tts] [--heroes 15] [--candidates 2] [--images kaggle|space]
  python code/free/run.py --resume-all      (cron: finishes waiting videos, adds clips when the free GPU quota is back)
Inputs : HF work/<project>/scenes.json + meta.json      State: HF work/<project>/free/ (any machine can resume)
Output : HF videos/<project>/final.mp4, thumbnail.png, report.json      Progress: HF work/<project>/status.json
Order  : hero images first -> their clips start while the other images are made; voice + music run alongside."""
import os, sys, json, time, glob, threading, traceback, argparse
from concurrent.futures import ThreadPoolExecutor, wait
CODE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(CODE)
sys.path[:0] = [CODE, f"{CODE}/gpu"]
if os.path.exists(f"{ROOT}/keys/keys.env"):  # laptop; in the cloud the keys come from secrets
    for l in open(f"{ROOT}/keys/keys.env"):
        if "=" in l and not l.startswith("#"): k, v = l.strip().split("=", 1); os.environ.setdefault(k, v.strip("'\""))
os.environ["HF_REPO"] = os.environ.get("HF_REPO") or "bekbol446/video_gen"  # empty repo variable -> default
os.environ.setdefault("WHISPER_DIR", f"{ROOT}/.cache/whisper"); os.environ.setdefault("SUB_FONT", "Arial" if sys.platform == "darwin" else "DejaVu Sans")
try: import static_ffmpeg; static_ffmpeg.add_paths(weak=True)  # laptop; cloud runners have ffmpeg installed
except ImportError: pass
from free import providers as pv
from models import pick_heroes
import editor
REPO = os.environ["HF_REPO"]


class Router:
    """Tries providers best-first. Quota error -> provider skipped for the rest of the run. Other error -> 1 retry, then next."""
    def __init__(self, provs, log, min_quality=0):
        self.provs = [p for p in provs if p.available() and p.quality >= min_quality]
        self.sem = {p.name: threading.Semaphore(p.limit) for p in self.provs}; self.dead, self.log = set(), log
    def run(self, method, item, *a):
        for p in self.provs:
            for attempt in range(2):
                if p.name in self.dead: break
                t = time.time()
                try:
                    with self.sem[p.name]: getattr(p, method)(*a)
                    self.log(item, p.name, time.time() - t); return p.name
                except pv.QuotaError as e:
                    self.dead.add(p.name); self.log(item, p.name, time.time() - t, f"quota: {e}"); break
                except Exception as e:
                    self.log(item, p.name, time.time() - t, f"error: {str(e)[:300]}"); time.sleep(5)
        return None
    def threads(self): return max(1, sum(p.limit for p in self.provs))


def run(argv):
    ap = argparse.ArgumentParser(); ap.add_argument("project")
    ap.add_argument("--voice", default="edge", choices=list(pv.VOICE)); ap.add_argument("--heroes", type=int, default=15)
    ap.add_argument("--candidates", type=int, default=1); ap.add_argument("--min-quality", type=int, default=6)
    ap.add_argument("--images", default="kaggle", choices=["kaggle", "space"], help="bulk images on Kaggle, or all on ZeroGPU Spaces/APIs")
    ap.add_argument("--no-upload", action="store_true")
    a = ap.parse_args(argv); P = a.project; t0 = time.time()
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi(token=os.environ["HF_TOKEN"])
    D = f"{ROOT}/projects/{P}"
    for sub in ("imgs", "clips", "voice", "music", "out"): os.makedirs(f"{D}/{sub}", exist_ok=True)
    # state lives on HF (work/<P>/free/), so a fresh cloud machine continues where the last one stopped
    from huggingface_hub import snapshot_download
    try:
        snapshot_download(REPO, repo_type="dataset", allow_patterns=[f"work/{P}/free/*", f"work/{P}/free/**/*"], local_dir=f"{D}/_sync", token=os.environ["HF_TOKEN"])
        import shutil
        for f in glob.glob(f"{D}/_sync/work/{P}/free/**/*", recursive=True):
            dst = f"{D}/" + f.split(f"/work/{P}/free/", 1)[1]
            if os.path.isfile(f) and not os.path.exists(dst): os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy(f, dst)
        shutil.rmtree(f"{D}/_sync", ignore_errors=True)
    except Exception as e: print("no saved state:", str(e)[:150])
    def save_state():
        if a.no_upload: return
        try: api.upload_folder(folder_path=D, path_in_repo=f"work/{P}/free", repo_id=REPO, repo_type="dataset",
                               allow_patterns=["imgs/*.png", "clips/*.mp4", "voice/*.wav", "music/*.wav", "*.json", "*.log"],
                               ignore_patterns=["*.part.*", "*.keep.*"])
        except Exception as e: print("state upload failed:", str(e)[:200])
    try: prev = json.load(open(f"{D}/status.json"))
    except Exception: prev = {}
    rd = lambda f: json.load(open(hf_hub_download(REPO, f"work/{P}/{f}", repo_type="dataset", token=os.environ["HF_TOKEN"], force_download=True)))
    if not os.path.exists(f"{D}/scenes.json"): json.dump(rd("scenes.json"), open(f"{D}/scenes.json", "w"), indent=1)
    if not os.path.exists(f"{D}/meta.json"):
        try: json.dump(rd("meta.json"), open(f"{D}/meta.json", "w"), indent=1)
        except Exception: json.dump({}, open(f"{D}/meta.json", "w"))
    scenes, meta = json.load(open(f"{D}/scenes.json")), json.load(open(f"{D}/meta.json"))
    n = len(scenes); heroes = pick_heroes(n, a.heroes, [i for i, s in enumerate(scenes) if s.get("hero")])

    # ---- log + status (status.json on HF at most once a minute)
    items, lk, last = [], threading.Lock(), [0.0]
    def status(state, force=False, **kw):
        st = dict(state=state, minutes=round((time.time() - t0) / 60, 1), cost_usd=0, scenes=n, heroes=heroes, args=argv[1:],
                  attempts=prev.get("attempts", 0) + 1, **kw)
        json.dump(st, open(f"{D}/status.json", "w"), indent=1)
        if force or time.time() - last[0] > 60:
            last[0] = time.time()
            try: api.upload_file(path_or_fileobj=json.dumps(st, indent=1).encode(), path_in_repo=f"work/{P}/status.json", repo_id=REPO, repo_type="dataset")
            except Exception as e: print("status upload failed:", e)
    def log(item, prov, sec, err=None):
        with lk: items.append(dict(item=item, provider=prov, sec=round(sec, 1), **({"error": err} if err else {})))
        print(f"[{(time.time() - t0) / 60:5.1f}m] {item:12} {prov:14} {sec:6.1f}s {err or 'ok'}", flush=True)
    status("starting", force=True)

    img_r, vid_r = Router(pv.IMAGE, log, a.min_quality), Router(pv.VIDEO, log, a.min_quality)
    mus_r = Router(pv.MUSIC, log)
    print("image:", [p.name for p in img_r.provs], "video:", [p.name for p in vid_r.provs], "voice:", a.voice, "heroes:", heroes)
    img = lambda i, s="": f"{D}/imgs/img_{i:03d}{s}.png"
    clip_pool = ThreadPoolExecutor(vid_r.threads()); clip_futs = []

    def do_clip(i):
        out = f"{D}/clips/clip_{i:03d}.mp4"
        if os.path.exists(out) or not os.path.exists(img(i)): return
        s = scenes[i]
        vid_r.run("clip", f"clip {i}", img(i), f'{s.get("motion", "")}. {s["prompt"]}, smooth natural cinematic motion', i, out + ".part.mp4")
        if os.path.exists(out + ".part.mp4"): os.replace(out + ".part.mp4", out)

    def do_image(i):
        for c, suf in enumerate(["", "_b"][:max(1, a.candidates)]):
            if not os.path.exists(img(i, suf)):
                tmp = img(i, suf) + ".part.png"
                if img_r.run("image", f"img {i}{suf}", scenes[i]["prompt"], 1000 * i + c, tmp): os.replace(tmp, img(i, suf))
            if c == 0 and i in heroes and os.path.exists(img(i)): clip_futs.append(clip_pool.submit(do_clip, i))

    def do_thumb():
        out = f"{D}/imgs/thumbnail.png"
        if os.path.exists(out) or not meta.get("thumb_title"): return
        tp = (f'YouTube thumbnail, {meta.get("thumb_visual", "")}, huge bold white sans-serif title text "{meta["thumb_title"]}" '
              'with thick black outline on the left side, high contrast, dramatic lighting, very sharp, eye-catching')
        if img_r.run("image", "thumbnail", tp, 7, out + ".part.png"):
            from PIL import Image
            Image.open(out + ".part.png").convert("RGB").resize((1280, 720)).save(out); os.remove(out + ".part.png")

    def do_voice():
        """One voice for the whole video. If the chosen one fails on any line, every line is redone with edge (same narrator)."""
        prov = pv.VOICE[a.voice]
        wav = lambda i: f"{D}/voice/a_{i:03d}.wav"
        def make(p, i, **kw):
            t = time.time(); p.voice(scenes[i]["text"], wav(i) + ".part.wav", **kw); os.replace(wav(i) + ".part.wav", wav(i)); log(f"voice {i}", p.name, time.time() - t)
        try:
            with ThreadPoolExecutor(prov.limit) as ex: list(ex.map(lambda i: os.path.exists(wav(i)) or make(prov, i), range(n)))
        except Exception as e:
            log("voice", prov.name, 0, f"failed, all lines -> edge: {str(e)[:200]}")
            for f in glob.glob(f"{D}/voice/a_*.wav"): os.remove(f)
            prov = pv.VOICE["edge"]
            with ThreadPoolExecutor(prov.limit) as ex: list(ex.map(lambda i: make(prov, i), range(n)))
        # Whisper listens to every line; a line with skipped / garbled words is made again (2 more takes, best one kept)
        from faster_whisper import WhisperModel
        from worker import wer
        wm = WhisperModel("small.en", device="cpu", compute_type="int8", download_root=os.environ["WHISPER_DIR"], cpu_threads=os.cpu_count())
        heard = lambda f: " ".join(x.text for x in wm.transcribe(f, vad_filter=False)[0])
        checks = {}
        for i in range(n):
            e = wer(scenes[i]["text"], heard(wav(i))); checks[i] = round(e, 2)
            for take, kw in enumerate(({"rate": "-4%"}, {"rate": "+3%"}) if prov.name == "edge" else ({}, {})):
                if e <= 0.2: break
                keep = wav(i) + ".keep.wav"; os.replace(wav(i), keep)
                try: make(prov, i, **kw)
                except Exception: os.replace(keep, wav(i)); break
                e2 = wer(scenes[i]["text"], heard(wav(i)))
                if e2 < e: e = e2; os.remove(keep)
                else: os.replace(keep, wav(i))
                checks[i] = round(e, 2); log(f"retake {i}", prov.name, 0, f"wer {e:.2f}")
        return {"provider": prov.name, "wer": checks, "bad_lines": {i: e for i, e in checks.items() if e > 0.2}}

    def do_music():
        out = f"{D}/music/music.wav"
        if not os.path.exists(out): mus_r.run("music", "music", meta.get("music_prompt", ""), 180, out)

    def kaggle_images(idxs, slug, thumb=False):
        """Bulk images on Kaggle (free T4s), so the small ZeroGPU quota is kept for clips. Hero batch -> clips start."""
        from free import kaggle
        jobs = [(os.path.basename(img(i, s)), scenes[i]["prompt"], 1000 * i + c) for i in idxs
                for c, s in enumerate(["", "_b"][:max(1, a.candidates)]) if not os.path.exists(img(i, s))]
        if thumb and meta.get("thumb_title") and not os.path.exists(f"{D}/imgs/thumbnail.png"):
            jobs.append(("thumbnail.png", f'YouTube thumbnail, {meta.get("thumb_visual", "")}, huge bold white sans-serif title text '
                         f'"{meta["thumb_title"]}" with thick black outline on the left side, high contrast, dramatic lighting, very sharp', 7))
        try: kaggle.run_images(jobs, f"{D}/imgs", log, slug=slug)
        except Exception as e: log("kaggle images", "kaggle_zimage", 0, f"error: {str(e)[:300]}")
        if os.path.exists(f"{D}/imgs/thumbnail.png"):
            from PIL import Image
            Image.open(f"{D}/imgs/thumbnail.png").convert("RGB").resize((1280, 720)).save(f"{D}/imgs/thumbnail.png")
        for i in idxs:
            if i in heroes and os.path.exists(img(i)): clip_futs.append(clip_pool.submit(do_clip, i))

    status("making images, clips, voice and music", force=True)
    with ThreadPoolExecutor(3) as side:
        fv, fm = side.submit(do_voice), side.submit(do_music)
        order = heroes + [i for i in range(n) if i not in heroes]          # hero images first: clips start sooner
        if a.images == "kaggle":  # two kernels: heroes (+ thumbnail) first, the rest alongside
            with ThreadPoolExecutor(2) as kx:
                list(kx.map(lambda x: kaggle_images(*x), [(heroes, "vg-img-heroes", True), ([i for i in range(n) if i not in heroes], "vg-img-rest")]))
        with ThreadPoolExecutor(img_r.threads()) as ex:  # Spaces / APIs: everything (or whatever Kaggle did not return)
            futs = [ex.submit(do_image, i) for i in order] + [ex.submit(do_thumb)]
            while not all(f.done() for f in futs):
                time.sleep(15)
                status("making images, clips, voice and music", images=len(glob.glob(f"{D}/imgs/img_???.png")),
                       clips=len(glob.glob(f"{D}/clips/clip_*.mp4")), voice=len(glob.glob(f"{D}/voice/a_???.wav")))
            for f in futs: f.result()
        while any(not f.done() for f in list(clip_futs)):
            time.sleep(15); status("making clips", clips=len(glob.glob(f"{D}/clips/clip_*.mp4")), clips_todo=len(heroes))
        voice_report = fv.result(); fm.result()
    clip_pool.shutdown()

    missing = [i for i in range(n) if not os.path.exists(img(i))]
    save_state()
    if missing:  # never edit a video with holes; a rerun later (quota back) fills them
        status("waiting: images missing (free quota used up?) - run again later to finish", force=True, missing=missing)
        json.dump(dict(items=items), open(f"{D}/report.json", "w"), indent=1); sys.exit(f"missing images {missing}")

    clips_now = len(glob.glob(f"{D}/clips/clip_*.mp4"))
    if prev.get("state") == "done" and clips_now == prev.get("clips_done", -1):  # resumed for clips, none came -> nothing to redo
        status("done", force=True, **{k: prev[k] for k in ("length", "lufs", "video", "clips_missing", "clips_done") if k in prev}); return
    status("editing", force=True)
    for f in glob.glob(f"{D}/imgs/*.part.png") + glob.glob(f"{D}/clips/*.part.mp4"): os.remove(f)
    music = f"{D}/music/music.wav" if os.path.exists(f"{D}/music/music.wav") else None
    clips = f"{D}/clips" if glob.glob(f"{D}/clips/clip_*.mp4") else None
    t = time.time(); ed = editor.build(scenes, f"{D}/imgs", clips, f"{D}/voice", music, f"{D}/edit", f"{D}/out"); log("edit", "local", time.time() - t)
    by = lambda k: {p: c for p in {x["provider"] for x in items}
                    if (c := sum(1 for x in items if x["item"].startswith(k) and x["provider"] == p and "error" not in x))}
    report = dict(project=P, minutes=round((time.time() - t0) / 60, 1), cost_usd=0, heroes=heroes,
                  clips=sorted(int(f[-7:-4]) for f in glob.glob(f"{D}/clips/clip_*.mp4")),
                  providers={"images": by("img"), "clips": by("clip"), "voice": by("voice")}, voice=voice_report,
                  edit={k: v for k, v in ed.items() if k != "scenes"}, items=items)
    json.dump(report, open(f"{D}/out/report.json", "w"), indent=1)
    if not a.no_upload:
        status("uploading", force=True)
        api.upload_folder(folder_path=f"{D}/out", path_in_repo=f"videos/{P}", repo_id=REPO, repo_type="dataset")
    clips_missing = [i for i in heroes if not os.path.exists(f"{D}/clips/clip_{i:03d}.mp4")]
    status("done", force=True, length=ed["length"], lufs=ed["lufs"], video=f"videos/{P}/final.mp4", clips_missing=clips_missing,
           clips_done=clips_now)
    save_state()
    print(json.dumps({k: v for k, v in report.items() if k != "items"}, indent=1))


def resume_all(max_attempts=6):
    """Every unfinished project, and finished ones that still miss hero clips (the free clip quota refills daily)."""
    from huggingface_hub import HfApi, hf_hub_download
    api = HfApi(token=os.environ["HF_TOKEN"])
    for f in api.list_repo_files(REPO, repo_type="dataset"):
        if not (f.startswith("work/") and f.endswith("/status.json") and f.count("/") == 2): continue
        st = json.load(open(hf_hub_download(REPO, f, repo_type="dataset", token=os.environ["HF_TOKEN"], force_download=True)))
        if "args" not in st or st.get("attempts", 0) >= max_attempts: continue  # only projects started by this orchestrator
        if st["state"].startswith("waiting") or (st["state"] == "done" and st.get("clips_missing")):
            print("== resume", f.split("/")[1], st["state"], flush=True)
            try: run([f.split("/")[1]] + st["args"])
            except SystemExit as e: print("stopped:", e)
            except Exception: traceback.print_exc()


if __name__ == "__main__":
    resume_all() if sys.argv[1:] == ["--resume-all"] else run(sys.argv[1:])
