# grok-dolphin-hybrid

Hybrid stack: **Grok Bot** orchestration + **Dolphin-Mistral 7B** (Ollama / FastAPI) with an **IMDb-style multi-level** system prompt.

## Pieces

| Piece | Role |
|-------|------|
| Grok Bot (ChinaDefense / desktop) | Research, batching, Hugging Face uploads, agent workflows |
| JARVIS FastAPI (`dolphin-mistral:7b`) | Local chat with G / PG / PG-13 / R / NC-17 rating ladder |
| This repo | Modelfile + prompt helpers to run the same behavior |

## Install

```bash
git clone https://github.com/sdcastillo/grok-dolphin-hybrid.git
cd grok-dolphin-hybrid
bash install.sh
```

That downloads [Samzzzed/dolphin-mistral-7b](https://huggingface.co/Samzzzed/dolphin-mistral-7b) (`dolphin-2.8-mistral-7b-v02-Q4_0.gguf`) and runs `ollama create dolphin-mistral-imdb:7b`.

One-liner (needs git + Ollama):

```bash
curl -fsSL https://raw.githubusercontent.com/sdcastillo/grok-dolphin-hybrid/main/install.sh | bash
```

(The one-liner only works if you already have this repo’s `Modelfile` in the current directory; prefer the clone path.)

Then:

```bash
ollama run dolphin-mistral-imdb:7b
# or
export OLLAMA_MODEL=dolphin-mistral-imdb:7b
```

## Model weights

GGUF lives on Hugging Face (not in git):

**https://huggingface.co/Samzzzed/dolphin-mistral-7b**

```bash
# download Q4_0 GGUF into this folder, then:
ollama create dolphin-mistral-imdb:7b -f Modelfile
ollama run dolphin-mistral-imdb:7b
```

## FastAPI rating helper

See `fastapi_imdb_prompts.py` — `build_ollama_payload(message, rating=...)` mirrors JARVIS_APP:

1. Infer IMDb/MPAA level when rating omitted  
2. Honor FastAPI `rating` as a **ceiling**  
3. Emit `IMDB_RATING: …` then answer at that level  

## Files

- `Modelfile` — Ollama ChatML + hybrid SYSTEM prompt  
- `SYSTEM.txt` — same system text standalone  
- `install.sh` — download GGUF from Hugging Face and `ollama create`
- `fastapi_imdb_prompts.py` — Python helper for the FastAPI app  

## License

Dolphin/Mistral lineage: Apache-2.0. Prompt glue: same as your app usage.
