---
layout: default
title: Grok–Dolphin Hybrid
description: Grok Bot plus local Dolphin-Mistral 7B, with an IMDb-style rating ladder for FastAPI.
samwiki: true
---

<p class="sw-level sw-level-advanced"><span class="sw-level-idx">Level 3</span><span class="sw-level-name">Advanced</span></p>

<section class="sw-lede" aria-labelledby="about-title">
  <div class="sw-lede-copy">
    <h2 id="about-title">Grok for the work, Dolphin for the local chat</h2>
    <p>This repository is the hybrid stack: <strong>Grok Bot</strong> for research, batching, Hugging Face uploads, and agent workflows, and <strong>Dolphin-Mistral 7B</strong> for local chat through Ollama and FastAPI. The weights are the Q4_0 GGUF of dolphin-2.8-mistral-7b-v02 on <a href="https://huggingface.co/Samzzzed/dolphin-mistral-7b">Samzzzed/dolphin-mistral-7b</a>. What is checked in here is the Modelfile, the system text, the installer, and a Python helper that builds the same chat payload JARVIS FastAPI sends. Ollama registers that file as <code>dolphin-mistral-imdb:7b</code>.</p>
    <p>The prompt is an IMDb-style ladder: G, PG, PG-13, R, and NC-17. <code>fastapi_imdb_prompts.py</code> infers a level when the caller omits one. An explicit FastAPI <code>rating</code> is a ceiling, so the answer uses the stricter of the inferred level and the requested level. The reply starts with a single line, <code>IMDB_RATING:</code>, and then stays inside that level. G refuses violence, sexual content, drugs, illegal acts, harm, profanity, and adult themes. NC-17 may discuss adult themes the user asked about, and still refuses real-world help with violent crime and any sexual content involving minors or anyone 17 or under.</p>
    <p><strong>Difficulty: advanced.</strong> On the SamWiki ladder this is Level 3, advanced. The install needs Git, a running Ollama, and a download of about 4.1 GB, then <code>ollama create dolphin-mistral-imdb:7b -f Modelfile</code>. JARVIS picks the tag up with <code>OLLAMA_MODEL=dolphin-mistral-imdb:7b</code>. The second half of the tree, <code>dolphin-pod/</code>, is a local SQLite registry for people and Tailscale devices on a private mesh. Location is omitted. A machine is added when someone registers it.</p>
    <p>The sections below keep the project notes that already live in this repository: the clone install, the Hugging Face weights, the FastAPI helper, the file list, and the DOLPHIN POD commands. Dolphin and Mistral weights are Apache-2.0. The prompt glue is the text in <a href="https://github.com/sdcastillo/grok-dolphin-hybrid/blob/main/SYSTEM.txt"><code>SYSTEM.txt</code></a> and the <a href="https://github.com/sdcastillo/grok-dolphin-hybrid/blob/main/Modelfile">Modelfile</a>. The GGUF stays on Hugging Face and out of git.</p>
  </div>
  <aside class="sw-find" aria-labelledby="facts-title">
    <h2 id="facts-title">On this page</h2>
    <ul>
      <li><strong>What it is</strong> Grok Bot orchestration plus a local Dolphin-Mistral 7B with an IMDb rating ladder.</li>
      <li><strong>Who it is for</strong> Someone running JARVIS FastAPI or Ollama who wants <code>dolphin-mistral-imdb:7b</code> on that ladder.</li>
      <li><strong>Difficulty: advanced</strong> Level 3 on the SamWiki ladder. A local GGUF, an Ollama Modelfile, and a FastAPI payload helper.</li>
      <li><strong>Weights</strong> <a href="https://huggingface.co/Samzzzed/dolphin-mistral-7b">Samzzzed/dolphin-mistral-7b</a>, file <code>dolphin-2.8-mistral-7b-v02-Q4_0.gguf</code>.</li>
      <li><strong>Registry</strong> <code>dolphin-pod/</code> stores opted-in people and Tailscale names. It does not store location.</li>
    </ul>
  </aside>
</section>

## What you run

- Clone the repository and run <code>bash install.sh</code>. The script downloads the GGUF and runs <code>ollama create</code>.
- Chat with <code>ollama run dolphin-mistral-imdb:7b</code>, or export <code>OLLAMA_MODEL=dolphin-mistral-imdb:7b</code> for JARVIS.
- Build a FastAPI payload with <code>build_ollama_payload(message, rating=...)</code> in <code>fastapi_imdb_prompts.py</code>.
- In <code>dolphin-pod/</code>, register a person who opted in, accept a hostname, and export a local CSV. The database file stays gitignored.

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

The one-liner only works if you already have this repo’s `Modelfile` in the current directory. Prefer the clone path.

Then:

```bash
ollama run dolphin-mistral-imdb:7b
# or
export OLLAMA_MODEL=dolphin-mistral-imdb:7b
```

## Model weights

The GGUF lives on Hugging Face, not in git:

**https://huggingface.co/Samzzzed/dolphin-mistral-7b**

```bash
# download Q4_0 GGUF into this folder, then:
ollama create dolphin-mistral-imdb:7b -f Modelfile
ollama run dolphin-mistral-imdb:7b
```

## FastAPI rating helper

`fastapi_imdb_prompts.py` — `build_ollama_payload(message, rating=...)` mirrors JARVIS_APP:

1. Infer an IMDb/MPAA level when rating is omitted.
2. Honor FastAPI `rating` as a **ceiling**.
3. Emit `IMDB_RATING: …` and then answer at that level.

`HYBRID.md` states the split in one place: Grok does the agentic work, Dolphin is the local chat engine, and the bridge is this rating prompt plus the Modelfile. The weights are not retrained.

## Files

- `Modelfile` — Ollama ChatML plus the hybrid SYSTEM prompt
- `SYSTEM.txt` — the same system text, standalone
- `install.sh` — download the GGUF from Hugging Face and `ollama create`
- `fastapi_imdb_prompts.py` — Python helper for the FastAPI app
- `HYBRID.md` — the three-line split between Grok, Dolphin, and the bridge
- `dolphin-pod/` — local SQLite registry, invite draft, rolodex, and outreach table

## DOLPHIN POD

The pod is a private Tailscale mesh plus a customer and device registry. It is a local tool (`pod.sh serve` on `127.0.0.1:8787` in the current notes). Exact location stays out of the database and out of posts. Unknown Tailscale nodes are left unenrolled. Someone joins by accepting an invite and sending a hostname.

```bash
cd dolphin-pod
python3 register.py list
python3 register.py add --first Ada --last Lovelace --email ada@example.com --phone +1-555-0100 \
  --machine ada-laptop --ip 100.x.x.x --os linux --role dev
python3 register.py invite --email them@example.com --first NAME --last NAME --role dev
python3 register.py accept --email them@example.com --machine hostname
python3 register.py who NAME
python3 register.py revoke --email them@example.com
python3 register.py export -o export.csv
bash status.sh
```

`role` is the mesh privilege (`member`, `dev`, `admin`). `contact_type` is the relationship bucket. The notes in `dolphin-pod/LAUNCH.md` say a private label stays off posts. The invite letter in `dolphin-pod/INVITE_LETTER.md` is a copy-paste draft. `invite_letter.py` can fill a local file. It does not send mail.

The rolodex is the same people as cards, with an optional organization and title, and no street address. The outreach table leaves channel, reply, and follow-up columns empty until someone fills them in:

```bash
python3 migrate_outreach.py
python3 register.py outreach
python3 register.py reply --email them@example.com --who NAME --replied-at "2026-09-18 16:00" --time-to-reply "2d"
```

## License

Dolphin/Mistral lineage: Apache-2.0. Prompt glue: the text shipped with this repository.

<section class="sw-contribute" aria-labelledby="contribute-title">
  <h2 id="contribute-title">Contribute</h2>
  <p>A clearer install note, a fix in the rating helper, or a small improvement to the pod CLI belongs in a pull request on this repository.</p>
  <p class="sw-actions">
    <a class="sw-btn sw-btn-pr" href="https://github.com/sdcastillo/grok-dolphin-hybrid/compare" target="_blank" rel="noopener noreferrer">Contribute / Open a PR</a>
    <a class="sw-btn sw-btn-source" href="https://github.com/sdcastillo/grok-dolphin-hybrid">View on GitHub</a>
  </p>
</section>
