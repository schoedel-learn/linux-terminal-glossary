# linux-terminal-glossary — Gemini Project Context

## Project purpose

This repository is a searchable glossary of Linux terminal commands aimed at
developers who use **Ubuntu Linux** to build applications and websites.  The
audience ranges from beginners setting up their first VPS to intermediate
developers running containers, managing services with systemd, and scripting
CI/CD pipelines.

## Primary development platform

All commands, flags, package names, file paths, and service configurations
documented here target **Ubuntu** (LTS releases, currently 22.04 / 24.04).
When a command behaves differently across distributions, prefer the Ubuntu /
Debian variant.

## Documentation sources — consult these first

When you need to verify command behaviour, flag syntax, default paths,
service names, or any Ubuntu-specific detail, check the official Ubuntu
documentation before relying on general knowledge:

| Source | URL | When to use |
|--------|-----|-------------|
| **Ubuntu Documentation** | <https://docs.ubuntu.com/> | Structured guides — installation, server configuration, cloud, snap, LXD, security hardening |
| **Ubuntu Community Help** | <https://help.ubuntu.com/> | Task-oriented community wiki — package management, networking, desktop, printing, hardware |

Prefer `docs.ubuntu.com` for server/infrastructure topics and `help.ubuntu.com`
for desktop and general how-to questions.

## How to use the documentation when answering questions

1. **Anchor descriptions to Ubuntu behaviour.** If a flag or file path is
   Ubuntu-specific (e.g. `/etc/netplan/`, `ufw`, `snap`), say so in the
   tooltip.
2. **Cite the docs when helpful.** In tooltips that mention non-obvious
   behaviour (e.g. `systemd` unit file locations, AppArmor profiles), you may
   add a note like "See Ubuntu Server docs for full options."
3. **Prefer `apt` / `snap` over distribution-agnostic alternatives** unless
   the command is intentionally cross-distro (e.g. `docker pull`).
4. **Verify default values against Ubuntu.** For example, the default SSH port,
   the default `ufw` policy, or the default Python version — check the Ubuntu
   docs for the current LTS release before hardcoding a value.

## Project file layout

```
linux-glossary/          ← static SPA (served files)
├── index.html           ← single-file app — HTML + CSS + JS inline
├── commands.json        ← 2,838 commands across 33 categories
└── search_index.json    ← TF-IDF search index

scripts/
└── rebuild_search_index.py

(workspace root)
├── linux_commands_data.py
├── rebuild_commands.py  ← merges all .py sources → commands.json
└── *.py                 ← per-category command sources
```

## commands.json entry schema

```json
{
  "id": 1,
  "cmd": "exact command string",
  "desc": "Imperative present-tense, ≤ 80 chars",
  "category": "Exact Category Name",
  "tooltip": "2–4 sentence beginner explanation. Define flags. Note Ubuntu-specific paths or gotchas."
}
```

## The 33 categories

Archiving & Compression · Bash Scripting · Cron & Scheduling · Disk &
Filesystem · Docker · Dokploy · Environment & Config · File Operations · File
Viewing & Editing · Gemini CLI · Git - Advanced · Git - Core · GitHub CLI ·
GitHub Copilot · I/O Redirection & Pipes · Navigation & Directory · Networking
· Node.js & npm/yarn · Package Management - APT/Ubuntu · Permissions &
Ownership · Process Management · Productivity & Search · Python & pip · SSH &
Remote · Self-Hosting · Shell & Bash · System Information · System Services &
Systemd · Text Processing · User & Group Management · VPS Management ·
Vim/Neovim · tmux
