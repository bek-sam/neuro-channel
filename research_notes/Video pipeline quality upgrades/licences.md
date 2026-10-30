# Licence verification: can these models produce videos for a monetized YouTube channel? (as of 2026-10-29)

**This is not legal advice.** These notes are a reading of the licence texts, which were fetched on 2026-10-29 straight from the official Hugging Face repos (`/resolve/main/LICENSE*` and model cards) or the official GitHub repos. Licences change, so re-check the linked file before relying on it. Operator profile assumed: a solo creator, revenue well under US$500k/yr, country unknown.

Verdict legend: **OK** / **OK w/ conditions** / **NOT OK** / **Unclear** / **Unverified**.

## Q1. Image models (Qwen-Image family, FLUX family, ERNIE-Image, HiDream-O1)

### Takeaway
Qwen-Image-2.1 and 2.1-Turbo are **NOT OK**. Both are under the Qwen *Research* Licence, which is non-commercial only. The older Qwen-Image releases (original, Edit-2509, Edit-2511, 2512) are Apache-2.0 and **OK**. FLUX 3 Image Klein is **OK w/ conditions**: you must be under US$5M revenue, run a content filter or review outputs, and add an AI disclosure where the law requires one. FLUX.2 klein-4B is Apache-2.0 and **OK**. FLUX.2 klein-9B and FLUX.2 dev use the FLUX Non-Commercial Licence v2.1, which is **Unclear, leaning NOT OK** for running the model yourself on a monetized channel. ERNIE-Image/Turbo (Apache-2.0) and HiDream-O1-Image (MIT) are **OK**.

### Cited Findings
**Qwen-Image-2.1 / 2.1-Turbo: NOT OK**
- Both repos' cards say `license: other`, `license_name: qwen-research`. The LICENSE files in the two repos are byte-identical. Title: "Qwen RESEARCH LICENSE AGREEMENT Release Date: September 20, 2026" — [Qwen-Image-2.1 LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE); [Qwen-Image-2.1-Turbo LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1-Turbo/blob/main/LICENSE)
- Definition 1(i): "'Non-Commercial' shall mean for research or evaluation purposes only." — [LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE)
- Section 2(a) grants the right "to use, reproduce, distribute, copy, create derivative works of, and make modifications to the Materials FOR NON-COMMERCIAL PURPOSES ONLY." Section 2(b) adds: "You shall not use the Materials for any commercial purpose without obtaining a separate commercial license from us… model-business@notice.qwencloud.com." — [LICENSE](https://huggingface.co/Qwen/Qwen-Image-2.1/blob/main/LICENSE)
- The licence has no separate output carve-out. The model card says: "This model is licensed under the [Qwen Research License Agreement]" — [model card](https://huggingface.co/Qwen/Qwen-Image-2.1)
- Other Qwen-Image-2.1 repos are also `license:other`: Qwen-Image-2.1-PE-T2I and PE-I2I (the prompt enhancers) and lightx2v/Qwen-Image-2.1-Turbo-INT8. One third-party repo, AtomicChat/Qwen-Image-2.1-Turbo-Uncensored-GGUF, is tagged `apache-2.0`, which looks like a mislabel. A third-party re-upload cannot relicense the weights. — [HF API listing](https://huggingface.co/api/models?author=lightx2v)

**Older Qwen-Image releases (original, Edit-2509, Edit-2511, 2512): OK**
- The HF card metadata for each is `license: apache-2.0` — [Qwen-Image](https://huggingface.co/Qwen/Qwen-Image), [Qwen-Image-Edit-2509](https://huggingface.co/Qwen/Qwen-Image-Edit-2509), [Qwen-Image-Edit-2511](https://huggingface.co/Qwen/Qwen-Image-Edit-2511), [Qwen-Image-2512](https://huggingface.co/Qwen/Qwen-Image-2512)
- Apache-2.0 has no field-of-use or revenue limits. If you redistribute the weights, you must keep the licence and NOTICE files. That does not apply to outputs.

**FLUX 3 Image Klein (`black-forest-labs/flux-3-image-klein`, created 2026-10-13): OK w/ conditions**
- Licence: "FLUX Kommunity License v.1.0". The repo is gated with auto-approval. — [LICENSE.md](https://huggingface.co/black-forest-labs/flux-3-image-klein/blob/main/LICENSE.md)
- 1(e): "'Qualifying User' means you, if at any time you together with your affiliates' gross annualized revenue is less than US$5,000,000." — [LICENSE.md](https://huggingface.co/black-forest-labs/flux-3-image-klein/blob/main/LICENSE.md)
- 2(a) grants a "worldwide… license… solely for: (i) your Non-Commercial Purposes…; and (ii) solely if you are a Qualifying User, use Outputs, including Outputs from Derivatives, for commercial purposes, and you may access and use the FLUX Model and Derivatives in a production environment solely for the purpose of generating such Outputs" — [LICENSE.md](https://huggingface.co/black-forest-labs/flux-3-image-klein/blob/main/LICENSE.md)
- 1(d) defines Output as "any result of operating… the FLUX Model… including but not limited to images, audio, video" — [LICENSE.md](https://huggingface.co/black-forest-labs/flux-3-image-klein/blob/main/LICENSE.md)
- Condition 2(e): you must "(i)(A) implement and maintain content filtering measures… or (B) ensure Output undergoes review for unlawful or infringing content before public… distribution…; and (ii) ensure Output includes disclosures… that the Output was generated or modified using artificial intelligence technologies to the extent required under applicable law." — [LICENSE.md](https://huggingface.co/black-forest-labs/flux-3-image-klein/blob/main/LICENSE.md)
- Restrictions §4 cover: military, surveillance, biometric processing, violating "rights of publicity or 'digital replica' rights", CSAM/NCII, and breaches of GDPR, CCPA or the EU AI Act. §4(b) bans using Outputs to improve competing models. §4(g) bars use "if you or they are (a) located in a comprehensively sanctioned jurisdiction" and says you "will not disguise your location through IP proxying". There is **no EU/UK/US/Korea exclusion**. — [LICENSE.md](https://huggingface.co/black-forest-labs/flux-3-image-klein/blob/main/LICENSE.md)
- The model card summary: "non-commercial use, plus commercial output generation by Qualifying Users with less than US$5M in gross annualized revenue." Its text encoder (Qwen3-VL-4B-Instruct) is "under Apache-2.0". — [model card](https://huggingface.co/black-forest-labs/flux-3-image-klein)
- The repo NOTICE.md returned HTTP 401 to an unauthenticated fetch because the repo is gated, so it is **unverified**. The `flux-3-image-klein-base` and `-comfy` repos are also tagged `license:other`. The `flux-3-image-klein-pup` repo is tagged `apache-2.0`; its scope was not checked. — [HF API](https://huggingface.co/api/models?author=black-forest-labs)

**FLUX.2 klein-4B: OK**
- The repo LICENSE.md is the Apache License 2.0, and the card says `license: apache-2.0`. The repo is not gated. — [FLUX.2-klein-4B LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-klein-4B/blob/main/LICENSE.md)

**FLUX.2 klein-9B and FLUX.2 dev: Unclear, leaning NOT OK for a monetized channel**
- Both repos ship the same "FLUX Non-Commercial License v2.1" (the two LICENSE.md files are byte-identical). The gate text: "By clicking 'Agree', you agree to the FLUX Non-Commercial License Agreement". — [FLUX.2-klein-9B LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-klein-9B/blob/main/LICENSE.md); [FLUX.2-dev LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md)
- 2(a) grants a licence to "access, use, create Derivatives of, and Distribute the FLUX Model… solely for your Non-Commercial Purposes." — [LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md)
- 1(c) defines Non-Commercial Purpose as applying "only so far as you do not receive any direct or indirect payment arising from the use of the FLUX Model… For clarity, use (a) for revenue-generating activity, (b) in direct interactions with or that has impact on end users… is not a Non-Commercial Purpose." — [LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md)
- But 2(d) also says: "You may use Output for any purpose (including for commercial purposes), except as expressly prohibited herein. You may not use the Output to train, fine-tune, or distill a model that is competitive with a FLUX Model." — [LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md)
- 2(e) has the same content-filter/review and AI-disclosure conditions as the Kommunity licence. — [LICENSE.md](https://huggingface.co/black-forest-labs/FLUX.2-dev/blob/main/LICENSE.md)

**ERNIE-Image / ERNIE-Image-Turbo: OK**
- The repo LICENSE is the Apache License 2.0, and both cards say `license: apache-2.0`. — [baidu/ERNIE-Image LICENSE](https://huggingface.co/baidu/ERNIE-Image/blob/main/LICENSE); [baidu/ERNIE-Image-Turbo](https://huggingface.co/baidu/ERNIE-Image-Turbo)

**HiDream-O1-Image: OK (MIT), with one caveat about the optional prompt agent**
- Model card: "The code in this repository and the HiDream-O1-Image models are licensed under MIT License." — [model card](https://huggingface.co/HiDream-ai/HiDream-O1-Image)
- The repo has no separate LICENSE file (HTTP 404), so the card's statement is the primary text.
- The optional local "Prompt Agent" uses google/gemma-4-31B-it, which "requires accepting the Gemma license". That is a separate licence and only matters if you use the agent. — [model card](https://huggingface.co/HiDream-ai/HiDream-O1-Image)

### Inferences
- **On the question "does running FLUX.2-dev / klein-9B locally for a monetized channel count as commercial use?"** On the text, yes, most likely. The grant in 2(a) covers *using the model* only for Non-Commercial Purposes, and 1(c) excludes "revenue-generating activity" and any use where you get "direct or indirect payment arising from the use of the FLUX Model". A monetized channel earns money indirectly from the generated images. The 2(d) clause lets you use Output commercially, but you only hold Output lawfully if you generated it under the 2(a) grant. One reading is "outputs are free to use however you like". The other is "the outputs clause covers outputs made during permitted non-commercial use, such as a hobby image you later sell". The text supports both readings, so the verdict is Unclear and the safe course is to avoid it.
- BFL's release of a separate Kommunity licence that *explicitly* adds "commercial output generation by Qualifying Users" suggests BFL does not think the Non-Commercial licence already allowed that. This is an inference, not a BFL statement.
- Practical answer: use FLUX.2 klein-4B (Apache-2.0) or FLUX 3 Image Klein (Kommunity, under $5M) instead of klein-9B or dev. Alternatively, buy a BFL commercial licence at https://bfl.ai/licensing.
- If you use FLUX 3 Klein, meeting 2(e) is cheap for a solo channel: review each image by hand before publishing, and use YouTube's "altered or synthetic content" disclosure where it applies.

### Gaps
- FLUX 3 Image Klein NOTICE.md: not readable because the repo is gated (401).
- No primary BFL FAQ or clarification on FLUX.2 NC outputs was located. BFL's licensing page (bfl.ai/licensing) was not fetched.
- ERNIE-Image's Prompt Enhancer and text-encoder sub-licences were not checked separately. The repo-level licence is Apache-2.0.

## Q2. Video models (Wan2.2 + lightx2v, LTX-2.5, MiniMax H3, Kandinsky 6)

### Takeaway
Wan2.2 and the lightx2v Wan2.2 distills (Apache-2.0) are **OK**. LTX-2.5 is **OK w/ conditions**: under US$10M revenue, and you must not strip any watermarking, provenance or disclosure features. MiniMax H3 open weights are **NOT OK** if you are in the EU, UK, South Korea or US. Elsewhere it is **Unclear, high risk**: the licence also bans *displaying* Outputs outside the permitted territory, and a public YouTube video is shown in all four excluded regions. Kandinsky 6 (MIT) is **OK**.

### Cited Findings
**Wan2.2: OK**
- The GitHub LICENSE.txt is the Apache License 2.0. — [Wan-Video/Wan2.2 LICENSE.txt](https://github.com/Wan-Video/Wan2.2/blob/main/LICENSE.txt)
- Model card: "The models in this repository are licensed under the Apache 2.0 License. We claim no rights over the your generated contents, granting you the freedom to use them while ensuring that your usage complies with the provisions of this license. You are fully accountable for your use of the models, which must not involve sharing any content that violates applicable laws, causes harm…" — [Wan2.2-T2V-A14B card](https://huggingface.co/Wan-AI/Wan2.2-T2V-A14B)

**lightx2v Wan2.2 4-step distills: OK**
- `lightx2v/Wan2.2-Lightning` and `lightx2v/Wan2.2-Distill-Models` both have card metadata `license: apache-2.0`. The Distill card shows an Apache 2.0 badge. — [Wan2.2-Lightning](https://huggingface.co/lightx2v/Wan2.2-Lightning); [Wan2.2-Distill-Models](https://huggingface.co/lightx2v/Wan2.2-Distill-Models)
- Note: lightx2v's *other* distills follow their base model's licence. Qwen-Image-2.1-Turbo-INT8 is `license:other`, and Minimax-h3-Turbo has no licence tag. — [HF API](https://huggingface.co/api/models?author=lightx2v)

**LTX-2.5 (Lightricks): OK w/ conditions; revenue threshold US$10M**
- The card links its licence to `ltx-2.x-community-license-agreement` → https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x. The repo is gated with auto-approval. The gate asks you to accept the privacy policy and consent to marketing. — [LTX-2.5 card](https://huggingface.co/Lightricks/LTX-2.5)
- The licence is "LTX-2.x Community License Agreement, License date: August 11, 2026". — [LICENSE-2_x](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x)
- §2.1 grants a "worldwide… license… to use, reproduce… LTX-2.x, for any purpose, subject to the restrictions set forth in Attachment A; provided however, that Entities with annual revenues of at least $10,000,000 (the 'Commercial Entities') are required to obtain a paid license" — [LICENSE-2_x](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x)
- The card summary: "Under $10M annual revenue — Commercial and production use at no cost under the LTX-2.x Community License." — [LTX-2.5 card](https://huggingface.co/Lightricks/LTX-2.5)
- §5: "Licensor claims no rights in the Output you generate… No use of the Output can contravene any provision as stated in the Agreement." — [LICENSE-2_x](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x)
- §6 requires compliance with the EU AI Act and the California AI Transparency Act. It also says: "You shall maintain… and shall not remove, disable, alter, or circumvent, any safety or security measures, disclosures, metadata, watermarking, content provenance, latent disclosure, or other transparency features… applied to any Output". It adds: "Licensor reserves the right to… modify the Output of LTX-2.x based on updates. You shall undertake reasonable efforts to use the latest version". — [LICENSE-2_x](https://github.com/Lightricks/LTX-2/blob/main/LICENSE-2_x)
- No territorial exclusion was found in LICENSE-2_x.
- Lightricks published an MIT-licensed `Lightricks/LTX-2-Marking` repo on 2026-10-28. It is probably the watermark/provenance tool the §6 clause refers to, but its contents were not checked. — [HF API](https://huggingface.co/api/models?author=Lightricks)

**MiniMax H3 open weights: NOT OK in the US/EU/UK/South Korea; Unclear elsewhere**
- "MiniMax H3 COMMUNITY LICENSE AGREEMENT… License date: August 2, 2026." The opening says: "The scope of this License Agreement… is expressly limited to the 'Applicable Territory'". — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- Defs 3 and 5: "'Applicable Territory' means worldwide, excluding the Excluded Territories." "'Excluded Territories' means the European Union, the United Kingdom, the Republic of Korea and the United States of America." — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- The grant applies "Solely within the Applicable Territory". — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- §V.4: "You may not use, reproduce, modify, distribute, or display the MiniMax H3 Works **or any of their Outputs** or results outside the Applicable Territory." AUP item 1 bans "Use outside the Applicable Territory". — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- Revenue: §IV.1 requires prior written authorization "if your commercial products and services generate more than 20 million US dollars… in yearly revenue". §IV.2: "You shall prominently display 'MiniMax H3' on the user interface of commercial product or service that uses MiniMax H3". — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- AUP item 12 bans use "to generate or disseminate information (including images…) in or to any public environment… without clearly and prominently disclosing that such information and/or content is machine-generated". Item 8 bans "false online engagement". Item 15 bans use that "violates or disregards the social, ethical, or moral standards of other countries or regions". — [LICENSE](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/LICENSE)
- The official Q&A explains the exclusion with regulatory uncertainty, adding: "MiniMax is also involved in ongoing copyright-related legal proceedings specifically concerning generative video AI". It says "The current limitation means 'not yet', not 'not ever.'" and that the API is "Globally available". It also says organisations in restricted regions "can apply for a formal license" via https://platform.minimax.io/h3-license. — [docs/QA-about-License.md](https://huggingface.co/MiniMaxAI/MiniMax-H3/blob/main/docs/QA-about-License.md)

**Kandinsky 6: OK**
- The cards for every Kandinsky-6.0 Pro/Lite (distill, pretrain, VSR) Diffusers repo say `license: mit`. — [Kandinsky-6.0-Pro-5s-Diffusers](https://huggingface.co/kandinskylab/Kandinsky-6.0-Pro-5s-Diffusers)
- The GitHub LICENSE is "The MIT License (MIT) Copyright (c) 2026 Kandinsky Lab". — [kandinskylab/kandinsky-6 LICENSE](https://github.com/kandinskylab/kandinsky-6/blob/main/LICENSE)
- It uses a Qwen2.5-VL text encoder (per the card). — [model card](https://huggingface.co/kandinskylab/Kandinsky-6.0-Pro-5s-Diffusers)

### Inferences
- For MiniMax H3, even a creator living in a permitted country is in a weak position. A public, monetized YouTube video is *displayed* in the US, EU, UK and Korea, which on a literal reading of §V.4 breaches the licence. To use H3 safely, either use the MiniMax API (governed by separate API terms, not reviewed here) or apply for the formal licence. Geo-blocking a channel from the US and EU is not a realistic fix.
- With LTX-2.5, do not run tools that strip watermarks or C2PA data, and keep the inference stack up to date (the §6 "reasonable efforts to use the latest version" clause). If you re-encode in a way that drops embedded provenance metadata, that could arguably count as "remove… metadata"; plain transcoding is ambiguous.
- Kandinsky 6's text encoder: Qwen2.5-VL-7B is Apache-2.0, but Qwen2.5-VL-3B shipped under the Qwen Research licence. The size used could not be confirmed (see Gaps).

### Gaps
- LTX-2.x "Attachment A" use restrictions were not quoted in full. Lines 158–164 of the licence confirm Attachment A is binding.
- The Kandinsky 6 text_encoder/config.json could not be fetched because the repo is gated, so the encoder size, and therefore its licence, is **unverified**.
- MiniMax API terms of service and the separate lightx2v/Minimax-h3-Turbo repo (no licence tag) were not reviewed.

## Q3. Voice/TTS models (Fish Audio Drama 3, Higgs TTS 3, Qwen3-TTS, Chatterbox, Kokoro)

### Takeaway
Fish Audio Drama 3 is **OK w/ conditions**. The binding LICENSE file is the *Community* Licence v1.0, despite a stale "research" label in the card metadata. Conditions: total revenue under US$500k from all sources, a "Built with Fish Audio" credit, no cloning without consent, and no watermark removal. Higgs TTS 3 is **OK w/ conditions** under its Creator Use Grant; the one hard requirement is a prominent credit to "Boson AI's Higgs Audio". Qwen3-TTS (Apache-2.0), Chatterbox (MIT, with a built-in PerTh watermark but no licence duty to keep it) and Kokoro (Apache-2.0) are **OK**.

### Cited Findings
**Fish Audio Drama 3: OK w/ conditions**
- **Label mismatch:** the card YAML says `license_name: fish-audio-research-license`, `license_link: LICENSE.md`. But the README body says "licensed under the [Fish Audio Community License](…/LICENSE)". The actual LICENSE file is titled "FISH AUDIO COMMUNITY LICENSE AGREEMENT Version 1.0 — Last Updated: October 13, 2026". No LICENSE.md exists; the only licence file is `LICENSE`. — [drama-3 card](https://huggingface.co/fishaudio/drama-3); [drama-3 LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- The licence's own definitions separate the two: "Model weights that Fish Audio makes available under a different license (for example, the Fish Audio S2-Pro weights under the Fish Audio Research License) are not Fish Audio Materials". It names "Fish Audio Drama 3" as a covered Model. — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- III(a) grants a licence "for a Commercial Purpose, but only while Your Annual Revenue is less than USD 500,000 (the 'Revenue Threshold')". Annual Revenue means "the total gross revenue of You and Your Affiliates… from all sources (whether or not derived from the Fish Audio Materials…)". — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- III(b): when you reach the threshold, notify business@fish.audio within 30 days. You then have a 90-day transition period, after which you need a separate licence. — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- III(c): Hosted Services are not licensed. But "None of the following is a Hosted Service: (1) generating speech for content that You create, select, or control… (for example, narration, dubbing…)". — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- IV(a): "If You distribute or make available… a product or service that uses any portion of them, You shall prominently display 'Built with Fish Audio' on a related website, user interface, blogpost, about page, or product documentation." — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- IV(b) bans generating "speech that imitates the voice of an identifiable natural person without that person's prior consent". It also bans: "(iv) intentionally remove, disable, circumvent, or obscure any watermark or provenance signal… (ordinary editing, mixing, compression, or format conversion… is not a breach)". You may not use outputs to train other speech models. — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- Ownership: "You own any outputs generated from the Models… to the extent permitted by applicable law." — [LICENSE](https://huggingface.co/fishaudio/drama-3/blob/main/LICENSE)
- No territorial exclusion was found; the grant is "worldwide".

**Higgs TTS 3 (bosonai/higgs-tts-3-4b): OK w/ conditions (Creator Use Grant)**
- The licence is titled "BOSON HIGGS TTS 3 RESEARCH AND NON-COMMERCIAL LICENSE AGREEMENT, Last Updated: July 8, 2026". — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- Intro: "Boson also grants digital creators a free, royalty-free license to create and publish creative content using the Higgs Materials, including monetized creative content, subject to an attribution requirement, as set forth in Section II-A". — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- II-A(a): "This grant covers using the Higgs Materials to generate audio for creative works — including podcasts, videos, audiobooks… and publishing and monetizing that content on channels You own or control… including ad-supported, sponsored, subscription, or otherwise monetized creator channels." — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- II-A(b), "Creator Acknowledgment (the one requirement)": you must credit Higgs Audio either "(i) In the audio itself" or "(ii) In the accompanying text, displayed prominently together with the content — such as… video description… must not be hidden or buried at the bottom of the credits". The suggested string: "This audio was created with Boson AI's Higgs Audio — https://www.boson.ai/higgs-audio". — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- II-A(c) excludes hosting or an API, redistributing or reselling the model, and embedding it in third-party products. — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- IV(b)(vii) bans public-facing synthetic content "without clear and conspicuous disclosure that the content is AI-generated… where required by law or where a reasonable person would otherwise be misled". IV(b)(viii) bans removing any "watermark, provenance signal". There is no revenue cap in the grant. You must not be in a comprehensively US-sanctioned country (IV(c)). — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- Termination does not force a creator to take down content that was published compliantly. — [LICENSE](https://huggingface.co/bosonai/higgs-tts-3-4b/blob/main/LICENSE)
- The card confirms: "Free for digital creators — including monetized content… The one requirement is to credit Boson AI's Higgs Audio". — [model card](https://huggingface.co/bosonai/higgs-tts-3-4b)
- Note: the brief's name "Higgs Audio V3" corresponds to the repo `bosonai/higgs-tts-3-4b`. The `higgs-audio-v3-*-stt` repos are speech-to-text models under Apache-2.0. — [HF API](https://huggingface.co/api/models?author=bosonai)

**Qwen3-TTS: OK**
- All official Qwen3-TTS-12Hz repos (0.6B/1.7B Base, CustomVoice, VoiceDesign, and the Tokenizer) say `license: apache-2.0`. — [Qwen3-TTS-12Hz-1.7B-Base](https://huggingface.co/Qwen/Qwen3-TTS-12Hz-1.7B-Base)

**Chatterbox (Resemble AI): OK**
- The GitHub LICENSE is "MIT License Copyright (c) 2025 Resemble AI". The HF chatterbox, chatterbox-turbo and multilingual repos are all `license: mit`. — [LICENSE](https://github.com/resemble-ai/chatterbox/blob/master/LICENSE); [HF](https://huggingface.co/ResembleAI/chatterbox)
- README: "Every audio file generated by Chatterbox includes Resemble AI's Perth (Perceptual Threshold) Watermarker… imperceptible neural watermarks that survive MP3 compression". The disclaimer says: "Don't use this model to do bad things." — [README](https://github.com/resemble-ai/chatterbox/blob/master/README.md)
- Exception: `ResembleAI/Dramabox` is `license:other`, so it is not covered by this verdict. — [HF API](https://huggingface.co/api/models?author=ResembleAI)

**Kokoro-82M: OK**
- Card: `license: apache-2.0`. It says: "With Apache-licensed weights, Kokoro can be deployed anywhere from production environments to personal projects… deployed in numerous projects and commercial APIs." — [hexgrad/Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M)

### Inferences
- For a YouTube channel, satisfy the Fish "Built with Fish Audio" requirement with a line in the video description or the channel About page. Whether a channel counts as "a product or service" is debatable, but the credit costs nothing.
- The Fish US$500k cap counts *all* revenue of you and your affiliates, not just channel income. A solo creator's day-job salary is arguably not "Your… gross revenue"; that is ambiguous for individuals.
- The Chatterbox watermark is a technical feature, not a licence obligation, because MIT imposes no such duty. Leaving it in is still sensible, since YouTube and other platforms may use such signals.

### Gaps
- The full text of Fish III(a) on contractors/integrators was truncated in extraction. It is not relevant to a solo creator.
- No standalone LICENSE file was fetched for Qwen3-TTS or Kokoro; the verdicts rely on the card metadata and card text.

## Q4. Music/SFX models (ACE-Step 1.5 / XL, Stable Audio Open, HunyuanVideo-Foley)

### Takeaway
ACE-Step 1.5 and the XL variants (MIT) are **OK**. Stable Audio Open 1.0 and Small are **OK w/ conditions**: under US$1M revenue, *registration* with Stability for commercial use, and a "Powered by Stability AI" credit. HunyuanVideo-Foley is **NOT OK** in the EU, UK or South Korea. Elsewhere it is **Unclear, high risk**, because the licence bans displaying Output outside its territory and YouTube shows it there.

### Cited Findings
**ACE-Step 1.5 / XL: OK**
- The GitHub LICENSE is "MIT License Copyright (c) 2026 ACEStep". The HF repos `ACE-Step/Ace-Step1.5`, `acestep-v15-xl-base/sft/turbo` and the 5Hz LMs are all `license: mit`. — [ACE-Step-1.5 LICENSE](https://github.com/ace-step/ACE-Step-1.5/blob/main/LICENSE); [HF](https://huggingface.co/ACE-Step/Ace-Step1.5)
- Caution: the community repo "mdmachine/ACEStep-XL-Regrind-V1" is CC-BY-NC-SA-4.0, and the "ACE-Step-v1.5-chinese-new-year-LoRA" is under creativeml-openrail-m. Fine-tunes carry their own licences. — [HF search](https://huggingface.co/api/models?search=ACE-Step)

**Stable Audio Open 1.0 / Small: OK w/ conditions**
- The licence is "STABILITY AI COMMUNITY LICENSE AGREEMENT Last Updated: July 5, 2024". The repo is gated. — [LICENSE.md](https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md)
- "If You are using or distributing the Stability AI Materials for a Commercial Purpose, You must register with Stability AI at (https://stability.ai/community-license). If at any time You or Your Affiliate(s)… generate more than USD $1,000,000 in annual revenue… any licenses granted to You under this Agreement shall terminate". — [LICENSE.md](https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md)
- Attribution: "If You distribute or make available… a product or service that uses any portion of them, You shall… (iii) prominently display 'Powered by Stability AI' on a related website, user interface, blogpost, about page, or product documentation." — [LICENSE.md](https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md)
- "You own any outputs generated from the Models". You may not use outputs to "create or improve any foundational generative AI model". Use must follow the Stability AUP. — [LICENSE.md](https://huggingface.co/stabilityai/stable-audio-open-1.0/blob/main/LICENSE.md)
- Stable Audio Open Small is also `license_name: stability-ai-community`. — [HF](https://huggingface.co/stabilityai/stable-audio-open-small)

**HunyuanVideo-Foley: NOT OK in the EU/UK/South Korea; Unclear elsewhere**
- The licence is "TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT, Tencent HunyuanVideo-Foley Release Date: August 28, 2025". It opens: "THIS LICENSE AGREEMENT DOES NOT APPLY IN THE EUROPEAN UNION, UNITED KINGDOM AND SOUTH KOREA AND IS EXPRESSLY LIMITED TO THE TERRITORY". — [LICENSE](https://huggingface.co/tencent/HunyuanVideo-Foley/blob/main/LICENSE)
- 1(l): "'Territory' shall mean the worldwide territory, excluding the territory of the European Union, United Kingdom and South Korea." — [LICENSE](https://huggingface.co/tencent/HunyuanVideo-Foley/blob/main/LICENSE)
- §5(c): "You must not use, reproduce, modify, distribute, or display the Tencent Hunyuan Works, Output or results of the Tencent Hunyuan Works outside the Territory." — [LICENSE](https://huggingface.co/tencent/HunyuanVideo-Foley/blob/main/LICENSE)
- The 100M-MAU threshold for needing a separate licence does not apply here. The licence says "You are encouraged to… mark… 'Powered by Tencent Hunyuan'"; this is encouraged, not required. — [LICENSE](https://huggingface.co/tencent/HunyuanVideo-Foley/blob/main/LICENSE)
- The US is **not** excluded under this licence, unlike MiniMax H3.

### Inferences
- Stable Audio Open is technically "OK w/ conditions", but the free registration step is easy to miss. Do it before the first monetized upload.
- HunyuanVideo-Foley carries the same YouTube display problem as MiniMax H3, but the excluded regions are only the EU, UK and South Korea. Monetized YouTube videos can be viewed in the EU and UK, so audio generated with Foley is shown "outside the Territory".

### Gaps
- The Stability AUP and the Tencent AUP were not quoted.
- It was not checked whether the stable-audio-open-small LICENSE text is identical to the 1.0 version.

## Q5. Upscaling and interpolation (FlashVSR, SeedVR2, RIFE, GIMM-VFI)

### Takeaway
FlashVSR and SeedVR2 (Apache-2.0) are **OK**, and so is RIFE (MIT). **GIMM-VFI is NOT OK.** Its code licence is the S-Lab License 1.0, which allows non-commercial use only.

### Cited Findings
- **FlashVSR:** the GitHub LICENSE is the Apache License 2.0. HF `JunhaoZhuang/FlashVSR` and `FlashVSR-v1.1` are `license: apache-2.0`. — [OpenImagingLab/FlashVSR LICENSE](https://github.com/OpenImagingLab/FlashVSR/blob/main/LICENSE); [HF FlashVSR-v1.1](https://huggingface.co/JunhaoZhuang/FlashVSR-v1.1)
- **SeedVR2:** the GitHub LICENSE is the Apache License 2.0. HF `ByteDance-Seed/SeedVR2-3B` and `-7B` are `license: apache-2.0`. — [ByteDance-Seed/SeedVR LICENSE](https://github.com/ByteDance-Seed/SeedVR/blob/main/LICENSE); [HF SeedVR2-7B](https://huggingface.co/ByteDance-Seed/SeedVR2-7B)
- **RIFE:** the ECCV2022-RIFE LICENSE is "MIT License Copyright (c) Megvii Inc.". The Practical-RIFE LICENSE is "MIT License Copyright (c) 2021 hzwer". — [ECCV2022-RIFE LICENSE](https://github.com/hzwer/ECCV2022-RIFE/blob/main/LICENSE); [Practical-RIFE LICENSE](https://github.com/hzwer/Practical-RIFE/blob/main/LICENSE)
- **GIMM-VFI:** "S-Lab License 1.0 Copyright 2024 S-Lab. Redistribution and use for non-commercial purpose in source and binary forms… are permitted… In the event that redistribution and/or use for commercial purpose… is required, please contact the contributor(s) of the work." — [GSeanCDAT/GIMM-VFI LICENSE](https://github.com/GSeanCDAT/GIMM-VFI/blob/main/LICENSE)

### Inferences
- Use RIFE (Practical-RIFE) for frame interpolation instead of GIMM-VFI. GIMM-VFI is only usable with a commercial licence negotiated with the authors.
- FlashVSR builds on Wan-family components, which are Apache-2.0, so no inherited restriction is expected. This was not separately verified.

### Gaps
- No official HF weight repo for GIMM-VFI was found. Released weights could have their own licence; it is assumed the code licence covers them.
- RIFE's model-weights download (Google Drive) licence was not separately confirmed.

---

## Summary table (for the report writer)

| Model | Licence (primary text) | Verdict | Conditions / notes | Geo exclusions |
|---|---|---|---|---|
| Qwen-Image-2.1 / 2.1-Turbo | Qwen Research License (2026-09-20) | **NOT OK** | Non-commercial = "research or evaluation purposes only"; commercial licence via model-business@notice.qwencloud.com | none (Chinese law, Hangzhou courts) |
| Qwen-Image / Edit-2509 / Edit-2511 / 2512 | Apache-2.0 (card metadata) | **OK** | — | none |
| FLUX 3 Image Klein | FLUX Kommunity License v1.0 | **OK w/ conditions** | <US$5M gross revenue (incl. affiliates); content filter OR human review before publishing; AI disclosure where law requires; no publicity/"digital replica" violations | sanctioned jurisdictions only; no VPN masking |
| FLUX.2 klein-4B | Apache-2.0 | **OK** | — | none |
| FLUX.2 klein-9B, FLUX.2 dev | FLUX Non-Commercial License v2.1 | **Unclear → treat as NOT OK** | Model use limited to Non-Commercial Purposes, which exclude "revenue-generating activity"; Output clause 2(d) conflicts | sanctions |
| ERNIE-Image / Turbo | Apache-2.0 | **OK** | — | none |
| HiDream-O1-Image | MIT (card) | **OK** | Optional Gemma prompt agent has its own licence | none |
| Wan2.2 | Apache-2.0 | **OK** | Card: lawful use, no harmful content | none |
| lightx2v Wan2.2 distills | Apache-2.0 | **OK** | — | none |
| LTX-2.5 | LTX-2.x Community License (2026-08-11) | **OK w/ conditions** | <US$10M annual revenue; don't strip watermark/metadata/provenance; comply with EU AI Act and CA AI Transparency Act; keep version current; Attachment A restrictions | none found |
| MiniMax H3 (open weights) | MiniMax H3 Community License (2026-08-02) | **NOT OK** in US/EU/UK/KR; **Unclear (high risk)** elsewhere | Display of Outputs outside the territory is prohibited (YouTube is global); machine-generated disclosure required; >US$20M needs authorisation | **US, EU, UK, South Korea excluded** |
| Kandinsky 6 | MIT | **OK** | Text-encoder (Qwen2.5-VL) size unverified | none |
| Fish Audio Drama 3 | Fish Audio Community License v1.0 (2026-10-13); card YAML wrongly says "research" | **OK w/ conditions** | Total revenue <US$500k; notify at threshold; "Built with Fish Audio" credit; no voice cloning without consent; don't remove watermark | none |
| Higgs TTS 3 (4B) | Boson Higgs TTS 3 Research & NC License + Creator Use Grant (2026-07-08) | **OK w/ conditions** | Prominent credit "Boson AI's Higgs Audio" in audio or video description; AI disclosure where required; no cloning without consent; no hosting or redistribution | US-sanctioned countries |
| Qwen3-TTS | Apache-2.0 | **OK** | — | none |
| Chatterbox | MIT | **OK** | PerTh watermark built in (not a licence duty) | none |
| Kokoro-82M | Apache-2.0 | **OK** | — | none |
| ACE-Step 1.5 / XL | MIT | **OK** | Check fine-tune/LoRA licences separately | none |
| Stable Audio Open 1.0 / Small | Stability AI Community License (2024-07-05) | **OK w/ conditions** | **Register** at stability.ai/community-license; <US$1M revenue; "Powered by Stability AI" credit | none |
| HunyuanVideo-Foley | Tencent Hunyuan Community License (2025-08-28) | **NOT OK** in EU/UK/KR; **Unclear (high risk)** elsewhere | Display of Output outside the territory is prohibited | **EU, UK, South Korea excluded** |
| FlashVSR | Apache-2.0 | **OK** | — | none |
| SeedVR2 | Apache-2.0 | **OK** | — | none |
| RIFE / Practical-RIFE | MIT | **OK** | — | none |
| GIMM-VFI | S-Lab License 1.0 | **NOT OK** | Non-commercial only; contact authors | none |
