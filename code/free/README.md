# Free pipeline (`code/free/`)

Makes a whole video without paying: free GPUs for images and clips, free voices, editing on this computer.
The paid Modal pipeline (`code/gpu/modal_app3.py`) is still there for when speed matters more than cost.

```
.venv/bin/python code/free/run.py <project> [--images kaggle|space] [--voice edge|qwen3tts] [--heroes 15] [--candidates 2]
```
Input: `work/<project>/scenes.json` + `meta.json` on the HF dataset. Output: `videos/<project>/final.mp4`, `thumbnail.png`, `report.json`.
Work files stay in `projects/<project>/`, so running the same command again **resumes** and only makes what is missing
(for example: more motion clips the next day, when the free GPU quota is back).

## How work is spread

| Stage | 1st choice | then | last resort | why |
|---|---|---|---|---|
| Images (bulk) | **Kaggle** T4 x2, Z-Image-Turbo | ZeroGPU Space Z-Image-Turbo | FLUX.2 klein Space, Gemini / Cloudflare (if keys), Pollinations | Kaggle has ~30 GPU h/week; the Space quota is kept for clips |
| Motion clips | **ZeroGPU Space** Wan2.2-I2V-A14B (6 steps) | – | slow camera move over the still | ~5 free GPU-min/day = ~5 clips; rerun later for more |
| Voice | **edge-tts** (Andrew) | Qwen3-TTS Space | – | unlimited, ~1 s/line; one narrator for the whole video |
| Voice check | faster-whisper on this computer | – | – | lines with WER > 0.2 are made again (best of 3 kept) |
| Music | library bed (HF dataset) | – | none | ACE-Step on Kaggle: next |
| Edit | ffmpeg on this computer | – | – | static ffmpeg in `.venv`, 10 cores |

Quality ladder: a provider that runs out of quota is skipped for the rest of the run; one image model and one
voice are kept per video when possible, so the look and the narrator stay the same.

## Measured (2026-10-30)

| Provider | Item | Time | Quality | Notes |
|---|---|---|---|---|
| ZeroGPU `Tongyi-MAI/Z-Image-Turbo` | image 2048x1152 | 18 s | 9 | Apache-2.0 |
| ZeroGPU `zerogpu-aoti/wan2-2-fp8da-aoti-faster` | 5 s clip 832x480 @16 fps | 57 s | 8 | editor interpolates to 32 fps, scales to 1080p |
| edge-tts AndrewMultilingual | one line | ~1-10 s | 7 | free, no key; retry on `NoAudioReceived` |
| Pollinations (anonymous) | image | 5 s | 3 | 1024x576, blurry, watermark: last resort only |
| Kaggle T4, Qwen-Image 20B offloaded | image | 29 min | 9 | unusable |
| Local edit (M-series, 10 cores) | 2 scenes, 19 s video | 16 s | – | -14.9 LUFS |

Not free with the current keys: Gemini (prepaid project, credits used up: a key from a project *without* billing gets free
TTS), Modal (monthly spend limit reached), HF Inference Providers ($0 for free accounts).

## More free quota (accounts the user can add to `keys/keys.env`)
- `CF_ACCOUNT_ID`, `CF_API_TOKEN`: Cloudflare Workers AI, 10,000 neurons/day (~170 FLUX-schnell images).
- `GEMINI_API_KEY` from a project without billing: free Gemini TTS.
- Hugging Face PRO ($9/month, not free): ZeroGPU 40 min/day instead of 5 = ~40 clips a day.

Full research: `research/free_providers_2026-10.md`.
