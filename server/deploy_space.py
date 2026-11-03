"""Deploys the MCP server to a free Hugging Face Space (CPU basic) and sets its secrets from keys/keys.env.
    python server/deploy_space.py [space-name]        (default: <your HF user>/video-mcp)
Creates MCP_TOKEN in keys/keys.env if missing, and prints the connector URL to paste into Claude."""
import os, sys, secrets
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ENV = f"{ROOT}/keys/keys.env"
env = dict(l.strip().split("=", 1) for l in open(ENV) if "=" in l and not l.startswith("#"))
if not env.get("MCP_TOKEN"):
    env["MCP_TOKEN"] = secrets.token_urlsafe(32)
    with open(ENV, "a") as f: f.write(f"\nMCP_TOKEN={env['MCP_TOKEN']}\n")
from huggingface_hub import HfApi
api = HfApi(token=env["HF_TOKEN"])
space = sys.argv[1] if len(sys.argv) > 1 else f"{api.whoami()['name']}/video-mcp"
api.create_repo(space, repo_type="space", space_sdk="docker", private=False, exist_ok=True)
for k in ("HF_TOKEN", "MCP_TOKEN", "GH_DISPATCH_TOKEN"):
    if env.get(k): api.add_space_secret(space, k, env[k])
api.add_space_variable(space, "HF_REPO", env.get("HF_REPO", "bekbol446/neuro-channel"))
api.add_space_variable(space, "GH_REPO", env.get("GH_REPO", "bek-sam/neuro-channel"))
d = os.path.dirname(os.path.abspath(__file__))
for f, dst in [("space/README.md", "README.md"), ("Dockerfile", "Dockerfile"), ("requirements.txt", "requirements.txt"), ("mcp_server.py", "mcp_server.py")]:
    api.upload_file(path_or_fileobj=f"{d}/{f}", path_in_repo=dst, repo_id=space, repo_type="space")
host = space.replace("/", "-").replace("_", "-").lower()
print(f"deployed: https://huggingface.co/spaces/{space}")
print(f"health:   https://{host}.hf.space/health")
print(f"connector URL (keep it private, it contains the token): https://{host}.hf.space/<MCP_TOKEN from keys/keys.env>/mcp")
