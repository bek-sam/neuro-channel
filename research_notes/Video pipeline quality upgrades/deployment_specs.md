# Deployment specs for candidate models on Modal GPUs (A10G / A100-40/80 / H100), as of late Oct 2026

Legend: **[MEASURED]** = number published by a source, with the hardware it names. **[ESTIMATE]** = my extrapolation, not a measurement. **[VENDOR]** = claim made by the model author with no independent check. Model cards were fetched on 2026-10-29.

General hardware note (inference, from general knowledge): A10G and A100 are Ampere GPUs, which have no FP8 tensor cores. FP8 checkpoints on them save VRAM and disk (they are upcast at runtime) but run no faster. On H100 (Hopper) FP8 matmuls are native. NVFP4 builds (LightWan, LTX-2.5 nvfp4-prequant, gufisha/WAN2.2) need Blackwell and cannot run on any GPU in the target list.

## Q1. Video: lightx2v Wan2.2-I2V-A14B 4-step distilled (720p), FP8 + SageAttention

### Takeaway
Official weights are in `lightx2v/Wan2.2-Distill-Models`, and the recommended runtime is the LightX2V repo's MoE distill script. The 720p 4-step I2V checkpoints were released in April 2026. The only published latency is 26.7 s for 4-step 720p I2V, measured on an RTX 5090 with NVFP4 plus sparse attention. No H100 or A100 number was found.

### Cited Findings
- Repo `lightx2v/Wan2.2-Distill-Models`. The 720p I2V files are `wan2.2_i2v_A14b_high_noise_lightx2v_4step_720p_260412.safetensors` and `wan2.2_i2v_A14b_low_noise_lightx2v_4step_720p_260412.safetensors`. FP8 builds are `wan2.2_i2v_A14b_{high,low}_noise_scaled_fp8_e4m3_lightx2v_4step.safetensors`. INT8 builds and a ComfyUI FP8 build (`..._comfyui.safetensors`) also exist, plus the workflow `wan2.2_moe_i2v_scale_fp8_comfyui.json`. — [HF lightx2v/Wan2.2-Distill-Models](https://huggingface.co/lightx2v/Wan2.2-Distill-Models)
- File sizes: BF16 about 28.6 GB per expert; FP8 and INT8 about 15 GB each. — [HF card](https://huggingface.co/lightx2v/Wan2.2-Distill-Models)
- The release date conflicts: one source says 2026-04-12 (it matches the `_260412` filename suffix), another says April 20, 2026. — [search summary of LightX2V changelog vs HF mirror](https://github.com/modeltc/lightx2v)
- The repo holds **DiT weights only**. You also need the T5 encoder, the CLIP vision encoder, the VAE and the tokenizer. Point `model_path` at the full `Wan-AI/Wan2.2-I2V-A14B` directory. — [HF card](https://huggingface.co/lightx2v/Wan2.2-Distill-Models)
- Run steps: `huggingface-cli download lightx2v/Wan2.2-Distill-Models --include ...`, then clone LightX2V and `pip install -r requirements.txt` (Docker is an option). In the JSON config set `high_noise_quantized_ckpt`, `low_noise_quantized_ckpt` and `t5_quantized_ckpt` for FP8, or `*_original_ckpt` for BF16. Then run `bash scripts/wan22/inference/distill/run_wan22_moe_i2v_distill.sh`. — [HF card](https://huggingface.co/lightx2v/Wan2.2-Distill-Models)
- Schedule: 4 steps, 2 on the high-noise expert and then 2 on the low-noise expert. — [HF lightx2v/LightWan2.2-A14B](https://huggingface.co/lightx2v/LightWan2.2-A14B)
- **[MEASURED, RTX 5090, NVFP4 + sparse attention, LightX2V, end-to-end]** I2V 720p at 4 steps took 26.7 s, against 2685 s for the 40-step baseline. I2V 480p at 4 steps took 10.7 s. T2V 720p at 4 steps took 22.5 s. Frame count was not stated. This LightWan variant **requires Blackwell**. — [HF LightWan2.2-A14B](https://huggingface.co/lightx2v/LightWan2.2-A14B)
- **[VENDOR]** LightX2V is "approximately 2x faster than ComfyUI". The card does not mention SageAttention; it only says to use an attention backend your GPU supports. — [HF card](https://huggingface.co/lightx2v/Wan2.2-Distill-Models)
- The card's `DiffusionPipeline.from_pretrained` snippet is a generic widget, not a working video pipeline. Use the LightX2V scripts. — [HF LightWan2.2-A14B](https://huggingface.co/lightx2v/LightWan2.2-A14B)
- `lightx2v/Wan2.2-Distill-Loras` offers LoRAs extracted from the distilled models, for use on the base Wan2.2 checkpoint (for example in diffusers `WanImageToVideoPipeline` or ComfyUI). — [search result](https://cnb.cool/ai-models/lightx2v/Wan2.2-Distill-Loras)
- Community H100 data: 640×640 T2V at 6 steps took about 36–60 s. This is not comparable to 4-step 720p. — [Novita blog](https://blogs.novita.ai/wan-2-2-vram-find-the-best-gpu-setup-for-deployment/)

### Inferences
- **[ESTIMATE]** H100 80GB, FP8 experts, SageAttention, 720p (1280×720) × 81 frames, 4 steps: roughly 30–60 s end-to-end including VAE decode. The H100 has about the same dense BF16/FP8 throughput as the 5090 in NVFP4 mode, or somewhat less, and SageAttention is a little behind sparse attention. Expect an A100-80GB to take about 2× the H100 time, since it has no FP8 compute.
- VRAM: two FP8 experts take about 30 GB total. Keep both resident on an A100-80GB or H100, or swap them (only one runs at a time). An A10G 24GB would need CPU offload of the inactive expert plus an FP8 T5, which makes it slow; don't use it for 720p.
- On Modal, bake the LightX2V repo into the image and put the weights (about 30 GB of experts, the T5, CLIP and VAE) on a Volume. Weight loading dominates cold start, so GPU snapshots help less (see Q12).

### Gaps
- No measured H100 or A100 seconds-per-clip for the FP8 and SageAttention configuration. The next step is LightX2V's GitHub benchmark docs, or a benchmark of our own.
- No published VRAM figure for the FP8 path.

## Q2. Video: LTX-2.5 (dev + distilled) I2V, multi-shot/keyframes, 2x upsampler

### Takeaway
Use the gated repo `Lightricks/LTX-2.5` with `ltx-pipelines` (`python -m ltx_pipelines.distilled`), or the diffusers pack `Lightricks/LTX-2.5-Diffusers` with diffusers installed from main. The distilled 22B DiT runs a fixed 8-step schedule at CFG 1, and the 2x latent spatial upsampler drives the two-stage pipeline. The card publishes no speed or VRAM numbers.

### Cited Findings
- Files on the card:
  - DiT: `diffusion_models/ltx-2.5-22b-distilled-transformer-bf16.safetensors` (fixed 8 steps, CFG 1) and `...-22b-dev-transformer-bf16.safetensors`.
  - Text encoder: `text_encoders/gemma4-12b-with-proj-ltx-2.5-bf16.safetensors`.
  - VAEs: `vae/ltx-2.5-video-vae-bf16.safetensors`, plus the lighter `ltx-2.5-video-vae-conv-bf16`, and the audio VAE `ltx-2.5-audio-vae-bf16`.
  - Upsamplers: `latent_upscale_models/ltx-2.5-latent-spatial-upscaler-x2-bf16-1.0.safetensors` (required for multi-stage) and `...temporal-upscaler-x2...`.
  - LoRA: `loras/ltx-2.5-22b-distilled-lora-450-bf16.safetensors`.
  - Duration head: `model_patches/ltx-2.5-duration-head-bf16.safetensors` (sets duration automatically when `--num-frames` is omitted).
  — [HF Lightricks/LTX-2.5](https://huggingface.co/Lightricks/LTX-2.5)
- I2V: add `--image PATH FRAME_IDX STRENGTH`, for example `--image first.jpg 0 1.0`. The flag can be repeated, which gives keyframes at other frame indices. Low-VRAM flags: `--quantization fp8-cast --offload cpu`. — [HF card](https://huggingface.co/Lightricks/LTX-2.5)
- Constraints: `frames % 8 == 1` (for example 121), and width and height divisible by 32. The diffusers two-stage example runs stage 1 at 544×960, then upsamples 2x to 1088×1920 at 24 fps. 4K is possible with `--spatial-upscalings 2` (3840×2176). — [HF card](https://huggingface.co/Lightricks/LTX-2.5)
- Diffusers classes: `LTX2ImageToVideoPipeline` and `LTX2LatentUpsamplePipeline`. Install diffusers from main, since LTX-2.5 is not in a release. — [HF card](https://huggingface.co/Lightricks/LTX-2.5)
- Multi-shot is listed as a native feature, but the card gives no code, only a link to the prompting guide. — [HF card](https://huggingface.co/Lightricks/LTX-2.5)
- Pitfalls:
  - The `*-comfy-int8-convrot` files are ComfyUI-only.
  - NVFP4 needs Blackwell and `ltx-kernels`.
  - The "Use this model" snippet uses placeholder filenames.
  - Some LTX-2.3 LoRAs don't work on 2.5.
  - Prompt adherence depends heavily on prompting style.
  - The repo is gated.
  — [HF card](https://huggingface.co/Lightricks/LTX-2.5)
- License: free commercial use under $10M annual revenue (LTX-2.x Community License). Above that, a paid agreement is required. — [HF card](https://huggingface.co/Lightricks/LTX-2.5)
- Community GGUF builds of the distilled model range from Q3_K_M (11.5 GB) to Q8_0 (23.6 GB), with Q4_K_M (15.1 GB) recommended. — [HF Abiray/LTX-2.5-Distilled-GGUF](https://huggingface.co/Abiray/LTX-2.5-Distilled-GGUF)
- Modal has official examples for the older LTX-Video: `/docs/examples/ltx` and `/docs/examples/image_to_video`. There is none for LTX-2.5. — [Modal examples](https://modal.com/docs/examples)

### Inferences
- **[ESTIMATE]** VRAM in BF16: about 44 GB for the 22B DiT, about 24 GB for the 12B Gemma encoder, plus the VAE and upsampler. That fits a single H100 or A100-80GB if the text encoder is offloaded after encoding (or swapped with `--offload cpu`). It does not fit an A100-40GB or A10G without `fp8-cast` plus offload or GGUF.
- **[ESTIMATE]** H100, distilled 8 steps, 121 frames, stage 1 at 544×960 then 2x upsample to 1088×1920: about 30–90 s per clip. No measurement exists, so benchmark before committing.
- The sound plan is to generate at roughly 960×544, upsample 2x in latent space to 1080p, and drop the separate FlashVSR pass for LTX shots.

### Gaps
- No measured seconds or VRAM for LTX-2.5 on any GPU.
- No code for the multi-shot API; only the prompting guide covers it.

## Q3. Video: MiniMax H3 open I2V/FLF checkpoint

### Takeaway
The weights went up around August 3, 2026, at `MiniMaxAI/MiniMax-H3`, with a ComfyUI repack at `Comfy-Org/MiniMax-H3`. Locally the model targets 768p (about 1 MP) at 24 fps with audio, up to about 15 s. **Commercial use of locally generated outputs needs a paid MiniMax license**, and reportedly local deployment is excluded in the US, EU, UK and South Korea. Treat that as a likely blocker.

### Cited Findings
- `Comfy-Org/MiniMax-H3`. The open weights target about 1 MP (768 px short edge), 24 fps, up to about 15 s. 2K output is hosted-only; local use needs a separate upscale. The I2V template covers first/last-frame (`fl2va`). Multiframe Reference anchors frames on the timeline through chained Add Guide nodes. — [Comfy docs MiniMax H3](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- Licensing: commercial use of local outputs requires a MiniMax commercial license, and Comfy is the only official reseller. — [Comfy docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- Minimum ComfyUI versions: 0.30.0 for T2V/I2V, 0.34.0 for Multiframe Reference, 0.35.0 for sparse attention, 0.36.0 for FastH3 (the FastVideo sparse-attention checkpoints). — [Comfy docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- Reported as a 33B base model producing 768p with stereo audio. The fl2va checkpoint in pruned int8 is about 21 GB. — [comfyui-wiki news](https://comfyui-wiki.com/en/news/2026-08-03-minimax-h3-open-weights-comfyui); [dev.to](https://dev.to/routeai_official/minimax-h3-is-open-weight-now-heres-whats-actually-downloadable-vs-api-only-441k)
- The license reportedly excludes local deployment in the US/EU/UK/South Korea. This is unconfirmed against the license text. — [mer.vin](https://mer.vin/news/minimax-h3-open-weight-video-model-blocked-us-eu-uk/)

### Inferences
- Modal runs in US and EU regions, so if the geographic exclusion is real, self-hosting H3 on Modal may be non-compliant. Verify the license before any work.
- **[ESTIMATE]** A 33B model in BF16 is about 66 GB, so use an H100 or A100-80GB, or the int8 build (about 21 GB fl2va) on an A100-40GB.

### Gaps
- No VRAM, step count or timing data found. Exact non-Comfy repo files were not verified, and there is no diffusers support.

## Q4. Video: Kandinsky 6.0 Lite (3B) / Pro (29B)

### Takeaway
The org is `kandinskylab`, with code at `github.com/kandinskylab/kandinsky-6`. Each size comes as base, distilled (10 steps) and pretrain checkpoints. Output is 5 s clips at 24 fps with 44 kHz synced audio, up to Full HD through a separate VSR pipeline. The license is reported as MIT. No speed or VRAM numbers were found.

### Cited Findings
- Model lines are Pro (29B) and Lite (3B), each with base, distilled (10 steps, PiFlow) and pretrain checkpoints. VSR runs at x2, x2.25 or x4 with 4 steps per tile; VSR-distill uses 2 steps per tile. Flow-matching shift is 5.0. — [comfyui-wiki Kandinsky 6.0](https://comfyui-wiki.com/en/models/kandinsky/kandinsky-6-0)
- Known HF IDs: `kandinskylab/Kandinsky-6.0-Lite-5s-Diffusers`, plus the Space `Kandinsky-6.0-Pro-distill-5s`. — [comfyui-wiki](https://comfyui-wiki.com/en/models/kandinsky/kandinsky-6-0); [HF kandinskylab spaces](https://huggingface.co/kandinskylab/spaces)
- MIT license, diffusers-format checkpoints, NVIDIA GPU and Python 3.13/3.14 required. — [SBBIT](https://www.sbbit.jp/article/cont1/187393)
- Modes are T2AV and I2AV, 5 s clips with lip-sync audio. — [comfyui-wiki FR](https://comfyui-wiki.com/fr/news/2026-10-06-kandinsky-6-0)

### Inferences
- **[ESTIMATE]** Pro 29B in BF16 is about 58 GB for the DiT alone, which means an H100 or A100-80GB. Lite 3B should fit an A10G.
- The 5 s clip limit fits an explainer shot cadence.
- The Python 3.13+ requirement means a separate Modal image from the other models.

### Gaps
- Exact repo IDs for Pro and Lite (base, distill, I2V) were not confirmed.
- No VRAM or timing figures.

## Q5. Post: FlashVSR (720p→1080p) and RIFE / GIMM-VFI (16→24 fps)

### Takeaway
Use FlashVSR v1.1 (`JunhaoZhuang/FlashVSR-v1.1`). It is built for **4×** upscaling and depends on Block-Sparse-Attention, which is verified on A100/A800 but gives only limited acceleration on Hopper. For 16→24 fps, RIFE (4.25/4.26) is several times faster than GIMM-VFI.

### Cited Findings
- FlashVSR weights: `JunhaoZhuang/FlashVSR` (v1) and `JunhaoZhuang/FlashVSR-v1.1` (recommended). Files: `LQ_proj_in.ckpt`, `TCDecoder.ckpt`, `Wan2.1_VAE.pth`, `diffusion_pytorch_model_streaming_dmd.safetensors`. Scripts in `examples/WanVSR` are `infer_flashvsr_v1.1_{full,tiny,tiny_long_video}.py`. — [GitHub OpenImagingLab/FlashVSR](https://github.com/OpenImagingLab/FlashVSR)
- **[MEASURED, A100]** About 17 fps for 768×1408 output. **[VENDOR]** Up to 12× faster than prior one-step diffusion VSR. — [GitHub](https://github.com/OpenImagingLab/FlashVSR); [CVPR 2026 poster](https://cvpr.thecvf.com/virtual/2026/poster/38690)
- The repo "strongly recommends" the 4× setting; 2× is not mentioned. Block-Sparse-Attention (mit-han-lab) works on A100/A800 with ideal acceleration and on H200 with limited acceleration. H100 is not mentioned, and the RTX 40/50 series is unknown. The build is memory-hungry, so limit ninja jobs. Python 3.11.13. — [GitHub](https://github.com/OpenImagingLab/FlashVSR)
- Some early ComfyUI ports drop LCSA and fall back to dense attention, which noticeably hurts quality at high resolution. — [GitHub](https://github.com/OpenImagingLab/FlashVSR)
- Community timing on the same clip: RIFE about 9 s, GIMM-VFI variants 25–53 s (GPU not named). — [comfy.icu GIMM-VFI node](https://comfy.icu/node/GIMMVFI_interpolate)
- RIFE at 1080p runs at about 60 fps on a 3090 and about 100 fps on a 4090 (version not stated). — [Clore.ai guide](https://docs.clore.ai/guides/guides_v2-fr/traitement-video/rife-interpolation)
- LightX2V has built-in RIFE frame interpolation (VFI tutorial). — [LightX2V docs](https://lightx2v-en.readthedocs.io/en/latest/method_tutorials/video_frame_interpolation.html)

### Inferences
- For 720p→1080p (1.5×), the common workaround is to run FlashVSR at 4× on a downscaled input, or run it at 4× and downscale the output. Either adds cost. **[ESTIMATE]** From the 17 fps A100 figure at about 1.08 MP, 1080p output (2.07 MP) runs at roughly 8–10 fps on an A100, so a 5 s, 24 fps clip (120 frames) takes about 12–15 s.
- Run FlashVSR on an **A100**, not an H100, since sparse-attention acceleration is verified on Ampere.
- RIFE 16→24 fps is negligible cost (about 1–2 s per 5 s clip on any of these GPUs) **[ESTIMATE]**, and it can share a container with ffmpeg. Wan2.2 outputs 16 fps natively, while LTX-2.5 and H3 output 24 fps and need no VFI.

### Gaps
- No measured 1080p FlashVSR numbers, no H100 numbers, and no VRAM figure.
- No A100 numbers for RIFE 4.26 or GIMM-VFI.

## Q6. Images: FLUX 3 Image Klein (5.6B, distilled)

### Takeaway
BFL released FLUX 3 Image Klein around 2026-10-15. It is a 5.6B image transformer with a separate Qwen3-VL-4B text encoder, and it supports multi-reference editing. The Comfy repo `black-forest-labs/flux-3-image-klein-comfy` ships **INT8 ConvRot** files. I found no official FP8 file. The diffusers repo ID `black-forest-labs/flux-3-image-klein` comes only from secondary sources.

### Cited Findings
- Comfy files: `diffusion_models/flux3_image_klein_int8_convrot.safetensors` (base) and `flux3_image_klein_sd_int8_convrot.safetensors` (distilled). Multiple references keep subjects recognizable; reference-based style transfer and layout bounding boxes are supported. The model generates native 4K. — [Comfy blog](https://blog.comfy.org/p/flux-3-image-klein-in-comfyui-56b)
- **[MEASURED by Comfy, 1024², INT8 ConvRot + distilled]** RTX 5070: from about 71 s down to under 8 s. RTX 4070: from 78 s down to under 9 s. That is 4.3–9.3× faster than the BF16 50-step baseline. — [Comfy blog](https://blog.comfy.org/p/flux-3-image-klein-in-comfyui-56b)
- Secondary sources:
  - Repo `black-forest-labs/flux-3-image-klein` plus a base variant.
  - Distilled model runs 16 steps.
  - Prompt upsampler `black-forest-labs/flux-3-image-klein-pup`, which BFL advises using; reportedly about 28 GB extra VRAM.
  - INT8 fits on 8 GB.
  - License "FLUX Kommunity License".
  — [eesel.ai](https://www.eesel.ai/blog/flux-3-klein); [mindstudio](https://www.mindstudio.ai/blog/flux-3-image-klein-local/); [braindetox](https://braindetox.kr/en/posts/flux_3_image_klein_open_weights_2026.html)
- Weights are about 11.2 GB in BF16 and 5.6 GB in FP8. — [braindetox (secondary)](https://braindetox.kr/en/posts/flux_3_image_klein_open_weights_2026.html)
- A user reports distorted eyes with both base and distilled. — [Comfy blog comments](https://blog.comfy.org/p/flux-3-image-klein-in-comfyui-56b)

### Inferences
- **[ESTIMATE]** H100 at 1024², BF16 distilled (16 steps): about 2–4 s per image. An A10G is about 3× slower.
- The prompt upsampler (about 28 GB) can be replaced by our own LLM rewriting step to save VRAM.

### Gaps
- The official HF model card, license, the diffusers pipeline class and an official FP8 file were not verified.

## Q7. Images: Qwen-Image-2.1-Turbo, ERNIE-Image-Turbo, HiDream-O1-Image (multi-reference)

### Takeaway
All three have official repos and code. Licensing differs:
- Qwen-Image-2.1-Turbo is **research-only** (non-commercial).
- ERNIE-Image-Turbo is Apache-2.0, 8 steps, and runs on 24 GB.
- HiDream-O1 is MIT. It is the strongest option for **multi-reference character consistency** (two or more `--ref_images`, layout boxes) but uses its own repo, not diffusers.

### Cited Findings
- **Qwen-Image-2.1-Turbo** (`Qwen/Qwen-Image-2.1-Turbo`):
  - Diffusers `QwenImage21Pipeline`. Install diffusers from source (it needs PR #14950) and `transformers>=5.17.0`.
  - The 8-step schedule is stored in the checkpoint; `num_inference_steps` is ignored and only explicit `sigmas` override it. CFG is 1. Use `use_kv_cache=True`.
  - Presets: 16:9 at 2752×1536, 1:1 at 2048×2048.
  - Editing via `image=`. Multi-reference showcase examples exist but no code.
  - License: Qwen Research License.
  - No VRAM or speed data.
  — [HF Qwen/Qwen-Image-2.1-Turbo](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo); license note [orcarouter](https://www.orcarouter.ai/blog/qwen-image-2-1-turbo-release)
- **ERNIE-Image-Turbo** (`baidu/ERNIE-Image-Turbo`):
  - 8B, BF16, `ErnieImagePipeline` (diffusers main).
  - `num_inference_steps=8`, `guidance_scale=1.0`, `use_pe=True` turns on the prompt enhancer.
  - Resolutions include 1376×768 (16:9) and 1024².
  - "Runs on consumer GPUs with 24G VRAM". Apache-2.0.
  - Multi-reference support is not stated.
  — [HF baidu/ERNIE-Image-Turbo](https://huggingface.co/baidu/ERNIE-Image-Turbo)
- **HiDream-O1-Image**:
  - Repos: `HiDream-ai/HiDream-O1-Image` (full, 50 steps, guidance 5.0, shift 3.0), `HiDream-ai/HiDream-O1-Image-Dev` (28 steps, guidance 0, shift 1.0, flash scheduler) and `HiDream-ai/HiDream-O1-Image-Dev-2604`.
  - About 8–9B, pixel-space, with no VAE or separate text encoder. Default output 2048².
  - Multi-reference via `--ref_images a.png b.png ...` (the example uses 10 references with `--shift 1`); `--layout_bboxes` takes 0–1 boxes.
  - The full model is recommended for editing.
  - The optional prompt agent needs Gemma-4-31B-it or an OpenAI-compatible API.
  - Pitfalls: without flash-attn, set `use_flash_attn: False` in `models/pipeline.py`; avoid PyTorch 2.9.x.
  - MIT. Benchmarks: GenEval 0.90.
  - No VRAM or speed data.
  — [HF HiDream-O1-Image-Dev](https://huggingface.co/HiDream-ai/HiDream-O1-Image-Dev)

### Inferences
- For a monetized YouTube channel, Qwen-Image-2.1-Turbo is ruled out unless Qwen grants a license. ERNIE-Image-Turbo (Apache) and HiDream-O1 (MIT) are commercially clean. FLUX 3 Klein's license still needs checking.
- **[ESTIMATE]** ERNIE Turbo, 8 steps at 1376×768 on an H100: about 1.5–3 s. On an A10G: about 6–10 s.
- **[ESTIMATE]** HiDream-O1 Dev, 28 steps at 2048² in pixel space: tens of seconds on an H100. Generate at a lower resolution for speed.
- Character consistency recipe: keep a fixed set of character reference sheets and pass two or more as `--ref_images` (HiDream-O1) or as multiple references (FLUX 3 Klein).

### Gaps
- No measured speed or VRAM for any of the three. No multi-reference code for the Qwen or ERNIE Turbo models.

## Q8. TTS: Fish Audio Drama 3, Qwen3-TTS 1.7B, Higgs TTS 3

### Takeaway
- Fish Audio Drama 3 (`fishaudio/drama-3`) is a 35B-total / 3B-active MoE with FP8 experts, served through SGLang-Omni or vLLM-Omni. Measured RTF is 0.131 at concurrency 1 on an H200. It needs an 80 GB GPU unless quantized.
- Qwen3-TTS 1.7B is Apache-2.0, small, and simple to run with a pip package.
- Higgs TTS 3 (4B) is non-commercial.

### Cited Findings
- **Fish Audio Drama 3** (`fishaudio/drama-3`):
  - 35B total parameters (36B in the metadata), 3B active, FP8 MoE experts with BF16 elsewhere. Codebook-MTP decoder with 10 codebooks. Up to 16 speakers (`<|speaker:N|>`), inline tags such as `[sighs]` and `[laughs]`, and a `previous_takes` editing mode.
  - Serving: `sgl-omni serve --model-path fishaudio/drama-3 --port 8000`, or `vllm serve fishaudio/drama-3 --omni --port 8091`.
  - Voice cloning: send `references: [{audio_path, text}]`.
  - **[MEASURED, H200, streaming]** Concurrency 1: RTF 0.131, TTFA 88.9 ms. Concurrency 16: RTF 0.373. Concurrency 64: RTF 0.801.
  - The 51 quantized builds sit in the HF model tree; examples are `plotarmordev/drama-3-NVFP4-Pruned` and `UltimateIntent/Fish-Audio-Drama-3-Q2-Q3`.
  - License: the metadata tag reads fish-audio-research-license, while the text says Fish Audio Community License. Verify before use.
  - No VRAM figure.
  — [HF fishaudio/drama-3](https://huggingface.co/fishaudio/drama-3)
- **Qwen3-TTS:**
  - Repos: `Qwen/Qwen3-TTS-12Hz-1.7B-{Base,CustomVoice,VoiceDesign}`, `Qwen/Qwen3-TTS-12Hz-0.6B-{Base,CustomVoice}`, `Qwen/Qwen3-TTS-Tokenizer-12Hz`.
  - Install `pip install -U qwen-tts` (flash-attn optional).
  - Usage: `Qwen3TTSModel.from_pretrained(..., dtype=torch.bfloat16, attn_implementation="flash_attention_2").generate_voice_clone(text, language, ref_audio, ref_text)`. Reuse the clone prompt via `create_voice_clone_prompt`.
  - Apache-2.0.
  — [GitHub QwenLM/Qwen3-TTS](https://github.com/QwenLM/Qwen3-TTS)
  - **[MEASURED, H200, vLLM-Omni]** 1.7B-CustomVoice RTF is 0.16 at concurrency 1 and 0.31 at concurrency 10 after optimizations. — [vLLM-Omni perf doc](https://bezzam-evals-voxtral.hf.space/vllm-omni/docs/design/qwen3_omni_tts_performance_optimization.md)
  - **[MEASURED, M1 Max, MLX]** RTF about 0.29, peak memory 3.7–4.6 GiB. — [vllm-omni-mlx](https://github.com/InferMatrixLab/vllm-omni-mlx/releases)
  - The vLLM recipe sets `gpu_memory_utilization` to 0.3 per stage. — [vLLM recipe](https://recipes.vllm.ai/Qwen/Qwen3-TTS-12Hz-1.7B-CustomVoice)
- **Higgs TTS 3:** `bosonai/higgs-tts-3-4b`, 4B, Qwen3-based autoregressive, 100+ languages, zero-shot cloning, 21 emotion tags, custom **non-commercial** license, released 2026-06-04. — [comfyui-wiki](https://comfyui-wiki.com/en/news/2026-06-04-higgs-tts-3-4b-boson); [llmreference](https://www.llmreference.com/model/higgs-audio-v3-tts)
- Modal's only official TTS example is Chatterbox (`/docs/examples/chatterbox_tts`). — [Modal examples](https://modal.com/docs/examples)

### Inferences
- **[ESTIMATE]** Drama 3 weights: about 35 GB of FP8 experts plus the BF16 shared and attention parts, so roughly 40–45 GB plus KV cache. That means an A100-80GB or H100; an A100-40GB only with a quantized community build. Serial narration RTF at concurrency 1 should be around 0.15–0.25 on an H100 and higher on an A100 (no native FP8, slower kernels). That is still well under real time, so 10 min of narration should take roughly 2–3 min on an H100.
- **[ESTIMATE]** Qwen3-TTS 1.7B uses about 4–8 GB of VRAM, so it fits an A10G. Plain HF inference RTF is probably about 0.3–0.6 on an A10G and 0.2–0.4 on an A100; vLLM-Omni on Hopper gets about 0.16. It is the cheapest commercially clean option.
- Drama 3's license (research vs community) decides whether it can be used on a monetized channel.

### Gaps
- No A10G or A100 RTF measured for any of the three models. No VRAM figure for Drama 3. No primary Boson card fetched for Higgs TTS 3.

## Q9. Music: ACE-Step 1.5 (instrumental beds)

### Takeaway
Use ACE-Step 1.5 turbo (`acestep-v15-turbo`): 8 steps, CFG off, shift 3.0, 48 kHz stereo, 10 s to 10 min. It needs about 4.7 GB for the 2B weights. **Modal has an official example** on an L40S. For instrumentals, pass lyrics `"[Instrumental]"` (empty lyrics).

### Cited Findings
- Diffusers ACE-Step turbo is guidance-distilled: 8 steps, guidance ignored, shift 3.0. Base uses 8 steps, guidance 7.0, shift 3.0. Output is 48 kHz stereo, 10 s to 10 min. — [Diffusers ACE-Step docs](https://huggingface.co/docs/diffusers/v0.39.0/api/pipelines/ace_step)
- **[VENDOR, mirror of README]** Under 2 s per full song on an A100 (0.5–10 s depending on think mode and steps); under 10 s on an RTX 3090. 2B weights are about 4.7 GB. XL 4B is about 9 GB and needs at least 12 GB with offload or at least 20 GB without. Turbo uses 8 steps; base and SFT use 50. — [Gitee mirror](https://gitee.com/renfei/ACE-Step-1.5); [GitHub ACE-Step-1.5](https://github.com/ACE-Step/ACE-Step-1.5); [HF ACE-Step/Ace-Step1.5](https://huggingface.co/ACE-Step/Ace-Step1.5/commit/066d57904366d65ef77848d43eca198d3753aea9)
- **Modal example** (`modal.com/docs/examples/generate_music`):
  - Pins ACE-Step-1.5 at tag v0.1.6. Runs on `gpu="l40s"`, image `nvidia/cuda:13.0.0-cudnn-devel-ubuntu22.04`, torch about 2.10.
  - `AceStepHandler().initialize_service(config_path="acestep-v15-turbo")`, plus `LLMHandler` with `acestep-5Hz-lm-4B` on the vLLM backend.
  - Weights go on Volume `ACE-Step-v15-model-cache`; `HF_HUB_ENABLE_HF_TRANSFER=1`.
  - Generation config: `thinking=True`; lyrics default to `"[Instrumental]"`; duration 1–300 s in the UI.
  - No timings given.
  — [Modal example](https://modal.com/docs/examples/generate_music)
- Third-party recipe: set vocal weight to 0 for pure instrumentals. — [Civitai recipe](https://developer.civitai.com/orchestration/recipes/ace-step-audio)

### Inferences
- For background beds, skip the 4B LM "thinking" mode (or run it once per video) to save VRAM and time. The DiT alone fits an A10G.
- **[ESTIMATE]** A 2–3 min instrumental with turbo on an A10G takes about 5–15 s.

### Gaps
- No official RTF measured on Modal hardware.

## Q10–12. Modal deployment: official examples, GPU memory snapshots, cold-start tips

### Takeaway
Modal has official examples for older LTX-Video, Flux (torch.compile), Flux Kontext, Chatterbox TTS and **ACE-Step 1.5**. It has none for Wan2.2, LTX-2.5, FlashVSR, RIFE or Qwen3-TTS. GPU memory snapshots exist but are **alpha**, and they don't speed up weight loading. For 15–45 GB video models, cold start is dominated by reading weights from the Volume.

### Cited Findings
- Examples:
  - `/docs/examples/ltx` and `/docs/examples/image_to_video` (LTX-Video)
  - `/docs/examples/flux` (torch.compile)
  - `/docs/examples/image_to_image` (Flux Kontext)
  - `/docs/examples/chatterbox_tts`
  - `/docs/examples/generate_music` (ACE-Step)
  - `/docs/examples/music-video-gen` (Wan2.1 fine-tune)
  - `/docs/examples/ministral3_inference` (snapshots cut cold start 10×)
  - No ComfyUI, upscaling or interpolation examples on the index.
  — [Modal examples](https://modal.com/docs/examples)
- CPU snapshots: `enable_memory_snapshot=True` (deployed apps only). GPU snapshots (alpha): add `experimental_options={"enable_gpu_snapshot": True}`. Code in `@modal.enter(snap=True)` is captured; `@modal.enter()` runs after restore. — [Modal memory snapshot guide](https://modal.com/docs/guide/memory-snapshot)
- Without GPU snapshots: load to CPU in `snap=True`, then move to GPU in `snap=False`. One example went from about 6 s to about 2 s. Typical speedup is 3–10×. — [Modal guide](https://modal.com/docs/guide/memory-snapshot)
- Limitations:
  - No multi-GPU.
  - `torch.compile` can break snapshot creation (set `TORCHINDUCTOR_COMPILE_THREADS=1`).
  - **No speedup when weight loading from storage dominates.**
  - Volume changes don't update snapshots.
  - Libraries that call `torch.cuda.is_available` at import can break CPU snapshots.
  - Put warmup forward passes and JIT compilation in `snap=True`.
  — [Modal guide](https://modal.com/docs/guide/memory-snapshot)

### Inferences
- Wan2.2 (about 30 GB of FP8 experts plus T5) and LTX-2.5 (about 44 GB DiT plus 24 GB Gemma): prefer longer `scaledown_window` and batch all of a video's shots into one container session. Don't rely on per-shot cold starts. GPU snapshots help capture compile and SageAttention or Triton JIT warmup, not byte loading.
- Use one Modal class per model family with separate images: LightX2V, ltx-pipelines, FlashVSR (Python 3.11 plus Block-Sparse-Attention build, A100), Kandinsky (Python 3.13+), TTS (sglang-omni or qwen-tts) and ACE-Step. The FlashVSR Block-Sparse-Attention compile should happen at image build time with a capped `MAX_JOBS`.

### Gaps
- No Modal-published cold-start measurements for diffusion video models of this size.
