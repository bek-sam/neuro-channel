# Orchestration frameworks, agentic video pipelines, and automatic QC for AI long-form explainers (as of 2026-10-29)

Method note: GitHub star counts and last-push dates came from the GitHub API (`gh api repos/<owner>/<repo>`) on 2026-10-29. Technique claims come from READMEs, arXiv abstracts, and official docs. Many arXiv fetches returned only abstracts, so implementation details are often missing and are listed under Gaps.

## Q1. Open-source end-to-end and agentic video generators: what to borrow for script, storyboard, shots, consistency, and pacing

### Takeaway
The active, useful repos split into two groups. (a) Agentic "director" pipelines such as ViMax and VideoClaw/FilmAgent use role-split LLM agents with reference images and VLM-based candidate selection. (b) Code-centric explainer agents such as Code2Video and Paper2Video use a planner, coder, and VLM critic loop that renders Manim or slides. For a neuroscience explainer, the most transferable ideas are from the code-centric group: a VLM critic on rendered frames, generating N keyframe candidates and having a VLM pick one, and quiz-style "did the video teach" evaluation. Multi-shot video models (HoloCine, LCT, MultiShotMaster) are research-grade and expensive. They are relevant only to the hero-clip path.

### Cited Findings
**Repo status (stars / last push, from GitHub API on 2026-10-29)**
- harry0703/MoneyPrinterTurbo: 136,343 stars, pushed 2026-10-30. Very active. It is a topic-to-short-video tool (short-form, stock footage), and its README now advertises "AI Agent, WebUI, API and CLI" modes, batch generation, and many LLM providers including Anthropic Claude — [GitHub API](https://api.github.com/repos/harry0703/MoneyPrinterTurbo), [README](https://github.com/harry0703/MoneyPrinterTurbo)
- RayVentura/ShortGPT: 8,089 stars, last push 2025-02-10. Effectively stale (more than 20 months without a push), and it describes itself as "Experimental" — [GitHub](https://github.com/RayVentura/ShortGPT)
- linyqh/NarratoAI: 11,621 stars, pushed 2026-10-24. Active. It does AI narration plus editing of existing footage, and recent work adds local TTS engines (IndexTTS-2 MLX, OmniVoice) — [GitHub](https://github.com/linyqh/NarratoAI)
- HKUDS/ViMax: 12,801 stars, pushed 2026-09-30. Active. v1.2.0 (2026-07-20) added a Web UI, an Agent Loop, render checkpoints, and resume; a technical report came out on 2026-06-09 — [GitHub](https://github.com/HKUDS/ViMax)
- showlab/MovieAgent: 371 stars, last push 2025-03-26. Stale — [GitHub](https://github.com/showlab/MovieAgent)
- lichao-sun/Mora: 1,590 stars, last push 2024-10-10. Abandoned or superseded — [GitHub](https://github.com/lichao-sun/Mora)
- HITsz-TMG/FilmAgent now redirects to HITsz-TMG/VideoClaw: 1,882 stars, pushed 2026-08-26. VideoClaw is the successor ("AIGC coworker", OpenClaw Skill integration, keeps every intermediate artifact). FilmAgent (SIGGRAPH Asia 2024) and Anim-Director are listed as its prior work — [GitHub](https://github.com/HITsz-TMG/VideoClaw)
- PKU-YuanGroup/Open-Sora-Plan: 12,202 stars, last push 2026-03-08. Slowing. It is a model-training repo, not a pipeline — [GitHub](https://github.com/PKU-YuanGroup/Open-Sora-Plan)
- bilibili/Index-anisora: 2,532 stars, pushed 2026-07-16. Anime-focused model — [GitHub](https://github.com/bilibili/Index-anisora)
- yihao-meng/HoloCine: 704 stars, last push 2025-11-26 (CVPR 2026 Highlight) — [GitHub](https://github.com/yihao-meng/HoloCine)
- showlab/Code2Video: 2,184 stars, pushed 2026-08-24 (ICML 2026) — [GitHub](https://github.com/showlab/Code2Video)
- showlab/Paper2Video: 2,398 stars, last push 2026-03-05 — [GitHub](https://github.com/showlab/Paper2Video)
- I could not find a canonical "StoryAgent" GitHub repo (`storyagent/StoryAgent` returns 404).
- Newer multi-shot repos turned up by a GitHub search: KlingAIResearch/ShotStream (ECCV 2026, 187 stars), KlingAIResearch/MultiShotMaster (CVPR 2026, 184 stars), KlingAIResearch/Mise-en-Video (3D-controllable multi-shot, pushed 2026-10-29), and HITsz-TMG/MSVBench (ACL 2026 Findings, a benchmark for multi-shot video) — [GitHub search](https://github.com/search?q=multi-shot+video+generation&type=repositories)

**Techniques**
- ViMax pipeline: Idea2Video, Script2Video, and Novel2Video flows go from story to characters, script, storyboard, shots, and video. It coordinates "references, first frames, camera continuity, and final assembly" and generates compatible shots in parallel — [ViMax README](https://github.com/HKUDS/ViMax)
- ViMax best-of-N keyframes: it "generates 2 keyframe candidates in parallel and selects one using your vision-capable chat model," configured with `image_selection.num_candidates`. The README notes this improves quality and consistency at higher API cost — [ViMax README](https://github.com/HKUDS/ViMax)
- ViMax lists "Consistency Check" as a core challenge: image generators can produce unusable images even with correct references. Its answer is automated QC for character consistency and composition — [ViMax README](https://github.com/HKUDS/ViMax)
- Code2Video uses three agents. The Planner structures lecture content into a temporally coherent flow and prepares visual assets. The Coder turns instructions into executable Python (Manim) with "scope-guided auto-fix." The Critic uses a VLM with "visual anchor prompts" to refine spatial layout and clarity. The paper reports about a 40% improvement over direct code generation and introduces the TeachQuiz metric, in which a VLM "unlearns" a topic, watches the video, and is quizzed. It also reports results on the MMMC benchmark — [arXiv 2510.01174](https://arxiv.org/abs/2510.01174)
- Paper2Video's PaperTalker does slide generation with layout refinement via tree search over visual choices, cursor grounding, subtitling, TTS, and talking-head rendering, with parallel slide-wise generation. It evaluates with Meta Similarity, PresentArena, PresentQuiz, and IP Memory on 101 papers. A faster variant without the talking head was added on 2025-10-15 — [arXiv 2510.05096](https://arxiv.org/abs/2510.05096), [README](https://github.com/showlab/Paper2Video)
- HoloCine takes shot-by-shot text prompts and keeps characters, objects, and style consistent across shots in a scene. It uses sparse inter-shot attention (FlashAttention-3 recommended) on Wan 2.2 components. Checkpoints are 14B full/sparse, "-l" variants for videos longer than 1 minute, and 5B variants for limited memory. A ComfyUI node exists via kijai/ComfyUI-WanVideoWrapper#1566 and Dango233/ComfyUI-WanVideoWrapper-Multishot, which the README marks as "still under test" — [HoloCine README](https://github.com/yihao-meng/HoloCine)
- Long Context Tuning (ICCV 2025) expands the context window of pre-trained single-shot video diffusion models so they learn scene-level multi-shot consistency directly — [arXiv 2503.10589](https://arxiv.org/abs/2503.10589), [CVF](https://openaccess.thecvf.com/content/ICCV2025/html/Guo_Long_Context_Tuning_for_Video_Generation_ICCV_2025_paper.html)

**Templating engines**
- remotion-dev/remotion: 68,941 stars, pushed 2026-10-29 ("Make videos programmatically with React") — [GitHub](https://github.com/remotion-dev/remotion)
- motion-canvas: 19,590 stars, last push 2026-07-02 (slower) — [GitHub](https://github.com/motion-canvas/motion-canvas)
- ManimCommunity/manim: 41,997 stars, pushed 2026-10-29 — [GitHub](https://github.com/ManimCommunity/manim)
- 3b1b/manim (ManimGL): 95,873 stars, pushed 2026-09-09 — [GitHub](https://github.com/3b1b/manim)

### Inferences
- The highest-value borrow is the Code2Video pattern: Claude writes Manim (ManimCommunity) code for diagram scenes, renders on the ARM VM (CPU is fine for Manim), samples frames, and a VLM critic flags overlap and clipping, then loops up to K times. This adds animated diagrams, which still images plus Ken Burns cannot provide.
- Adopt ViMax-style `num_candidates` for Qwen-Image. Generating 2–4 candidates per scene is cheap on Modal (batched per call), and a VLM or reward model then picks the winner.
- A TeachQuiz-style check can be run cheaply: give Claude only the narration plus frame captions and quiz it on the script's key claims. This catches scenes whose visuals do not support the point being made.
- Do not adopt MoneyPrinterTurbo or ShortGPT wholesale. They target shorts with stock footage. MoneyPrinterTurbo's subtitle and edit modules may still be worth reading.
- HoloCine and multi-shot models would only matter for multi-shot hero sequences. They need a 14B model and FA3 on H100-class GPUs, so they are probably not cost-effective for 40–80-scene explainers.

### Gaps
- I did not read the ViMax technical report or the Code2Video full paper. The exact critic prompts, the "visual anchor" construction, and the cost per video are not captured.
- I did not check repo stats for AniSora-specific pipeline features, MovieAgent's CoT planning details, or StoryAgent.
- I did not verify Remotion's license terms. Remotion has a company license for some organizations, so this should be checked before adopting it.

## Q2. Workflow engines for GPU jobs on a single 4-core/24 GB ARM VM

### Takeaway
Keep Modal as the GPU executor and put a lightweight durable-workflow layer on the VM. The candidates are DBOS (Postgres-backed, library-only, with queue concurrency and rate limits), Prefect, Hatchet, or a plain task queue such as Huey. Temporal is a heavy, separate service and is overkill here. Modal itself provides per-input retries, crash rescheduling, and `.map()` with `return_exceptions`. ComfyUI is optional; the current direct-Python Modal functions are simpler.

### Cited Findings
- Modal retries: `@app.function(retries=N)` retries with a fixed 1 s delay, and `modal.Retries` supports exponential backoff. With `Function.map()`, each input is retried independently, and `return_exceptions=True` puts exceptions in the results list instead of raising them. Crashed containers (for example on OOM) are rescheduled; deployed apps retry crashes indefinitely with crash-loop backoff — [Modal docs: retries](https://modal.com/docs/guide/retries)
- Modal pattern from its SD3.5 example: load the model in `@modal.enter()`, keep weights in a Volume (HF cache), pin the model revision, generate multiple images per call with `num_images_per_prompt` ("much cheaper" than separate calls), and call `torch.cuda.empty_cache()`. It quotes a cold start of about one minute on H100 — [Modal example](https://modal.com/docs/examples/comfyapp) (this URL served the SD3.5/diffusers example). The ComfyUI-specific example URL I tried returned 404.
- Comfy-Org/ComfyUI: 144,026 stars, very active. Comfy-Org/comfy-cli: 1,036 stars, active. BennyKok/comfyui-deploy: 1,535 stars, last push 2025-11-13, so slowing — [GitHub API](https://github.com/Comfy-Org/ComfyUI), [comfy-cli](https://github.com/Comfy-Org/comfy-cli), [comfyui-deploy](https://github.com/BennyKok/comfyui-deploy)
- DBOS Python (dbos-inc/dbos-transact-py): 1,656 stars, pushed 2026-10-29. Its description is "Database-Backed Durable Python Workflows." Queues support per-queue or per-process concurrency caps, a global concurrency limit changeable at runtime, rate limits (for example 2 starts per 10 s), and partitioned queues. They are durable with no broker but require Postgres — [GitHub](https://github.com/dbos-inc/dbos-transact-py), [DBOS queue docs](https://docs.dbos.dev/python/reference/queues), [queue patterns](https://docs.dbos.dev/python/examples/queue-patterns), [PyPI](https://pypi.org/project/dbos/2.11.0a2/)
- Hatchet: 8,201 stars, active ("orchestration engine for background tasks, AI agents, and durable workflows") — [GitHub](https://github.com/hatchet-dev/hatchet)
- Prefect: 24,101 stars, active — [GitHub](https://github.com/PrefectHQ/prefect)
- Temporal: 24,076 stars, active. It is a separate "Temporal service" server — [GitHub](https://github.com/temporalio/temporal)
- Inngest: 6,000 stars, active ("serverless, servers, or the edge") — [GitHub](https://github.com/inngest/inngest)
- Huey: 6,057 stars, pushed 2026-10-24 ("a little task queue for python") — [GitHub](https://github.com/coleifer/huey)
- Inference-acceleration options for Wan on Modal: ModelTC/LightX2V (2,972 stars, active) and hao-ai-lab/FastVideo (4,759 stars, active) — [LightX2V](https://github.com/ModelTC/LightX2V), [FastVideo](https://github.com/hao-ai-lab/FastVideo)

### Inferences
- Recommended setup on the VM: a single Python process running DBOS with a local Postgres container, which fits in 24 GB alongside the MCP server. Each video is a workflow and each scene stage is a step that calls Modal `.spawn()` or `.map()`. A DBOS queue with a concurrency limit acts as a GPU-parallelism guard. If Postgres is unwanted, Huey with SQLite storage plus idempotent, hash-keyed stage outputs in the HF dataset is the minimal option.
- Budget guard: have every step write `estimated_gpu_seconds × price` to a ledger table and refuse to enqueue once a per-video cap is hit. I found no Modal-native per-app spend cap in the docs I fetched; see Gaps.
- The MCP server should expose coarse tools (`start_video`, `status`, `rerun_scene(id, stage)`, `approve`) on top of the workflow engine. This way Claude-driven reruns are durable and idempotent.
- Temporal and Hatchet each require a server (Hatchet also needs Postgres and RabbitMQ in self-host mode). That is more operations than a single free VM justifies.

### Gaps
- I did not verify Modal workspace spend limits or budget alerts, or the details of `FunctionCall.get` and polling. I also did not check Modal memory snapshots for GPU.
- I did not confirm that Hatchet, Temporal, or Postgres images run on ARM64. They likely do, but this is unverified.
- I did not verify whether DBOS supports SQLite. Search results showed only Postgres.

## Q3. Automatic QC: VLM judges, video and image quality metrics, TTS checks, and best-of-N

### Takeaway
Use a layered QC. First, cheap numeric gates: image reward score, the WER of Whisper re-transcription against the narration, and loudness measured with pyloudnorm. Second, a VLM judge (Qwen3-VL on Modal, or Claude vision) using a rubric for artefacts, anatomy, prompt adherence, and on-image text. Third, for Wan clips, VideoScore2 or selected VBench dimensions such as motion smoothness and subject consistency. Best-of-N selection by reward model or VLM is directly supported by the literature (VideoScore2, ViMax).

### Cited Findings
- VBench (Vchitect/VBench, 1,835 stars, pushed 2026-08-21) breaks quality into hierarchical dimensions with per-dimension evaluators aligned to human preference. VBench++ adds VBench-I2V (folder `vbench2_beta_i2v`, relevant to Wan I2V), VBench-Long (`vbench2_beta_long`), and Trustworthiness. VBench-2.0 (`VBench-2.0/` folder) adds 18 "intrinsic faithfulness" dimensions across Human Fidelity, Controllability, Creativity, Physics, and Commonsense. It has supported "evaluating customized videos" for single dimensions since 2025-05 — [VBench README](https://github.com/Vchitect/VBench), [arXiv 2503.21755](https://arxiv.org/abs/2503.21755)
- VideoScore2 (arXiv 2509.22799, TIGER-Lab) scores generated video on visual quality, text alignment, and physical/commonsense consistency, with written rationales. It was trained on VideoFeedback2 (27,168 videos from 22 T2V models) using SFT then GRPO, and reaches 44.35 accuracy on VideoScore-Bench-v2. The authors demonstrate it as a Best-of-N reward model. Weights and a demo are on HF — [arXiv 2509.22799](https://arxiv.org/abs/2509.22799), [HF space](https://tiger-lab-videoscore2.hf.space)
- Sci-VBench (arXiv 2608.09873) is a newer benchmark for knowledge- and reasoning-intensive video generation in science domains, and it uses VideoScore2 as a baseline judge. It is relevant to "is the science depicted correctly" — [arXiv 2608.09873](https://arxiv.org/pdf/2608.09873)
- DOVER (VQAssessment/DOVER, 535 stars) was last pushed 2024-08-12 and is stale. teowu/FAST-VQA-and-FasterVQA was last pushed 2022 (the repo checked has 4 stars; it may be a mirror). Both are older UGC-quality models — [DOVER](https://github.com/VQAssessment/DOVER), [FAST-VQA](https://github.com/teowu/FAST-VQA-and-FasterVQA)
- Q-Future/Q-Align (631 stars, pushed 2026-06-24) is an all-in-one LMM scorer for image quality, image aesthetics, and video quality — [GitHub](https://github.com/Q-Future/Q-Align)
- Image preference models: ImageReward (now zai-org/ImageReward, 1,706 stars, last push 2025-10-29), HPSv3 (MizzenAI/HPSv3, ICCV 2025, 369 stars, last push 2025-12-05), and PickScore (606 stars, last push 2024-12-21, stale). CodeGoat24/UnifiedReward (825 stars, pushed 2026-06-18) covers UnifiedReward, UnifiedReward-Think (NeurIPS 2025), and UnifiedReward-Flex — [ImageReward](https://github.com/zai-org/ImageReward), [HPSv3](https://github.com/MizzenAI/HPSv3), [PickScore](https://github.com/yuvalkirstain/PickScore), [UnifiedReward](https://github.com/CodeGoat24/UnifiedReward)
- QwenLM/Qwen3-VL: 20,146 stars, last push 2026-01-30 — [GitHub](https://github.com/QwenLM/Qwen3-VL)
- Code2Video's critic is a VLM with visual anchor prompts that refines layout on rendered frames. Its evaluation also uses VLM-as-a-Judge aesthetic scores — [arXiv 2510.01174](https://arxiv.org/abs/2510.01174)
- ViMax selects among keyframe candidates with a vision-capable chat model — [ViMax README](https://github.com/HKUDS/ViMax)
- Audio tools: SYSTRAN/faster-whisper (26,310 stars, active) can re-transcribe TTS output for a WER check. csteinmetz1/pyloudnorm (786 stars) implements ITU-R BS.1770-4 loudness. resemble-ai/chatterbox (27,413 stars, last push 2026-07-21) — [faster-whisper](https://github.com/SYSTRAN/faster-whisper), [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm), [chatterbox](https://github.com/resemble-ai/chatterbox)
- Multi-shot evaluation: HITsz-TMG/MSVBench (ACL 2026 Findings) evaluates multi-shot video at a "human-level" — [GitHub](https://github.com/HITsz-TMG/MSVBench)

### Inferences
Suggested QC ladder per scene:
1. Image: N=2–4 Qwen-Image candidates, scored by HPSv3 or ImageReward on the same Modal GPU (cheap, about the same call). The top 2 go to a VLM rubric (Qwen3-VL-8B on Modal, or Claude vision batched per scene) with JSON output: `{artefacts, anatomy_ok, text_garbled, matches_prompt 1-5, matches_narration 1-5}`. Fail leads to regeneration with an amended prompt, max 2 retries, then fallback to a Manim or diagram scene.
2. Hero clip: sample 8–16 frames. Run the VLM rubric plus VBench-I2V subject consistency, motion smoothness, and temporal flicker, or VideoScore2. If generating multiple Wan seeds is too expensive, accept or reject only.
3. Voice: faster-whisper re-transcribe, then compute WER against the narration (threshold around 5–8%, needs tuning). Also check per-word timing gaps for hallucinated silences, regenerate the line with a different seed if needed, and normalise integrated loudness with pyloudnorm or ffmpeg `loudnorm` to a consistent target.
4. Whole video: Claude reviews a contact sheet (one frame per scene with its narration line) as a final VLM pass for repetition and visual monotony.

- Prefer Claude vision for semantic adherence ("does this depict hippocampal place cells?"). Use open reward models and Qwen3-VL for cheap bulk filtering. Avoid DOVER and FAST-VQA because they are stale and trained on UGC.

### Gaps
- I found no published per-image cost numbers for Claude vision versus Qwen3-VL judging. Compute these from current Anthropic pricing and Modal GPU-seconds.
- I did not find calibrated WER thresholds for TTS QC or a YouTube-official loudness target in a primary source.
- I did not verify the HPSv3 and ImageReward licenses, or whether Qwen3.5-VL or newer Qwen VL releases supersede Qwen3-VL (the repo's last push was January 2026, which suggests a possible successor).

## Q4. Editing quality and the YouTube feedback loop

### Takeaway
The only primary-sourced item here is YouTube Test & Compare. It tests up to 3 titles and/or thumbnails, and the winner is chosen by watch time share, not CTR. It is desktop and Studio-only and needs advanced features enabled. Changing the title or thumbnail mid-test stops the test. Because no evidence was gathered on retention-editing practice, captions, or chaptering, those are recommendations, not findings.

### Cited Findings
- Test & Compare can test title only, thumbnail only, or both together, with up to 3 variants. The winner is the variant with the highest watch time share, which YouTube chose over CTR because it better reflects whether viewers found the video worthwhile. Tests should finish within two weeks. Outcomes are Winner, Performed Same, or Inconclusive (in which case the first upload stays the default). It is desktop Studio only and requires advanced features. It is not available for Shorts, made-for-kids, mature, or private videos. Editing during a test stops it. Thumbnails below 720p are downscaled to 480p. A control group sees only the default — [YouTube Help 13861714](https://support.google.com/youtube/answer/13861714)
- Third-party guides say title testing was added after thumbnails (around late 2025). One gives an illustrative case where a 9% CTR / 3:48 average-view-duration thumbnail loses to a 6.8% / 6:17 one. This is a blog illustration, not a measured result — [thumbnailtest.com](https://thumbnailtest.com/news/youtube-releases-title-test-compare/), [vidanalyze](https://vidanalyze.com/news/youtube-ab-testing-for-titles-thumbnails-2026-guide)
- Remotion, Manim, and Motion Canvas status: see Q1 — [Remotion](https://github.com/remotion-dev/remotion), [Manim](https://github.com/ManimCommunity/manim)

### Inferences
- Generate 3 thumbnail and title variants per video in the pipeline and set up Test & Compare manually in Studio. I found nothing showing it is exposed in the Data API.
- Feed per-video retention (audience retention curve) back to Claude. Map dips to scene IDs using the scene timeline already in the HF dataset, so that Claude learns which scene types, such as long static images or dense narration, lose viewers.
- Auto-chapters: write chapter timestamps derived from the scene JSON section boundaries and the faster-whisper word timings into the description (`00:00` first line).
- Kinetic typography and captions can be done with ASS-styled subtitles in ffmpeg (word-level highlight from faster-whisper word timestamps), or with Remotion if the license is acceptable. Manim scenes cover animated diagrams.

### Gaps
- I did not research retention-editing evidence (cut frequency, B-roll variety, pattern interrupts) from primary sources such as YouTube Creator Insider or academic retention studies. No sourced claims are available.
- I did not verify whether the YouTube Analytics API exposes per-video audience-retention data (`audienceWatchRatio` / `elapsedVideoTimeRatio`) or whether Test & Compare results are readable via the API.
- I did not verify YouTube's automatic chapter rules (minimum 3 chapters, 10 s minimum each). This comes from memory, not a source.

## Q5. Recommended architecture changes with concrete repos

### Takeaway
Keep the stack (Claude script, Modal GPU functions, ffmpeg, HF dataset) and add four things. (1) A durable workflow and queue layer on the VM (DBOS or Huey) with idempotent stage outputs and a spend ledger. (2) Best-of-N plus a VLM/reward-model QC loop per scene (ViMax and VideoScore2 patterns). (3) A Manim code-agent path for diagram scenes with a VLM critic (the Code2Video pattern). (4) Test & Compare thumbnail and title variants plus a retention-to-scene feedback loop.

### Cited Findings
- Best-of-N keyframes with VLM selection: [ViMax](https://github.com/HKUDS/ViMax)
- Planner, Coder (auto-fix), and VLM Critic for Manim educational video, about 40% better than direct code generation: [Code2Video arXiv 2510.01174](https://arxiv.org/abs/2510.01174), [repo](https://github.com/showlab/Code2Video)
- Parallel per-slide/scene generation with tree-search layout selection: [Paper2Video arXiv 2510.05096](https://arxiv.org/abs/2510.05096)
- Video reward model usable for Best-of-N: [VideoScore2](https://arxiv.org/abs/2509.22799); I2V-specific metrics: [VBench-I2V](https://github.com/Vchitect/VBench/tree/master/vbench2_beta_i2v)
- Durable queues with concurrency and rate limits: [DBOS](https://docs.dbos.dev/python/examples/queue-patterns); Modal per-input retries and backoff: [Modal retries](https://modal.com/docs/guide/retries)
- Batch candidates in one Modal call (cheaper): [Modal example](https://modal.com/docs/examples/comfyapp)
- Wan acceleration: [LightX2V](https://github.com/ModelTC/LightX2V), [FastVideo](https://github.com/hao-ai-lab/FastVideo)
- Thumbnail and title A/B by watch-time share: [YouTube Help](https://support.google.com/youtube/answer/13861714)

### Inferences
Concrete changes, in priority order:
1. **Stage contract.** Each stage is `stage(scene_id, inputs_hash) -> artifact + qc.json`, stored in the HF dataset keyed by hash. Reruns become idempotent and Claude can target a single scene through MCP.
2. **Workflow layer.** Use DBOS (Postgres in Docker on the ARM VM) with a `gpu` queue (concurrency 4–8, rate-limited), a ledger table, and a per-video budget cap. The fallback is Huey with SQLite.
3. **QC module.** Run reward model and Qwen3-VL as a Modal function (the same GPU container as Qwen-Image if VRAM allows). Use Claude vision for semantic checks and a final contact-sheet review. Use faster-whisper for WER and pyloudnorm for loudness. Store results in the HF dataset to tune thresholds over time.
4. **Scene-type router.** Claude's scene JSON gains `visual_type: image | hero_clip | manim_diagram | kinetic_text`. `manim_diagram` scenes go through a Code2Video-style coder and critic loop rendered on the VM's CPU.
5. **Publishing loop.** Generate 3 thumbnails and titles, run Test & Compare manually, pull retention curves, map them to scene IDs, and feed them to Claude's script prompt as "lessons."
- Things to avoid: ShortGPT (stale), Mora (abandoned), MovieAgent (stale), DOVER/FAST-VQA (stale), and comfyui-deploy (slowing). ComfyUI is only worth it if you want to adopt community workflows such as the HoloCine and Wan wrapper nodes.

### Gaps
- I ran no end-to-end cost model (GPU-seconds per 15-minute video with best-of-N and QC). Inputs are needed from current Modal pricing and measured stage timings.
- I did not test ARM64 compatibility for Manim's dependencies (Cairo, Pango, LaTeX) or for DBOS/Postgres on Oracle Ampere. It is likely fine but unverified.
