# GitHub Copilot Instructions — linux-terminal-glossary

This is a static single-page application (SPA) that serves a searchable glossary
of **2,838 terminal commands** across **33 categories**. There is no build step,
no framework, and no package.json — everything ships as three plain files.

---

## Project structure

```
linux-glossary/
├── index.html          # Single-file SPA — all HTML, CSS, and JS inline
├── commands.json       # Master data — 2,838 commands, flat list + categories array
├── search_index.json   # TF-IDF search index (built by rebuild_search_index.py)
└── .github/
    └── copilot-instructions.md

# Source files (workspace root, not served):
../linux_commands_data.py      # Original command dataset
../dokploy.py                  # Dokploy category source
../vps.py                      # VPS Management category source
../copilot.py                  # GitHub Copilot category source
../npm_extra.py                # Node.js / npm category source
../self_hosting.py             # Self-Hosting category source
../networking_extra.py         # Networking additions source
../rebuild_commands.py         # Merges all source files → commands.json
../rebuild_search_index.py     # Rebuilds search_index.json from commands.json
```

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
- `category` must exactly match one of the 33 existing category names (case-sensitive)
- The top-level `categories` array in commands.json is always kept sorted A–Z
- The top-level `total` field must equal `len(commands)` after any modification

---

## The 33 categories (sorted A–Z)

```
Archiving & Compression    Bash Scripting             Cron & Scheduling
Disk & Filesystem          Docker                     Dokploy
Environment & Config       File Operations            File Viewing & Editing
Gemini CLI                 Git - Advanced             Git - Core
GitHub CLI                 GitHub Copilot             I/O Redirection & Pipes
Navigation & Directory     Networking                 Node.js & npm/yarn
Package Management - APT/Ubuntu  Permissions & Ownership  Process Management
Productivity & Search      Python & pip               SSH & Remote
Self-Hosting               Shell & Bash               System Information
System Services & Systemd  Text Processing            User & Group Management
VPS Management             Vim/Neovim                 tmux
```

When adding a new category: add it to the source `.py` file, run
`rebuild_commands.py`, then `rebuild_search_index.py`, and update the
count in all three places inside `index.html` (title tag, loading spinner
text, history panel empty-state text).

---

## Source file conventions (Python category files)

Each category lives in a Python source file as a list of dicts:

```python
CATEGORY_NAME = [
    {
        "cmd": "exact command",
        "desc": "Short imperative description",
        "tooltip": "Beginner-friendly explanation. Define any jargon. Explain flags. "
                   "Note when to use vs. when not to. Point out common gotchas."
    },
    ...
]
```

**Style rules for tooltips:**
- Written for a novice who may not know what flags like `-v`, `-r`, `-f` mean
- Also useful for intermediate users — mention when a flag is dangerous or irreversible
- 2–4 sentences maximum; avoid bullet points inside tooltips
- Do not start with "This command..." — start with the subject directly
- Mention related commands when helpful (e.g. "Pair this with `borg prune` to avoid unbounded growth")

**Deduplication:** The merge script skips any `cmd` string already present in
`commands.json`. If you need to update an existing entry, edit `commands.json`
directly rather than through a source file.

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
  --color-primary          /* indigo accent */
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
| `SEARCH_INDEX`           | TF-IDF index array loaded from search_index.json |
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

- The `tip` field renders as a `<div class="qs-tip">` with an indigo left border
- The `why` field renders as `.qs-cmd-why` in italic below each command label
- Steps collapse/expand; both `.qs-tip` and `.qs-cmds` are hidden when collapsed
- Clicking a command runs `runSearch(cmd)` and closes the drawer

---

## Build pipeline

When adding a new category or expanding an existing one:

```bash
# 1. Write / edit the source .py file
# 2. Run the merge script
python3 rebuild_commands.py      # → updates commands.json

# 3. Rebuild the search index
python3 rebuild_search_index.py  # → updates search_index.json

# 4. Copy both JSON files to the site folder
cp commands.json linux-glossary/
cp search_index.json linux-glossary/

# 5. Update the 3 count references in index.html (title, spinner, history empty state)

# 6. Commit, push, and deploy
git add commands.json search_index.json index.html
git commit -m "feat: ..."
git push origin main
```

---

## What Copilot should and should not do

**Do:**
- Follow the `{cmd, desc, category, tooltip}` schema exactly when suggesting new entries
- Keep tooltips beginner-friendly: define abbreviations, explain flags, note dangers
- Use the existing CSS custom properties — never introduce hardcoded colors
- Keep all JS vanilla — no imports, no modules, no framework suggestions
- Maintain mobile-first CSS ordering (base → `@media min-width`)
- Preserve the sorted A–Z order of `CATEGORIES`

**Do not:**
- Suggest splitting `index.html` into separate CSS/JS files
- Suggest npm, webpack, Vite, or any build tooling
- Add commands without tooltips
- Introduce new CSS variables without adding them to `:root`
- Change the localStorage key names (would break existing user data)
- Suggest frameworks (React, Vue, Alpine) for UI changes
