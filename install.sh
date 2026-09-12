#!/usr/bin/env bash
# Install Samzzzed/dolphin-mistral-7b and register it with Ollama
# as dolphin-mistral-imdb:7b (Grok–Dolphin hybrid / FastAPI IMDb ladder).
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$REPO_DIR"

HF_REPO="${HF_REPO:-Samzzzed/dolphin-mistral-7b}"
GGUF_NAME="${GGUF_NAME:-dolphin-2.8-mistral-7b-v02-Q4_0.gguf}"
OLLAMA_TAG="${OLLAMA_TAG:-dolphin-mistral-imdb:7b}"
HF_URL="https://huggingface.co/${HF_REPO}/resolve/main/${GGUF_NAME}"

need() {
  command -v "$1" >/dev/null 2>&1
}

echo "==> grok-dolphin-hybrid installer"
echo "    Hugging Face: https://huggingface.co/${HF_REPO}"
echo "    Ollama tag:   ${OLLAMA_TAG}"

if ! need ollama; then
  echo "Ollama is not installed."
  echo "Install from https://ollama.com/download then re-run:  bash install.sh"
  exit 1
fi

if ! curl -sf --max-time 3 http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
  echo "Starting ollama serve in the background..."
  nohup ollama serve >/tmp/ollama-hybrid.log 2>&1 &
  for _ in $(seq 1 20); do
    curl -sf --max-time 1 http://127.0.0.1:11434/api/tags >/dev/null 2>&1 && break
    sleep 1
  done
fi

if [[ ! -f "$GGUF_NAME" ]]; then
  echo "==> Downloading ${GGUF_NAME} (~4.1 GB)..."
  if need hf; then
    hf download "$HF_REPO" "$GGUF_NAME" --local-dir "$REPO_DIR"
  elif need huggingface-cli; then
    huggingface-cli download "$HF_REPO" "$GGUF_NAME" --local-dir "$REPO_DIR" --local-dir-use-symlinks False
  elif need curl; then
    curl -L --fail --progress-bar -o "${GGUF_NAME}.partial" "$HF_URL"
    mv "${GGUF_NAME}.partial" "$GGUF_NAME"
  else
    echo "Need hf, huggingface-cli, or curl to download the GGUF."
    exit 1
  fi
else
  echo "==> Found existing $GGUF_NAME — skipping download"
fi

if [[ ! -f Modelfile ]]; then
  echo "Modelfile missing next to install.sh"
  exit 1
fi

echo "==> Creating Ollama model ${OLLAMA_TAG}"
ollama create "$OLLAMA_TAG" -f Modelfile

echo
echo "Done. Try:"
echo "  ollama run ${OLLAMA_TAG}"
echo
echo "Or point JARVIS FastAPI at it:"
echo "  export OLLAMA_MODEL=${OLLAMA_TAG}"
