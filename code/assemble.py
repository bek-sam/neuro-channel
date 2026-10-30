"""Assemble final video: scenes.json + clips/ -> voice, subtitles, final MP4.
Usage: python3 assemble.py <project_dir>
project_dir has scenes.json ([{"text":..., "prompt":...}, ...]) and clips/clip_000.mp4 ...
"""
import json, os, subprocess, sys, textwrap
import soundfile as sf
from kokoro_onnx import Kokoro

D = sys.argv[1]
VOICE = os.environ.get("VOICE", "am_michael")
HERE = os.path.dirname(os.path.abspath(__file__))
scenes = json.load(open(f"{D}/scenes.json"))
k = Kokoro(f"{HERE}/models/kokoro-v1.0.onnx", f"{HERE}/models/voices-v1.0.bin")
os.makedirs(f"{D}/parts", exist_ok=True)

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

def ts(t):
    h, m = int(t // 3600), int(t % 3600 // 60)
    return f"{h:02d}:{m:02d}:{t % 60:06.3f}".replace(".", ",")

srt, t0 = [], 0.0
for i, s in enumerate(scenes):
    audio, sr = k.create(s["text"], voice=VOICE, speed=1.0, lang="en-us")
    wav = f"{D}/parts/a_{i:03d}.wav"
    sf.write(wav, audio, sr)
    dur = len(audio) / sr + 0.4  # small pause after each scene
    # subtitles: split text into ~8-word chunks, spread over the scene time
    words = s["text"].split()
    chunks = [" ".join(words[j:j + 8]) for j in range(0, len(words), 8)]
    step = (dur - 0.4) / len(chunks)
    for c_i, c in enumerate(chunks):
        a = t0 + c_i * step
        srt.append(f"{len(srt) + 1}\n{ts(a)} --> {ts(a + step)}\n{c}\n")
    t0 += dur
    # video: loop/trim clip to match voice length, 1080p
    clip, img = f"{D}/clips/clip_{i:03d}.mp4", f"{D}/imgs/img_{i:03d}.png"
    out = f"{D}/parts/p_{i:03d}.mp4"
    if os.path.exists(clip):
        # first 3.6s (before any morphing), slowed 1.5x, played forward+back = smooth loop
        run(f'ffmpeg -loglevel error -y -i {clip} -filter_complex "[0]trim=0:3.6,setpts=1.5*(PTS-STARTPTS),scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,split[a][b];[b]reverse[r];[a][r]concat=n=2" -an -c:v libx264 -preset veryfast -crf 18 {D}/parts/loop_{i:03d}.mp4')
        src = f"-stream_loop -1 -i {D}/parts/loop_{i:03d}.mp4"; vf = "format=yuv420p"
    elif not os.path.exists(img):
        # last resort: reuse the previous scene's loop, or a dark frame
        prev = f"{D}/parts/loop_{i-1:03d}.mp4"
        src = f"-stream_loop -1 -i {prev}" if os.path.exists(prev) else "-f lavfi -i color=c=black:s=1920x1080:r=30"
        vf = "format=yuv420p"
    else:
        # fallback: slow zoom on the still image (Ken Burns)
        n = int(dur * 30) + 1
        src = f"-loop 1 -i {img}"
        vf = f"scale=3840:-2,zoompan=z='1+0.12*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1920x1080:fps=30,format=yuv420p"
    run(f'ffmpeg -loglevel error -y {src} -i {wav} -t {dur:.2f} -vf "{vf}" -af apad '
        f'-c:v libx264 -preset veryfast -crf 20 -c:a aac -ar 48000 {out}')
    print(f"scene {i}: {dur:.1f}s", flush=True)

open(f"{D}/subs.srt", "w").write("\n".join(srt))
open(f"{D}/parts/list.txt", "w").write("".join(f"file 'p_{i:03d}.mp4'\n" for i in range(len(scenes))))
run(f"ffmpeg -loglevel error -y -f concat -safe 0 -i {D}/parts/list.txt -c copy {D}/joined.mp4")
style = "FontName=Arial,FontSize=20,Bold=1,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=2,MarginV=40"
run(f"ffmpeg -loglevel error -y -i {D}/joined.mp4 -vf \"subtitles={D}/subs.srt:force_style='{style}'\" "
    f"-c:v libx264 -preset veryfast -crf 20 -c:a copy {D}/final.mp4")
print("DONE", f"{D}/final.mp4", f"{t0:.1f}s")
