#!/bin/bash
# Runs the MCP server on a Linux VM (e.g. Oracle Cloud Always Free) with Docker, on port 7860.
# Put HF_TOKEN, MCP_TOKEN and optional GH_DISPATCH_TOKEN in ~/video-mcp.env first. Put HTTPS in front (Caddy) for Claude.
set -euo pipefail
cd "$(dirname "$0")"
docker build -t video-mcp .
docker rm -f video-mcp 2>/dev/null || true
docker run -d --name video-mcp --restart unless-stopped --env-file ~/video-mcp.env -p 7860:7860 video-mcp
sleep 3; curl -s localhost:7860/health
