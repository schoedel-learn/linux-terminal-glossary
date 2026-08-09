# Linux Terminal Glossary

A fast, searchable glossary of **7,600+ Linux terminal commands** across **50
categories** — built for people who are learning the command line AND for
seasoned admins who need a quick reference on a server. Covers Linux web
application development, self-hosting, and LPIC-2/RHCSA-level administration.

**Live site:** https://schoedel-learn.github.io/linux-terminal-glossary/

## What it does

- 🔍 **Hybrid semantic search** — type a goal ("kill process", "copy files remotely")
  and get ranked commands from TWO signals fused at once: a multilingual
  embedding model (multilingual-e5-small, runs in your browser) that
  understands concepts and Spanish queries, PLUS a lexical layer (TF-IDF +
  synonyms + typo correction + exact match pinning). Fused with Reciprocal
  Rank Fusion — the standard modern retrieval technique. Degrades gracefully
  to keyword mode when offline.
- ✍️ **Typo-tolerant** — "gerp" still finds `grep` (Damerau-Levenshtein
  correction).
- 🌎 **Bilingual** — Spanish queries work ("borrar archivos" → `rm`).
- 📂 **50 categories** — Administration, Docker, Git, Python & pip, Networking,
  SSH & Remote, Vim/Neovim, tmux, Web App Development, and more.
- 💡 **Explain button** on every command — a beginner-friendly tooltip that
  defines jargon, explains flags, and flags dangerous commands.
- 📋 **One-click copy** for every command.
- 🚀 **Self-hosting Quick Start Guide** — 8 steps of commands for deploying on
  a VPS.
- 🌙 Dark-first, mobile-first, zero dependencies. A single HTML file and two
  JSON files. No build step, no framework, no tracking.

## Run locally

```bash
cd linux-terminal-glossary
python3 -m http.server 8000
# open http://localhost:8000
```

(Open `index.html` by double-click also works, since there are no module
imports — but a local server is recommended.)

## Add or fix a command

The data lives in `commands.json` — it is the single source of truth.

```json
{
  "id": 3268,
  "cmd": "the exact command",
  "desc": "One sentence — what it does (imperative voice)",
  "category": "Exact Category Name",
  "tooltip": "2–4 sentence beginner-friendly explanation. Define jargon. Explain flags. Note gotchas."
}
```

Rules:

- `id` = `max(id) + 1`; `cmd` strings must be unique (deduplication key)
- `category` must match one of the 50 names in the `categories` array exactly
- Keep `commands.json` pretty-printed (`indent=2`) — one-line JSON destroys git diffs
- Update `total` to equal `len(commands)`

Then rebuild the search index, refresh the embeddings, and update the count
references in `index.html` (title, spinner, history empty-state — the title is
now dynamic; the spinner has no count; the empty-state is templated):

```bash
python3 scripts/rebuild_search_index.py       # → updates search_index.json
MODEL_DIR=/tmp/ltg-emb/models /tmp/ltg-emb/bin/python scripts/build_embeddings.py  # → search_vectors.json
```

## Project layout

```
index.html                   # Single-file SPA — all HTML, CSS, JS inline
commands.json                # Master data: 7,600+ commands, 50 categories
search_index.json            # TF-IDF index + synonyms (generated)
search_vectors.json          # fp16 semantic embeddings, one 384-dim vector per command (generated)
catalogs/                    # Per-category source files merged by scripts/merge_catalogs.py
scripts/rebuild_search_index.py  # Regenerates search_index.json (add synonyms here)
scripts/build_embeddings.py  # Regenerates search_vectors.json (needs onnxruntime+tokenizers venv)
scripts/merge_catalogs.py    # Folds catalogs/*.json into commands.json
.github/                     # Copilot instructions + issue template
```

## How search works (the short version)

**Hybrid, both signals at once:**

1. **Semantic arm** — every command is pre-embedded with the multilingual
   `multilingual-e5-small` model (384-dim, fp16, ~4MB). At search time your
   browser loads the same model once (~135MB, cached) via transformers.js,
   embeds only your query, and dot-products against all precomputed vectors.
   This is what understands *concepts* and *Spanish*: "what's using port 80"
   finds `ss -tlnp` even though no synonym says so.
2. **Lexical arm** — TF-IDF cosine + a 167-term synonym map (including ~34
   Spanish terms), plus typo correction (Damerau-Levenshtein: "gerp" → grep)
   and exact-match pinning (`docker ps` always lands first).
3. **Fusion** — Reciprocal Rank Fusion merges both ranked lists: each result
   scores `1/(k + rank)` from each arm. No weight tuning; both signals
   contribute simultaneously. The badge shows `hybrid` when both fired.
4. **Fallback** — if the model can't load (offline, blocked CDN), search
   degrades to the lexical arm with zero errors.

## Reporting problems

Found a wrong flag, a missing command, or a confusing tooltip? Open an issue
via the **Report an issue** button in the app — it pre-fills a GitHub issue
template.

## License

MIT — see [LICENSE](LICENSE).
