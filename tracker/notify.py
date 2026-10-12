"""Delivery: Discord webhook (and plain text for the console)."""

from __future__ import annotations

import json
import os

from .alerts import OKAZJA, Alert

MAX_DISCORD = 1900  # Discord caps a message at 2000 characters

ICON = {OKAZJA: "🟢", "wolumen": "📊", "ruch": "⚡", "wybicie": "🚀", "trend": "📈", "smart money": "🕵️",
        "poziom": "🔑", "konfluencja": "🔥"}


def format_text(alerts: list[Alert], title: str, markdown: bool = True) -> str:
    if not alerts:
        return f"{title}\nBrak nowych anomalii."
    lines = [title if not markdown else f"**{title}**"]
    for a in alerts:
        tag = " [PORTFEL]" if a.in_portfolio else (" [okazje]" if a.on_dip_list else "")
        head = f"{ICON.get(a.kind, '•')} **{a.ticker}**{tag} {a.headline}" if markdown else f"{a.ticker}{tag}: {a.headline}"
        lines.append(f"{head}\n   {a.name} — {a.detail}")
    return "\n".join(lines)


def chunk(text: str, limit: int = MAX_DISCORD) -> list[str]:
    parts, current = [], ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > limit:
            parts.append(current)
            current = ""
        current += line + "\n"
    if current.strip():
        parts.append(current)
    return parts


def send_discord(text: str, webhook: str | None = None) -> bool:
    """Post ``text`` to a Discord webhook; ``False`` when no webhook is set."""
    webhook = webhook or os.environ.get("DISCORD_WEBHOOK_URL")
    if not webhook:
        return False
    import requests

    for part in chunk(text):
        response = requests.post(webhook, data=json.dumps({"content": part}),
                                 headers={"Content-Type": "application/json"}, timeout=20)
        response.raise_for_status()
    return True
