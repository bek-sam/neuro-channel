"""Editor v2: runs on a Modal CPU machine. Pulls images / clips / voice from Hugging Face, builds the final 1080p video.
Per scene: AI motion clip first (if any) -> crossfade -> slow camera move (Ken Burns) on the 2nd image.
Subtitles timed word-by-word with Whisper. Audio normalized to -14 LUFS (YouTube). Optional music with ducking."""
import os, glob, json, subprocess, time
from worker import _pull, _hf, REPO

W, H, FPS, PAUSE, XF = 1920, 1080, 30, 0.35, 0.5


def sh(c):
    r = subprocess.run(c, shell=True, capture_output=True, text=True)
    if r.returncode: raise RuntimeError(c[:200] + "\n" + r.stderr[-1500:])
    return r.stdout


def dur(f): return float(sh(f"ffprobe -v error -show_entries format=duration -of csv=p=0 '{f}'").strip())


def kenburns(img, seconds, out, kind):
    """Slow camera move over a still image. kind 0..3 = zoom in, zoom out, pan right, pan left."""
    n = int(seconds * FPS) + 2
    if kind == 0:   z, x, y = f"1+0.10*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif kind == 1: z, x, y = f"1.10-0.10*on/{n}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif kind == 2: z, x, y = "1.08", f"(iw-iw/zoom)*on/{n}", "ih/2-(ih/zoom/2)"
    else:           z, x, y = "1.08", f"(iw-iw/zoom)*(1-on/{n})", "ih/2-(ih/zoom/2)"
    sh(f"ffmpeg -loglevel error -y -loop 1 -i '{img}' -vf \"scale=3840:2160:force_original_aspect_ratio=increase,crop=3840:2160,"
       f"zoompan=z='{z}':x='{x}':y='{y}':d={n}:s={W}x{H}:fps={FPS},format=yuv420p\" -t {seconds:.3f} "
       f"-c:v libx264 -preset veryfast -crf 18 -an '{out}'")


def norm_clip(clip, seconds, out):
    """AI clip -> 1080p 30fps, cut to `seconds` (slowed slightly if it is a bit too short)."""
    d = dur(clip); speed = min(1.0, d / seconds) if seconds > d else 1.0
    sh(f"ffmpeg -loglevel error -y -i '{clip}' -vf \"setpts=PTS/{speed:.4f},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
       f"crop={W}:{H},fps={FPS},format=yuv420p\" -t {seconds:.3f} -c:v libx264 -preset veryfast -crf 18 -an '{out}'")


def xfade(a, b, out, a_len):
    sh(f"ffmpeg -loglevel error -y -i '{a}' -i '{b}' -filter_complex \"[0][1]xfade=transition=fade:duration={XF}:offset={a_len - XF:.3f},format=yuv420p\" "
       f"-c:v libx264 -preset veryfast -crf 18 -an '{out}'")


def voice_kokoro(scenes, d):
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro("/models/kokoro-v1.0.onnx", "/models/voices-v1.0.bin")
    for i, s in enumerate(scenes):
        a, sr = k.create(s["text"], voice="am_michael", speed=1.0, lang="en-us"); sf.write(f"{d}/a_{i:03d}.wav", a, sr)


def ass_subs(wav, out):
    """Word-timed subtitles: phrases of up to 4 words, YouTube style."""
    from faster_whisper import WhisperModel
    m = WhisperModel("small.en", device="cpu", compute_type="int8", download_root="/cache/whisper", cpu_threads=16)
    segs, _ = m.transcribe(wav, word_timestamps=True, vad_filter=False)
    words = [w for s in segs for w in s.words]
    t = lambda x: f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"
    lines, cur = [], []
    for w in words:
        cur.append(w)
        if len(cur) >= 4 or w.word.strip().endswith((".", ",", "?", "!")) or cur[-1].end - cur[0].start > 1.8:
            lines.append(cur); cur = []
    if cur: lines.append(cur)
    hdr = ("[Script Info]\nScriptType: v4.00+\nPlayResX: 1920\nPlayResY: 1080\n\n[V4+ Styles]\n"
           "Format: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Outline, Shadow, Alignment, MarginV\n"
           "Style: Default,DejaVu Sans,64,&H00FFFFFF,&H00000000,&H64000000,1,4,1,2,90\n\n[Events]\n"
           "Format: Layer, Start, End, Style, Text\n")
    ev = "".join(f"Dialogue: 0,{t(l[0].start)},{t(max(l[-1].end, l[0].start + 0.4))},Default,{' '.join(w.word.strip() for w in l)}\n" for l in lines)
    open(out, "w").write(hdr + ev)
    return len(lines)


def edit(project, scenes, voice_model, hero_model):
    t0 = time.time(); D = "/tmp/ed"; os.makedirs(f"{D}/parts", exist_ok=True)
    imgs = _pull(project, "imgs", D)
    clips = _pull(project, f"clips_{hero_model}", D) if hero_model else None
    if voice_model == "chatterbox":
        vdir = _pull(project, "voice_chatterbox", D)
    else:
        vdir = f"{D}/voice"; os.makedirs(vdir, exist_ok=True); voice_kokoro(scenes, vdir)
    report = []
    for i, s in enumerate(scenes):
        wav = f"{vdir}/a_{i:03d}.wav"; L = dur(wav) + PAUSE
        img, img_b = f"{imgs}/img_{i:03d}.png", f"{imgs}/img_{i:03d}_b.png"
        img_b = img_b if os.path.exists(img_b) else img
        clip = f"{clips}/clip_{i:03d}.mp4" if clips else None
        P = f"{D}/parts"; seg = f"{P}/v_{i:03d}.mp4"
        if clip and os.path.exists(clip):
            c = min(dur(clip), L)
            rest = L - c
            if rest < 1.5:                       # clip covers (almost) the whole scene
                norm_clip(clip, L, seg); how = "clip"
            else:                                # clip, then camera move on the 2nd image
                # same image as the clip's start -> no "different person" jump after the dissolve
                norm_clip(clip, c, f"{P}/a.mp4"); kenburns(img, rest + XF, f"{P}/b.mp4", i % 4)
                xfade(f"{P}/a.mp4", f"{P}/b.mp4", seg, c); how = "clip+still"
        elif os.path.exists(img):
            if L > 7:                            # two camera moves on the two images
                h = L / 2 + XF / 2
                kenburns(img, h, f"{P}/a.mp4", i % 4); kenburns(img_b, h, f"{P}/b.mp4", (i + 1) % 4)
                xfade(f"{P}/a.mp4", f"{P}/b.mp4", seg, h); how = "2 stills"
            else:
                kenburns(img, L, seg, i % 4); how = "still"
        else:
            sh(f"ffmpeg -loglevel error -y -f lavfi -i color=c=black:s={W}x{H}:r={FPS} -t {L:.3f} -c:v libx264 -pix_fmt yuv420p '{seg}'"); how = "black"
        # add this scene's voice (+ short pause)
        sh(f"ffmpeg -loglevel error -y -i '{seg}' -i '{wav}' -filter_complex \"[1:a]aresample=48000,apad=whole_dur={L:.3f}[a]\" "
           f"-map 0:v -map [a] -t {L:.3f} -c:v copy -c:a aac -b:a 192k '{P}/p_{i:03d}.mp4'")
        report.append((i, how, round(L, 1))); print("scene", i, how, round(L, 1), flush=True)
    open(f"{D}/list.txt", "w").write("".join(f"file 'parts/p_{i:03d}.mp4'\n" for i in range(len(scenes))))
    sh(f"ffmpeg -loglevel error -y -f concat -safe 0 -i {D}/list.txt -c copy {D}/joined.mp4")
    sh(f"ffmpeg -loglevel error -y -i {D}/joined.mp4 -vn -ac 1 -ar 16000 {D}/voice.wav")
    n_sub = ass_subs(f"{D}/voice.wav", f"{D}/subs.ass")
    # optional background music: put any royalty-free mp3 at assets/music.mp3 in the HF dataset
    music = None
    try:
        from huggingface_hub import hf_hub_download
        music = hf_hub_download(REPO, "assets/music.mp3", repo_type="dataset", token=os.environ["HF_TOKEN"])
    except Exception: pass
    if music:
        af = ("[1:a]volume=0.22,aresample=48000[m];[m][0:a]sidechaincompress=threshold=0.04:ratio=8:attack=20:release=500[md];"
              "[0:a][md]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[a]")
        ins = f"-i {D}/joined.mp4 -stream_loop -1 -i '{music}'"
    else:
        af, ins = "[0:a]loudnorm=I=-14:TP=-1.5:LRA=11[a]", f"-i {D}/joined.mp4"
    sh(f"ffmpeg -loglevel error -y {ins} -filter_complex \"[0:v]ass={D}/subs.ass[v];{af}\" -map [v] -map [a] "
       f"-c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -movflags +faststart {D}/final.mp4")
    out = f"{D}/out"; os.makedirs(out, exist_ok=True)
    os.replace(f"{D}/final.mp4", f"{out}/final.mp4"); os.replace(f"{D}/subs.ass", f"{out}/subs.ass")
    if os.path.exists(f"{imgs}/thumbnail.png"): sh(f"cp '{imgs}/thumbnail.png' {out}/thumbnail.png")
    _hf().upload_folder(folder_path=out, path_in_repo=f"videos/{project}", repo_id=REPO, repo_type="dataset")
    return {"seconds": round(time.time() - t0), "length": round(dur(f"{out}/final.mp4"), 1), "subtitle_lines": n_sub,
            "music": bool(music), "scenes": report}
