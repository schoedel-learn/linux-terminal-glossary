# GitHub Copilot Instructions — linux-terminal-glossary

This is a static single-page application (SPA) that serves a searchable glossary
of **3,267 terminal commands** across **29 categories**. There is no build step,
no framework, and no package.json — everything ships as plain files.

---

## Project structure

```
linux-terminal-glossary/
├── index.html                   # Single-file SPA — all HTML, CSS, and JS inline
├── commands.json                # Master data — 4,800+ commands, flat list + categories array
├── search_index.json            # TF-IDF search index + synonyms (built by scripts/rebuild_search_index.py)
├── search_vectors.json          # fp16 semantic embeddings, one 384-dim vector per command (built by scripts/build_embeddings.py)
├── catalogs/                    # Per-category source files folded into commands.json by scripts/merge_catalogs.py
├── scripts/
│   ├── rebuild_search_index.py  # Regenerates search_index.json from commands.json
│   ├── build_embeddings.py      # Regenerates search_vectors.json (needs onnxruntime+tokenizers venv, model files)
│   └── merge_catalogs.py        # Folds catalogs/*.json into commands.json (exact-match dedup)
└── .github/
    ├── copilot-instructions.md  # This file
    └── ISSUE_TEMPLATE/command-report.yml
```

There are **no separate source files** for command data — `catalogs/*.json`
feed `commands.json`, which is the single source of truth. The old workflow
(merging category `.py` source files via a `rebuild_commands.py`) was retired —
do not recreate it.

---

## commands.json schema

Every command entry must follow this exact shape:

```json
{
  "id": 1,
  "cmd": "the exact command string",
  "desc": "One sentence — what the command does (≤ 80 chars preferred)",
  "category": "Exact Category Name",
  "tooltip": "2–4 sentence beginner-friendly explanation. Define jargon. Explain flags. Note gotchas."
}
```

**Rules:**
- `id` is a sequential integer; new entries get `max(id) + 1`
- `cmd` is the deduplicated primary key — no two entries share the same `cmd` string
- `desc` is present tense, imperative voice: "List all running containers" not "Lists..."
- `tooltip` is mandatory — every entry must have one; never leave it empty
- `category` must exactly match one of the 29 existing category names (case-sensitive)
- The top-level `categories` array in commands.json is always kept sorted A–Z
- The top-level `total` field must equal `len(commands)` after any modification
- **`commands.json` is always pretty-printed with `indent=2`** — never minify it.
  A one-line JSON file makes every future git diff unreadable (git compares
  line-by-line). If you regenerate the file, write it with `json.dump(data, f, indent=2)`.

---

## The 29 categories (sorted A–Z)

```
Administration        AI Agents & MCP        Archiving & Compression
Bash Scripting        Cron & Scheduling      Docker
Dokploy               Environment & Config   File Operations
File Viewing & Editing  Gemini CLI           Git - Advanced
Git - Core            GitHub CLI             GitHub Copilot
I/O Redirection & Pipes  Navigation & Directory  Networking
Node.js & npm/yarn    Productivity & Search  Python & pip
SSH & Remote          Self-Hosting           Shell & Bash
Terminal Configuration  Text Processing      VPS Management
Vim/Neovim            tmux
```

When adding a new category: add it to the `categories` array (keeping A–Z
order), add entries with that category name, rebuild the search index, and
update the command count in all three places inside `index.html` (title tag,
loading spinner text, history panel empty-state text).

---

## Style rules for tooltips

- Written for a novice who may not know what flags like `-v`, `-r`, `-f` mean
- Also useful for intermediate users — mention when a flag is dangerous or irreversible
- 2–4 sentences maximum; avoid bullet points inside tooltips
- Do not start with "This command..." — start with the subject directly
- Mention related commands when helpful (e.g. "Pair this with `borg prune` to avoid unbounded growth")

**Deduplication:** never add a `cmd` string that already exists in
`commands.json`. To update an existing entry, edit it in place — do not add a duplicate.

---

## index.html conventions

- **Single file** — all CSS is in a `<style>` block in `<head>`, all JS is in a
  `<script>` block at the end of `<body>`. Do not split into separate files.
- **No frameworks** — vanilla JS only. No React, Vue, or any npm dependency.
- **CSS custom properties** — all colors, spacing, and typography use CSS variables
  defined in `:root`. Never use hardcoded hex colors or pixel values outside the
  `:root` block.
- **Key CSS variables:**
  ```css
  --color-primary          /* accent */
  --color-bg               /* page background */
  --color-surface          /* card background */
  --color-surface-2        /* elevated surface */
  --color-border           /* dividers */
  --color-text             /* primary text */
  --color-text-muted       /* secondary text */
  --color-text-faint       /* tertiary / disabled text */
  --space-1 … --space-8    /* spacing scale */
  --text-xs/sm/base/lg     /* font size scale */
  --radius-sm/md/lg/full   /* border radius scale */
  ```
- **Mobile-first** — all layout is mobile-first. Desktop styles go inside
  `@media (min-width: 768px)` or `@media (min-width: 1024px)` breakpoints.
- **Tap targets** — interactive elements on mobile must be ≥ 44px tall
  (per Apple HIG). Use `min-height: 44px` and `padding` rather than fixed heights.
- **Sticky header** — `.sticky-header` wraps `.topbar` and `.filter-bar` with
  `position: sticky; top: 0; z-index: 50`. Do not break this wrapper.

---

## Key JS globals and functions

| Variable / Function      | Description |
|--------------------------|-------------|
| `COMMANDS`               | Flat array of all command objects loaded from commands.json |
| `CATEGORIES`             | Sorted array of category name strings |
| `SEARCH_INDEX`           | TF-IDF index object loaded from search_index.json |
| `IDF`                    | IDF weight map `{ token: float }` |
| `SYNONYMS`               | Synonym expansion map `{ word: [word, ...] }` |
| `selectCategory(name)`   | Filters the command grid to a category; `'All'` resets |
| `runSearch(query)`       | Runs TF-IDF + synonym search; renders results |
| `renderCommands(cmds)`   | Renders a command card array into `#content` |
| `openTooltip(id, el)`    | Shows the singleton tooltip popover for a command |
| `historyLoad()`          | Returns recently searched array from localStorage |
| `historySave(query)`     | Appends a query to localStorage history |
| `QS_STEPS`               | Array of 8 Quick Start Guide step objects |

**localStorage keys:**
- `ltg_search_history` — recently searched queries (array of `{q, ts}`)
- `ltg_qs_progress` — Quick Start Guide step progress `{0: true, 1: true, ...}`

---

## Tooltip popover

The tooltip system uses a **single singleton `<div id="tooltipPopover">`** that
repositions on each open. Do not create per-card tooltip elements.

- Triggered by the ⓘ button on each command card
- Auto-closes on: Escape key, scroll, click outside, opening another tooltip
- Always rendered within the viewport (position is clamped in JS)

---

## Quick Start Guide (self-hosting cheat sheet)

Defined as `QS_STEPS` — an array of 8 step objects. Each step has:

```js
{
  title:    '1. Step Name',
  desc:     'One-line summary shown in collapsed state',
  tip:      'HTML string — beginner callout shown at top of expanded step',
  commands: [
    { cmd: 'the command', label: 'Short label', why: 'One sentence explaining why this step matters' }
  ]
}
```

- The `tip` field renders as a `<div class="qs-tip">` with an accent left border
- The `why` field renders as `.qs-cmd-why` in italic below each command label
- Steps collapse/expand; both `.qs-tip` and `.qs-cmds` are hidden when collapsed
- Clicking a command runs `runSearch(cmd)` and closes the drawer

---

## Build pipeline

There is no build step for the site itself. To add or change commands:

```bash
# 1. Edit the catalog in catalogs/<category>.json (or commands.json directly for
#    small fixes — keep it pretty-printed, indent=2)

# 2. Merge catalogs into the master
python3 scripts/merge_catalogs.py     # → updates commands.json

# 3. Rebuild the search index
python3 scripts/rebuild_search_index.py   # → updates search_index.json

# 4. Rebuild the semantic vectors (only when the command set changed)
MODEL_DIR=/tmp/ltg-emb/models /tmp/ltg-emb/bin/python scripts/build_embeddings.py  # → search_vectors.json

# 5. Commit and push (GitHub Pages serves from main)
git add commands.json search_index.json search_vectors.json index.html catalogs/
git commit -m "feat: ..."
git push origin main
```

The command count in index.html is **dynamic** (title and empty-state are set
from `COMMANDS.length`; the loading spinner has no count) — do not hardcode it.

## Semantic search (hybrid)

- Corpus vectors are precomputed (fp16, `search_vectors.json`) with the
  multilingual `Xenova/multilingual-e5-small` model — passages use the
  `passage: ` prefix in `scripts/build_embeddings.py`.
- The browser loads the same model via transformers.js (CDN, cached) and
  embeds only the QUERY (with the `query: ` prefix), then dot-products against
  the precomputed vectors.
- Two signals are fused with Reciprocal Rank Fusion (RRF, k=60): the semantic
  cosine list and the lexical list (TF-IDF + synonyms + exact pinning).
- Typo correction uses Damerau-Levenshtein (transposition = 1 edit) against
  the set of known cmd tokens; corrected tokens REPLACE the typo in scoring.
- Key JS: `SEARCH_VECTORS`, `SEM_READY/SEM_LOADING/SEM_PIPELINE`, `semCache`,
  `decodeVectors()`, `buildFuzzyIndex()`, `fuzzyCorrect()`, `initSemantic()`,
  `semanticRank()`, `rrfFuse()`, `enhanceWithSemantic()`.
- Do not change the model id without regenerating `search_vectors.json`.
- New synonyms (including Spanish terms — `borrar`, `procesos`, `archivos`,
  etc.) go in the `SEARCH_SYNONYMS` map inside `scripts/rebuild_search_index.py`.

---

## What Copilot should and should not do

**Do:**
- Follow the `{cmd, desc, category, tooltip}` schema exactly when suggesting new entries
- Keep tooltips beginner-friendly: define abbreviations, explain flags, note dangers
- Use the existing CSS custom properties — never introduce hardcoded colors
- Keep all JS vanilla — no imports, no modules, no framework suggestions
- Maintain mobile-first CSS ordering (base → `@media min-width`)
- Preserve the sorted A–Z order of `CATEGORIES`
- Keep `commands.json` pretty-printed (`indent=2`) — never minify it

**Do not:**
- Suggest splitting `index.html` into separate CSS/JS files
- Suggest npm, webpack, Vite, or any build tooling
- Add commands without tooltips
- Introduce new CSS variables without adding them to `:root`
- Change the localStorage key names (would break existing user data)
- Recreate the old source-file merge workflow (`rebuild_commands.py`, category `.py` files)
- Suggest frameworks (React, Vue, Alpine) for UI changes
