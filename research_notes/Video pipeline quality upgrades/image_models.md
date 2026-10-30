# Open / self-hostable image models and consistency techniques (as of 29 Oct 2026)

Scope: still images for an automated faceless neuroscience/psychology explainer pipeline (40-80 stills per video, Ken Burns + first frames for image-to-video). Current setup: Qwen-Image-2.1 on A100-40GB at about 60 s/image.

**Biggest finding: the current model, Qwen-Image-2.1, is under the Qwen Research License (non-commercial research or evaluation only).** The licence's position on outputs is disputed (see Q1). For a monetized channel this is a real licence risk, and it should be settled before anything else is tuned.

---

## Q1. Which open models lead on quality now, and what are their licences, specs and speeds?

### Takeaway
On the Artificial Analysis (AA) arena in late Oct 2026, the leading open-weights models are FLUX 3 Image Klein (Elo 1043) and Qwen-Image-2.1 (1042), then Bria Fibo 2.0 (1039) and Ideogram 4.0 (Quality) (1026). Both of the top two have restrictive licences. Qwen-Image-2.1 is research-only. FLUX 3 Klein allows free commercial use only below US$5M annual revenue, which a solo channel almost certainly meets. Among models whose weights are fully permissive, the strongest are ERNIE-Image (Apache 2.0) and HiDream-O1 (MIT), but both rank well below the top two. Any self-hosted open model is still about 130-180 Elo behind the closed leaders (GPT Image 2.x, Nano Banana 2.1).

### Cited Findings
**Leaderboard (AA Text-to-Image, open-weights filter; the page has no date but lists releases up to Oct 2026; FLUX.2 [dev] is the anchor fixed at Elo 1000)** — [AA leaderboard](https://artificialanalysis.ai/image/leaderboard/text-to-image?open-weights=true)
- FLUX 3 Image Klein 1043 · Qwen-Image-2.1 1042 · Fibo 2.0 (Bria) 1039 · Ideogram 4.0 (Quality) 1026 · Ideogram 4.0 1002 · FLUX.2 [dev] 1000 · Ming-Image-0.1-Design 999 · FLUX.2 [dev] Turbo (fal) 994 · NVIDIA Cosmos3-Super-Text2Image 985 · HunyuanImage 3.0 Instruct 987 · HiDream-O1-Image 975 · HunyuanImage 3.0 932 · **FLUX.2 [klein] 9B 929** · ERNIE Image Turbo 914 · ERNIE Image 907 · Qwen Image (original) 903 · FLUX.1 Krea [dev] 896 · GLM-Image 885 · FLUX.2 [klein] 4B 837 · FLUX.1 [dev] 823 · OmniGen V2 717 · BAGEL 594.
- On this scale the original Qwen-Image is 903 and Qwen-Image-2.1 is 1042. FLUX.2 klein 9B (929) sits about 113 Elo below Qwen-Image-2.1, so on arena preference **testing klein-9B would be a step down** — [AA](https://artificialanalysis.ai/image/leaderboard/text-to-image?open-weights=true)
- Superseded rankings: earlier snapshots put HiDream-O1-Image-Dev-2604 at #1 open (Elo 1186 around Jul 2026, then ERNIE Image 1161). The leaderboard has since been re-versioned ("AA-Image-T2I v2.1"), so absolute Elo values from different snapshots cannot be compared — [AA v2.1](https://artificialanalysis.ai/image/leaderboard/text-to-image)

**Qwen-Image-2.1 (Alibaba, released 2026-09-20; Turbo released 2026-10-09)** — [GitHub](https://github.com/QwenLM/Qwen-Image-2.1)
- 7B DiT (32 single-stream layers) with a Qwen3-VL-8B text encoder. Native 2K output (default 2048×2048, with 16:9 and other presets). The original checkpoint uses 40 steps. **Qwen-Image-2.1-Turbo uses 8 steps at CFG 1.** Diffusers supports it from day 0 via `QwenImage21Pipeline`. One model does both generation and editing, takes up to 10 reference images, supports mask, circle and painted local edits, and outputs native RGBA. Pro is a hosted API only — [GitHub](https://github.com/QwenLM/Qwen-Image-2.1)
- Licence: the Qwen Research License. Section 2(a) allows use "FOR NON-COMMERCIAL PURPOSES ONLY", defined as "for research or evaluation purposes only". Section 2(b): "You shall not use the Materials for any commercial purpose without obtaining a separate commercial license." Qwen posted on X that "Outputs are not part of the licensed Materials", but that post never uses the word "commercial". HF discussion #40, asking for clarity, was still unresolved. Users report that the commercial-licence email address (model-business@notice.qwencloud.com) bounces — [Latenode](https://latenode.com/ai-trends/qwen-image-2-1-commercial-licence); [runtimewire](https://runtimewire.com/article/alibaba-qwen-image-2-1-transparent-editing-research-license); [HF discussion](https://huggingface.co/Qwen/Qwen-Image-2.1/discussions/6)
- Qwen-Image 2.0 (Feb 2026) was API-only, with no open weights — [datanorth](https://datanorth.ai/news/qwen-releases-qwen-image-2-1)
- Earlier Qwen image models (Qwen-Image 1.0, Edit, Layered, 2512) were Apache 2.0, according to secondary sources — [Latenode citing CellCog](https://latenode.com/ai-trends/qwen-image-2-1-commercial-licence); [Medium rundown: "Qwen-Image is fully Apache 2.0"](https://medium.com/diffusion-doodles/model-rundown-z-image-turbo-qwen-image-2512-edit-2511-flux-2-dev-fc787f5e87ad)

**FLUX 3 Image Klein (Black Forest Labs, open weights 2026-10-15)** — [BFL blog](https://bfl.ai/blog/flux-3-image-klein)
- 5.6B generator (text encoder not counted). The base checkpoint runs 50 steps and the distilled one 16. FP8, INT8 and NVFP4 builds are published. Weights take 11.2 GB in BF16 and 5.6 GB in FP8, and the INT8 build runs on 8 GB RTX cards. BFL claims native 4K output. One model covers text-to-image, editing and multi-reference with up to 10 references. Day-one support: ComfyUI, Diffusers, TensorRT-LLM, SGLang Diffusion, vLLM-Omni. LoRA training works day one in Diffusers and ostris AI Toolkit — [BFL blog](https://bfl.ai/blog/flux-3-image-klein)
- Measured speeds at 1024²: distilled 16-step takes 0.55 s on GB300 and 8.9 s on RTX 4070; distilled INT8 takes about 4 s on RTX 5090; base 50-step takes 1.7 s on GB300. Serving a LoRA adds about 5%. BFL's internal evaluations claim +91 Elo over FLUX.2 klein 9B in text-to-image and +70 in editing. API price from $0.009/image — [BFL blog](https://bfl.ai/blog/flux-3-image-klein)
- Licence (FLUX Kommunity License): free commercial use for "Qualifying Users" with gross annualized revenue, affiliates included, below US$5M. Qualifying users must filter or review outputs for unlawful or infringing content and disclose AI generation where the law requires it. Some coverage calls it research or non-commercial plus the threshold, so the HF licence text is the controlling document — [VentureBeat](https://venturebeat.com/technology/black-forest-labs-opens-flux-3-image-klein-weights-with-free-commercial-use-limited-to-smaller-businesses); [eugfa](https://eugfa.org/briefing/flux-klein-licence)
- FLUX 3 Image (the full model) is API-only: Elo 1117, $48 per 1k images — [AA](https://artificialanalysis.ai/image/leaderboard/text-to-image?open-weights=true)

**FLUX.2 [klein] 9B / 4B and FLUX.2 [dev] (Black Forest Labs)**
- klein 9B: FLUX Non-Commercial License; local use is non-commercial and commercial use goes through the API. klein 4B: Apache 2.0, about 13 GB VRAM. klein 9B needs about 24 GB (official), with third-party figures of 19.6-29 GB. Sub-second on an RTX 4090 according to third parties — [BFL help](https://help.bfl.ai/articles/6122710168-which-flux-2-model-should-i-choose); [BFL klein](https://bfl.ai/models/flux-2-klein)
- FLUX Non-Commercial License v2.1 text: "We claim no ownership rights in and to the Outputs. You may use Output for any purpose (including for commercial purposes), except as expressly prohibited". However, using the *model* "for revenue-generating activity" does not count as a Non-Commercial Purpose. Commentators disagree on whether running it locally to make monetized content is allowed — [HF LICENSE mirror](https://huggingface.co/ModelsLab/FLUX.2-klein-9B/blob/main/LICENSE.md); [HF discussion #24](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/discussions/24); [digitalapplied](https://www.digitalapplied.com/blog/ai-creative-licensing-landmines-agency-client-work)
- FLUX.2 [dev] has multi-reference with up to 10 references and is described as strong for character consistency, but it is weaker at typography and complex layouts — [Medium rundown](https://medium.com/diffusion-doodles/model-rundown-z-image-turbo-qwen-image-2512-edit-2511-flux-2-dev-fc787f5e87ad)

**Permissive alternatives**
- ERNIE-Image (Baidu): 8B single-stream DiT, open weights released 2026-04-15 (baidu/ERNIE-Image and ERNIE-Image-Turbo), **Apache 2.0** — [GitHub baidu/ERNIE-Image](https://github.com/baidu/ernie-image)
- HiDream-O1-Image (May 2026): 8B, pixel-native with no VAE, **MIT licence for both code and models**. The Dev-2604 checkpoint followed on 14 May — [GitHub HiDream-O1](https://github.com/HiDream-ai/HiDream-O1-Image); [aifilms](https://studio.aifilms.ai/blog/hidream-o1-image-open-source-pixel-native)
- Ideogram 4.0 (9.3B, 2026-06-03): the weights fall under the Ideogram Non-Commercial Model Agreement, with **no small-business exemption**; only the inference code is Apache 2.0. NF4 runs on a single 24 GB GPU — [Ideogram blog](https://ideogram.ai/blog/ideogram-4.0/); [vidcella review](https://vidcella.ai/posts/ideogram-4-0-review); [invideo](https://invideo.io/blog/ideogram-ai-image-generator/)

### Inferences
- If the licence must be watertight, **FLUX 3 Image Klein** is the best quality-to-licence option for a creator earning under $5M. It ties Qwen-Image-2.1 on the arena, takes 10 references, is small (fits easily on an A100-40GB in BF16), and is fast: probably about 2-4 s/image distilled on an A100 (extrapolated, not measured). Next come ERNIE-Image/Turbo (Apache) and HiDream-O1 (MIT), at roughly 70-130 Elo lower.
- The FLUX.2 klein 9B test can probably be skipped: it ranks well below Qwen-Image-2.1, carries the non-commercial licence ambiguity, and is beaten by FLUX 3 Klein in BFL's own figures.
- Qwen-Image-2.1-Turbo (8 steps) should cut the current ~60 s (40 steps) to roughly 12-15 s on the same A100. That is estimated from the step ratio and not measured, and it does not fix the licence.

### Gaps
- Not captured in this pass: HunyuanImage 3.0 licence and VRAM, Z-Image, Lumina, SD3.5, Fibo 2.0 and Cosmos3 licences. From prior knowledge (unverified here): HunyuanImage 3.0 is an 80B MoE under the Tencent Hunyuan Community License, which excludes the EU, UK and South Korea, and it needs multiple GPUs. SD3.5 is under the Stability Community License (free below $1M revenue).
- There are no measured A100/H100 sec/image figures for Qwen-Image-2.1, ERNIE or HiDream-O1. Benchmark them locally.
- Whether Qwen-Image-2.1 outputs may be used commercially is unresolved.

---

## Q2. Few-step / distilled / quantized variants

### Takeaway
Official distillations now exist: Qwen-Image-2.1-Turbo (8 steps) and FLUX 3 Klein distilled (16 steps, with an NVFP4 build). Nunchaku SVDQuant INT4/NVFP4 checkpoints combined with Lightning 4/8-step LoRAs cover the older Qwen-Image and Edit-2509/2511 models. NVFP4 needs Blackwell, so on an A100 use INT4 or FP8.

### Cited Findings
- Qwen-Image-2.1-Turbo runs 8 steps at CFG 1 and needs Diffusers built from source — [GitHub](https://github.com/QwenLM/Qwen-Image-2.1)
- FLUX 3 Klein distilled: 16 steps, 0.55 s on GB300 at 1MP, under 0.6 s in NVFP4 — [BFL](https://bfl.ai/blog/flux-3-image-klein)
- Nunchaku published 4-bit 4/8-step Lightning Qwen-Image on 2025-08-27. INT4 and NVFP4 4-step builds come at rank 32 and 128 with the Lightning v1.0 LoRA fused in. Async offloading brings the Qwen-Image transformer down to about 3 GiB of VRAM — [nunchaku GitHub](https://github.com/nunchaku-ai/nunchaku); [HF nunchaku-qwen-image](https://huggingface.co/nunchaku-ai/nunchaku-qwen-image); [Edit-2509 build](https://huggingface.co/nunchaku-ai/nunchaku-qwen-image-edit-2509)
- Nunchaku is now integrated into Diffusers. A Nunchaku-Lite ERNIE-Image-Turbo build renders 1024² in about 1.7 s on an RTX 5090 — [HF blog](https://huggingface.co/blog/nunchaku-diffusers)
- fal's FLUX.2 [dev] Turbo (994) and Flash (988) score only 6-12 Elo below FLUX.2 dev (1000), so few-step distillation costs little arena preference — [AA](https://artificialanalysis.ai/image/leaderboard/text-to-image?open-weights=true)

### Inferences
- The Turbo/Flash results suggest few-step distillation costs about 1% in Elo. For Ken Burns stills, 8-16 steps is the right default.

### Gaps
- No A100/H100 figures were found for Nunchaku Qwen-Image Lightning. Nothing was found on TeaCache or FBCache for image models, and no Nunchaku build for Qwen-Image-2.1 or FLUX 3 Klein was confirmed.

---

## Q3. Character and style consistency

### Takeaway
Native multi-reference editing is now built into the leading open models (Qwen-Image-2.1 and FLUX 3 Klein, up to 10 refs each; FLUX.2 dev also 10). It has largely replaced IP-Adapter, InstantID and PuLID for keeping one protagonist across scenes. The most robust channel-level setup is a character LoRA plus a style LoRA trained on the chosen base, combined with reference-conditioned generation from a fixed "character sheet".

### Cited Findings
- Qwen-Image-2.1 takes up to 10 references for multi-subject composition and is said to preserve identity for people and products. Prefix KV-cache reuse speeds up multi-image edits — [GitHub](https://github.com/QwenLM/Qwen-Image-2.1)
- FLUX 3 Klein takes up to 10 references, and BFL claims it ranks #1 among open models in multi-reference and editing — [BFL](https://bfl.ai/blog/flux-3-image-klein)
- Qwen-Image-Edit-2511 kept art style and facial features in a 2026 local test, though it dropped one background element. Reviewers call its character consistency much stronger than 2509 but are unsure it beats FLUX.1 Kontext. FLUX.2 dev multi-reference is rated stronger on consistency — [Medium rundown](https://medium.com/diffusion-doodles/model-rundown-z-image-turbo-qwen-image-2512-edit-2511-flux-2-dev-fc787f5e87ad); [note.com 8-model test](https://note.com/ai_0049/n/n8051776106dc?hl=en)
- OmniGen V2 scores 717 and BAGEL 594 on AA, far behind, so neither suits photoreal output — [AA](https://artificialanalysis.ai/image/leaderboard/text-to-image?open-weights=true)
- LoRA cost: the hosted Qwen-Image trainer charges $2 per 1,000 steps, so a 3k-7k-step character run is about $6-14 — [muapi](https://muapi.ai/it/playground/qwen-image-lora-trainer). Character LoRAs typically take 3000-7000 steps (Z-Image guide) — [RunComfy](https://www.runcomfy.com/trainer/ai-toolkit/z-image-base-lora-training). An ai-toolkit LoRA for FLUX.2 or Wan usually costs under $15 in total on rented GPUs, including iterations — [Spheron](https://www.spheron.network/blog/fine-tune-flux2-wan-lora-cost-gpu-cloud-2026/). FLUX.1 fine-tuned on an H100 in under an hour — [Paperspace](https://blog.paperspace.com/fine-tune-flux-schnell-dev/)
- AI Toolkit supports FLUX 3 Klein LoRA training from day one — [BFL](https://bfl.ai/blog/flux-3-image-klein)

### Inferences
- Suggested pipeline:
  1. Generate a canonical protagonist sheet once: front, 3/4 and profile views plus wardrobe.
  2. Feed 2-4 sheet images as references in every scene prompt.
  3. Add a style LoRA (about 20-40 curated stills in the channel look) for cross-video consistency.
  4. Once enough good frames exist, train a character LoRA, about $10-15 and roughly 1 GPU-hour.
- Faceless explainers can sidestep face-ID drift altogether: show the protagonist from behind, in silhouette or at a distance, or use a stylized character.

### Gaps
- No 2026 primary benchmarks were retrieved for PuLID-FLUX2, USO, UNO, DreamO or InstantID. Nothing was found on musubi-tuner or kohya support for Qwen-Image-2.1 or its training cost.

---

## Q4. Upscaling and detail

### Takeaway
SeedVR2 (ByteDance; 3B/7B; one-step diffusion restoration) is now the standard ComfyUI upscaler for both images and video, with official ComfyUI docs and FP8/INT8/NVFP4 builds. Native 2K output from Qwen-Image-2.1, and the claimed native 4K from FLUX 3 Klein, may make upscaling unnecessary for 1080p delivery.

### Cited Findings
- SeedVR2 comes in 3B and 7B, each in FP16, FP8, INT8, NVFP4 and MXFP8. The 7B gives higher quality at higher VRAM and time cost — [ComfyUI docs](https://docs.comfy.org/tutorials/utility/seedvr2)
- On GPUs under 24 GB, keep batch size low and turn on preserve_vram. BlockSwap trades speed for VRAM — [comfyorg/comfyui_seedvr2](https://github.com/comfyorg/comfyui_seedvr2)
- SeedVR2 can oversharpen AI-generated content — [weirdwonderfulai](https://weirdwonderfulai.art/resources/seedvr2-upscaler-for-video-and-images/)

### Inferences
- A 2048×1152 render (16:9 at native 2K) already covers 1080p Ken Burns with about 1.07× headroom, which is too little for deep zooms. Either render larger than 2K, or run SeedVR2-3B at 2× on the stills that need a deep push-in (to roughly 4K).

### Gaps
- No 2026 SeedVR2-vs-SUPIR comparisons were retrieved, and no Real-ESRGAN or 4x-UltraSharp figures.

---

## Q5. Thumbnail generation with text rendering

### Takeaway
Qwen-Image-2.1 renders text well and has native RGBA, which makes it easy to composite a transparent subject over a background. Ideogram 4.0 is typography-focused but non-commercial when self-hosted. Its API, or GPT Image or Nano Banana, is the safe commercial route for text-heavy thumbnails.

### Cited Findings
- Qwen-Image-2.1 supports native RGBA generation and editing, including changing text on transparent layers — [datanorth](https://datanorth.ai/news/qwen-releases-qwen-image-2-1); [GitHub](https://github.com/QwenLM/Qwen-Image-2.1)
- Ideogram 4.0 self-hosted is non-commercial, while paid Ideogram tiers and the API include commercial rights — [vidcella](https://vidcella.ai/posts/ideogram-4-0-review)
- FLUX.2 dev is reported to be weaker at typography — [Medium rundown](https://medium.com/diffusion-doodles/model-rundown-z-image-turbo-qwen-image-2512-edit-2511-flux-2-dev-fc787f5e87ad)

### Inferences
- More reliable approach: generate the subject and background without text, then add the 2-4 word headline with a real font in PIL or ffmpeg. This guarantees spelling and brand consistency. Keep model-rendered text for stylized one-offs.

### Gaps
- No primary-source thumbnail CTR studies tied to specific models were found.

---

## Q6. Closed API comparison (price and arena position)

### Takeaway
The closed leaders are GPT Image 2.5 (Elo 1222, about $0.21/image at max), Nano Banana 2.1 (1176, about $0.034) and MAI-Image-2.6 (1166, about $0.039). For 60 stills, Nano Banana 2.1 costs about $2 per video against roughly $12.6 for GPT Image 2.5 max. Midjourney still has no official API.

### Cited Findings
- AA overall top entries (price per 1k images at 1024² default): GPT Image 2.5 Sunburst (max) 1222 / $210.7 · GPT Image 2.5 Flare (max) 1207 / $210.7 · GPT Image 2 (high) 1186 / $211 · **Nano Banana 2.1 1176 / $33.6** · MAI-Image-2.6 1166 / $38.9 · Grok Imagine Image 2.0 1166 / $60 · Nano Banana 2 (Gemini 3.1 Flash Image) 1140 / $67 · Muse Image 1127 / $10 · GPT Image 1.5 (high) 1123 / $133 · MAI-Image-2.6-Flash 1119 / $19.5 · Nano Banana Pro 1118 / $134 · FLUX 3 Image 1117 / $48 · Nano Banana 2 Lite 1107 / $33.6 — [AA](https://artificialanalysis.ai/image/leaderboard/text-to-image?open-weights=true)
- Seedream 5.0 Pro: about $0.045-0.0675/image depending on provider. Lite: about $0.032-0.035. Flash: $0.018 (Oct 2026) — [atlascloud](https://www.atlascloud.ai/blog/tips/seedream-5-pro-vs-midjourney); [trezalabs](https://www.trezalabs.com/blog/seedream-5-0-flash-api-pricing-through-a-pipeline); [apiyi](https://help.apiyi.com/en/seedream-5-0-lite-api-guide-cheaper-than-4-5-en.html)
- Imagen 4 Fast/Standard/Ultra on Vertex: $0.02/$0.04/$0.06. Reportedly removed from the Gemini API on 17 Aug — [ecorpit](https://ecorpit.com/ai-image-generation-api-cost-comparison-2026/)
- Midjourney (V8.x) has no official API and is sold by subscription only ($10/$30/$60/$120 per month) — [atlascloud](https://www.atlascloud.ai/blog/tips/seedream-5-pro-vs-midjourney)
- FLUX.1 Kontext [pro] costs $0.04/image on fal; FLUX.2 [pro] Edit costs $0.03/MP — [fal](https://fal.ai/learn/tools/ai-image-editing-tools)
- FLUX 3 Klein API starts at $0.009 per image — [BFL](https://bfl.ai/blog/flux-3-image-klein)

### Inferences
- A hybrid setup is cheap. Use a self-hosted, licence-clean model (FLUX 3 Klein) for 60-80 scene stills, and a closed API such as Nano Banana 2.1 or GPT Image 2.5 for the single thumbnail and any hero shots. That keeps API spend under about $1-3 per video while giving thumbnails a quality jump of about 130-180 Elo.
- Muse Image ($10 per 1k, Elo 1127) beats every open model on the arena at about 1 cent per image, so it is worth evaluating as a cheap all-API fallback.

### Gaps
- No Midjourney or Ideogram 3/4.5 arena rows were captured. Seedream 5 and Imagen 4 arena positions were not captured, and the pricing sources are third-party.
