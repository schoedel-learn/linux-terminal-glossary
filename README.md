# Linux Terminal Glossary

A fast, searchable glossary of **3,267 Linux terminal commands** across **29
categories** — built for people who are learning the command line AND for
seasoned admins who need a quick reference on a server.

**Live site:** https://schoedel-learn.github.io/linux-terminal-glossary/

## What it does

- 🔍 **Semantic search** — type a goal ("kill process", "copy files remotely")
  and get ranked commands, thanks to a TF-IDF index with synonym expansion.
  No need to know the exact command name.
- 📂 **29 categories** — Administration, Docker, Git, Python & pip, Networking,
  SSH & Remote, Vim/Neovim, tmux, and more.
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
- `category` must match one of the 29 names in the `categories` array exactly
- Keep `commands.json` pretty-printed (`indent=2`) — one-line JSON destroys git diffs
- Update `total` to equal `len(commands)`

Then rebuild the search index and refresh the three count references in
`index.html` (title, loading spinner, history empty-state):

```bash
python3 scripts/rebuild_search_index.py
grep -n '3,267' index.html   # update the three occurrences if the count changed
```

## Project layout

```
index.html                   # Single-file SPA — all HTML, CSS, JS inline
commands.json                # Master data: 3,267 commands, 29 categories
search_index.json            # TF-IDF search index (generated)
scripts/rebuild_search_index.py  # Regenerates search_index.json
.github/                     # Copilot instructions + issue template
```

## How search works (the short version)

Each command's text is tokenized and weighted with **TF-IDF**: words that are
common inside one entry but rare across the whole glossary score highest.
A synonym map expands your query ("kill process" → kill/pkill/pgrep/ps), so
you can search by intent, not just by command name.

## Reporting problems

Found a wrong flag, a missing command, or a confusing tooltip? Open an issue
via the **Report an issue** button in the app — it pre-fills a GitHub issue
template.

## License

MIT — see [LICENSE](LICENSE).
