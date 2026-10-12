#!/usr/bin/env python3
"""Render a web page on a GitHub runner and report what a visitor sees.

The cloud Claude session cannot open rafmall.ch, so a workflow runs this
script instead: it prints the rendered text, navigation links and stylesheet
hints to the job log (which the session can read through the API) and drops
a screenshot both into out/ (artifact) and, base64-encoded, into the log so
the session can rebuild and view it.

    python scripts/peek_site.py https://rafmall.ch
"""

from __future__ import annotations

import base64
import json
import re
import sys
from pathlib import Path


def main() -> int:
    url = sys.argv[1] if len(sys.argv) > 1 else "https://rafmall.ch"
    out = Path("out/peek")
    out.mkdir(parents=True, exist_ok=True)

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(2_000)

        info = page.evaluate("""() => {
            const css = getComputedStyle(document.body);
            const vars = {};
            const root = getComputedStyle(document.documentElement);
            for (const name of ['--background','--foreground','--primary','--primary-foreground','--secondary',
                                '--accent','--muted','--card','--border','--radius','--font-sans']) {
                const v = root.getPropertyValue(name).trim(); if (v) vars[name] = v;
            }
            const links = [...document.querySelectorAll('a[href]')].map(a => ({text: a.innerText.trim().slice(0,60), href: a.getAttribute('href')}))
                           .filter(l => l.text || l.href).slice(0, 80);
            const heads = [...document.querySelectorAll('h1,h2,h3')].map(h => h.tagName + ': ' + h.innerText.trim().slice(0,120)).slice(0, 60);
            const fonts = new Set(); document.querySelectorAll('body *').forEach(e => { if (fonts.size < 6) fonts.add(getComputedStyle(e).fontFamily); });
            return {title: document.title, lang: document.documentElement.lang,
                    bodyBg: css.backgroundColor, bodyColor: css.color, bodyFont: css.fontFamily,
                    vars, links, heads, fonts: [...fonts],
                    scripts: [...document.scripts].map(s => s.src).filter(Boolean).slice(0, 10),
                    generator: (document.querySelector('meta[name=generator]') || {}).content || '',
                    description: (document.querySelector('meta[name=description]') || {}).content || ''};
        }""")
        text = page.inner_text("body")
        png = page.screenshot(full_page=True)
        browser.close()

    (out / "page.txt").write_text(text, encoding="utf-8")
    (out / "info.json").write_text(json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8")
    (out / "screenshot.png").write_bytes(png)

    # A smaller JPEG for the log: ~900px wide, capped height, so it fits in a few thousand lines.
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(png)).convert("RGB")
        w = 900
        im = im.resize((w, int(im.height * w / im.width)))
        if im.height > 3200:
            im = im.crop((0, 0, w, 3200))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=55, optimize=True)
        small = buf.getvalue()
        (out / "screenshot_small.jpg").write_bytes(small)
    except Exception as exc:  # Pillow missing: ship the PNG instead
        print(f"[peek] bez Pillow ({exc}); kodowanie PNG", file=sys.stderr)
        small = png

    print("=== PEEK URL", url)
    print("=== INFO", json.dumps(info, ensure_ascii=False))
    print("=== TEXT BEGIN")
    print(text[:20_000])
    print("=== TEXT END")
    b64 = base64.b64encode(small).decode()
    print(f"=== IMG BEGIN {len(small)} bytes, {len(b64)} b64 chars")
    for i in range(0, len(b64), 76):
        print(b64[i:i + 76])
    print("=== IMG END")
    return 0


if __name__ == "__main__":
    sys.exit(main())
