"""Export a screen into an Obsidian vault.

Three kinds of note are written, all plain Markdown with YAML properties so
Obsidian's own Bases/Dataview views can sort and filter them:

* **hub** - one note for the topic, always showing the latest ranking plus a
  history table that accumulates across runs;
* **run** - one dated note per screening run, with the full ranking, the
  rejected names and the parameters used;
* **company** - one note per company in the universe, with the scores as
  properties and a per-company history table.

Rules the vault owner set, and that this module follows:

* Nothing is ever deleted and nothing is recreated from memory: an existing
  note is edited in place.  Everything the screener owns lives between two
  marker comments; text outside them - the owner's own notes - is untouched,
  and properties the screener does not know are kept.
* A note on the same company that already exists elsewhere in the vault is
  updated there instead of a duplicate being created next to it.
* File names carry no Polish letters and none of ``# [ ] ( ) { } , .``.
* Writes are skipped when nothing changed, since the vault sits in iCloud
  and every rewrite is a sync.
"""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

from ..pipeline import ScreenResult
from . import format as fmt
from .views import FUNDAMENTAL_VIEW, TECHNICAL_VIEW, format_metric, label

HUB_TITLE = "Screener robotyka humanoidalna Azja"
RUN_PREFIX = "Screener przebieg"
RUNS_DIR = "Przebiegi"
COMPANIES_DIR = "Spolki"
START_NOTE = "START.md"

BLOCK_START = "<!-- screener:start -->"
BLOCK_END = "<!-- screener:end -->"
BLOCK_NOTICE = (
    "> [!info] Sekcja generowana automatycznie przez screener.\n"
    "> Zmiany wewnątrz niej zostaną nadpisane przy kolejnym przebiegu. "
    "Własne notatki dopisuj poniżej znacznika końca sekcji."
)

DISCLAIMER = (
    "Wyniki to pozycje centylowe wewnątrz tego uniwersum, nie oceny bezwzględne. "
    "To nie jest rekomendacja inwestycyjna."
)

_POLISH = str.maketrans("ąćęłńóśźżĄĆĘŁŃÓŚŹŻ", "acelnoszzACELNOSZZ")
_FORBIDDEN = re.compile(r'[#\[\]\(\)\{\},\.\\/:*?"<>|]')
_SKIP_DIRS = {".obsidian", ".trash", "99-Archiwum", "98-Zalaczniki"}
_HISTORY_LIMIT = 120


class ObsidianError(RuntimeError):
    """The vault cannot be written at all (missing path, unreadable note)."""


@dataclass
class ObsidianSettings:
    vault: Path
    folder: str = "01-Inwestycje/Screener robotyka"
    top: int = 15
    tags: list[str] = field(
        default_factory=lambda: ["inwestycje", "akcje", "screener", "robotyka-humanoidalna"]
    )
    company_notes: bool = True
    update_start: bool = True

    @classmethod
    def from_config(cls, config: dict, vault_override: str | None = None) -> "ObsidianSettings":
        block = config.get("obsidian") or {}
        vault = vault_override or block.get("vault")
        if not vault:
            raise ObsidianError(
                "brak ścieżki do sejfu - ustaw obsidian.vault w konfiguracji "
                "albo podaj --obsidian-vault"
            )
        settings = cls(vault=Path(str(vault)).expanduser())
        if block.get("folder"):
            settings.folder = str(block["folder"]).strip("/\\")
        if block.get("top") is not None:
            settings.top = int(block["top"])
        if block.get("tags"):
            settings.tags = [str(t) for t in block["tags"]]
        if block.get("company_notes") is not None:
            settings.company_notes = bool(block["company_notes"])
        if block.get("update_start") is not None:
            settings.update_start = bool(block["update_start"])
        return settings


@dataclass
class ObsidianSummary:
    created: list[Path] = field(default_factory=list)
    updated: list[Path] = field(default_factory=list)
    unchanged: list[Path] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    start_status: str = "pominięto"
    hub_path: Path | None = None

    def describe(self) -> str:
        lines = [
            f"Obsidian: utworzono {len(self.created)}, zaktualizowano {len(self.updated)}, "
            f"bez zmian {len(self.unchanged)}; START.md: {self.start_status}",
        ]
        if self.hub_path:
            lines.append(f"  hub: {self.hub_path}")
        lines.extend(f"  pominięto: {reason}" for reason in self.skipped)
        return "\n".join(lines)


# -- naming ------------------------------------------------------------------


def safe_name(text: str) -> str:
    """A file/basename the vault rules allow: ASCII letters, no reserved chars."""
    text = (text or "").translate(_POLISH)
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = _FORBIDDEN.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text or "bez nazwy"


def run_title(run_date: str) -> str:
    return f"{RUN_PREFIX} {run_date}"


def company_title(record: dict) -> str:
    return safe_name(record.get("name") or record.get("ticker") or "")


# -- note I/O -----------------------------------------------------------------

_FRONTMATTER = re.compile(r"\A---[ \t]*\r?\n(.*?)\r?\n---[ \t]*\r?\n?", re.DOTALL)
_BLOCK = re.compile(re.escape(BLOCK_START) + r".*?" + re.escape(BLOCK_END), re.DOTALL)
_DATED_ROW = re.compile(r"^\| (\d{4}-\d{2}-\d{2}) \|.*$", re.MULTILINE)


def read_note(path: Path) -> tuple[dict | None, str, str]:
    """``(frontmatter, body, raw_text)``; frontmatter is ``None`` when unparseable."""
    raw = path.read_text(encoding="utf-8")
    match = _FRONTMATTER.match(raw)
    if not match:
        return {}, raw, raw
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None, raw, raw
    if data is None:
        data = {}
    if not isinstance(data, dict):
        return None, raw, raw
    return data, raw[match.end():], raw


class _FrontmatterDumper(yaml.SafeDumper):
    """SafeDumper without anchors.

    The same ``date`` object lands in several properties; PyYAML would emit
    ``&id001`` / ``*id001`` for the repeats, which Obsidian does not read as
    a date and which makes byte-identical content serialise differently from
    one run to the next.
    """

    def ignore_aliases(self, data) -> bool:
        return True


def compose_note(frontmatter: dict, body: str) -> str:
    dumped = yaml.dump(
        frontmatter,
        Dumper=_FrontmatterDumper,
        allow_unicode=True,
        sort_keys=False,
        default_flow_style=False,
    ).rstrip("\n")
    return f"---\n{dumped}\n---\n{body}"


def replace_block(body: str, block: str) -> str:
    """Swap the managed block in, or append it when the note has none."""
    if _BLOCK.search(body):
        return _BLOCK.sub(lambda _match: block, body, count=1)
    if not body.strip():
        return block + "\n"
    stripped = body.rstrip("\n")
    return f"{stripped}\n\n{block}\n"


def existing_block(body: str) -> str:
    match = _BLOCK.search(body)
    return match.group(0) if match else ""


def previous_history_rows(block: str, today: str) -> list[str]:
    """Date-keyed table rows from the old block, minus today's (re-run)."""
    rows = [m.group(0) for m in _DATED_ROW.finditer(block) if m.group(1) != today]
    rows.sort(key=lambda line: line[2:12], reverse=True)
    return rows[:_HISTORY_LIMIT]


def merge_frontmatter(existing: dict, updates: dict, tags: list[str], today: date) -> dict:
    """Owner's keys kept; screener's keys set; ``None`` removes a stale key."""
    merged = dict(existing)
    merged.setdefault("utworzono", today)
    merged["zaktualizowano"] = today

    old_tags = merged.get("tags") or []
    if isinstance(old_tags, str):
        old_tags = [old_tags]
    merged["tags"] = list(dict.fromkeys([*[str(t) for t in old_tags], *tags]))

    for key, value in updates.items():
        if value is None:
            merged.pop(key, None)
        else:
            merged[key] = value
    return merged


# -- vault index -------------------------------------------------------------


def index_vault(vault: Path) -> dict[str, list[Path]]:
    """Lower-cased basename -> every note with that name (archive excluded)."""
    index: dict[str, list[Path]] = {}
    for root, dirs, files in os.walk(vault):
        dirs[:] = [d for d in dirs if d not in _SKIP_DIRS and not d.startswith(".")]
        for name in files:
            if name.lower().endswith(".md"):
                index.setdefault(name[:-3].lower(), []).append(Path(root) / name)
    return index


def resolve_note_path(index: dict, title: str, preferred_dir: Path) -> Path:
    """Where a note with this title lives, or where it should be created."""
    candidates = index.get(title.lower(), [])
    for path in candidates:
        if path.parent == preferred_dir:
            return path
    if candidates:
        return candidates[0]
    return preferred_dir / f"{title}.md"


# -- export ------------------------------------------------------------------


def export_obsidian(result: ScreenResult, settings: ObsidianSettings, config: dict | None = None) -> ObsidianSummary:
    vault = settings.vault
    if not vault.exists() or not vault.is_dir():
        raise ObsidianError(f"sejf nie istnieje albo nie jest katalogiem: {vault}")

    base = vault / settings.folder
    runs_dir = base / RUNS_DIR
    companies_dir = base / COMPANIES_DIR
    today = date.fromisoformat(result.run_date)
    summary = ObsidianSummary()
    index = index_vault(vault)

    ranked = result.ranked
    rejected = result.rejected
    top_names = [company_title(r) for r in ranked.head(3).to_dict("records")]

    # Run note first: the hub and company notes link to it.
    run_path = resolve_note_path(index, run_title(result.run_date), runs_dir)
    _write(
        run_path,
        updates={
            "zrodlo": _source(result),
            "profil": result.profile_name,
            "dostawca": result.provider_name,
            "w_rankingu": int(len(ranked)),
            "uniwersum": int(result.screened_count),
        },
        tags=[*settings.tags, "przebieg"],
        title=f"Screener robotyki humanoidalnej — przebieg {result.run_date}",
        block_builder=lambda _old: _run_block(result, settings, config or {}),
        today=today,
        summary=summary,
    )

    hub_path = resolve_note_path(index, HUB_TITLE, base)
    _write(
        hub_path,
        updates={
            "zrodlo": _source(result),
            "ostatni_przebieg": today,
            "profil": result.profile_name,
            "w_rankingu": int(len(ranked)),
            "uniwersum": int(result.screened_count),
        },
        tags=settings.tags,
        title="Screener robotyki humanoidalnej — Azja",
        block_builder=lambda old: _hub_block(result, settings, old, top_names),
        today=today,
        summary=summary,
    )
    summary.hub_path = hub_path

    if settings.company_notes:
        positions = {t: i for i, t in enumerate(ranked["ticker"], start=1)}
        for record in [*ranked.to_dict("records"), *rejected.to_dict("records")]:
            title = company_title(record)
            path = resolve_note_path(index, title, companies_dir)
            position = positions.get(record["ticker"])
            _write(
                path,
                updates=_company_properties(record, position, result, today),
                tags=[*settings.tags, "spolka"],
                title=record.get("name") or record["ticker"],
                block_builder=lambda old, r=record, p=position: _company_block(r, p, result, old, settings),
                today=today,
                summary=summary,
            )

    summary.start_status = (
        _link_in_start(vault, HUB_TITLE) if settings.update_start else "pominięto"
    )
    return summary


def _write(path: Path, *, updates: dict, tags: list[str], title: str, block_builder, today: date, summary: ObsidianSummary) -> None:
    """Create or update one note, preserving whatever is not the screener's."""
    if path.exists():
        frontmatter, body, raw = read_note(path)
        if frontmatter is None:
            summary.skipped.append(f"{path} - nie udało się odczytać właściwości (YAML)")
            return
        existed = True
    else:
        frontmatter, body, raw, existed = {}, f"# {title}\n", None, False

    block = block_builder(existing_block(body))
    new_text = compose_note(merge_frontmatter(frontmatter, updates, tags, today), replace_block(body, block))

    if existed and new_text == raw:
        summary.unchanged.append(path)
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(new_text)
    (summary.updated if existed else summary.created).append(path)


# -- note content ------------------------------------------------------------


def _source(result: ScreenResult) -> str:
    return f"screener rafmall ({result.provider_name})"


def _wrap(sections: list[str]) -> str:
    inner = "\n\n".join(s.strip("\n") for s in sections if s and s.strip())
    return f"{BLOCK_START}\n{BLOCK_NOTICE}\n\n{inner}\n{BLOCK_END}"


def _link(title: str, enabled: bool = True) -> str:
    return f"[[{title}]]" if enabled else title


def _table(header: list[str], rows: list[list[str]]) -> str:
    if not rows:
        return "_brak_"
    lines = ["| " + " | ".join(header) + " |", "|" + "|".join(["---"] * len(header)) + "|"]
    lines.extend("| " + " | ".join(_cell(c) for c in row) + " |" for row in rows)
    return "\n".join(lines)


def _cell(value) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _join_names(names: list[str], link: bool) -> str:
    return ", ".join(_link(n, link) for n in names) if names else "—"


def _run_block(result: ScreenResult, settings: ObsidianSettings, config: dict) -> str:
    ranked, rejected = result.ranked, result.rejected
    link = settings.company_notes
    top3 = [company_title(r) for r in ranked.head(3).to_dict("records")]

    summary = (
        f"Przebieg z {result.run_date}: profil **{result.profile_name}**, źródło "
        f"{result.provider_name}, {result.screened_count} spółek w uniwersum, "
        f"**{len(ranked)} w rankingu**, {len(rejected)} odrzuconych przez filtry. "
        f"Czołówka: {_join_names(top3, link)}.\n\n{DISCLAIMER}"
    )

    ranking_rows = [
        [
            str(i),
            _link(company_title(r), link),
            r["ticker"],
            r.get("market") or "—",
            r.get("segment") or "—",
            fmt.score(r.get("composite_score")),
            fmt.score(r.get("fundamental_score")),
            fmt.score(r.get("technical_score")),
            fmt.pct(r.get("fundamental_coverage"), digits=0),
            fmt.usd(r.get("market_cap_usd")),
            fmt.pct(r.get("revenue_growth"), signed=True),
            fmt.pct(r.get("return_on_equity")),
            fmt.pct(r.get("px_vs_sma200"), signed=True),
            fmt.pct(r.get("rs_6m"), signed=True),
        ]
        for i, r in enumerate(ranked.to_dict("records"), start=1)
    ]
    ranking = _table(
        ["#", "Spółka", "Ticker", "Rynek", "Segment", "Łącznie", "Fund.", "Tech.",
         "Pokrycie", "Kapitalizacja", "Wzrost przych.", "ROE", "vs SMA200", "RS 6M"],
        ranking_rows,
    )

    rejected_rows = [
        [_link(company_title(r), link), r["ticker"], r.get("market") or "—", r.get("excluded_reason") or "—"]
        for r in rejected.to_dict("records")
    ]
    rejected_table = _table(["Spółka", "Ticker", "Rynek", "Powód"], rejected_rows)

    filters = (config.get("filters") or {}) if config else {}
    params = [
        f"- profil scoringu: `{result.profile_name}`",
        f"- źródło danych: `{result.provider_name}`",
        f"- spółek w uniwersum: {result.screened_count}",
    ]
    params.extend(f"- filtr `{k}`: {v}" for k, v in filters.items() if v is not None)

    warnings = ""
    if result.warnings:
        warnings = "### Ostrzeżenia\n" + "\n".join(f"- {w}" for w in result.warnings[:30])

    return _wrap(
        [
            f"## W skrócie\n{summary}",
            f"## Szczegóły\n### Ranking\n{ranking}",
            f"### Odrzucone przez filtry ({len(rejected)})\n{rejected_table}",
            warnings,
            "### Parametry przebiegu\n" + "\n".join(params),
            f"## Powiązane\n- [[{HUB_TITLE}]]\n- [[START]]",
        ]
    )


def _hub_block(result: ScreenResult, settings: ObsidianSettings, old_block: str, top_names: list[str]) -> str:
    ranked = result.ranked
    link = settings.company_notes
    run_link = f"[[{run_title(result.run_date)}]]"

    summary = (
        "Ranking spółek z ekspozycją na robotykę humanoidalną (Japonia, Korea, Tajwan, "
        "Chiny/HK), liczony przez screener `rafmall` z oceną fundamentalną i techniczną.\n\n"
        f"Ostatni przebieg: **{result.run_date}**, profil **{result.profile_name}**, "
        f"źródło {result.provider_name} — w rankingu {len(ranked)} z {result.screened_count} "
        f"spółek. Czołówka: {_join_names(top_names, link)}.\n\n{DISCLAIMER}"
    )

    top_rows = [
        [
            str(i),
            _link(company_title(r), link),
            r.get("market") or "—",
            r.get("segment") or "—",
            fmt.score(r.get("composite_score")),
            fmt.score(r.get("fundamental_score")),
            fmt.score(r.get("technical_score")),
            fmt.pct(r.get("fundamental_coverage"), digits=0),
        ]
        for i, r in enumerate(ranked.head(settings.top).to_dict("records"), start=1)
    ]
    top_table = _table(["#", "Spółka", "Rynek", "Segment", "Łącznie", "Fund.", "Tech.", "Pokrycie"], top_rows)

    today_row = (
        f"| {result.run_date} | {run_link} | {result.profile_name} | "
        f"{len(ranked)} / {result.screened_count} | {_join_names(top_names, link)} |"
    )
    history_rows = [today_row, *previous_history_rows(old_block, result.run_date)]
    history = "\n".join(
        ["| Data | Przebieg | Profil | W rankingu | Czołówka |", "|---|---|---|---|---|", *history_rows]
    )

    how_to_read = "\n".join(
        [
            "- Każdy wskaźnik to pozycja centylowa wśród spółek, które przeszły filtry. "
            "Zmiana uniwersum zmienia każdy wynik.",
            "- **Pokrycie** mówi, jaka część wskaźników fundamentalnych była dostępna u dostawcy. "
            "Wynik przy niskim pokryciu znaczy mniej.",
            "- Ujemne C/Z jest pomijane, nie odwracane: spółka ze stratą nie jest „tania”.",
            "- Pełny ranking, odrzucone spółki i parametry są w notatce każdego przebiegu.",
        ]
    )

    related = [f"- {run_link}", "- [[START]]"]
    if link:
        related.append(f"- Notatki spółek: `{settings.folder}/{COMPANIES_DIR}`")

    return _wrap(
        [
            f"## W skrócie\n{summary}",
            f"## Szczegóły\n### Aktualny ranking (top {settings.top})\n{top_table}\n\n"
            f"Pełny ranking i lista odrzuconych: {run_link}.",
            f"### Historia przebiegów\n{history}",
            f"### Jak czytać wyniki\n{how_to_read}",
            "## Powiązane\n" + "\n".join(related),
        ]
    )


def _company_properties(record: dict, position: int | None, result: ScreenResult, today: date) -> dict:
    in_ranking = position is not None
    cap = record.get("market_cap_usd")
    return {
        "zrodlo": _source(result),
        "ticker": record["ticker"],
        "nazwa": record.get("name") or record["ticker"],
        "rynek": record.get("market") or None,
        "segment": record.get("segment") or None,
        "status": "w rankingu" if in_ranking else "odrzucona",
        "powod_odrzucenia": None if in_ranking else (record.get("excluded_reason") or "nieznany"),
        "pozycja": position,
        "wynik_laczny": _int(record.get("composite_score")) if in_ranking else None,
        "wynik_fundamentalny": _int(record.get("fundamental_score")) if in_ranking else None,
        "wynik_techniczny": _int(record.get("technical_score")) if in_ranking else None,
        "pokrycie_fund_pct": _int(_times(record.get("fundamental_coverage"), 100)) if in_ranking else None,
        "kapitalizacja_usd_mln": _int(_times(cap, 1e-6)),
        "ostatni_przebieg": today,
        "profil": result.profile_name,
    }


def _company_block(record: dict, position: int | None, result: ScreenResult, old_block: str, settings: ObsidianSettings) -> str:
    name = record.get("name") or record["ticker"]
    run_link = f"[[{run_title(result.run_date)}]]"
    in_ranking = position is not None

    if in_ranking:
        status = (
            f"W przebiegu z {result.run_date} (profil {result.profile_name}) pozycja "
            f"**{position} z {len(result.ranked)}**, wynik łączny **{fmt.score(record.get('composite_score'))}** "
            f"(fundamenty {fmt.score(record.get('fundamental_score'))}, technika "
            f"{fmt.score(record.get('technical_score'))}, pokrycie danych "
            f"{fmt.pct(record.get('fundamental_coverage'), digits=0)})."
        )
    else:
        status = (
            f"W przebiegu z {result.run_date} spółka **nie weszła do rankingu** — "
            f"powód: {record.get('excluded_reason') or 'nieznany'}."
        )

    summary = (
        f"{name} ({record['ticker']}) — {record.get('market') or '—'}, segment "
        f"{record.get('segment') or '—'}. {record.get('notes') or ''}\n\n{status}\n\n{DISCLAIMER}"
    )

    fundamentals = _table(
        ["Wskaźnik", "Wartość"],
        [[label(k), format_metric(k, kind, record.get(k))] for k, kind in FUNDAMENTAL_VIEW],
    )
    technicals = _table(
        ["Wskaźnik", "Wartość"],
        [[label(k), format_metric(k, kind, record.get(k))] for k, kind in TECHNICAL_VIEW],
    )

    today_row = "| {date} | {pos} | {total} | {fund} | {tech} | {profile} |".format(
        date=result.run_date,
        pos=position if in_ranking else "—",
        total=fmt.score(record.get("composite_score")) if in_ranking else "odrzucona",
        fund=fmt.score(record.get("fundamental_score")) if in_ranking else "—",
        tech=fmt.score(record.get("technical_score")) if in_ranking else "—",
        profile=result.profile_name,
    )
    history_rows = [today_row, *previous_history_rows(old_block, result.run_date)]
    history = "\n".join(
        ["| Data | Pozycja | Łącznie | Fund. | Tech. | Profil |", "|---|---|---|---|---|---|", *history_rows]
    )

    return _wrap(
        [
            f"## W skrócie\n{summary}",
            f"## Szczegóły\n### Fundamenty\n{fundamentals}",
            f"### Technika\n{technicals}",
            f"### Historia wyników\n{history}",
            f"## Powiązane\n- [[{HUB_TITLE}]]\n- {run_link}\n- [[START]]",
        ]
    )


# -- START.md ----------------------------------------------------------------


def _link_in_start(vault: Path, hub_title: str) -> str:
    """Add one link to the hub under the investments heading of START.md."""
    path = vault / START_NOTE
    if not path.exists():
        return "brak pliku START.md"

    text = path.read_text(encoding="utf-8")
    if f"[[{hub_title}" in text:
        return "link już był"

    lines = text.splitlines(keepends=True)
    heading = next(
        (i for i, line in enumerate(lines) if line.lstrip().startswith("#") and "inwestycje" in line.lower()),
        None,
    )
    entry = f"- [[{hub_title}]]\n"

    if heading is None:
        new_text = text.rstrip("\n") + f"\n\n{entry}" if text.strip() else entry
        status = "dodano link na końcu (brak sekcji Inwestycje)"
    else:
        end = next(
            (i for i in range(heading + 1, len(lines)) if lines[i].lstrip().startswith("#")),
            len(lines),
        )
        insert_at = end
        while insert_at > heading + 1 and not lines[insert_at - 1].strip():
            insert_at -= 1
        if insert_at > 0 and not lines[insert_at - 1].endswith("\n"):
            lines[insert_at - 1] += "\n"
        lines.insert(insert_at, entry)
        new_text = "".join(lines)
        status = "dodano link w sekcji Inwestycje"

    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(new_text)
    return status


# -- small helpers -----------------------------------------------------------


def _int(value) -> int | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return None


def _times(value, factor: float) -> float | None:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    try:
        return float(value) * factor
    except (TypeError, ValueError):
        return None
