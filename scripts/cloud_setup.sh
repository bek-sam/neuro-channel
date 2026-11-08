#!/bin/bash
# One-time: gives the GitHub Actions workflow (.github/workflows/video.yml) the keys it needs to run videos in the cloud.
# Values are read from keys/keys.env and sent only to GitHub's encrypted secret store (never printed).
set -euo pipefail
cd "$(dirname "$0")/.."
set -a; . keys/keys.env; set +a
R=bek-sam/neuro-channel
printf '%s' "$HF_TOKEN" | gh secret set HF_TOKEN -R $R
printf '%s' "$KAGGLE_API_TOKEN" | gh secret set KAGGLE_API_TOKEN -R $R
for k in CF_ACCOUNT_ID CF_API_TOKEN GEMINI_API_KEY MODAL_TOKEN_ID MODAL_TOKEN_SECRET MUAPI_API_KEY; do [ -n "${!k:-}" ] && printf '%s' "${!k}" | gh secret set $k -R $R; done
gh variable set HF_REPO -R $R --body "${HF_REPO:-bekbol446/neuro-channel}"
for k in MODAL_MONTHLY_USD MUAPI_MONTHLY_USD MUAPI_MODEL; do [ -n "${!k:-}" ] && gh variable set $k -R $R --body "${!k}"; done
gh secret list -R $R; gh variable list -R $R
echo "ready: gh workflow run video.yml -R $R -f project=<name>"
