# Open-weight / self-hostable video generation for a faceless explainer pipeline (state as of 29 Oct 2026)

Context: current hero model is Wan2.2-I2V-A14B on Modal H100 (~900 s per 5 s clip = ~$0.99/clip at $3.95/h). Fallback is Wan2.2-TI2V-5B. Untested candidate is LTX-2.5 (~120 s on H100 = ~$0.13/clip). Cost conversions: H100 = $0.00110/s, A100-80 = $0.00069/s, A100-40 = $0.00058/s, A10G = $0.00031/s.

Research method note: about 20 searches and fetches. Primary sources fetched: the Artificial Analysis I2V leaderboard, the LTX-2.5-Diffusers HF card, the Cosmos3-Super-I2V-4Step HF card, the lightx2v GitHub README, and the RunPod MiniMax H3 write-up. Much other 2026 coverage is secondary (blogs, aggregators), and claims from it are flagged as such. Items marked "(prior knowledge, not re-verified)" are 2025-era facts from well-known repos. Their links are included, but they were not re-fetched in this session.

## Q1. Which open models lead on quality for I2V/T2V now?

### Takeaway
The open-weight landscape changed a lot in mid-2026. Wan stopped open-sourcing flagships after 2.2: Wan 2.5, 2.6 and 3.0 are API-only. The open quality leader on the Artificial Analysis (AA) I2V arena is now **MiniMax H3 (768p, 33B, open since 3 Aug 2026)**. It ranks #4 overall, above Veo 3.1 and Kling 3.0. **Its licence appears to bar use in the US/EU/UK/South Korea**, which may rule it out depending on where the channel operates. The next open entries are **LTX-2.5 Fast/Pro (Aug 2026)**, which are far behind H3 but fast, and **NVIDIA Cosmos3-Super-I2V (64B)**, which is multi-GPU only and tuned for physical-AI footage. Wan2.2-A14B is still the best fully permissive (Apache 2.0) single-GPU option, and with 4-step distillation it gets much cheaper.

### Cited Findings
**Artificial Analysis I2V leaderboard (with audio, AA-Video-I2V v2.1, fetched 29 Oct 2026)** — [AA I2V leaderboard](https://artificialanalysis.ai/video/leaderboard/image-to-video)
- #1 Dreamina Seedance 2.5, Elo 1152, Jul 2026, $34.12/min. #3 Seedance 2.0, 1135, $22.45/min.
- **#4 MiniMax H3 (768p), Elo 1128, open weights, Jul 2026, $4.80/min via API.**
- #6 HeyGen Video 1, 1119, $2.40/min. #9 Wan 3.0, 1111 (closed), $12.00/min. #10 Agnes-Video-2.5, 1103, $2.40/min.
- #17 Kling 3.0 1080p Pro, 1000 (anchor), $10.08/min. #21 Veo 3.1, 956, $24.00/min. #22 Veo 3.1 Fast, 934, $7.20/min. #24 Veo 3.1 Lite, 928, $4.80/min.
- **Open-weight entries:** #4 MiniMax H3 (1128), #25 LTX-2.5 Fast (916), #26 LTX-2.5 Pro (909), #28 LTX-2.3 Pro (837), #29 LTX-2.3 Fast (830).
- Silent board: the open leader is MiniMax H3 (768p) at 1112, followed by LTX-2.5 Fast (916) and LTX-2.5 Pro (907). The silent top 5 are Seedance 2.5 (1126), MiniMax H3 Max (1124), Bach 1.0 Pro (1120), Hyperflow H3 (1114) and Agnes-Video-2.5 (1113).
- Wan2.2, HunyuanVideo 1.5, SkyReels, Kandinsky and Cosmos3 did not appear in the extracted open-weight list of the with-audio board. A search snippet showed Cosmos3-Super-Image2Video-4Step at Elo 1263 on the open silent board in an earlier snapshot — [search snippet of AA page](https://artificialanalysis.ai/video/leaderboard/image-to-video). This conflicts in scale with the current 1112 for H3, which suggests the Elo was re-based between versions.

**MiniMax H3 (open base)** — [RunPod blog, updated 25 Aug 2026](https://www.runpod.io/blog/minimax-h3-the-open-weight-omni-modal-video-model-and-what-it-takes-to-run-it)
- 33.1B dense single-stream "Omni Transformer". About 13B sits in AdaLN branches that can be precomputed and cached. The text encoder is Qwen3-VL-32B.
- 768p locally. 2K is only available through the hosted "H3-Regenerate-2K" stage. 24 fps, 4–15 s clips, native 32 kHz stereo audio.
- The open checkpoints are H3-Base `FL2VA` (first/last frame to video+audio) and `Ref2VA`, both CFG-distilled.
- ComfyUI has day-0 support. Diffusers is not mentioned. The RunPod guide suggests about 600 GB of volume disk. No VRAM or timing figures are given.
- **Licence:** "MiniMax H3 Community License", source-available with territory restrictions. It "appears to not authorize use in the United States, European Union, United Kingdom, or South Korea", including use of outputs.
- A 12 GB VRAM claim (RTX 3060) circulates but is unofficial. It needs a lot of system RAM and streams weights from disk — [mer.vin](https://mer.vin/news/minimax-h3-open-weight-video-model-blocked-us-eu-uk/), [instasd](https://instasd.com/post/minimax-h3-open-weights-comfyui-local). One source claims a $20M revenue cap, which conflicts with the territory framing. Verify against the HF card MiniMaxAI/MiniMax-H3.
- lightx2v lists MiniMax-H3 as a supported model — [lightx2v README](https://github.com/modeltc/lightx2v).

**LTX-2.5 (Lightricks, released 11 Aug 2026)**
- HF Diffusers card: 19B (BF16). Example resolution is 960x544 with a two-stage recipe: generate at half resolution, then x2 latent upsampler. 24 fps, 121-frame examples. A `duration_head` can predict length.
  - Variants: distilled transformer (default, unguided sigma schedule) and full/SFT `transformer_full/` (about 30 steps). There is also an optional diffusion decoder pipeline.
  - Pipelines: `LTX2Pipeline`, `LTX2LatentUpsamplePipeline`, `LTX2VideoDiffusionDecodePipeline`, `ModularPipeline`. Needs diffusers from the main branch.
  - Repo is 72 GB, or 110 GB with the full transformer. CPU offload is recommended. I2V is supported.
  - Licence: LTX-2.x Community License, free for commercial use under $10M annual revenue — [HF LTX-2.5-Diffusers](https://huggingface.co/Lightricks/LTX-2.5-Diffusers).
- Secondary coverage gives 22B (vs 19B on the card), native multi-shot (consistent character, lighting and voice across cuts), a diffusion decoder, 4K HDR, and runs from 16 GB VRAM — [ComfyUI wiki](https://comfyui-wiki.com/en/news/2026-08-11-ltx-2-5-open-weights-release), [RITS/NYU Shanghai](https://rits.shanghai.nyu.edu/ai/ltx-2-5-adds-native-multi-shot-video-and-a-diffusion-decoder/).
- Vendor speed claim: a 10 s 720p clip in 6.8 s on 2x GB200 — [cryptobriefing](https://cryptobriefing.com/ltx-2-5-ai-video-model-release/). A critic notes these charts are vendor, not independent — [search summary, ComfyUI wiki/Medium](https://medium.com/@creativeaininja/ltx-2-5-what-lightricks-open-weights-video-model-actually-does-and-how-to-run-it-a17bad9664fd).
- Sources conflict on whether 2.5 Pro reaches 4K — [aireiter](https://aireiter.com/blog/ltx-2-5-api-pricing-guide).
- LTX-2.3 (Mar 2026) is superseded by 2.5 — [wink.ai roundup](https://wink.ai/blog/best-open-source-image-to-video-ai-models).

**NVIDIA Cosmos3-Super-Image2Video(-4Step)** — [HF card](https://huggingface.co/nvidia/Cosmos3-Super-Image2Video-4Step)
- Released 20 Jul 2026. 64B Mixture-of-Transformers. The 4-step variant is DMD2-distilled with no CFG, for up to 25x fewer evaluations than 50-step+CFG.
- Recommended 832x480. Accepts 256p/480p/720p. 5–400 frames (189 by default), about 24 fps.
- Needs a 4–8x H100/H200 node or a single B200. "Does not fit on a single smaller GPU", and a single H100 may OOM.
- Estimated times for 189 frames at 480p: 6.4 s on 1x B200, 4.0 s on 4x H200. These are derived estimates, not measurements.
- Licence OpenMDW-1.1, commercial use OK. Diffusers support via `Cosmos3DistilledModularPipeline` (main branch).
- Intended for physical AI (robotics, AV). A community NVFP4 quant exists (unofficial) — [prometheusAIR](https://huggingface.co/prometheusAIR/Cosmos3-Super-Image2Video-4Step-NVFP4).

**Wan family**
- Wan 2.5 (2025) and 2.6 (Dec 2025) were API-only. Wan 3.0 entered API beta on 6 Aug 2026 with no open weights as of an HF check on 20 Aug 2026. Alibaba did release Wan-Animate-2 under Apache 2.0 on 7 Aug 2026. Wan 2.2 (Apache 2.0, 28 Jul 2025) is the last open flagship — [atlascloud](https://www.atlascloud.ai/ja/blog/tips/is-wan-3.0-open-source), [mindstudio](https://www.mindstudio.ai/blog/what-is-wan-2-5-image).
- One site claims open Wan 3.0 1.3B/14B weights from April 2026 — [wan27.org](https://wan27.org/blog/wan-3-open-source). This is contradicted by the above, and the site looks like an unofficial fan or SEO domain. Treat it as false unless the Wan-AI HF org shows the weights.

**Kandinsky 6.0 Video**
- Weights released 6 Oct 2026, MIT licence. 29B Pro and 3B Lite. 5 s clips with synced 44 kHz audio, T2V and I2V — [sbbit.jp](https://www.sbbit.jp/article/cont1/187393), [vo3ai](https://www.vo3ai.com/kandinsky-6-video).
- Distilled variants at 10 steps vs 50 steps for the full models. Runs on 16–32 GB cards via block offload. Pro needs about 58 GiB system RAM at the 16 GB preset — [miraflow](https://miraflow.ai/blog/kandinsky-6-0-video-explained-open-source-audio-video-model-2026).
- No timing numbers were found, and it is not on the AA open list extracted above.

**MAGI-2 Preview (Sand AI, Aug 2026)**
- 114B MoE with about 6B active, unified audio-video, 10 s clips, Apache 2.0 — [pinggy roundup (secondary)](https://pinggy.io/blog/best_video_generation_ai_models/). Not verified against a primary source.

**SkyReels V3 (Skywork, open 29 Jan 2026)**
- Reference-image-to-video (R2V-14B), video extension (V2V-14B), and audio-driven avatar (A2V-19B). Custom Skywork licence — [HF SkyReels-V3-V2V-14B](https://huggingface.co/Skywork/SkyReels-V3-V2V-14B), [HF A2V-19B](https://huggingface.co/Skywork/SkyReels-V3-A2V-19B), [10jqka](https://stock.10jqka.com.cn/20260129/c674414059.shtml).

**HunyuanVideo 1.5**
- lightx2v released 4-step distilled HunyuanVideo-1.5 models on 24 Nov 2025, claiming about 25x vs 50 steps — [lightx2v README](https://github.com/modeltc/lightx2v).
- No HunyuanVideo 2 open release was found.

### Inferences
- **MiniMax H3 is the only open model that clearly beats Wan 2.2 and LTX-2.5 on human preference.** Its licence territory clause is a hard blocker if the operator or audience is in the US/EU/UK. YouTube monetisation of outputs viewed there may also be a grey area. Get legal clarity before adopting it. Technically, its FL2VA checkpoint (first/last frame) is a good fit for scene chaining.
- LTX-2.5's AA Elo (about 910) sits roughly 90 below Kling 3.0 and about 45 below Veo 3.1. It is fast and cheap, but quality is mid-tier. Because it renders 24 fps natively with an x2 upsampler, it can reach about 1080p in one pass.
- Cosmos3-Super is impractical on Modal single-GPU H100 economics, since it needs 4–8 GPUs or a B200. Its physical-AI tuning also fits abstract neuroscience b-roll poorly.
- Wan2.2-A14B is still competitive as an Apache-licensed model, but its 900 s per clip runtime is the real problem. Acceleration (Q2) is the cheapest upgrade.

### Gaps
- No measured H100 or A100 seconds-per-clip for MiniMax H3, Kandinsky 6 or LTX-2.5 at 720p/1080p. The user's own ~120 s LTX-2.5 estimate is unverified.
- Exact MiniMax H3 licence text was not fetched. The territory restriction comes from secondary sources.
- VBench leaderboard positions for 2026 models were not retrieved.
- Mochi and CogVideoX successors: nothing new found. Treat them as superseded (2024-era).
- Step-Video and MAGI-1 are 2025-era and were not re-checked.

## Q2. Few-step / distilled variants and acceleration

### Takeaway
4-step distillation is the single biggest lever. lightx2v ships Wan2.2-I2V-A14B 4-step distilled models, including 720p I2V (Apr 2026). Its model card reports **26.7 s vs ~2685 s (40 steps) for a 720p I2V run** (GPU unstated, likely Blackwell). On an H100 a realistic estimate is roughly 60–150 s per 5 s clip, which is about **$0.07–0.17 per clip**. Stacking FP8, SageAttention and feature caching (TeaCache/MagCache) adds about 1.5–2x. The quality cost is mainly reduced motion amplitude or "slow-mo" and some loss of detail. Community fix LoRAs for this exist.

### Cited Findings
**lightx2v framework** — [README, news through 26 Oct 2026](https://github.com/modeltc/lightx2v)
- Supported models include Wan2.1/2.2 (T2V, I2V, S2V, Animate, VACE), HunyuanVideo-1.5 (4-step), LTX-2/2.3/2.5 distilled, MiniMax-H3, Self-Forcing and SeedVR2.
- Quantization: W8A8 (INT8/FP8) and W4A4 NVFP4. FP8/NVFP4 for Self-Forcing autoregressive models arrived on 27 Feb 2026.
- Feature caching: TeaCache, MagCache, TaylorSeer. Attention backends: SageAttention and FlashAttention. Parallelism: TP, SP (Ulysses), CFG-parallel.
- Claimed speedups: Wan2.2 NVFP4 4-step >50x vs 40-step on a single RTX 5090; HunyuanVideo-1.5 4-step about 25x vs 50-step.

**Wan2.2 distill models**
- 720p 4-step I2V models were released on 12 Apr 2026. High-VRAM configuration recommends 80 GB+ (A100/H100). High-noise and low-noise expert variants are provided. BF16 gives the best quality and FP8/INT8 is slightly lower — [HF lightx2v/Wan2.2-Distill-Models](https://huggingface.co/lightx2v/Wan2.2-Distill-Models).
- LightWan2.2 card: 720p I2V at 4 steps took 26.7 s vs about 2685 s at 40 steps (GPU not named; card targets a single Blackwell GPU) — [HF lightx2v/LightWan2.2-A14B](https://huggingface.co/lightx2v/LightWan2.2-A14B).
- Older H100 table (Wan2.1-I2V-14B 480p, 81 frames): the lightx2v framework alone gives about 1.9–2.1x vs the 40-step baseline, without distillation — [search summary of lightx2v docs](https://huggingface.co/lightx2v/Wan2.2-Distill-Models).
- Third-party table: 480p, 81 frames, 14B, about 22 s at 4 steps (LightX2V) vs about 95 s at 30 steps, GPU unspecified — [wan27.org guide](https://wan27.org/blog/wan-2-2-image-to-video-workflow-guide). This is an unofficial site.
- Community add-ons: a 2-step I2V variant ([HF Leon1000](https://huggingface.co/Leon1000/Wan2.2_I2V_LightX2V_2Step)) and an "I2V LightX2V Slow-Mo Fix" LoRA ([HF rzgar](https://huggingface.co/rzgar/Wan2.2_I2V_LightX2V_Slow-Mo_Fix)). The existence of the slow-mo fix confirms that reduced motion is the known quality cost of distillation.
- Wan 2.2 Lightning 4-step ComfyUI workflows — [RunComfy](https://www.runcomfy.com/comfyui-workflows/wan-2-2-lightning-t2v-i2v-comfyui-ultra-fast-video-gen).

**Other distilled options**
- Cosmos3 4-step via DMD2 (up to 25x fewer evaluations) — [HF](https://huggingface.co/nvidia/Cosmos3-Super-Image2Video-4Step).
- Kandinsky 6 distilled at 10 steps — [miraflow](https://miraflow.ai/blog/kandinsky-6-0-video-explained-open-source-audio-video-model-2026).
- The LTX-2.5 default transformer is already distilled and unguided — [HF](https://huggingface.co/Lightricks/LTX-2.5-Diffusers).
- MiniMax H3 open checkpoints are CFG-distilled (one pass per step instead of two) — [RunPod](https://www.runpod.io/blog/minimax-h3-the-open-weight-omni-modal-video-model-and-what-it-takes-to-run-it).
- CausVid and Self-Forcing (arXiv 2506.08009, NeurIPS 2025) convert bidirectional Wan into causal few-step streaming generators — [atlascloud long-video blog](https://www.atlascloud.ai/th/blog/guides/long-video-generation-blog-1).

### Inferences
- Estimate for the current pipeline: the 900 s per clip run presumably uses about 40 steps with CFG, which is 80 transformer evaluations. 4-step distilled without CFG is 4 evaluations, so the denoising loop should fall about 15–20x. VAE decode, text encoding and model loading are fixed overhead (maybe 20–60 s). **Expected: about 60–120 s per clip at 1280x720 on H100, or roughly $0.07–0.13.** This is an estimate; benchmark it.
  - Adding FP8 weights and SageAttention2 should give a further 1.3–1.8x (prior knowledge from the SageAttention repo, not re-verified: https://github.com/thu-ml/SageAttention).
- TeaCache/MagCache gain much less on top of 4-step distillation, because there are few steps left to skip. Use them only with non-distilled runs.
- Multi-GPU USP/xDiT cuts latency but not cost per clip, and Modal bills per GPU-second. It helps only when wall-clock time matters.
- Consider running the distilled Wan2.2 on A100-80 ($2.50/h). It may cost the same or less per clip than H100 if it is under about 1.6x slower.

### Gaps
- No independent, measured H100 timing for Wan2.2-I2V-A14B 4-step at 720p was found. No quantitative quality comparison (VBench/arena) of distilled vs 40-step Wan2.2 was found.
- Measured NVFP4 benefit on H100: none found. NVFP4 needs Blackwell hardware; H100 supports FP8 only (prior knowledge).

## Q3. Long-video / multi-shot

### Takeaway
For explainers built from 40–80 separate 5–10 s scenes, true minute-long generation is unnecessary. The useful tools are:
- first/last-frame conditioning, which chains scenes or makes a clip return to a still: MiniMax H3 FL2VA, Wan2.1 FLF2V, LTX keyframe interpolation;
- LTX-2.5's native multi-shot, for consistent characters and lighting across cuts;
- Wan VACE or SkyReels-V3 V2V for extension and control.

Autoregressive streaming methods (Self-Forcing++, which reaches about 4 min) are research-grade and narrow.

### Cited Findings
- Self-Forcing++ (ICLR 2026, arXiv 2510.02283) generates up to 4 min 15 s without long-video teachers — [HF paper](https://huggingface.co/papers/2510.02283), [ICLR proceedings](https://proceedings.iclr.cc/paper_files/paper/2026/hash/8a30aba6514b56d02976f49797f6338a-Abstract-Conference.html).
  - One vendor judges it "valuable in a narrow lane", needing dedicated training and generalising poorly to general scenes — [atlascloud](https://www.atlascloud.ai/th/blog/guides/long-video-generation-blog-1).
- LoL (arXiv 2601.16914, Jan 2026) does minute-scale generation on Wan2.1-1.3B. Code or weights were unclear at the time of writing — [atlascloud](https://www.atlascloud.ai/th/blog/guides/long-video-generation-blog-1).
- lightx2v supports Self-Forcing with FP8/NVFP4 (Feb 2026) — [lightx2v](https://github.com/modeltc/lightx2v).
- LTX-2.5 native multi-shot holds character, environment, lighting and voice across cuts in a single generation — [RITS](https://rits.shanghai.nyu.edu/ai/ltx-2-5-adds-native-multi-shot-video-and-a-diffusion-decoder/). LTX-2.x also supports keyframe interpolation — [wink.ai](https://wink.ai/blog/best-open-source-image-to-video-ai-models).
- MiniMax H3 FL2VA (first+last frame) is open, with clips of 4–15 s — [RunPod](https://www.runpod.io/blog/minimax-h3-the-open-weight-omni-modal-video-model-and-what-it-takes-to-run-it).
- Cosmos3 generates up to 400 frames (about 16 s at 24 fps) natively from multiple images — [HF](https://huggingface.co/nvidia/Cosmos3-Super-Image2Video-4Step).
- SkyReels-V3 V2V-14B does video extension — [HF](https://huggingface.co/Skywork/SkyReels-V3-V2V-14B).
- Prior knowledge, not re-verified:
  - FramePack (lllyasviel) does next-frame-section packing on HunyuanVideo, runs on about 6 GB, and makes minute-long clips with constant memory — https://github.com/lllyasviel/FramePack.
  - SkyReels-V2 uses diffusion forcing for "infinite-length" extension — https://github.com/SkyworkAI/SkyReels-V2.
  - Wan2.1-FLF2V-14B-720P and Wan2.1-VACE-14B handle first-last-frame generation and control/extension/inpainting — https://github.com/Wan-Video/Wan2.1.
  - MAGI-1 generates autoregressive chunks — https://github.com/SandAI-org/MAGI-1.

### Inferences
- For "almost still" fallback clips and seamless loops, FLF2V with first frame = last frame = the still image gives subtle, controllable motion. That beats TI2V-5B's near-still output.
- Chaining extended shots by conditioning on the last frame accumulates colour drift after 2–3 hops. Keep each scene to one generation and use cuts. This is the norm for explainers anyway.

### Gaps
- No 2026 benchmark comparing FramePack, SkyReels-V2 DF and Self-Forcing++ quality was found. FramePack and SkyReels-V2 are 2025-era and likely superseded in quality by LTX-2.5 multi-shot and H3 15 s clips.

## Q4. Post-processing: interpolation, upscaling, camera control

### Takeaway
Generate at 720p (Wan: 16 fps; LTX/H3: 24 fps), then upscale to 1080p with **FlashVSR**, which is fast and streaming (about 41 s for a 10 s 720p-to-1080p clip). Use **SeedVR2** only for hero shots, since it is about 7–8x slower. For Wan's 16 fps output, interpolate to 24/30 fps with RIFE (cheap) or GIMM-VFI (higher quality).

### Cited Findings
- Comfy docs benchmark, 10 s 720p-to-1080p: FlashVSR (local) about 41 s vs SeedVR2 (RTX 5090) about 312 s. SeedVR2 is recommended for the "quality mode" — [Comfy docs video upscale](https://docs.comfy.org/tutorials/utility/video-upscale).
- FlashVSR runs at about 17 fps at 768x1408 on a single A100 (per its paper). SeedVR2 is the heaviest option, needing multiple H100s for 1080p–2K self-hosted — [invideo](https://invideo.io/blog/ai-video-upscalers/).
- SeedVR2 is better for heavily degraded or low-res input. FlashVSR is better for clean sources and long clips — [upsampler](https://upsampler.com/blog/seedvr-vs-flashvsr-ai-video-super-resolution-2026).
- Topaz community comparison of SLS/SLM vs SeedVR2 vs FlashVSR — [Topaz forum](https://community.topazlabs.com/t/sls-vs-slm-vs-seedvr2-vs-flashvsr-comparison/98005/1).
- lightx2v supports SeedVR2 inference — [lightx2v](https://github.com/modeltc/lightx2v).
- Built-in upscalers: LTX-2.5 includes an x2 latent upsampler — [HF](https://huggingface.co/Lightricks/LTX-2.5-Diffusers). MiniMax H3's 2K regenerate stage is API-only — [RunPod](https://www.runpod.io/blog/minimax-h3-the-open-weight-omni-modal-video-model-and-what-it-takes-to-run-it).
- Prior knowledge, not re-verified:
  - RIFE (https://github.com/hzwer/ECCV2022-RIFE) runs at real-time-class speed.
  - GIMM-VFI (https://github.com/GSeanCDAT/GIMM-VFI) and FILM (https://github.com/google-research/frame-interpolation) are slower but better on large motion.
  - Real-ESRGAN (https://github.com/xinntao/Real-ESRGAN) works per-frame and flickers on video.
  - Camera-motion LoRAs exist for Wan 2.x (e.g. Wan2.1 "camera control" LoRAs, ReCamMaster, Uni3C) and for LTX (LTX-Video control LoRAs).

### Inferences
- Pipeline cost: FlashVSR at about 41 s per 10 s clip implies about 20 s per 5 s clip. On an A100-40 that is about $0.01 per clip (estimate), which is negligible next to generation.
- Explainer content (diagrams, brain renders, abstract visuals) is clean, so FlashVSR is suitable. Real-ESRGAN per-frame upscaling should be avoided because of temporal flicker.

### Gaps
- No 2026 measured GIMM-VFI vs RIFE timings were found. No 2026-specific camera-control LoRA survey was done.

## Q5. Closed APIs: quality and cost per second

### Takeaway
On the AA arena, closed leaders are Seedance 2.5/2.0 (very expensive), H3 Max, Wan 3.0, HeyGen Video 1 and Agnes-Video-2.5. The last two are notable because they are cheap and highly ranked. **HeyGen Video 1 and Agnes-Video-2.5 at $2.40/min ($0.04/s, about $0.20 per 5 s clip) beat Veo 3.1 and Kling 3.0 on Elo at a fraction of the price.** The Sora 2 API was retired on 24 Sep 2026.

### Cited Findings (AA prices are per minute of video, converted to 5 s)
| Model | AA I2V Elo (audio) | $/min (AA) | ≈ $/5 s |
|---|---|---|---|
| Seedance 2.5 | 1152 (#1) | 34.12 | 2.84 |
| Seedance 2.0 | 1135 | 22.45 | 1.87 |
| MiniMax H3 (768p, API) | 1128 | 4.80 | 0.40 |
| HeyGen Video 1 | 1119 | 2.40 | 0.20 |
| MiniMax H3 Max | 1115 | 9.60 | 0.80 |
| Wan 3.0 | 1111 | 12.00 | 1.00 |
| Agnes-Video-2.5 | 1103 | 2.40 | 0.20 |
| Kling 3.0 1080p Pro | 1000 | 10.08 | 0.84 |
| Veo 3.1 | 956 | 24.00 | 2.00 |
| Veo 3.1 Fast | 934 | 7.20 | 0.60 |
| Veo 3.1 Lite | 928 | 4.80 | 0.40 |
| LTX-2.5 Fast (API) | 916 | 7.80 | 0.65 |

Source for the table: [AA I2V leaderboard](https://artificialanalysis.ai/video/leaderboard/image-to-video).

- Aggregator per-second rates:
  - Veo 3.1 at 1080p is $0.40/s, 4K $0.60/s. Lite is $0.05/s at 720p and $0.08/s at 1080p.
  - Kling 3.0 is about $0.075/s at 720p without audio, and $0.11–0.14/s at 1080p.
  - Sora 2 was $0.10/s at 720p and Sora-2-Pro up to $0.70/s at 1080p, with the API sunset on 24 Sep 2026.
  - Sources: [invideo pricing Aug 2026](https://invideo.io/blog/ai-video-model-pricing), [cometapi](https://www.cometapi.com/ai-video-api-pricing/), [modelslab](https://modelslab.com/blog/api/veo-3-1-vs-kling-3-sora-2-ai-video-api-cost-2026). These are secondary sources and should be checked against official pricing pages.
- Runway Gen-4 and Hailuo were not in the extracted top 25. Runway now hosts LTX-2.5 — [search summary](https://alphasignal.ai/news/lightricks-ltx-2-5-generates-10-second-videos-faster-than-real-time).

### Inferences
- Self-hosted Wan2.2 today costs about $0.99/clip, which is more than HeyGen Video 1 or Agnes at $0.20 or the MiniMax H3 API at $0.40, and those are much higher quality. Even unaccelerated, the current setup is not cost-competitive with top-quality APIs. 4-step Wan (about $0.10) or LTX-2.5 (about $0.13) restores the cost advantage, but at lower quality.
- AA arena prompts skew toward people and cinematic scenes. Rankings may transfer imperfectly to abstract neuroscience b-roll.

### Gaps
- Official per-second prices were not verified for HeyGen Video 1, Agnes-Video-2.5, Runway Gen-4.x or Hailuo. AA lists prices but not resolution tiers.
- VBench 2026 leaderboard not retrieved.

## Q6. Recommendations: budget (~$0.10–0.30 per 5 s clip) and max quality

### Takeaway
- **Budget (self-hosted, licence-safe):** keep Wan2.2-I2V-A14B, but switch to the **lightx2v 4-step 720p distilled models** with FP8 and SageAttention. Estimated about $0.07–0.15 per clip on H100, or test A100-80.
  - In parallel, A/B test **LTX-2.5 distilled** (about $0.13 per clip by the user's estimate). It has native 24 fps, a built-in x2 upsampler and multi-shot, and is permissive under $10M revenue.
  - Post-process with FlashVSR to 1080p and RIFE (Wan only) to 24 fps.
- **Budget (API):** HeyGen Video 1 or Agnes-Video-2.5 at about $0.20 per 5 s are top-10 on AA. Verify that their API supports I2V at 1080p.
- **Max quality, open:** MiniMax H3 (768p) plus FlashVSR or SeedVR2, **only if the licence's territory restriction does not apply**. Otherwise LTX-2.5 Pro / full transformer.
- **Max quality, any:** Seedance 2.5 (about $2.84 per 5 s). For the best value at the top tier, use the MiniMax H3 API ($0.40 per 5 s, #4).

### Cited Findings
- See the Q1, Q2 and Q5 citations: [AA](https://artificialanalysis.ai/video/leaderboard/image-to-video), [lightx2v distill](https://huggingface.co/lightx2v/Wan2.2-Distill-Models), [LTX-2.5 card](https://huggingface.co/Lightricks/LTX-2.5-Diffusers), [RunPod H3](https://www.runpod.io/blog/minimax-h3-the-open-weight-omni-modal-video-model-and-what-it-takes-to-run-it), [Comfy upscale](https://docs.comfy.org/tutorials/utility/video-upscale).

### Inferences
- Per-video math for 60 scenes x 5 s:
  - current Wan, about $59;
  - 4-step Wan or LTX-2.5, about $6–9 (estimate);
  - HeyGen or Agnes API, about $12;
  - MiniMax H3 API, about $24;
  - Seedance 2.5, about $170.
- Suggested tiering: use LTX-2.5 or 4-step Wan for most scenes, and spend API budget on 5–10 hero shots per video.
- Drop LTX-Video 0.9.5 (2025, superseded), HunyuanVideo 1.5 non-distilled (too slow; if retried, use the lightx2v 4-step variant), Mochi and CogVideoX.

### Gaps
- All self-hosted per-clip costs for the new options are estimates. A one-day benchmark on Modal is needed: Wan2.2 4-step 720p, LTX-2.5 distilled at 1080p via the upsampler, and Kandinsky 6 Lite, with 10 identical neuroscience prompts.
