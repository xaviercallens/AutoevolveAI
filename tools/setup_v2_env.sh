#!/usr/bin/env bash
# Build the repo-local Python 3.11 venv the v2 cards assume (system python here is 3.10).
set -euo pipefail
cd "$(dirname "$0")/.."
command -v uv >/dev/null || pip install --user uv
export PATH="$HOME/.local/bin:$PATH"
uv python install 3.11
uv venv .venv-v2 --python 3.11
uv pip install --python .venv-v2/bin/python \
  torch numpy pytest pytest-cov pytest-asyncio hypothesis fakeredis redis fastapi httpx uvicorn \
  pydantic pyyaml psutil radon docker chromadb peft transformers datasets trl fastmcp sympy pint
echo "ready: source .venv-v2/bin/activate"
