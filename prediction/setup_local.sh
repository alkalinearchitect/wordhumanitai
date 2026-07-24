#!/usr/bin/env bash
# HumanitAI prediction stack — one-shot setup (free, local, no API keys)
# Run from repo root:  bash prediction/setup_local.sh
set -e
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "[1/4] Python 3.12 venv + OASIS engine (camel-oasis) + openai"
uv venv --python 3.12 .venv-oasis
. .venv-oasis/bin/activate
uv pip install -q camel-oasis openai
echo "      done"

echo "[2/4] Ollama (local LLM server) — user-space, from GitHub release"
if [ ! -x /opt/data/ollama-install/bin/ollama ]; then
  mkdir -p /tmp/ollama_dl && cd /tmp/ollama_dl
  TAG=$(curl -s https://api.github.com/repos/ollama/ollama/releases/latest | python3 -c "import sys,json;print(json.load(sys.stdin)['tag_name'])")
  curl -fsSL "https://github.com/ollama/ollama/releases/download/$TAG/ollama-linux-amd64.tar.zst" -o o.tzst
  python3 - "$PWD/ollama-linux-amd64.tar.zst" <<'PY'
import sys,zstandard,tarfile
src=sys.argv[1]
dctx=zstandard.ZstdDecompressor()
with dctx.stream_reader(open(src,'rb')) as r, tarfile.open(fileobj=r,mode='r|') as t:
    t.extractall(path='/opt/data/ollama-install')
PY
  chmod +x /opt/data/ollama-install/bin/ollama
fi
echo "      ollama at /opt/data/ollama-install/bin/ollama"

echo "[3/4] Start Ollama server + pull qwen2.5:3b (free open-weight model)"
export PATH=/opt/data/ollama-install/bin:$PATH OLLAMA_HOST=127.0.0.1:11434 OLLAMA_MODELS=/opt/data/.ollama-models
mkdir -p /opt/data/.ollama-models
( ollama serve >/tmp/ollama.log 2>&1 & ) || true
sleep 3
ollama pull qwen2.5:3b
echo "      done"

echo "[4/4] Run the UK simulation"
export OLLAMA_BASE_URL=http://127.0.0.1:11434/v1 OLLAMA_MODEL=qwen2.5:3b
python3 prediction/mirofish_uk_sim.py
echo "DONE"
