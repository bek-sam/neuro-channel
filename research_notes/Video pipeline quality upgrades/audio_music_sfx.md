# Audio: Music, SFX/Foley, Post-Production Mixing, and Lip-Sync Options (as of late Oct 2026)

Scope: an automated faceless YouTube explainer pipeline (neuroscience/psychology, 10-20 min, calm ambient/cinematic score under narration, occasional SFX). Research date 2026-10-29. Note on sourcing: about 20 tool calls were used. Primary repos were fetched for ACE-Step 1.5, YuE(2), MMAudio, ThinkSound, InfiniteTalk, Demucs, the HunyuanVideo-Foley HF card and the Stability Community License. Pricing and Content ID points rely mostly on secondary 2026 blogs and are flagged as such.

## Music generation: open-weight vs API (quality, length, speed/VRAM, licence, Content ID)

### Takeaway
For a monetized channel, **ACE-Step 1.5 (MIT, Jan 2026; XL 4B variant Apr 2026)** is the strongest default for local generation. It is commercially permissive, runs in under 4 GB of VRAM (up to 20 GB+ for XL), produces up to 10 minutes per call, generates a full song in seconds, and supports repaint/editing. **YuE2 (Sept 2026)** is newer and has an instrumental mode. Individual creators may monetize its output, but the weights are CC BY-NC 4.0 and need 24 GB of VRAM. Among APIs, ElevenLabs Music (commercial on paid tiers) and Stable Audio 2.5 (cheap per call) suit an automated pipeline. Udio is effectively unusable: downloads have been disabled since Oct 2025. Content ID risk comes from fingerprint matches to registered tracks, not from a track being AI-made. The main danger is that someone else registers similar AI output or a generic stock track.

### Cited Findings
**ACE-Step 1.5 (ace-step/ACE-Step-1.5)**
- Licence is MIT ("This project is licensed under MIT") — [GitHub ACE-Step-1.5](https://github.com/ace-step/ACE-Step-1.5). The HF model card also says MIT and states generated music can be used commercially. Training data is described as licensed/royalty-free, but that claim is self-reported — [NYU RITS summary](https://rits.shanghai.nyu.edu/ai/ace-step-1-5-open-source-music-generation-that-rivals-commercial-ai/). AMD's Feb 2026 blog also calls it MIT and commercial-use friendly — [AMD blog](https://www.amd.com/en/blogs/2026/commercial-grade-ai-music-generation-on-amd-ryzen-ai-and-radeon-ace-step-1-5.html). Conflict: ComfyUI Wiki lists Apache-2.0 — [ComfyUI Wiki](https://comfyui-wiki.com/en/models/ace-step/ace-step-v1-5). The repo says MIT.
- Release date was 2026-01-28 per [NYU RITS](https://rits.shanghai.nyu.edu/ai/ace-step-1-5-open-source-music-generation-that-rivals-commercial-ai/). ComfyUI Wiki says Feb 2026. **ACE-Step 1.5 XL (4B DiT; xl-base / xl-sft / xl-turbo) was released 2026-04-02** — [GitHub](https://github.com/ace-step/ACE-Step-1.5). This supersedes ACE-Step v1 (3.5B, 2025) — [ace-step/ACE-Step](https://github.com/ace-step/ACE-Step).
- Duration is 10 s to 10 min (600 s) — [GitHub](https://github.com/ace-step/ACE-Step-1.5).
- Speed is "under 2 seconds per full song on an A100 and under 10 seconds on an RTX 3090" (0.5-10 s on A100 depending on think mode/steps) — [GitHub](https://github.com/ace-step/ACE-Step-1.5).
- VRAM: "runs locally with less than 4GB of VRAM". Tiers: ≤6 GB runs the 2B turbo DiT with INT8 and CPU offload. 8-16 GB runs the 2B turbo/sft with a 0.6B/1.7B LM. ≥24 GB runs XL sft with the 4B LM. XL needs ≥12 GB with offload/quantization or ≥20 GB without. Supports Mac, AMD, Intel and CUDA — [GitHub](https://github.com/ace-step/ACE-Step-1.5).
- Features: repaint (selective local regeneration), "Complete", cover generation, multi-track generation, Vocal2BGM, track separation, and LoRA training from "8 songs, 1 hour on 3090 (12GB)". There is no dedicated loop function, though the abstract mentions "short loops" — [GitHub](https://github.com/ace-step/ACE-Step-1.5).

**YuE / YuE2 (multimodal-art-projection/YuE)**
- YuE2 plans melody and chords from lyrics plus a style prompt, then renders a full song. Instrumental generation and covers were added to the `yue2-music` agent skill on 2026-09-25 (input: text description, ABC score or reference recording). The tech report came out 2026-09-26 and the arXiv paper 2026-09-29. YuE2-Turbo, ComfyUI nodes and a free NOIZ demo are also listed — [GitHub YuE](https://github.com/multimodal-art-projection/YuE). This supersedes YuE v1 (Jan 2025).
- Licence: code is Apache 2.0. **Weights are CC BY-NC 4.0 plus an "additional creator permission"**: personal users, content creators and musicians may monetize outputs with no fees, but companies must negotiate a commercial licence — [GitHub YuE](https://github.com/multimodal-art-projection/YuE).
- Hardware: Linux, NVIDIA BF16 GPU, **24 GB VRAM**, 48 kHz stereo output. Speed and maximum length are not stated — [GitHub YuE](https://github.com/multimodal-art-projection/YuE).
- Claims that YuE2 beats Suno V6 come from a vendor-style blog and are unverified — [MindStudio](https://www.mindstudio.ai/blog/yue2-open-music-generation-model).

**Other 2026 open models**
- HeartMuLa: a 2026 family of open music foundation models. 3B variants are released and the 7B is pending. It focuses on lyric controllability — [GitHub heartlib](https://github.com/HeartMuLa/heartlib).
- MiniMax Music 3 is described as "open-weight" in one blog without detail. Unverified; see Gaps.

**Stable Audio Open / Open Small (Stability AI Community License)**
- Commercial use is free until you or your affiliates exceed **USD 1M annual revenue**, after which the licence terminates unless Stability grants an enterprise licence. Commercial use requires **registration** with Stability. "You own any outputs ... to the extent permitted by applicable law." Outputs may not be used to train other foundation models — [Stability AI Community License](https://stability.ai/community-license-agreement). Re-hosts of Stable Audio Open Small repeat the <$1M condition and the acceptable-use policy (AUP) — [HF re-host](https://huggingface.co/joeriben/stable-audio-open-small).
- Stable Audio Open's VAE is reused inside ThinkSound, so the Stability licence propagates to that model — [ThinkSound GitHub](https://github.com/FunAudioLLM/ThinkSound).

**APIs**
- **Suno**: Pro is about $10/mo ($8/mo annual) with commercial rights. Download caps reportedly sit at 20 songs/mo on Pro and 60 on Premier (Sept 2026 snapshot). Premier is quoted at $24 or $30, sources conflict. Suno settled with Warner (Nov 2025). The Sony case was still ongoing in 2026. All of this is secondary-source data — [MuseGen blog](https://www.musegen.ai/blog/suno-vs-udio); [DEV](https://dev.to/akaranjkar08/suno-songs-on-youtube-2026-content-id-and-disclosure-40p7). Suno's terms reportedly promise no copyright vests in output — [Genx Notes](https://blog.genxnotes.com/en/can-you-get-youtube-content-id-on-suno-generated-ai-music/). Suno has no official public API (the "APIs" are third-party wrappers). See Gaps.
- **Udio**: signed deals with UMG, Warner, Merlin and Kobalt. **Audio/video/stem downloads have been disabled on all plans since 29 Oct 2025**, and terms limit use to personal, non-commercial. **This supersedes earlier Udio commercial-use info** — [MuseGen](https://www.musegen.ai/blog/suno-vs-udio); [Layer3](https://www.layer3labs.io/comparisons/suno-vs-udio).
- **ElevenLabs Eleven Music (API)**: commercial rights vary by tier, per the official Music v1 Terms rights table. The free tier has no commercial licence and requires attribution. Starter ($6/mo) is reportedly the minimum for commercial use. API needs a paid plan — [ElevenLabs Music API page](https://elevenlabs.io/ja/eleven-music-api); [smallest.ai](https://smallest.ai/blog/elevenlabs-pricing-plans-cost-what-you-get-in-2026). Music v2 launched (~May 2026) with section-level editing and an up-to-50% price cut on music generation — [createwith](https://www.createwith.com/tool/elevenlabs/updates/elevenlabs-launches-music-v2-with-better-vocals-and-50-price-cut); [mer.vin](https://mer.vin/2026/05/elevenlabs-music-v2-genre-switching-ai-songs-with-section-level-editing/?amp=1). ElevenLabs markets it as trained on licensed data and cleared for commercial use (secondhand) — [MindStudio](https://www.mindstudio.ai/blog/elevenlabs-music-v2-commercial-content-licensed-ai-music).
- **Stable Audio 2.5 API**: was 20 credits ($0.20) per generation of up to 3 min ($0.01/credit) — [CometAPI](https://www.cometapi.com/ai-music-api-pricing/). A reported **cut to 8 credits (~$0.08/call) on 2026-10-23** comes from a single third-party tracker — [UsagePricing](https://www.usagepricing.com/blueprint/activity/stability-ai-2026-10-23-stable-audio-api-price-cut).
- **Google Lyria**: Lyria 2 (lyria-002, Vertex, GA) costs $0.06 per ~30 s clip. **Lyria 3 Clip costs $0.04 per 30 s**, so Lyria 3 appears to supersede Lyria 2/MusicFX — [CometAPI](https://www.cometapi.com/ai-music-api-pricing/). No Lyria RealTime price was found.

**Content ID**
- Content ID matches audio fingerprints against registered references. It does not detect "AI-ness". Claims arise when someone registered a similar track first or when output lands close to an existing song — [DEV](https://dev.to/akaranjkar08/suno-songs-on-youtube-2026-content-id-and-disclosure-40p7); [sunowatermark](https://sunowatermark.com/youtube-content-id-ai-music/). Most distributors reportedly won't register Suno tracks for Content ID, and Amuse reportedly disabled Content ID registration for AI music in 2026 (unverified) — [Genx Notes](https://blog.genxnotes.com/en/can-you-get-youtube-content-id-on-suno-generated-ai-music/); [DEV](https://dev.to/akaranjkar08/suno-songs-on-youtube-2026-content-id-and-disclosure-40p7).
- AI music should be disclosed through YouTube's "altered or synthetic content" label when it is the main focus — [DEV](https://dev.to/akaranjkar08/suno-songs-on-youtube-2026-content-id-and-disclosure-40p7). This label is probably not required for background score; see Inferences.

### Inferences
- Recommended stack: ACE-Step 1.5 (2B turbo for speed, XL-sft for quality) generating 3-6 min instrumental beds per video segment. Use repaint for transitions, crossfade-loop to cover 10-20 min, and keep a hash/archive of every generated track plus prompt/seed as provenance evidence for disputing claims.
- Generic calm ambient pads are exactly the content most at risk of collisions with registered stock/AI tracks. Prefer unique generations per video over reusing popular library tracks. Never register your own beds with Content ID, since that creates claim wars on re-uploads.
- YuE2 is fine legally for a solo creator but adds little for instrumental beds at 24 GB. Its strength is vocals/songs.
- MusicGen/AudioCraft weights are CC-BY-NC (prior knowledge, not re-verified this session), so avoid them for monetized use. Stable Audio Open is usable under $1M revenue with registration, but caps out at short clips (~47 s for Open, ~11 s for Small, prior knowledge), so it is better suited to stingers and textures than to full beds.
- Udio is out. Suno works but has no official API and download caps, which makes it a poor fit for automation.

### Gaps
- No primary-source fetch was done for DiffRhythm, SongBloom, Levo/LeVo, MusicGen licence or MiniMax Music (open status unclear, likely API-only). Their licences need checking on their repos and HF cards.
- No independent instrumental-quality benchmark comparing ACE-Step 1.5 vs YuE2 vs APIs was found.
- Exact ElevenLabs Music per-minute API price after the v2 price cut, and official Suno/YouTube help-page text, were not retrieved.
- Whether YouTube's 2025-26 "inauthentic/mass-produced content" monetization policy affects AI-score channels was not researched.

## SFX / foley / video-to-audio

### Takeaway
The best video-synced open models (**MMAudio**, **ThinkSound/PrismAudio**) have **non-commercial weights**. **HunyuanVideo-Foley** is the strongest open option with a commercial path, but it uses the Tencent Hunyuan Community licence, which reportedly carries territorial exclusions (EU/UK/South Korea). For a monetized pipeline with only occasional transition whooshes and hero-clip ambience, the **ElevenLabs SFX API** (commercial on paid tiers, 0.1-30 s, loop option) or Stable Audio Open (under $1M revenue) are the license-clean choices. Use HunyuanVideo-Foley only after reading its licence and confirming your territory.

### Cited Findings
- **MMAudio**: code is MIT, **weights CC-BY-NC 4.0**, and the authors don't guarantee commercial suitability. Uses about 6 GB VRAM (fp16). Default/training duration is 8 s and longer clips may degrade. Trained on AudioSet, Freesound, VGGSound, AudioCaps and WavCaps. No 2026 updates (last log entry Mar 2025; CVPR 2025) — [GitHub MMAudio](https://github.com/hkchengrex/MMAudio).
- **ThinkSound**: Apache 2.0 nominally, but "code, models, and dataset are for research and educational purposes only. Commercial use is NOT permitted". It bundles the Stable Audio Open VAE under the Stability licence. The follow-up **PrismAudio** (ICLR 2026) was released on the `prismaudio` branch on 2026-03-24 — [GitHub ThinkSound](https://github.com/FunAudioLLM/ThinkSound).
- **HunyuanVideo-Foley**: licence tag `tencent-hunyuan-community`. XL model with offload added 2025-09-29. No 2026 news on the HF card — [HF card](https://huggingface.co/tencent/HunyuanVideo-Foley). VRAM is 20 GB for XXL (12 GB with offload) and 16 GB for XL (8 GB with offload). Reported DeSync is 0.74 vs MMAudio's 0.80 (lower is better; author/third-party figures) — [search summary of README / habr](https://huggingface.co/spaces/tencent/HunyuanVideo-Foley/blob/main/README.md?code=true). The claim that the licence excludes EU/UK/South Korea and allows commercial use under conditions comes from secondary blogs — [aifilms](https://studio.aifilms.ai/blog/hunyuanvideo-foley); [xugj520 guide](https://www.xugj520.cn/archives/hunyuanvideo-foley-ai-foley.html).
- **ElevenLabs Sound Effects**: duration 0.1-30 s, 40 credits per second when duration is set, and a seamless-loop option — [ElevenLabs SFX docs](https://elevenlabs.io/docs/capabilities/sound-effects). Third parties quote ~$0.12/min, which conflicts with the per-second credit pricing — [Picsart API](https://picsart.com/api-platform/models/elevenlabs-sfx/pricing).
- Stable Audio Open for SFX: commercial use under the $1M-revenue Community License with registration — [Stability license](https://stability.ai/community-license-agreement).

### Inferences
- Explainer videos rarely need frame-accurate foley. A library of 20-50 pre-generated whooshes, risers, soft impacts and "neural" textures is enough. Generate them once (ElevenLabs SFX or Stable Audio Open), QC them, and reuse them by tag. Video-to-audio models matter only for AI-generated "hero clips", where HunyuanVideo-Foley (licence permitting) is the quality pick.
- AudioLDM2 (prior knowledge: weights CC-BY-NC-SA) is superseded in quality by the models above and is not recommended.

### Gaps
- The full Tencent Hunyuan Community licence text (territory clause, MAU thresholds) was not fetched directly.
- No independent speed benchmarks (seconds per 8 s clip) for MMAudio, HunyuanVideo-Foley or PrismAudio were found.
- PrismAudio's own licence/weights terms (prismaudio branch) were not checked.

## Royalty-free libraries with APIs

### Takeaway
**Freesound (CC0 filter)** and **Pixabay** are free and API-accessible. Epidemic Sound has a developer API, but production use needs a sales-negotiated paid tier. Library tracks carry **higher Content ID collision risk** than unique generations, because the same tracks get used and sometimes registered by others.

### Cited Findings
- Freesound has a RESTful API. Licences are per sound (CC0, CC-BY, CC-BY-NC), so filter to CC0 (or CC-BY with attribution) — [Wikipedia Freesound](https://en.Wikipedia.com/wiki/Freesound); [toolradar guide](https://toolradar.com/guides/best-free-music-and-sound-effects-for-commercial-use).
- Pixabay Music: free, commercial use, no attribution required. Pre-2019 uploads are CC0 — [Cinevva guide](https://app.cinevva.com/guides/free-sound-effects-music); [toolradar](https://toolradar.com/tools/pixabay-music).
- Epidemic Sound API: the free developer tier covers prototyping only, with the full catalog but no go-live or sublicensing. Going live needs a paid tier through sales, with no public price — [Epidemic Sound blog](https://www.epidemicsound.com/blog/free-api/); [Partner API](https://go.epidemicsound.com/developers/partner-api/).

### Inferences
- Epidemic's consumer creator subscription includes channel whitelisting for Content ID (prior knowledge). This is its main advantage over Pixabay, whose tracks occasionally get claimed by third parties who register them.

### Gaps
- Whether Pixabay's public API (pixabay.com/api/docs) exposes an audio/music endpoint was not confirmed. It historically covered only images and videos.
- The YouTube Audio Library has no public API (prior knowledge, not verified this session).

## Automatic mixing and post-production

### Takeaway
Do it all in ffmpeg. Use `sidechaincompress` with narration as the key and music as the compressed input, add `amix`, then run two-pass `loudnorm` to about -14 LUFS integrated with a true peak of -1.5 to -1 dBTP, and verify with `ebur128`. Use Demucs only to strip vocals from generated music. It is archived but still usable. DeepFilterNet (MIT/Apache) is the license-clean speech cleanup option.

### Cited Findings
- Ducking pattern: run sidechaincompress on music keyed by narration, with threshold ~0.015-0.02 and ratio ~6-10 — [skills.sh audio-mixing-patterns](https://skills.sh/yonatangross/orchestkit/audio-mixing-patterns); [imgix duck](https://docs.imgix.com/apis/video/audio/audio-mark-duck).
- Two-pass loudnorm: pass 1 uses `loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json -f null -`, then pass 2 feeds the measured values back with `linear=true`. Use `-c:v copy` when only the audio changes — [DEV loudnorm guide](https://dev.to/javidjamae/ffmpeg-loudnorm-filter-ebu-r128-loudness-normalization-guide-15d4); [ahosting](https://www.ahosting.net/faq/ffmpeg-hosting/how-to-normalize-audio-loudness-with-ffmpeg.html).
- YouTube normalizes to about -14 LUFS. Voice/podcast content commonly targets -14 to -16 — [ahosting](https://www.ahosting.net/faq/ffmpeg-hosting/how-to-normalize-audio-loudness-with-ffmpeg.html); [fileflows](https://fileflows.com/docs/plugins/audio-nodes/audio-file-normalization).
- Demucs: **archived Jan 1, 2025**, unmaintained, MIT. Fork at adefossez/demucs gets only critical fixes. Models are `htdemucs`, `htdemucs_ft` (4x slower, slightly better), `htdemucs_6s` (piano weak) and `hdemucs_mmi` — [GitHub Demucs](https://github.com/facebookresearch/demucs).
- DeepFilterNet: dual MIT/Apache-2.0 (per mirrors) — [mirror](https://github.com/lucribas/DeepFilterNet); [MLX conversion](https://huggingface.co/mlx-community/DeepFilterNet-mlx/commit/fc73d82b5039bd88401eef6cd757a2e8d37fef3b). Resemble Enhance is open-source speech denoise plus bandwidth enhancement (licence not confirmed in sources) — [The Decoder](https://the-decoder.com/resemble-ais-open-source-model-transforms-noisy-audio-into-crystal-clear-speech/).

### Inferences
- Suggested chain (template, untested). It is a sketch only: verify the dB/threshold values by ear.
  ```
  [1:a]volume=-18dB,afade=t=in:d=3[m];
  [m][0:a]sidechaincompress=threshold=0.02:ratio=8:attack=20:release=400:makeup=1[duck];
  [0:a][duck]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-14:TP=-1.5:LRA=11[out]
  ```
  `[0:a]` must be split with `asplit` because it is used twice. Follow the mix with a second loudnorm pass using the measured values and `linear=true`.
- Keep the music bed about 18-24 dB below the voice before ducking. An ACE-Step instrumental may contain stray vocal-like artifacts. Running `htdemucs` with `--two-stems=vocals` and keeping the "no_vocals" stem is a cheap safety step.
- TTS narration is usually clean. A denoiser (DeepFilterNet) is needed only for recorded voice. VoiceFixer/Resemble Enhance can over-process TTS.

### Gaps
- No licence confirmation for Resemble Enhance or VoiceFixer, and no 2026 maintenance status for either.
- No source tested ACE-Step outputs for residual vocals.

## Lip-sync / talking avatars (brief)

### Takeaway
If a presenter is added later: **MuseTalk (MIT, real-time, 256px)** for lightweight dubbing-style lip-sync, **LatentSync 1.6 (OpenRAIL++, 512px, ~18 GB)** for sharper lip-sync, and **InfiniteTalk (Apache-2.0, Wan2.1-14B based, 480/720p, long-form)** for full-body audio-driven video. Its successor **LongCat-Video-Avatar-1.5 (May 2026)** is the newest open option. HeyGen's API costs about $1-4+/min, pay-as-you-go.

### Cited Findings
- MuseTalk: MIT code and models, commercial use allowed, 30 fps+ real-time, ~6-8 GB at 256x256 — [creativeainews](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/); [sync.so](https://sync.so/blog/what-is-musetalk).
- LatentSync 1.6: OpenRAIL++, ~18 GB, 512x512, ~6 fps — [creativeainews](https://www.creativeainews.com/articles/open-source-lip-sync-licenses-commercial-use-2026/); [aifilms](https://studio.aifilms.ai/blog/latentsync-1-6-musetalk-1-5-open-source-lip-sync-dubbing).
- InfiniteTalk: Apache 2.0 ("models in this repository"), 480p/720p, default 1000 frames (~40 s). Image-to-video is good to ~1 min before color shift, while video-to-video supports unlimited length. 4-8 step LoRAs (lightx2v/FusionX) are available, and fp8 quantization exists. Base model Wan2.1-I2V-14B carries its own terms. **LongCat-Video-Avatar** was released 2025-12-16 and **LongCat-Video-Avatar-1.5** (Whisper-Large audio, 8-step distillation, multi-stream) on 2026-05-21 — [GitHub InfiniteTalk](https://github.com/MeiGen-AI/InfiniteTalk).
- HeyGen API: separate pay-as-you-go wallet ($5 minimum), no free API credits since Feb 2026. About $1/min standard and ~$4/min Avatar IV (other sources say $3-6), or $0.0167-$0.0667/s — [G2](https://www.g2.com/articles/heygen-api-pricing); [arcade](https://www.arcade.software/post/heygen-pricing). Hedra API: prepaid wallet, billed by generated length, 110+ models. No reliable per-minute API price was found (~$2.88/min on the Lite plan per one blog) — [novoads](https://novoads.ai/en/blog/hedra-pricing).

### Inferences
- For a 10-20 min explainer with occasional presenter segments, an InfiniteTalk/LongCat avatar for short intro/outro clips plus faceless visuals elsewhere is cheapest. A continuous HeyGen presenter would cost about $10-80 per video at the rates above.

### Gaps
- No licence or quality data was found for Wan-S2V, MultiTalk, FantasyTalking or Hallo3 this session.
- LongCat-Video-Avatar's licence was not verified.
