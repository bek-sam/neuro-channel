# TTS for long-form documentary narration (state as of 2026-10-29)

Context: automated faceless YouTube channel (neuroscience/psychology), 10-20 min English narration, one consistent cloned narrator. Current stack: Chatterbox (Resemble AI) on Modal A10G (~20 s/line) + reference clip; fallback Kokoro-onnx CPU; faster-whisper subtitles.

Cost basis used throughout: 15 min at ~150 wpm is ~2,250 words, or about 13,500 characters including spaces. Cost per video = price per 1M chars x 0.0135. This is my estimate, not a sourced figure.

---

## Q1. Which open-weight models lead now (naturalness, stability, cloning, control, speed/VRAM, licence)?

### Takeaway
The open-weight field has moved a long way since mid-2025. On the Artificial Analysis (AA) open-weights board, Fish Audio Drama 3 (Oct 2026, Elo 1278) leads, followed by Breeze TTS 2 (1228) and Ant Group's Ming-3.0-tts (1187). The models in the original question list are well down the board: Higgs Audio V3 is 1039, Chatterbox 1024, Zonos 1000 and VibeVoice 1.5B 955. Kokoro (1062) still scores above Chatterbox. Licences matter more than rank here. Drama 3 is free for commercial use under $500k annual revenue. Breeze TTS 2 is non-commercial. Higgs TTS 3 is non-commercial but has a Creator Use Grant that explicitly allows monetized videos with attribution. Qwen3-TTS (Apache 2.0) and Chatterbox (MIT) are the cleanest permissive options.

### Cited Findings

**Leaderboard snapshot (AA open-weights / provider-voice board, fetched 2026-10-29; the page shows no "as of" date; 95% CI roughly ±12-20 Elo)** — [AA open-weights leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard/provider-voice/open-weights)
| Rank | Model | Elo | Released |
|---|---|---|---|
| 1 | Fish Audio Drama 3 | 1278 | Oct 2026 |
| 2 | Fish Audio Drama 3 Preview | 1240 | Oct 2026 |
| 3 | BreezeBlue Breeze TTS 2 | 1228 | Aug 2026 |
| 4 | Ant Group Ming-3.0-tts | 1187 | Oct 2026 |
| 5 | Fish Audio S2 Pro | 1109 | Mar 2026 |
| 6 | StepFun Step Audio EditX | 1099 | Feb 2026 |
| 7 | Mistral Voxtral TTS (4B) | 1090 | Mar 2026 |
| 8 | NVIDIA Magpie-Multilingual 357M | 1067 | Feb 2026 |
| 9 | Kokoro 82M v1.0 | 1062 | Jan 2025 |
| 10 | Maya1 | 1046 | Jun 2025 |
| 11 | OpenAudio S1 Mini (Fish) | 1044 | Jun 2025 |
| 12 | Boson Higgs Audio V3 TTS | 1039 | Jun 2026 |
| 13 | Resemble Chatterbox | 1024 | May 2025 |
| 14 | Zyphra Zonos-v0.1 (anchor) | 1000 | Feb 2025 |
| 16 | Microsoft VibeVoice 1.5B | 955 | Aug 2025 |
| 17 | Coqui XTTS v2 | 915 | Nov 2023 |
| 18 | StyleTTS 2 | 891 | Jun 2023 |
- Snapshot dates conflict. An earlier AA FAQ text cited S2 Pro as the top open-weights model at Elo 1123, and an older AA post had Alibaba Fun-Realtime-TTS at #1 overall (Elo 1219). Drama 3, released in October, has since superseded both. — [AA leaderboard search summary](https://artificialanalysis.ai/text-to-speech/leaderboard); [AA Fun-Realtime-TTS article](https://artificialanalysis.ai/articles/fun-realtime-tts-new-text-to-speech-model-topping-artificial-analysis-leaderboard)
- On the overall AA board, Drama 3 ranks #6 and is the only open-weight model in the top 10. The models above it are all proprietary: Eleven v4 Turbo, Eleven v4, Qwen-Audio-3.1-TTS-Plus, Cartesia Sonic 3.6 and Gemini 3.8 Flash TTS. — [AA leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard)

**Fish Audio Drama 3 (Oct 2026). Top open-weight model.**
- It is a 35B mixture-of-experts model with ~3B parameters active (8 of 256 experts plus 1 shared), initialized from Qwen3.5-35B-A3B. It speaks 83 languages. Throughput is 271 frames/s for a single stream on one H200 (S2: 177 frames/s), and audio runs at ~21.5 frames/s, so it is roughly 12x real time on an H200. The page gives no VRAM figure. — [Fish Audio blog](https://fish.audio/blog/fish-audio-drama-3/)
- Control works through natural-language direction in square brackets placed anywhere in a line (e.g. `[whispering]`), plus paired `<emphasis>…</emphasis>` tags around words. It clones from a reference clip. Fish also positions it for audiobooks and chapter-length scripts, but gives no maximum length. — [Fish Audio blog](https://fish.audio/blog/fish-audio-drama-3/)
- On AA's Pronunciation Robustness test it scores 93.2% overall (S2.1 Pro: 88.1%) and 95.9% on brands, places and technical terms. That category matters for neuroscience terminology. — [Fish Audio blog](https://fish.audio/blog/fish-audio-drama-3/)
- Licence: Fish Audio Community License v1.0. It is free for commercial use if you and your affiliates earn under US$500k a year. Above that cap, or to offer the model as a TTS/inference service, you need a licence from Fish. It also bans cloning a real person's voice without consent. — [Fish Audio blog](https://fish.audio/blog/fish-audio-drama-3/); [eesel.ai](https://www.eesel.ai/blog/fish-audio-drama-3)
- The Hugging Face repo tag still reads "fish-audio-research-license", with a pending PR to update the licence link, so the metadata is inconsistent. Read the LICENSE file itself. — [HF discussion](https://huggingface.co/fishaudio/drama-3/discussions/3)
- A third-party repack says the licence also bars using outputs to train other speech models. This is unverified. — [HF repack](https://huggingface.co/cicalooo/ComfyUI-FishDramatics)
- Community quantizations exist (Q2/Q3 GGUF, NVFP4-pruned), which suggests people are trying to fit it on smaller GPUs. — [HF UltimateIntent quant](https://huggingface.co/UltimateIntent/Fish-Audio-Drama-3-Q2-Q3/discussions); [HF NVFP4](https://huggingface.co/plotarmordev/drama-3-NVFP4-Pruned/discussions)

**Breeze TTS 2 (BreezeBlue, Aug 2026). Elo 1228, but NOT usable commercially for free.**
- The code is Apache 2.0, but the weights fall under the "BreezeBlue Research and Non-Commercial License". Commercial use needs a paid licence, and a paid hosted subscription does not grant self-host rights. It is English and Mandarin only. — [HF model card](https://huggingface.co/BreezeBlue/Breeze-TTS-2); [GitHub](https://github.com/breezeblue-ai/breeze-tts); [Breeze-TTS-2.cpp](https://github.com/HoppouAI/Breeze-TTS-2.cpp)
- VRAM is ~7.7 GiB recommended (12 GB target). Cloning needs the reference clip plus an exact transcript, and a wrong transcript degrades output. A community port reports RTF 0.23 on inputs over 6,000 characters at ~6 GB. — [GitHub](https://github.com/breezeblue-ai/breeze-tts); [Breeze-TTS-2.cpp](https://github.com/HoppouAI/Breeze-TTS-2.cpp)

**Higgs TTS 3 / Higgs Audio V3 (Boson AI, released 2026-06-04). Elo 1039.**
- It has been renamed to Higgs TTS 3 (repo `bosonai/higgs-tts-3-4b`). The backbone is ~4B parameters (~5B in BF16) and covers 102 languages. On 1x H100 it runs at RTF 0.147 at concurrency 1 and generates 61.8 audio-s/s at concurrency 16. — [HF model card](https://huggingface.co/bosonai/higgs-tts-3-4b)
- Control: 21 emotion tags (e.g. `<|emotion:awe|>`), style tags (singing/shouting/whispering), 9 sound-effect tags, and speed, pitch, pause and expressiveness controls. Supplying the reference transcript "materially improves" cloning. On the EmergentTTS win-rate benchmark it scores 53.65% overall, the top score among the models Boson listed (vendor-reported), but it is weak on complex pronunciation (25.1%). — [HF model card](https://huggingface.co/bosonai/higgs-tts-3-4b)
- Licence: Research and Non-Commercial. A Creator Use Grant allows monetized videos, podcasts and audiobooks on commercial channels. Attribution to "Boson AI's Higgs Audio" is required in the audio or prominently in the description, not buried. The grant excludes API hosting, resale and embedding in apps. — [HF model card](https://huggingface.co/bosonai/higgs-tts-3-4b)
- Superseded: Higgs Audio v2 (2025) has been replaced by v3.

**Chatterbox family (Resemble AI). Elo 1024 for the original.**
- Current lineup:
  - Turbo: 350M, English, paralinguistic tags like `[laugh]`, single-step decoder, lower VRAM.
  - Nano: 110M, about 3x real time on 8 CPU cores.
  - Multilingual V3: 500M, 23+ languages, better speaker similarity and fewer hallucinations.
  - Multilingual V2: legacy.
  - Original: 500M, with CFG and exaggeration controls.
  - The README gives no release dates. — [GitHub resemble-ai/chatterbox](https://github.com/resemble-ai/chatterbox)
- The licence is MIT. Every output carries Resemble's Perth imperceptible watermark, which survives MP3 compression. Defaults are exaggeration 0.5 and cfg_weight 0.5. For dramatic delivery, use cfg_weight ~0.3 and exaggeration ≥0.7. For a fast reference speaker, use cfg_weight ~0.3. The README calls Turbo excellent for narration but gives no long-form guidance. — [GitHub](https://github.com/resemble-ai/chatterbox)
- Turbo's tag set includes [sigh], [gasp], [chuckle], [cough] and [clear throat], all English only. — [ComfyUI Fill-ChatterBox](https://github.com/filliptm/ComfyUI_Fill-ChatterBox); [therundown.ai](https://www.therundown.ai/tools/chatterbox-turbo)
- A third-party comparison says Chatterbox "sometimes adds odd artifacts at the end of longer generations". — [voicecreator.pro](https://voicecreator.pro/blog/qwen3-vs-omnivoice-vs-chatterbox-voice-cloning) (via search snippet; the page itself returned 429)

**Qwen3-TTS (Alibaba Qwen, Jan 2026). Not on the AA open-weights board.**
- The weights are Apache 2.0, so commercial use is allowed. The 1.7B-Base model does 3-second zero-shot cloning and needs the reference transcript. VRAM estimates conflict (4 / 6 / 16 GB depending on source). — [lilting.ch](https://lilting.ch/en/articles/qwen3-tts-voice-synthesis); [insiderllm](https://insiderllm.com/guides/crane-qwen3-tts-local-voice-cloning/)
- The technical report claims it can synthesize more than 10 minutes of natural, fluent speech. — [Qwen3-TTS Technical Report, arXiv 2601.15621](https://arxiv.org/html/2601.15621v1)
- A Medium long-form test reports that Qwen3 1.7B "maintains consistency" over 10+ minute narration where other open models drift, but it was the slowest of the four tested. — [Medium / Data Science Collective](https://medium.com/data-science-collective/high-quality-long-form-tts-with-qwen3-open-weight-models-cdd6e3d00df0) (snippet only; the full page returned 403)
- Its proprietary successors, Qwen-Audio-3.0/3.1-TTS-Plus, are API-only. — [AA leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard); [Qwen-Audio-3.0-TTS paper](https://arxiv.org/html/2607.23938v1)

**Microsoft VibeVoice. Elo 955.**
- In September 2025 Microsoft removed the TTS code because of misuse. The README says the tool "was used in ways inconsistent with the stated intent". The 1.5B and 7B weights remain on HF, and a community fork (vibevoice-community/VibeVoice) preserves the code. Microsoft has since shipped ASR and real-time models instead. I found no evidence of a 2026 re-release of long-form TTS. — [windowsnews.ai](https://windowsnews.ai/article/microsoft-pulls-vibevoice-tts-code-after-misuse-shifts-to-open-source-asr-and-real-time-models.378734); [byteiota](https://byteiota.com/microsoft-vibevoice-the-voice-ai-microsoft-pulled-back/); [joaoqueiros](https://www.ai.joaoqueiros.com/blog/vibevoice-local-tts-microsoft-removed-code-safe-setup)
- It was designed for up to ~90 min of multi-speaker audio in English and Chinese. — [siliconflow](https://www.siliconflow.com/articles/en/best-open-source-models-for-text-to-audio-narration)

**Other 2026 releases**
- Mistral Voxtral TTS: 4B, 9 languages, short-clip cloning, AA Elo 1090. Licence reports conflict (NVIDIA Open Model License vs CC BY-NC). Its successor Voxtral 3 TTS (Elo 1223) appears API-only. — [Forbes](https://www.forbes.com/sites/ronschmelzer/2026/03/26/mistral-releases-open-weight-voice-ai-built-for-speed/); [KDnuggets](https://www.kdnuggets.com/open-weight-text-to-speach-with-voxtral-tts); [AA](https://artificialanalysis.ai/text-to-speech/leaderboard)
- Hume TADA (Mar 2026): promoted for long-form, with up to ~700 s in one pass. Only listicles mention it. — [MarkTechPost](https://www.marktechpost.com/2026/05/30/best-text-to-speech-tts-models-in-2026-a-benchmark-based-comparison/); [edenai](https://www.edenai.co/post/top-free-text-to-speech-tools-apis-and-open-source-models)
- OmniVoice and MOSS-TTS-v1.5 beat Higgs TTS 3 on the "Emotions" category of EmergentTTS (61.07% and 60.54% vs 53.75%). — [Higgs HF card](https://huggingface.co/bosonai/higgs-tts-3-4b)
- VoxCPM2: one author reports a 224 s English audiobook passage at 1.37% WER. — [HF vdavidr](https://huggingface.co/vdavidr/textToAudioTTS-voxcpm2-audiobook-champion)
- IndexTTS2 is recommended for duration control and emotional expression. In the Qwen-Audio-3.0 paper table it scored lower than Qwen-Audio-3.0 on the long-form columns, but I could not verify the metric. — [siliconflow](https://www.siliconflow.com/articles/en/best-open-source-models-for-text-to-audio-narration); [arXiv 2607.23938](https://arxiv.org/html/2607.23938v1)

### Inferences
- Moving off Chatterbox could be a big quality jump: Drama 3 sits ~250 Elo above it on AA, and Higgs 3, Qwen3-TTS, Breeze 2 and S2 Pro all beat or match it. Chatterbox's ranking is from May 2025, and Turbo / Multilingual V3 may score better but are not separately ranked on AA.
- Best licence-safe open options for a monetized channel:
  - Drama 3: free commercial use under the $500k revenue cap, and the best quality and pronunciation.
  - Higgs TTS 3: Creator Grant, with attribution in the description.
  - Qwen3-TTS 1.7B: Apache, the best-reported long-form consistency.
  - Chatterbox: MIT, but watermarked.
- Avoid self-hosting Breeze TTS 2 (non-commercial). Avoid VibeVoice too: it ranks low, its code was pulled, and its reputation is tied to misuse.
- An A10G (24 GB) should fit Qwen3-TTS, Higgs 3 4B (BF16 ~10 GB plus KV cache) and Breeze. Drama 3 at 35B total would need ~70 GB in BF16, so it needs an A100-80GB/H100 or a quantized build. Its cheap launch API ($10/1M chars until 2026-11-12) is probably simpler. These sizes are my estimates from parameter counts, not measured.
- Kokoro (Elo 1062) actually outranks original Chatterbox on AA, so it is better than its "flat" reputation suggests as a fallback. It still has no cloning.

### Gaps
- None of the AA boards I fetched ranks IndexTTS2, Dia/Dia2, F5-TTS, Orpheus, Sesame CSM, MegaTTS3, Spark-TTS, CosyVoice 3, Kyutai TTS or Llasa, so I have no comparable Elo for them. I also did not check the HF TTS Arena V2 board (tool budget).
- I found no controlled 15-minute drift benchmark across models. Long-form claims are vendor or single-blogger reports.
- Drama 3 VRAM and minimum GPU are unpublished. Ming-3.0-tts licence and details are unknown.
- I did not verify current licences for IndexTTS2, Dia2, F5-TTS (earlier weights were CC-BY-NC), Orpheus or CosyVoice 3.

---

## Q2. Best practices for long-form generation and mastering

### Takeaway
Few sources document this rigorously. The common thread is to chunk at sentence or paragraph boundaries and to reuse one fixed reference clip with its exact transcript, since Higgs, Breeze and Qwen3 all say the transcript improves cloning. Then run ASR-based QC and retry failed chunks. Chatterbox's own knobs are cfg_weight and exaggeration. The loudness and mastering targets below come from general practice and were not verified this session.

### Cited Findings
- Reference transcripts: Higgs TTS 3 says supplying the transcript "materially improves" cloning, Breeze TTS 2 says a wrong transcript degrades results, and Qwen3-TTS Base requires one. — [Higgs HF](https://huggingface.co/bosonai/higgs-tts-3-4b); [Breeze GitHub](https://github.com/breezeblue-ai/breeze-tts); [insiderllm](https://insiderllm.com/guides/crane-qwen3-tts-local-voice-cloning/)
- Higgs tag placement: emotion, style and speed/pitch tags go at the start of the chunk, while pause and sound-effect tags go inline. — [Higgs HF](https://huggingface.co/bosonai/higgs-tts-3-4b)
- Chatterbox pacing: higher exaggeration speeds speech up, and lowering cfg_weight compensates. — [Chatterbox GitHub](https://github.com/resemble-ai/chatterbox)
- Community Qwen3-TTS apps split long text at sentence boundaries with a chunk-size setting. — [sup3rmass1ve/qwen3-tts](https://github.com/sup3rmass1ve/qwen3-tts)
- Fish Drama 3 supports in-line `[direction]` and `<emphasis>` tags, which act as an SSML-like layer for narration beats such as "[thoughtful, slower]". — [Fish blog](https://fish.audio/blog/fish-audio-drama-3/)
- YouTube's "inauthentic content" policy (renamed in July 2025, with channel-level enforcement) targets mass-produced, templated content. It does not target AI voice reading original scripts. Most sources are creator blogs, so verify against YouTube's official page. — [AIR Media-Tech](https://air.io/en/news-air/how-youtube-treats-ai-in-2026-new-update); [gulfnews](https://gulfnews.com/technology/youtube-updates-monetisation-policies-ai-and-repetitive-content-ban-begins-july-15-1.500192660); [outlierkit](https://outlierkit.com/resources/faceless-youtube-channel-demonetized/)

### Inferences (recommended pipeline, not sourced)
1. **Chunking:** use 1-3 sentences per chunk (~150-350 characters). Never split mid-sentence, and keep paragraph boundaries as longer pauses. Very long chunks risk end-of-clip artefacts (the Chatterbox report above), and very short ones lose prosody continuity.
2. **Consistency:**
   - Use one fixed 10-20 s clean reference clip plus its exact transcript.
   - Pin seed, temperature and cfg/exaggeration per channel.
   - For LLM-based TTS, optionally condition on the previous chunk's text or audio if the model supports it (Higgs and Fish support multi-turn context).
3. **Text normalization:** expand acronyms and numbers (e.g. "fMRI" becomes "eff-em-ar-eye", "5-HT" becomes "five-H-T") using a pronunciation dictionary for neuroscience terms. Drama 3's high technical-term robustness reduces this work.
4. **Automatic QC:**
   - Transcribe each chunk with faster-whisper (already in the stack).
   - Compute WER against the normalized script and retry with a new seed if WER > ~5-10%.
   - Also retry if duration per character falls outside the median ±40% (a sign of hallucination or truncation), or if the clip has trailing silence or noise longer than ~1 s.
   - Optionally check speaker similarity (ECAPA embedding cosine against the reference) to catch voice drift.
   - Cap retries at 3, then fall back to a different seed or settings.
5. **Assembly:** trim leading and trailing silence (e.g. ffmpeg `silenceremove`), insert fixed pauses (~250-400 ms between sentences, ~600-900 ms between paragraphs), and use short 10-20 ms crossfades.
6. **Mastering chain (ffmpeg):** `highpass=f=70`, a gentle de-esser (`deesser` filter or a 5-8 kHz dynamic EQ), a light compressor (`acompressor=ratio=2:threshold=-18dB`), then two-pass `loudnorm=I=-14:TP=-1.5:LRA=7`.
   - Under music, duck the bed ~15-20 dB below the voice.
   - YouTube normalizes playback to about -14 LUFS, so mastering louder gains nothing. This is widely cited, but I did not find a source this session.
7. **Disclosure:** keep the script human-edited and original. The policy risk comes from templated mass production, not from TTS. Make sure the narrator reference voice is one you have rights or consent for (required by the Fish and Higgs licences).

### Gaps
- I found no authoritative source this session for YouTube's -14 LUFS normalization or for WER retry thresholds. The values above are practitioner conventions.
- I found no published study of optimal chunk length per model.

---

## Q3. API options: quality and price per 15-min video

### Takeaway
ElevenLabs v4 and v4 Turbo now top the overall AA arena (Elo 1336 and 1334), but they cost 3-5x more than Gemini 3.8 Flash TTS (1283) or Fish Drama 3 API (1278). All of these are under ~$1.10 per 15-minute video at API list prices, so cost is not the deciding factor at this channel's volume. Voice cloning and consistency matter more.

### Cited Findings
**AA overall board (provider voices), fetched 2026-10-29** — [AA leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard). Per-video cost is my calculation at ~13.5k characters.
| Model | Elo | $/1M chars | ≈ $/15-min video |
|---|---|---|---|
| ElevenLabs Eleven v4 Turbo | 1336 | 40 | 0.54 |
| ElevenLabs Eleven v4 | 1334 | 80 | 1.08 |
| Alibaba Qwen-Audio-3.1-TTS-Plus | 1305 | 19.3 | 0.26 |
| Cartesia Sonic 3.6 | 1296 | 49 | 0.66 |
| Google Gemini 3.8 Flash TTS | 1283 | 16.5 | 0.22 |
| Fish Audio Drama 3 (API) | 1278 | 15 (AA); blog says $50 list, $10 launch until 2026-11-12 | 0.14-0.68 |
| Inworld Realtime TTS-2 | 1267 | 20.8 | 0.28 |
| Smallest.ai Lightning V3.1 Pro | 1266 | 19.5 | 0.26 |
| Gemini 3.8 Flash-Lite TTS | 1259 | 11 | 0.15 |
| Speechify Simba 3.2 | 1249 | 6.6 | 0.09 |
| Mistral Voxtral 3 TTS | 1223 | 13 | 0.18 |
| ElevenLabs v3 Conversational | 1215 | 50 | 0.68 |
| Gemini 3.1 Flash TTS | 1212 | 18.3 | 0.25 |
| Cartesia Sonic 3.5 | 1194 | 49 | 0.66 |
| Fish Audio S2.1 Pro | 1188 | 15 | 0.20 |
| ElevenLabs Eleven v3 | 1188 | 100 | 1.35 |
| MiniMax Speech 2.8 HD | 1174 | 100 | 1.35 |
- ElevenLabs v4 list price is $0.08/1k chars and v4 Turbo $0.04/1k. A 72% launch discount ended 2026-10-12. Requests are limited to 10,000 characters, and v4 covers 90+ languages. Subscription plans use ~1 credit per character. — [eesel.ai v4 pricing](https://www.eesel.ai/blog/eleven-v4-pricing); [OpenRouter](https://openrouter.ai/elevenlabs/eleven-v4); [Cartesia on ElevenLabs pricing](https://www.cartesia.ai/learn/elevenlabs-pricing)
- OpenAI gpt-4o-mini-tts costs $0.60/1M input tokens and $12/1M audio output tokens (~$0.015/min, about $0.23 per 15 min). I found no successor model in 2026 and it is not in the AA top 30. — [OpenAI community](https://community.openai.com/t/understanding-gpt-4o-mini-tts-pricing-input-characters-cost/1151816); [costgoat](https://costgoat.com/pricing/openai-tts)
- Superseded: Eleven v3 (Elo 1188, $100/1M) and Multilingual v2 have been replaced by v4. Gemini 2.5 TTS has given way to the 3.1 and 3.8 Flash models. Cartesia Sonic 3.5 has been replaced by 3.6. — [AA leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard)
- AA's controlled-voice board, which uses the same 8 cloned voices for every model and so is the most relevant to a cloned narrator, is led by Inworld Realtime TTS-2 at 1146 Elo. — [AA controlled voice](https://artificialanalysis.ai/text-to-speech/leaderboard/controlled-voice)

### Inferences
- For a cloned narrator, the controlled-voice board is more relevant than the provider-voice board. I only got its leader, so check where ElevenLabs, Fish and Cartesia rank there.
- At 4-8 videos/month, even Eleven v4 costs under ~$10/month at API rates. The real costs are the subscription tier needed for Professional Voice Cloning and the 10k-character request cap, which means ~2 requests per video at minimum, or more with sentence chunking.
- For comparison, Modal A10G self-hosting of Chatterbox at ~20 s/line and ~150 lines would take ~50 GPU-minutes per video. My unverified estimate is ~$1 per video, roughly the same as Eleven v4 and slower.

### Gaps
- I found no 2026 pricing for Hume Octave (Octave 2), PlayHT (status after 2025 is unclear), MiniMax subscription tiers or the Fish Audio API plan, and none of these were checked. Google Chirp 3 HD pricing was not checked either.
- I did not find the controlled-voice (cloning) ranks for most models.
- AA prices come from AA's table. Vendor pages may differ, and Fish's own blog lists $50/1M vs AA's $15.

---

## Q4. Recommendation (budget vs max quality)

### Takeaway
- **Max quality:** ElevenLabs Eleven v4 with a Professional Voice Clone of the narrator (#1-2 on AA, ~$1.08 per 15-min video at list price).
- **Best value API:** Fish Audio Drama 3 API (#6 overall, top open model, ~$0.14 per video at the launch price) or Gemini 3.8 Flash TTS (~$0.22 per video).
- **Best self-hosted and licence-safe:** Fish Drama 3 weights if revenue stays under $500k and a big enough GPU is available. Otherwise Qwen3-TTS 1.7B (Apache, strong long-form consistency) or Higgs TTS 3 (Creator Grant, attribution required).
- Keep Chatterbox Turbo/MIT or Kokoro only as fallbacks.

### Cited Findings
- Rankings, prices and licences are cited in Q1-Q3 above. — [AA leaderboard](https://artificialanalysis.ai/text-to-speech/leaderboard); [Fish blog](https://fish.audio/blog/fish-audio-drama-3/); [Higgs HF](https://huggingface.co/bosonai/higgs-tts-3-4b); [Qwen3-TTS report](https://arxiv.org/html/2601.15621v1)

### Inferences
- **Practical plan:**
  1. Run an A/B test on one 15-minute script with the same reference voice across Drama 3 (API), Eleven v4 (PVC or IVC), Qwen3-TTS 1.7B (Modal A10G) and Higgs TTS 3 (Modal A10G).
  2. Score each with the whisper WER and speaker-similarity QC from Q2, plus a blind listen to minutes 1, 8 and 14 to spot drift.
  3. Choose the API route if WER and drift are comparable, since it is cheaper and faster than Chatterbox on Modal at this volume.
- **Licence watch:**
  - Chatterbox outputs carry the Perth watermark. That is harmless, and arguably useful for AI-disclosure compliance.
  - Higgs requires visible attribution in the description.
  - Drama 3 requires a commercial licence once the business passes $500k revenue.
  - Breeze TTS 2 and the VibeVoice forks should not be used for a monetized channel.

### Gaps
- No hands-on listening tests were done. Final model choice should rest on the A/B above.
