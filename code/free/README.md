# Free pipeline (`code/free/`)

Makes a whole video in the cloud without paying. The laptop only starts it.
The paid Modal pipeline (`code/gpu/modal_app3.py`) is still there for when speed matters more than cost
(Modal also gives $30 of free credit each month, about 7 `turbo` videos).

```
gh workflow run video.yml -f project=<name> [-f args="--heroes 15 --voice edge"]     # in the cloud (GitHub Actions)
python code/free/run.py <project> [--images kaggle|space] [--voice edge|qwen3tts] [--heroes 15] [--candidates 1]
python code/free/run.py --resume-all                                                   # what the 6-hourly cron runs
```
Input: `work/<project>/scenes.json` + `meta.json` on the HF dataset. Output: `videos/<project>/final.mp4`, `thumbnail.png`, `report.json`.
State is saved to `work/<project>/free/` on the HF dataset, so any machine resumes where the last one stopped.
One-time cloud setup: `bash scripts/cloud_setup.sh` (stores the HF and Kaggle keys as encrypted GitHub secrets).

## Where each part runs

| Stage | 1st choice | then | last resort | why |
|---|---|---|---|---|
| Orchestrator + edit | **GitHub Actions** runner (ffmpeg, 6 h max) | any machine with Python | – | free; private repo ~2,000 min/month, public unlimited |
| Images | **Kaggle** T4 x2, Z-Image-Turbo, 2 kernels in parallel | ZeroGPU Space Z-Image-Turbo | FLUX.2 klein Space, Gemini / Cloudflare (if keys) | Kaggle ~30 GPU h/week; the Space quota is kept for clips |
| Motion clips | **ZeroGPU Spaces**: Wan2.2-I2V-A14B (2 Spaces), then LTX-2.3 | **Modal** H100 Wan2.2 14B 4-step (`modal_clip.py`), then **Muapi** (paid) | slow camera move over the still | ZeroGPU ~5 free GPU-min/day = ~5 clips, one quota per HF account for all 3 Spaces; Modal and Muapi stop at their monthly caps |
| Voice | **edge-tts** (Andrew) | Qwen3-TTS Space | – | unlimited, ~1 s/line; one narrator for the whole video |
| Voice check | faster-whisper on the runner | – | – | lines with WER > 0.2 are made again (best of 3 kept) |
| Music | library bed (HF dataset) | – | none | |

A provider that runs out of quota is skipped for the rest of the run. One image model and one voice are kept
per video when possible, so the look and the narrator stay the same. A video is never edited with missing images:
it waits (state `waiting`) and the cron finishes it when quota is back.

## Measured (2026-10-30)

| Provider | Item | Time | Quality | Notes |
|---|---|---|---|---|
| ZeroGPU `Tongyi-MAI/Z-Image-Turbo` | image 2048x1152 | 18 s | 9 | Apache-2.0 |
| ZeroGPU `zerogpu-aoti/wan2-2-fp8da-aoti-faster` | 5 s clip 832x480 @16 fps | 57 s | 8 | editor interpolates to 32 fps, scales to 1080p |
| ZeroGPU `r3gm/wan2-2-fp8da-aoti-preview` (2026-11-08) | 5 s clip 832x480 @16 fps | 36 s | 8 | same model, backup Space |
| ZeroGPU `Lightricks/LTX-2-3` (2026-11-08) | 5 s clip 1280x704 @24 fps | 61 s | 8 | steadier shapes than Wan on our test shot |
| Kaggle T4, Z-Image-Turbo bf16 | image 1440x816 | 4.8 min (+4.8 min load per kernel) | 9 | fp16 = black images; 1920x1088 = out of memory |
| Kaggle T4, Qwen-Image 20B offloaded | image | 29 min | 9 | unusable |
| edge-tts AndrewMultilingual | one line | 1-10 s | 7 | free, no key; retry on `NoAudioReceived` |
| Pollinations (anonymous) | image | 5 s | 3 | 1024x576, blurry, watermark; good models need a key now |
| Edit (ffmpeg) | 2 scenes, 19 s video | 16 s on 10 cores | – | -14.9 LUFS |

A 32-scene video, free: ~1.5 h of Kaggle images (2 kernels), clips over 2-3 days of ZeroGPU quota, ~3 Kaggle GPU-hours.

Not free with the current keys: Gemini (prepaid project, credits used up; a key from a project *without* billing gets
free TTS), HF Inference Providers ($0 for free accounts), Kaggle L4/A100 (free accounts get T4).

## Clips that can cost money (monthly caps)

When the free ZeroGPU quota is used up, clips go to Modal and then Muapi until each one's cap for the month:

| Provider | Cap (env / repo variable) | Default | Per clip |
|---|---|---|---|
| Modal H100 (`code/free/modal_clip.py`, deploy once) | `MODAL_MONTHLY_USD` | 25 (the free credit is 30) | counted as wall time × $3.95/h + 30 s |
| Muapi (`MUAPI_API_KEY`, model `MUAPI_MODEL`) | `MUAPI_MONTHLY_USD` | 5 (0 = off) | the charge Muapi reports; default model Kling 2.5 Turbo Std, $0.28 |

Spend is kept in `budget/<YYYY-MM>.json` on the HF dataset, so every runner sees the same total. Any image-to-video
endpoint on muapi.ai works as `MUAPI_MODEL` (e.g. `seedance-2-mini-image-to-video` $0.20, `veo3.1-lite-image-to-video` $0.30).

## Runs never collide

A run claims its project (`runner` + `heartbeat` in `status.json`, refreshed every 2 minutes). Another run of the same
project (the cron and a dispatch, say) leaves it alone unless the heartbeat is more than 10 minutes old. Kaggle kernels
are named after the project, and Whisper results are kept in `voice_checks.json`, so a resume only re-checks changed lines.

## More free quota (accounts the user can add)
- `CF_ACCOUNT_ID`, `CF_API_TOKEN`: Cloudflare Workers AI, 10,000 neurons/day (~170 FLUX-schnell images).
- `GEMINI_API_KEY` from a project without billing: free Gemini TTS.
- Hugging Face PRO ($9/month, not free): ZeroGPU 40 min/day instead of 5 = ~40 clips a day.

Full research: `research/free_providers_2026-10.md`.
