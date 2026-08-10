#!/usr/bin/env python3
"""Generate static SEO pages for the Linux Terminal Glossary.

Reads commands.json and emits:
  command/<slug>-<id>/index.html   — one crawlable page per command
  category/<cat-slug>/index.html   — one index page per category
  sitemap.xml                      — all command + category URLs
  robots.txt                       — allow all, reference the sitemap

Run inside the GitHub Actions deploy (before upload-pages-artifact) so the
pages are always generated from the current corpus. Idempotent; ~2-4s for
7,600+ commands.

Usage: python3 scripts/build_static_pages.py [SITE_URL]
"""

import html
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMMANDS_PATH = ROOT / "commands.json"
OUT_DIR = ROOT / "site"  # built output; uploaded as the Pages artifact root

# Custom domain (live 2026-08-09); github.io only while DNS/TLS cut over.
SITE_URL = sys.argv[1] if len(sys.argv) > 1 else "https://linux.schoedeldesign.ai"

BRAND_LINKS = f"""
<footer class="site-footer">
  <div class="footer-inner">
    <p class="footer-brand">Built by <a href="https://schoedeldesign.ai" rel="noopener">Schoedel Design</a> — AI-native design &amp; development</p>
    <p class="footer-tag">Also by Schoedel Design: <a href="https://proset.ai" rel="noopener">Proset AI</a> — bilingual AI transcription &amp; productivity for students and professionals</p>
    <p class="footer-back"><a href="{SITE_URL}/">← Back to the searchable glossary</a></p>
  </div>
</footer>
"""

CSS = """\
:root{--bg:#0d1117;--surface:#161b22;--surface2:#1c2128;--border:#30363d;--text:#e6edf3;--muted:#8b949e;--accent:#58a6ff}
*{box-sizing:border-box}body{margin:0;font-family:Inter,system-ui,-apple-system,sans-serif;background:var(--bg);color:var(--text);line-height:1.6}
.wrap{max-width:760px;margin:0 auto;padding:24px 20px 60px}
a{color:var(--accent);text-decoration:none}a:hover{text-decoration:underline}
.breadcrumb{font-size:13px;color:var(--muted);margin-bottom:8px}.breadcrumb a{color:var(--muted)}
h1{font-size:26px;margin:8px 0 4px;word-break:break-word}
.subtitle{color:var(--muted);margin:0 0 20px}
.cmd{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:16px;margin:16px 0;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:15px;overflow-x:auto;white-space:pre-wrap;word-break:break-all}
.copy{background:var(--surface2);border:1px solid var(--border);color:var(--text);border-radius:6px;padding:6px 12px;font-size:13px;cursor:pointer}
.copy:hover{border-color:var(--accent)}
.desc{font-size:16px;margin:12px 0}
.tooltip{background:var(--surface);border-left:3px solid var(--accent);border-radius:0 8px 8px 0;padding:14px 16px;color:#c9d1d9;font-size:14.5px}
.nav{display:flex;justify-content:space-between;gap:12px;margin-top:28px;font-size:14px}
.cat-list{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:8px}
.cat-list a{display:block;background:var(--surface);border:1px solid var(--border);border-radius:6px;padding:8px 12px;font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cat-list a:hover{border-color:var(--accent)}
.site-footer{margin-top:40px;padding-top:16px;border-top:1px solid var(--border);font-size:13.5px;color:var(--muted)}
.site-footer p{margin:4px 0}
.site-footer a{color:var(--text)}
.search-cta{background:var(--surface);border:1px solid var(--border);border-radius:8px;padding:14px 16px;margin:20px 0;font-size:14.5px}
"""


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return re.sub(r"-+", "-", text)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def page(title: str, description: str, body: str, canonical_path: str,
         category: str = "", jsonld: str = "") -> str:
    canonical = f"{SITE_URL}/{canonical_path}"
    og_title = html.escape(title.split("—")[0].strip())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="icon" href="https://schoedeldesign.ai/wp-content/uploads/2025/08/cropped-Schoedel-Design-640-x-264-px-1-32x32.png" sizes="32x32">
<script defer data-domain="schoedeldesign.ai" src="https://analytics.schoedeldesign.ai/js/script.js"></script>
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Linux Terminal Glossary">
<meta property="og:title" content="{esc(og_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(og_title)}">
<meta name="twitter:description" content="{esc(description)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
{jsonld}
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
  <nav class="breadcrumb"><a href="{SITE_URL}/">Linux Terminal Glossary</a>{f' &rsaquo; <a href="{SITE_URL}/category/{category}">{esc(category)}</a>' if category else ''}</nav>
  {body}
  {BRAND_LINKS}
</div>
<script>
document.querySelectorAll('.copy').forEach(function (b) {{
  b.addEventListener('click', function () {{
    navigator.clipboard.writeText(b.dataset.cmd).then(function () {{
      var old = b.textContent; b.textContent = 'Copied!';
      setTimeout(function () {{ b.textContent = old; }}, 1200);
    }});
  }});
}});
</script>
</body>
</html>
"""


def main() -> None:
    data = json.loads((ROOT / "commands.json").read_text())
    commands = data["commands"]
    categories = data["categories"]
    out = OUT_DIR
    cmd_dir = out / "command"
    cat_dir = out / "category"

    # cleanup old generated trees so removed commands don't linger
    import shutil
    if cmd_dir.exists():
        shutil.rmtree(cmd_dir)
    if cat_dir.exists():
        shutil.rmtree(cat_dir)
    cmd_dir.mkdir(parents=True)
    cat_dir.mkdir(parents=True)

    by_cat: dict[str, list] = {c: [] for c in categories}
    urls = [f"{SITE_URL}/"]

    n = 0
    for c in commands:
        cmd = c["cmd"]
        desc = c.get("desc", "")
        tip = c.get("tooltip", "")
        cat = c.get("category", "Uncategorized")
        cid = c.get("id", n)
        slug = slugify(cmd)[:60] or "cmd"
        path = f"command/{slug}-{cid}/"
        rel = f"{path}index.html"
        (out / path).mkdir(parents=True, exist_ok=True)

        title = f"{cmd} — {cat} | Linux Terminal Glossary"
        description = (desc + " — " + tip)[:160]
        crumbs = {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Linux Terminal Glossary", "item": f"{SITE_URL}/"},
                {"@type": "ListItem", "position": 2, "name": cat, "item": f"{SITE_URL}/category/{slugify(cat)}/"},
                {"@type": "ListItem", "position": 3, "name": cmd},
            ],
        }
        body = f"""
  <h1><code>{esc(cmd)}</code></h1>
  <p class="subtitle">Category: <a href="{SITE_URL}/category/{slugify(cat)}/">{esc(cat)}</a></p>
  <div class="cmd">{esc(cmd)}</div>
  <button class="copy" data-cmd="{esc(cmd)}">Copy command</button>
  <p class="desc">{esc(desc)}</p>
  <div class="tooltip">{esc(tip)}</div>
  <div class="search-cta">Looking for more? <a href="{SITE_URL}/">Search all {len(commands):,} commands</a> — works offline, in English or Spanish, and fixes typos.</div>
"""
        (out / rel).write_text(page(title, description, body, path, category=cat,
                                   jsonld=f'<script type="application/ld+json">{json.dumps(crumbs)}</script>'))
        by_cat.setdefault(cat, []).append((cmd, path))
        urls.append(f"{SITE_URL}/{path}")
        n += 1

    # category index pages
    for cat, items in by_cat.items():
        cat_slug = slugify(cat)
        title = f"{cat} commands — Linux Terminal Glossary"
        description = f"{len(items)} Linux terminal commands in the {cat} category — flags, examples, and explanations."
        rows = "".join(
            f'<a href="{SITE_URL}/{path}">{esc(cmd)}</a>' for cmd, path in items
        )
        body = f"""
  <h1>{esc(cat)}</h1>
  <p class="subtitle">{len(items)} commands</p>
  <div class="cat-list">{rows}</div>
  <div class="search-cta"><a href="{SITE_URL}/">Search all {len(commands):,} commands</a> instead.</div>
"""
        (cat_dir / cat_slug).mkdir(parents=True, exist_ok=True)
        (cat_dir / cat_slug / "index.html").write_text(
            page(title, description, body, f"category/{cat_slug}/", category=cat))
        urls.append(f"{SITE_URL}/category/{cat_slug}/")

    # sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for u in urls:
        sitemap += f"  <url><loc>{u}</loc></url>\n"
    sitemap += "</urlset>\n"
    (out / "sitemap.xml").write_text(sitemap)

    (out / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: " + f"{SITE_URL}/sitemap.xml\n")

    print(f"generated {n} command pages, {len(by_cat)} category pages, sitemap.xml, robots.txt")
    print(f"site root: {SITE_URL} | output: {out}")


if __name__ == "__main__":
    main()
