# Free providers for the explainer pipeline (checked 2026-10-30)

How this was checked. Official docs and pricing pages were fetched on 2026-10-30. Some claims were also tested live without credentials: Pollinations image and TTS anonymously, edge-tts 7.3.1 synthesis, `gradio_client.view_api()` on public Spaces, the NASA and Wikimedia APIs, and the HF model-licence API.
Tags: **[V]** = verified from an official page or a live test today. **[3P]** = only third-party sources (aggregators, blogs). **[U]** = could not verify.
No accounts were created and no credentials were used.

---

## Summary table

| Service | Capability | Free quota | Key needed | Card needed | Automatable | Verified source |
|---|---|---|---|---|---|---|
| Kaggle Notebooks | GPU batch jobs (T4x2/P100), CPU | 30 GPU-h/week [3P quoting Kaggle docs]; 12 h/session; 20 GB disk; 29 GB RAM GPU sessions | Kaggle account + API token, phone verify | No | Yes: `kaggle kernels push` | github.com/Kaggle/kaggle-api/blob/main/docs/kernels.md |
| HF ZeroGPU Spaces | img/video/TTS/music via public Spaces | 2 min/day anon, **5 min/day free**, 40 min/day PRO | HF token (optional, recommended) | No | Yes: `gradio_client` | huggingface.co/docs/hub/spaces-zerogpu |
| HF Inference Providers | serverless APIs | **$0 for free users** (PRO $2/mo) | HF token | Yes, to buy credits | Yes | huggingface.co/docs/inference-providers/pricing |
| Gemini API | text LLM, **TTS** (gemini-3.8-flash-tts etc.) | Free tier exists for Flash/Flash-Lite/2.5 Pro + TTS; RPM/RPD shown only in AI Studio [U numbers] | API key (Google account) | No | Yes | ai.google.dev/gemini-api/docs/pricing |
| Gemini image/video/music | Nano Banana, Lyria, Omni (video) | **No free tier** | key + billing | Yes | — | same |
| Cloudflare Workers AI | FLUX-1-schnell, FLUX.2 klein, SDXL; MeloTTS, Aura; Whisper | **10,000 Neurons/day**, reset 00:00 UTC | account ID + API token | No (Workers Free) | Yes (REST) | developers.cloudflare.com/workers-ai/platform/pricing/ |
| Pollinations | img, TTS, text, video | **Anonymous works today** for non-`paid_only` models; signed-up accounts get only one-time "Quest Pollen" | Not for anon; `sk_` key otherwise | No | Yes (GET URL) | github.com/pollinations/pollinations/blob/main/APIDOCS.md + live test |
| edge-tts | TTS (MS Edge neural voices) | Unlimited (unofficial) | No | No | Yes | pypi.org/project/edge-tts (7.3.1, 2026-10-13) + live test |
| Groq | LLM, Whisper, Orpheus TTS | e.g. Orpheus 10 RPM/100 RPD; whisper 2K RPD, 28.8K audio-s/day ("Developer plan" table, free tier unclear) | key | No [3P] | Yes | console.groq.com/docs/rate-limits |
| OpenRouter | LLM `:free` models | 20 RPM, 50 RPD (1000 RPD after $10 purchased) | key | No | Yes | openrouter.ai/docs/api/reference/limits |
| Together AI | — | **No free credits** ($5 min purchase) | key | Yes | — | support.together.ai (article 7378830629) |
| fal / Replicate | img/video | No documented free tier [U] | key | Yes (effectively) | — | fal.ai/docs FAQ, replicate.com/pricing |
| SiliconFlow | img/video/TTS | $1 signup credit; no $0 models listed | key | [U] | Yes | siliconflow.com/pricing |
| Modal | GPU serverless (T4…H100) | **$30/mo** compute; 10 GPU concurrency | account | No [3P] | Yes (Python SDK) | modal.com/pricing |
| Lightning AI | GPU studios | 5 credits on signup + 25 more with a card; ~80 GPU-h interruptible (per FAQ) | account + phone | No for 5 credits | Partly (SDK/SSH) | lightning.ai/pricing |
| GitHub Actions | CPU ffmpeg | **Public repo: free, unlimited** std runners (4 vCPU/16 GB/14 GB SSD). Private: $12/mo credit (~2,000 min 2-core) | GitHub account | No | Yes | docs.github.com billing + runners pages |
| Oracle Always Free | ARM CPU VM | A1: 1,500 OCPU-h + 9,000 GB-h/mo (= **2 OCPU/12 GB**, not 4/24), 200 GB block, 10 TB egress | account | Yes, at signup [U, widely reported] | Yes | docs.oracle.com Always Free page |
| Colab free | GPU notebooks | T4-ish, unpublished, varies | Google account | No | **No** (interactive only) | [3P] |
| SageMaker Studio Lab | GPU notebook | [U] (FAQ returned 403) | account (approval) | No | No | [U] |
| Paperspace/DO Notebooks | GPU notebook | "free GPU plan" still in DO docs, availability-based | account | [U] | Poor | docs.digitalocean.com/products/paperspace/notebooks |
| Pexels API | stock photo/video | 200 req/h, 20k/mo | key | No | Yes | pexels.com/api/documentation |
| Pixabay API | stock photo/video | 100 req/60 s | key | No | Limited (no bulk automation) | pixabay.com/api/docs |
| Wikimedia Commons | media (mixed licences) | no key; polite UA required | No | No | Yes | live test |
| NASA Images | photo/video/audio | no key | No | No | Yes | live test + nasa.gov guidelines |

---

## 1. Kaggle Notebooks

- **GPU quota**: 30 h/week, "sometimes more depending on demand", resets weekly. TPU v3-8: 20 h/week. [3P: agentdeals.dev quoting kaggle.com/docs/efficient-gpu-usage, read 2026-10-23]. The Kaggle docs pages render with JS and could not be fetched directly. **[U official]**
- **GPU types in the UI**: GPU T4 x2 (2 x 16 GB, separate devices) or P100 16 GB [3P].
- **Accelerator IDs for `kaggle kernels push --accelerator`** [V, kernels.md, "as of Sep 2026"]: `NvidiaTeslaT4` (default, T4x2), `NvidiaTeslaA100`, `NvidiaL4`, `NvidiaL4X1`, `NvidiaH100`, `NvidiaRtxPro6000`, `TpuV5E8`, `TpuV6E8`. The doc says some of these are limited to competition participants or Kaggle admins. Assume a free user gets T4x2 (and maybe P100). `NvidiaTeslaP100` is **not** in the list. Test whether `NvidiaL4` works on your account.
- **Session**: 12 h for CPU/GPU, 9 h for TPU [3P quoting docs]. Older sources say 9 h for GPU.
- **Specs**: GPU session 4 cores / 29 GB RAM. CPU session 4 cores / 30 GB. Disk is 20 GB auto-saved in `/kaggle/working`, plus a larger temporary scratch area [3P].
- **Concurrency**: not documented. **[U]** The quota is pooled, so two GPU kernels at once burn it twice as fast. Plan for 1–2 parallel GPU kernels.
- **Internet**: available but needs a **phone-verified** account (`enable_internet: true` in metadata).
- **Automation** [V kaggle-api docs]:
  - Auth: `KAGGLE_API_TOKEN` env var, `~/.kaggle/access_token`, `kaggle auth login`, or the legacy `~/.kaggle/kaggle.json`.
  - Flow: `kaggle kernels init -p dir` → edit `kernel-metadata.json` (`id`, `title`, `code_file`, `language: python`, `kernel_type: script`, `is_private`, `enable_gpu`, `enable_internet`, `dataset_sources`, `model_sources`) → `kaggle kernels push -p dir --accelerator NvidiaTeslaT4 -t 43200` → poll `kaggle kernels status owner/slug` → `kaggle kernels output owner/slug -p out/ -o`.
  - Exact metadata field names come from the separate `kernels_metadata.md`. They are long-standing names but were not re-read today. **[U]**
- **Terms**: Kaggle services are for "personal, internal, non-commercial use" [3P quoting kaggle.com/terms]. A non-monetized research channel fits this. Mining or crypto use is banned, and abuse of the automation path could be flagged. Batch "commit" runs are the intended unattended mode.
- **Best use**: Wan2.2 I2V/TI2V-5B, Qwen-Image, FLUX-schnell, Kokoro and ACE-Step **batch jobs**. 2 x T4 means no bf16 and 16 GB per card: use fp16 or GGUF quantised models, and expect Wan2.2-14B to be slow. TI2V-5B or LTX are more realistic.

## 2. Hugging Face

### ZeroGPU [V huggingface.co/docs/hub/spaces-zerogpu]
- **Hardware**: NVIDIA **RTX Pro 6000 Blackwell**. `large` = half card, 48 GB (default). `xlarge` = full card, 96 GB, at 2x quota cost. The API still labels the hardware `zero-a10g`.
- **Daily quota**:

  | Tier | Daily quota | Queue priority |
  |---|---|---|
  | Unauthenticated | 2 min | low |
  | Free account | **5 min** | medium |
  | PRO | 40 min, extendable at $1 per 10 min | highest |
  | Team | 40 min | highest |
  | Enterprise | 60 min | highest |

  Quota resets **24 h after your first GPU use**, not at midnight.
- **Billing is per call duration.** The Space's `@spaces.GPU(duration=...)` defines the reservation (default 60 s). A low remaining quota also lowers your queue priority.
- **Per token?** The docs say "When you authenticate with your token, your account's GPU quota is consumed. Unauthenticated requests use a shared pool" [V, spaces-api-endpoints]. Forum reports say token calls sometimes fell back to IP or anonymous quota, fixed via Gradio upgrades [3P]. Use `gradio_client` ≥2.x (current release is 2.7.2).
- **Quota is per account, not per token.** Several tokens on one account share the same 5 min. Multiple accounts to multiply quota would likely breach the HF ToS. Not advised.
- **Realistic free budget**: 5 min/day ≈ 3–6 Wan2.2-fast clips, or roughly 20–40 FLUX-schnell or Z-Image images. Not enough for daily production on its own.
- **Hosting**: a free account can host 2 ZeroGPU Spaces, but only if it is older than 30 days and has a verified email.
- **Call shape** [V, `view_api` run live today]:
```python
from gradio_client import Client, handle_file
c = Client("black-forest-labs/FLUX.1-schnell", token=HF_TOKEN)
img_path, seed = c.predict(prompt="...", seed=0, randomize_seed=True, width=1280, height=720,
                           num_inference_steps=4, api_name="/infer")   # returns (filepath-dict/str, seed)
v = Client("zerogpu-aoti/wan2-2-fp8da-aoti-faster", token=HF_TOKEN)
video, seed = v.predict(input_image=handle_file("frame.png"), prompt="slow push-in, cinematic",
                        steps=6, duration_seconds=3.5, guidance_scale=1, guidance_scale_2=1,
                        seed=42, randomize_seed=True, api_name="/generate_video")
```
- **Callable public Spaces** (all RUNNING on ZeroGPU on 2026-10-30, likes in brackets):

  | Area | Space | Endpoint and params, where checked |
  |---|---|---|
  | Wan2.2 I2V | `zerogpu-aoti/wan2-2-fp8da-aoti-faster` (3784) | `/generate_video`, checked above |
  | Wan2.2 I2V | `r3gm/wan2-2-fp8da-aoti-preview` | — |
  | Wan2.2 first+last frame | `multimodalart/wan-2-2-first-last-frame` | — |
  | Wan2.2 Animate | `alexnasa/Wan2.2-Animate-ZEROGPU` | — |
  | LTX-Video | `Lightricks/ltx-video-distilled` | — |
  | Qwen-Image | `Qwen/Qwen-Image` | `/infer(prompt, seed, randomize_seed, aspect_ratio in {1:1,16:9,…}, guidance_scale=4, num_inference_steps=50, prompt_enhance=True)` |
  | Qwen-Image-Edit | `Qwen/Qwen-Image-Edit` | — |
  | FLUX | `black-forest-labs/FLUX.1-schnell` | `/infer`, see above |
  | FLUX | `black-forest-labs/FLUX.1-dev`, `FLUX.2-dev`, `FLUX.2-klein-4B`, `FLUX.2-klein-9B`, `flux-3-image-klein` | — |
  | Z-Image | `Tongyi-MAI/Z-Image-Turbo` | `/generate(prompt, resolution='1280x720 ( 16:9 )', seed, steps=8, shift=3, random_seed)` |
  | Z-Image | `mrfakename/Z-Image-Turbo` | — |
  | TTS | `hexgrad/Kokoro-TTS` | no named endpoints exposed via view_api; may need `fn_index` or be API-disabled **[U]** |
  | TTS | `ResembleAI/Chatterbox`, `ResembleAI/chatterbox-turbo-demo`, `yasserrmd/VibeVoice` | — |
  | Music | `facebook/MusicGen`, `ACE-Step/Ace-Step-v1.5` | — |

  Spaces disappear, change APIs or hit `RUNTIME_ERROR`. Keep a ranked fallback list and call `view_api()` at startup.
- **Licences** (HF model API, checked today):
  - Apache-2.0: Wan2.2, Qwen-Image, FLUX.1-schnell, FLUX.2-klein-4B, Z-Image-Turbo, Kokoro, ACE-Step.
  - MIT: Chatterbox, MeloTTS.
  - **Non-commercial**: FLUX.1-dev, FLUX.2-dev, FLUX.2-klein-9B (BFL NC licence), MusicGen (CC-BY-NC-4.0).
  - LTX-Video: custom ("other").
  - Non-commercial is OK for a non-monetized research channel, but it blocks any later monetization. Prefer the Apache/MIT options.

### Inference Providers [V pricing doc]
- **Free users: no monthly credits** ("Free Users — None"). PRO gets $2/mo, Team/Enterprise $2/seat. This changed from the earlier $0.10/mo free credit.
- The HF "free serverless inference" path is effectively gone for free accounts. hf-inference is now mostly CPU models.

## 3. Google Gemini API [V ai.google.dev pricing, last updated 2026-10-28]

- **Free tier** (Standard) is "Free of charge" for:
  - Text: `gemini-3.8-flash`, `gemini-3.6-flash`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-lite`, `gemini-3-flash-preview`, `gemini-2.5-pro`, `gemini-2.5-flash`, `gemini-2.5-flash-lite`.
  - Gemma 4.
  - Embeddings: `gemini-embedding-2`, `-001`.
  - **TTS**: `gemini-3.8-flash-tts`, `gemini-3.8-flash-lite-tts`, `gemini-3.1-flash-tts-preview`, `gemini-2.5-flash-preview-tts`.
  - Live, transcribe and native-audio models.
- **Not free**:
  - `gemini-4-argon`, `gemini-3.1-pro-preview`, `gemini-2.5-pro-preview-tts`.
  - **All image models**: `gemini-nano-banana-2.1`, `gemini-3.1-flash-image` (Nano Banana 2), `gemini-3.1-flash-lite-image`, `gemini-3-pro-image`, `gemini-2.5-flash-image`.
  - **Lyria** music (`lyria-3.5`, `lyria-3-clip-preview`, `lyria-3-pro-preview`).
  - `gemini-omni-1.1-flash` (video).
  - Imagen and Veo are no longer on the pricing page at all. A third-party source says Imagen 4 was turned off on 2026-08-17 [3P].
  - **So Gemini cannot be used for free image generation.**
- **Rate limits**: per **project**, not per key. RPD resets at **midnight Pacific**. The exact free RPM/RPD per model are **shown only in AI Studio** (aistudio.google.com/rate-limit) and are not on the docs page. **[U numbers]** Third-party figures conflict (100–1,500 RPD for Flash). For TTS, budget for ~10 RPM and a few hundred RPD until you check your own quota.
- **Terms gotchas**:
  - Free-tier content **is used to improve Google products**. Do not send private data.
  - Your region is supported: Kazakhstan, Kyrgyzstan, Uzbekistan and Tajikistan are all on the available-regions list.
  - TTS output carries a SynthID watermark? Not stated for audio **[U]**. Images do carry SynthID.
  - TTS prices double on 2027-01-01 (paid tier only).
- **Key/card**: an AI Studio API key from a Google account. No card for the free tier.
- **The SDK has moved to the Interactions API.** The docs now show `client.interactions.create` (REST `POST /v1beta/interactions`). Whether `generate_content` still works for TTS was not checked. **[U]**
- **TTS call** [V, docs]:
```python
from google import genai; import base64
client = genai.Client(api_key=GEMINI_API_KEY)
it = client.interactions.create(
    model="gemini-3.8-flash-tts",
    input=[{"type": "user_input", "content": [{"type": "text", "text": narration,
            "annotations": [{"type": "speech_metadata", "style": "calm documentary narrator"}]}]}],
    response_format={"type": "audio"},                       # WAV 24 kHz mono 16-bit
    generation_config={"speech_config": [{"voice": "Charon"}]})
open("vo.wav", "wb").write(base64.b64decode(it.output_audio.data))
```
  - 30 voices: Zephyr, Puck, **Charon** (informative), Kore, Fenrir, Leda, Orus, Aoede, Callirrhoe, Autonoe, Enceladus, Iapetus, Umbriel, Algieba, Despina, Erinome, Algenib, Rasalgethi, Laomedeia, Achernar, Alnilam, Schedar, Gacrux, Pulcherrima, Achird, Zubenelgenubi, Vindemiatrix, Sadachbia, Sadaltager, Sulafat.
  - Multi-speaker supports up to 2 speakers.
- **Image call (paid only)**: `client.interactions.create(model="gemini-nano-banana-2.1", input=prompt)` → `it.output_image.data` (base64).

## 4. Cloudflare Workers AI [V pricing/limits/model pages]

- **Free allocation**: **10,000 Neurons/day** on Workers Free *and* Paid, reset at 00:00 UTC. Paid overage is $0.011 per 1k Neurons. No card is needed for Workers Free.
- **Image models** (cost in Neurons):
  - `@cf/black-forest-labs/flux-1-schnell`: 4.8 per 512² tile + 9.6 per step. A 1024² image at 4 steps ≈ 58 N, so **~170 images/day**. Max 8 steps. Output is a base64 JPEG.
  - `@cf/black-forest-labs/flux-2-klein-4b`: 26 N per output tile, so a 1024² image ≈ 105 N (~95/day).
  - `@cf/black-forest-labs/flux-2-klein-9b`: 1,364 N per first megapixel (~7/day).
  - `flux-2-dev`, `leonardo/lucid-origin` (636 N/tile) and `phoenix-1.0` are expensive.
  - `stable-diffusion-xl-base-1.0`, `sdxl-lightning` and `dreamshaper-8-lcm` are also listed.
- **TTS**:
  - `@cf/myshell-ai/melotts` (MIT): **18.63 N/audio-minute, so ~530 min/day**. Params: `prompt`, `lang`. Returns MP3.
  - `@cf/deepgram/aura-2-en`: 2,727 N per 1k chars, so only ~3.6k chars/day. `aura-1`: 1,364 N per 1k chars.
- **ASR**: `@cf/openai/whisper-large-v3-turbo`: 46.6 N/min (~214 min/day). `whisper`: 41 N/min. Also `whisper-tiny-en`, `nova-3`.
- **No video or music models.**
- **Rate limits**: text-to-image 720 rpm, ASR 720 rpm, TTS not listed.
- **Call shape**:
```python
import requests, base64
U = f"https://api.cloudflare.com/client/v4/accounts/{CF_ACCOUNT_ID}/ai/run/"
H = {"Authorization": f"Bearer {CF_API_TOKEN}"}
r = requests.post(U + "@cf/black-forest-labs/flux-1-schnell", headers=H, json={"prompt": p, "steps": 4, "seed": 123})
open("img.jpg", "wb").write(base64.b64decode(r.json()["result"]["image"]))
r = requests.post(U + "@cf/myshell-ai/melotts", headers=H, json={"prompt": text, "lang": "en"})
# JSON case: r.json()["result"]["audio"] (base64 mp3)  — exact field unverified [U]; may also return audio/mpeg bytes
```
  The `result` envelope is the standard Cloudflare v4 REST shape. The melotts JSON field name was not confirmed. **[U]**
- **Account**: one free Cloudflare account. Create an API token with the "Workers AI" permission and note the account ID. The FLUX-schnell page points to the BFL ToS (Apache weights).

## 5. Pollinations.ai [V APIDOCS.md + live anonymous tests today]

- **New base URL**: `https://gen.pollinations.ai`.
  - Image: `/image/{prompt}`. Text: `/text/{prompt}`. Audio: `/audio/{text}`. Video: `/video/{prompt}`.
  - OpenAI-compatible routes under `/v1` (`chat/completions`, `images/generations`, `audio/speech`).
- **The legacy `image.pollinations.ai/prompt/...` still answers.** It returned a 200 JPEG today with model "sana".
- **Anonymous use works** (no key):
  - `GET gen.pollinations.ai/image/a%20red%20apple?model=tongyi-mai/z-image-turbo&width=512&height=512` returned a 200 JPEG.
  - `GET gen.pollinations.ai/audio/Hello%20world?voice=nova` returned a 200 `audio/mpeg`.
- **No published anonymous quota.** Treat anonymous access as best-effort, and expect stricter limits or queues.
- **Accounts and credits**:
  - Keys are `sk_` (server) or `pk_` (app/OAuth). Legacy raw `pk_` keys are capped at 1 pollen per IP per hour.
  - Pollen ≈ $1 each.
  - Free pollen now comes **only from one-time "Quests"**: 0.25 for the first API key, 0.25 each for the first text/image/audio/video model use, 1 for Discord, 1 for the CLI, 2 for early adopter. That is roughly 2–5 pollen total. **There is no recurring daily free allowance for accounts.** The older Seed/Flower tiers appear to be gone. [V quests/catalog]
- **Free (non-`paid_only`) models**, with cost and `per_user_rpm`:
  - Image:
    - `tongyi-mai/z-image-turbo` (default): 0.004 pollen/image, 60 rpm.
    - `black-forest-labs/flux.1-schnell`: 0.002, 60 rpm.
    - `black-forest-labs/flux.2-klein-4b`: 0.005, 60 rpm.
    - `lykon/dreamshaper-8-lcm`: 0.0001, 300 rpm.
    - `microsoft/mai-image-2.6(-flash)`: 12 rpm.
    - `flux.1.1-pro`, `flux.1-kontext-pro`: 0.03.
  - Audio: `openai/tts-1`, `tts-1-hd`, `microsoft/mai-voice-2.1(-flash)`, `openai/whisper-large-v3`, `gpt-transcribe`.
  - Everything else is paid-only, including Kokoro, Qwen-TTS, ElevenLabs, Gemini TTS, Lyria, Stable Audio, all video models (Wan 3.0, Seedance 2, Kling 3, MiniMax H3…), Qwen-Image, Seedream, and Nano Banana.
- **Voices** (OpenAI-style and ElevenLabs-style names): alloy, echo, fable, onyx, nova, shimmer, ash, ballad, coral, sage, verse, rachel, adam, josh, brian, george…
- **Gotchas**:
  - **Identical requests are served from a shared cache**, and the default seed is 42. Always pass a random `seed`.
  - The `safe` filter is off by default.
  - The legacy endpoint may add a logo (`nologo=false` was echoed in its metadata). The new gen endpoint showed no logo parameter.
  - Pollinations routes to third-party upstreams, so model licence and terms follow the upstream: Z-Image is Apache, FLUX-schnell is Apache, OpenAI TTS output follows OpenAI terms.
- **Call shape**:
```python
import requests, urllib.parse, random
p = urllib.parse.quote(prompt)
img = requests.get(f"https://gen.pollinations.ai/image/{p}",
                   params={"model": "tongyi-mai/z-image-turbo", "width": 1280, "height": 720,
                           "seed": random.randint(1, 2**31)}, timeout=180).content
mp3 = requests.get(f"https://gen.pollinations.ai/audio/{urllib.parse.quote(text)}",
                   params={"voice": "onyx"}, timeout=180).content
# with key: headers={"Authorization": f"Bearer {POLLINATIONS_SK}"}
```

## 6. edge-tts [V PyPI + live test]

- **Version**: 7.3.1, released 2026-10-13. Actively maintained, and **it worked today**: an AndrewMultilingual MP3 and SRT were generated with no key.
- **Gotchas**:
  - It is an unofficial use of the Edge "Read Aloud" endpoint. No SLA, and Microsoft could break it at any time.
  - Custom SSML has been removed. Only `rate`, `volume` and `pitch` are adjustable.
  - Open issues (2026-10-28) report intermittent `NoAudioReceived` errors. Add retries with backoff, and fall back to another voice.
  - Licensing of the output for YouTube is a grey area. It is commonly used, but it sits outside the Azure TTS commercial terms. Acceptable risk for a non-monetized research channel. Credit "Microsoft Edge TTS" if unsure.
- **Best English narrator voices** (from `--list-voices`):
  - `en-US-AndrewMultilingualNeural` / `AndrewNeural`: warm, confident.
  - `en-US-BrianMultilingualNeural`: casual.
  - `en-US-ChristopherNeural`: "Reliable, Authority", news/novel style.
  - `en-US-GuyNeural`, `en-US-EricNeural`, `en-US-SteffanNeural`: news.
  - `en-US-AriaNeural`, `en-US-AvaMultilingualNeural`, `en-US-EmmaMultilingualNeural` (the default voice).
  - `en-GB-RyanNeural`, `en-GB-SoniaNeural`, `en-GB-ThomasNeural`.
  - `en-AU-WilliamMultilingualNeural`.
- **Call shape**:
```python
import edge_tts, asyncio
async def tts(text, out_mp3, out_srt):
    c = edge_tts.Communicate(text, "en-US-AndrewMultilingualNeural", rate="-5%", boundary="WordBoundary")
    sub = edge_tts.SubMaker()
    with open(out_mp3, "wb") as f:
        async for ch in c.stream():
            if ch["type"] == "audio": f.write(ch["data"])
            elif ch["type"] in ("WordBoundary", "SentenceBoundary"): sub.feed(ch)
    open(out_srt, "w").write(sub.get_srt())
asyncio.run(tts(text, "vo.mp3", "vo.srt"))
```
  The default `boundary` is `SentenceBoundary`. Pass `WordBoundary` for word-level captions. The signature was checked in 7.3.1.

## 7. Other API providers

- **Groq** [V rate-limits page]:
  - The published table is labelled "base limits for the Developer plan". Free-tier values are shown only in the console. **[U free]**
  - Listed limits: `canopylabs/orpheus-v1-english` TTS 10 RPM / 100 RPD / 3.6K TPD; `whisper-large-v3(-turbo)` 20 RPM / 2K RPD / 7.2K audio-s/h / 28.8K audio-s/day; LLMs (`openai/gpt-oss-120b`, `qwen/qwen3.8-27b`) 30 RPM / 1K RPD.
  - PlayAI TTS is no longer listed. The free tier needs no card [3P].
- **OpenRouter** [V]: `:free` models get 20 RPM and **50 RPD**, rising to 1,000 RPD after $10 in lifetime purchases. Text only. Free image models were not confirmed. **[U]**
- **Together AI** [V support article]: **no signup credits** ("promotions have ended"). $5 minimum purchase plus a card. The FLUX.1-schnell-Free endpoint was a 2024 three-month promotion and is not current.
- **fal.ai**: the FAQ mentions grants and coupons expiring in 1 week to 1 year, but there is no documented standing free tier. **[U]** Third parties claim $1–$20.
- **Replicate**: the pricing page shows pay-per-use only, with no free tier stated. **[U]**
- **SiliconFlow** [V pricing]: "$1 in free credits" at signup. No $0 models listed. Cheapest image is Z-Image-Turbo at $0.005, Wan2.2 I2V/T2V at $0.29 per video. TTS models: CosyVoice2, IndexTTS-2, Fish-Speech.
- **Novita**: nothing found. **[U]**
- **Kling / Hailuo / Vidu / PixVerse**: the consumer apps have daily watermarked credits [3P]. **No free API credits were confirmed.** APIs are prepaid; PixVerse's starter is about $1 for 5 clips [3P]. Treat as paid.

## 8. Compute platforms

- **Colab free**: unpublished, fluctuating T4 quota, 90-min idle timeout, ~12 h cap [3P]. Colab's FAQ deprioritises or bans non-interactive use, and there is no official job API. **Not suitable for automation.**
- **Lightning AI** [V pricing page]:
  - 5 credits on registration, plus 25 more after adding a card (up to 30 credits ≈ 80 GPU-h interruptible). Credits expire after 12 months. Phone number required.
  - Free hour allotments listed: T4 75 h, L4 31 h, L40S 5 h, A100-40GB 10 h, RTX Pro 6000 3 h.
  - 1 active Studio, which restarts every 4 h. 10 GB storage. SDK/SSH automation is possible.
  - The page is internally inconsistent, so re-check before relying on it.
- **Paperspace (now DigitalOcean)**: the DO docs still say Notebooks "include a free GPU plan", but it is availability-based and there is no headless API for free notebooks. Effectively not usable for automation. **[U details]**
- **SageMaker Studio Lab**: the FAQ returned 403. Historically 4 h GPU/day and an approval queue. **[U]** Interactive only.
- **Modal** [V pricing]:
  - **Starter: $30/month free compute**, 100 containers, 10 GPU concurrency. Per-second rates: T4 $0.000164/s ($0.59/h), L4 $0.80/h, A10 $1.10/h, A100-40 $2.10/h, H100 $3.95/h.
  - $30 ≈ 50 h T4, 37 h L4 or 7.6 h H100 per month.
  - No card needed per third parties [3P]. A card is needed to go past $30.
  - Academics can get up to $10k. **Fully automatable** from Python: `modal run`, `@app.function(gpu="L4")`.
- **GitHub Actions** [V]:
  - **Public repos: standard runners are free and unmetered.** Linux x64/arm64 = **4 vCPU, 16 GB RAM, 14 GB SSD**.
  - Private repos: 2 vCPU / 8 GB, with a $12/month included credit (~2,000 min on a 2-core Linux runner at $0.006/min). Usage is blocked at the limit if no card is on file.
  - Artifacts are limited to 500 MB on the free plan, so push outputs elsewhere (release assets, R2, HF dataset).
  - Job limit is 6 h per job (long-standing; not re-read today **[U]**).
  - A public repo exposes your code and logs, so keep keys in Secrets. Using Actions as general free compute unrelated to the repo can be a ToS issue; ffmpeg rendering of the repo's own videos is a reasonable use.
- **Oracle Cloud Always Free** [V docs]:
  - Ampere A1: 1,500 OCPU-h + 9,000 GB-h per month = **2 OCPU / 12 GB**. This is lower than the old 4/24 figure; the page now says this.
  - 200 GB block storage, 10 TB egress. Must be in the home region.
  - **Idle reclamation**: if 95th-percentile CPU, network and memory all stay below 20% over 7 days, the instance can be reclaimed.
  - A card is required for identity at signup (widely reported, not on this page). **[U]**
  - A1 capacity is often "out of host capacity" in popular regions.

## 9. Stock media

- **Pexels** [V]:
  - Free key (Pexels account). Header `Authorization: KEY`.
  - Endpoints: `GET https://api.pexels.com/v1/search?query=` and `/v1/videos/search?query=`.
  - 200 req/h, 20k req/month by default; free unlimited on request if you attribute properly.
  - API terms require a prominent "Photos provided by Pexels" link and photographer credit where possible.
  - Licence: free use and modification, no attribution required by the licence itself. Banned: selling unaltered copies, depicting people offensively, implying endorsement, redistributing on stock sites. Video use is fine.
- **Pixabay** [V]:
  - Key in the `key` param, 100 req/60 s per key. **Results must be cached for 24 h.** No permanent hotlinking: download the files.
  - **"Automated bulk queries and systematic mass downloads are not allowed"** and the API is meant for human-driven requests. Keep it to a few searches per video.
  - Videos: `GET https://pixabay.com/api/videos/?key=..&q=..`, returning large/medium/small/tiny versions.
  - Licence: free, modifiable, no attribution required. Banned: standalone redistribution, and commercial use of recognisable brands.
  - Pixabay music has no API.
- **Wikimedia Commons** [V live]:
  - No key. Send a descriptive User-Agent.
  - The `api.php` search returns per-file `LicenseShortName` and `Artist` (e.g., CC0). Licences vary per file (CC-BY and CC-BY-SA need attribution; SA has share-alike implications), so **filter by licence** and log attribution.
  - The search backend sometimes returns `cirrussearch-too-busy-error`. Retry.
- **NASA Image and Video Library** [V live + nasa.gov guidelines]:
  - `GET https://images-api.nasa.gov/search?q=..&media_type=image|video|audio`. No key; worked today.
  - Most NASA media is not copyrighted in the US. Credit "NASA".
  - Do not imply endorsement, and do not use the NASA insignia or logos. Third-party-credited items keep their own copyright.
  - **AI rule**: no NASA insignia on AI-generated imagery, never write "according to NASA" about AI output, and label AI content as such.

## 10. Other notable options and leads

- **Kaggle + Modal + Cloudflare** together cover most GPU needs for free. HF ZeroGPU is a bonus at 5 min/day.
- **Music, free and licence-safe**:
  - ACE-Step v1.5 (Apache-2.0) on Kaggle or ZeroGPU (`ACE-Step/Ace-Step-v1.5`).
  - MusicGen is CC-BY-NC: fine for a research channel, not if you monetize.
  - The YouTube Audio Library has no API but is free for YouTube use.
  - Gemini Lyria is paid only.
- **Video gen free**:
  - Kaggle T4x2 running Wan2.2-TI2V-5B, LTX-Video or Wan2.1-1.3B.
  - ZeroGPU Wan2.2-fast Spaces.
  - Modal $30 for L4/A100 bursts.
  - No commercial video API with free API credits was confirmed.
- **Not verified today**: Google Cloud $300 trial (needs card); Puter.js "user-pays" AI; Chutes, DeepInfra and Hyperbolic signup credits. **[U]**
