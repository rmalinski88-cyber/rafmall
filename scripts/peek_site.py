#!/usr/bin/env python3
"""Render a web page on a GitHub runner and report what a visitor sees.

The cloud Claude session cannot open rafmall.ch, so a workflow runs this
script instead: it prints the rendered text, navigation links and stylesheet
hints to the job log (which the session can read through the API) and drops
a screenshot both into out/ (artifact) and, base64-encoded, into the log so
the session can rebuild and view it.

    python scripts/peek_site.py https://rafmall.ch
    PEEK_CLICKS="Zakładka A|Zakładka B" python scripts/peek_site.py https://rafmall.ch/portfel

Text is collected from every frame (widgets embedded as iframes included).
With PEEK_CLICKS set, each label is clicked in turn (a tab, a filter button)
and the text after the click is printed in its own block.
"""

from __future__ import annotations

import base64
import json
import os
import re
import sys
from pathlib import Path


def main() -> int:
    urls = [u.strip() for u in (sys.argv[1] if len(sys.argv) > 1 else "https://rafmall.ch").split(",") if u.strip()]
    clicks = [c.strip() for c in os.environ.get("PEEK_CLICKS", "").split("|") if c.strip()]
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        for i, url in enumerate(urls):
            peek_one(browser, url, Path("out/peek") / (str(i) if i else ""), clicks)
        browser.close()
    return 0


def page_text(page) -> str:
    """Visible text of the page and of every embedded frame."""
    parts = []
    for frame in page.frames:
        try:
            parts.append(frame.evaluate("() => document.body ? document.body.innerText : ''"))
        except Exception:  # detached frame, cross-origin oddities
            continue
    return "\n\n".join(t for t in parts if t)


def click_through(page, clicks: list[str]) -> list[tuple[str, str]]:
    """Click each label (looked up in every frame) and capture the text afterwards."""
    results = []
    for label in clicks:
        target = None
        for frame in page.frames:
            try:
                for exact in (True, False):
                    loc = frame.get_by_text(label, exact=exact)
                    if loc.count():
                        target = loc.first
                        break
                if target is not None:
                    break
            except Exception:
                continue
        if target is None:
            results.append((label, "[peek] nie znaleziono elementu o tym tekście"))
            continue
        try:
            target.click(timeout=5_000)
            page.wait_for_timeout(2_500)
            results.append((label, page_text(page)))
        except Exception as exc:
            results.append((label, f"[peek] klik nieudany: {exc}"))
    return results


def peek_one(browser, url: str, out: Path, clicks: list[str] | None = None) -> None:
    out.mkdir(parents=True, exist_ok=True)
    if True:
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        page.goto(url, wait_until="networkidle", timeout=60_000)
        # SPAs fetch their data after load: wait, scroll to the bottom (lazy content), wait again.
        page.wait_for_timeout(4_000)
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(3_000)
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(500)

        info = page.evaluate("""() => {
            const css = getComputedStyle(document.body);
            const vars = {};
            const root = getComputedStyle(document.documentElement);
            for (const name of ['--background','--foreground','--primary','--primary-foreground','--secondary',
                                '--accent','--muted','--card','--border','--radius','--font-sans']) {
                const v = root.getPropertyValue(name).trim(); if (v) vars[name] = v;
            }
            const links = [...document.querySelectorAll('a[href]')].map(a => ({text: a.innerText.trim().slice(0,60), href: a.getAttribute('href')}))
                           .filter(l => l.text || l.href).slice(0, 300);
            const heads = [...document.querySelectorAll('h1,h2,h3')].map(h => h.tagName + ': ' + h.innerText.trim().slice(0,120)).slice(0, 60);
            const fonts = new Set(); document.querySelectorAll('body *').forEach(e => { if (fonts.size < 6) fonts.add(getComputedStyle(e).fontFamily); });
            return {title: document.title, lang: document.documentElement.lang,
                    bodyBg: css.backgroundColor, bodyColor: css.color, bodyFont: css.fontFamily,
                    vars, links, heads, fonts: [...fonts],
                    scripts: [...document.scripts].map(s => s.src).filter(Boolean).slice(0, 10),
                    generator: (document.querySelector('meta[name=generator]') || {}).content || '',
                    description: (document.querySelector('meta[name=description]') || {}).content || ''};
        }""")
        info["frames"] = [{"name": f.name, "url": f.url} for f in page.frames if f is not page.main_frame]
        text = page_text(page)
        png = page.screenshot(full_page=True)
        clicked = click_through(page, clicks or [])
        page.close()

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
        if im.height > 2600:
            im = im.crop((0, 0, w, 2600))
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=50, optimize=True)
        small = buf.getvalue()
        (out / "screenshot_small.jpg").write_bytes(small)
    except Exception as exc:  # Pillow missing: ship the PNG instead
        print(f"[peek] bez Pillow ({exc}); kodowanie PNG", file=sys.stderr)
        small = png

    print("=== PEEK URL", url)
    print("=== INFO", json.dumps(info, ensure_ascii=False))
    print("=== TEXT BEGIN")
    print(text[:60_000])
    print("=== TEXT END")
    for label, body in clicked:
        print(f"=== CLICK BEGIN {label}")
        print(body[:60_000])
        print("=== CLICK END")
    b64 = base64.b64encode(small).decode()
    print(f"=== IMG BEGIN {len(small)} bytes, {len(b64)} b64 chars")
    for i in range(0, len(b64), 76):
        print(b64[i:i + 76])
    print("=== IMG END")


if __name__ == "__main__":
    sys.exit(main())
