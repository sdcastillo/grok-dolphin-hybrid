# Grok × Dolphin hybrid

- **Grok** handles agentic work (research, legal binders, HF datasets/models, batch Ollama jobs).
- **Dolphin** is the local uncensored chat engine behind JARVIS FastAPI / Tailscale Funnel.
- **Bridge**: rating prompts in FastAPI + this Modelfile so the mimic model infers IMDb level and applies the multi-level persona without retraining weights.
