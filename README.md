# Free video generator

Makes finished 1920×1080 videos from a script with open-source models, running on free GPU providers.
Connect it to Claude as an MCP server, ask for a video, and Claude writes the scenes and starts the render.

| Part | Model | Runs on (free) | Fallback |
|---|---|---|---|
| Images | Z-Image-Turbo | Kaggle T4 ×2 | Hugging Face ZeroGPU Space, FLUX.2 klein Space |
| Motion clips | Wan2.2 / LTX-2.3 image-to-video | Hugging Face ZeroGPU Spaces (3) | Modal H100 Wan2.2 14B (free $30/month credit), then Muapi Kling/Veo/Seedance (paid, capped), then a slow camera move |
| Voice | edge-tts or Qwen3-TTS | GitHub Actions runner / ZeroGPU Space | the other one |
| Voice check | faster-whisper | GitHub Actions runner | lines it mishears are made again |
| Edit | ffmpeg (32 fps, 1080p, music, subtitles, −14 LUFS) | GitHub Actions runner | any machine with Python |

State lives in a Hugging Face dataset, so any machine resumes where the last one stopped. When a provider runs out of
free quota the video waits, and the cron in `.github/workflows/video.yml` finishes it every 6 hours.
Details and measured timings: [`code/free/README.md`](code/free/README.md).

## Setup (once)

1. Fork this repo. Create a private Hugging Face dataset for your videos, and get a Hugging Face token with write
   access to it and a Kaggle API token.
2. Put them in `keys/keys.env` (gitignored):
   ```
   HF_TOKEN=...
   KAGGLE_API_TOKEN=...
   HF_REPO=<you>/<dataset>
   # optional, more motion clips:
   # Modal (then once: modal deploy code/free/modal_clip.py)
   MODAL_TOKEN_ID=...
   MODAL_TOKEN_SECRET=...
   # Muapi, paid; MUAPI_MONTHLY_USD caps it (default 5, 0 = off)
   MUAPI_API_KEY=...
   ```
3. `bash scripts/cloud_setup.sh` stores them as encrypted GitHub Actions secrets (edit `R=` in it to your fork).

## Connect it to Claude

The server is [`server/mcp_server.py`](server/mcp_server.py). Tools: `how_to_write_scenes`, `create_video`,
`get_status`, `list_videos`, `get_video`.

**Locally** (Claude Code or Claude Desktop):
```
pip install -r server/requirements.txt
claude mcp add video -- python /path/to/repo/server/mcp_server.py
```
For Claude Desktop, add the same command to `claude_desktop_config.json` under `mcpServers`.

**In the cloud** (free), then add it in claude.ai under Settings → Connectors → Add custom connector:
- **Hugging Face Space** (free CPU): `python server/deploy_space.py` creates the Space, sets its secrets and prints
  the connector URL `https://<space>.hf.space/<MCP_TOKEN>/mcp`.
- **Oracle Cloud Always Free VM** or any Linux host with Docker: copy `server/`, put the keys in `~/video-mcp.env`,
  run `server/start_vm.sh`, and put HTTPS in front of port 7860 (Caddy does it in one line).

Without `GH_DISPATCH_TOKEN` a new video is queued and the next cron run starts it. To start renders at once, make a
fine-grained GitHub token for your fork with **Actions: Read and write** and add it as `GH_DISPATCH_TOKEN`.

Then ask Claude: *"Make a 5-minute video about why we can't stop scrolling."*

## Other parts

- `code/gpu/`: the first version on Modal GPUs (faster, not free), with its own MCP server.
- `research/`, `reports/`: notes on models, licences and free providers.
