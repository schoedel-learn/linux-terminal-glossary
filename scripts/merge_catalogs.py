#!/usr/bin/env python3
"""Merge category catalogs from catalogs/*.json into commands.json.

commands.json remains the single source of truth. Each catalog file adds
commands for one category. Entries are deduplicated by cmd string
(case-insensitive) against the whole corpus. New categories are added to the
categories array and the array is kept sorted A-Z. New entries are appended
at the end (preserving commands.json's human-curated display order). Ids are
assigned sequentially starting at max(id) + 1.

Usage:
    python3 scripts/merge_catalogs.py                # merge every catalogs/*.json
    python3 scripts/merge_catalogs.py catalogs/foo.json   # merge specific files

After merging, run scripts/rebuild_search_index.py to refresh the index.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS_PATH = ROOT / "commands.json"
CATALOGS_DIR = ROOT / "catalogs"

MAX_DESC_CHARS = 100


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> int:
    data = load_json(COMMANDS_PATH)
    categories: list[str] = list(data["categories"])
    commands: list[dict] = data["commands"]

    existing = {str(c["cmd"]).strip().lower() for c in commands}

    if len(sys.argv) > 1:
        catalog_paths = [Path(a) for a in sys.argv[1:]]
    else:
        if not CATALOGS_DIR.is_dir():
            print(f"Catalog directory not found: {CATALOGS_DIR}")
            return 1
        catalog_paths = sorted(CATALOGS_DIR.glob("*.json"))

    if not catalog_paths:
        print("No catalog files found.")
        return 1

    next_id = max(int(c["id"]) for c in commands) + 1
    added_total = 0
    skipped_total = 0
    warnings: list[str] = []

    for path in catalog_paths:
        cat = load_json(path)
        category = str(cat.get("category", "")).strip()
        if not category:
            warnings.append(f"{path.name}: missing 'category' — skipped")
            continue
        if category not in categories:
            categories.append(category)

        added = 0
        skipped = 0
        for e in cat.get("commands", []):
            cmd = str(e.get("cmd", "")).strip()
            desc = str(e.get("desc", "")).strip()
            tooltip = str(e.get("tooltip", "")).strip()
            if not cmd:
                skipped += 1
                continue
            key = cmd.lower()
            if key in existing:
                skipped += 1
                continue
            if not desc:
                warnings.append(f"{path.name}: '{cmd}' has no desc")
            elif len(desc) > MAX_DESC_CHARS:
                warnings.append(
                    f"{path.name}: '{cmd}' desc is {len(desc)} chars "
                    f"(> {MAX_DESC_CHARS})"
                )
            elif not desc[0].isupper():
                warnings.append(f"{path.name}: '{cmd}' desc should start uppercase")
            if not tooltip:
                warnings.append(f"{path.name}: '{cmd}' has no tooltip")

            commands.append(
                {
                    "id": next_id,
                    "category": category,
                    "cmd": cmd,
                    "desc": desc,
                    "tooltip": tooltip,
                }
            )
            existing.add(key)
            next_id += 1
            added += 1

        added_total += added
        skipped_total += skipped
        print(f"{path.name}: +{added} (skipped {skipped} dupes/invalid)")

    categories.sort()
    data["categories"] = categories
    data["total"] = len(commands)
    COMMANDS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")

    print(f"\nTotal: {len(commands)} commands (+{added_total}, skipped {skipped_total})")
    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"  - {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
