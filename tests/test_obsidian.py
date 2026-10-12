"""Obsidian export tests.

The vault rules that matter most are the destructive ones - never lose the
owner's text or properties, never create a duplicate of a note that already
exists, never rewrite a file that did not change - so those get the most
attention here.
"""

from __future__ import annotations

import os

import pytest
import yaml

from screener.config import load_config
from screener.pipeline import run_screen
from screener.providers.fixture import FixtureProvider
from screener.report.obsidian import (
    BLOCK_END,
    BLOCK_START,
    COMPANIES_DIR,
    HUB_TITLE,
    RUNS_DIR,
    ObsidianError,
    ObsidianSettings,
    company_title,
    export_obsidian,
    merge_frontmatter,
    previous_history_rows,
    read_note,
    replace_block,
    run_title,
    safe_name,
)
from screener.universe import load_universe

START_TEXT = "# START\n\n## 01 Inwestycje\n- [[Portfel]]\n\n## 02 Baza wiedzy\n- [[AI]]\n"


@pytest.fixture(scope="module")
def config() -> dict:
    return load_config("config/default.yml")


@pytest.fixture(scope="module")
def universe():
    return load_universe("data/universe_humanoid_asia.csv")


def _result(universe, config, run_date: str = "2026-10-12"):
    result = run_screen(universe, FixtureProvider(), config, profile_name="growth")
    result.run_date = run_date
    return result


@pytest.fixture
def vault(tmp_path):
    root = tmp_path / "Rafmal1"
    root.mkdir()
    (root / "START.md").write_text(START_TEXT, encoding="utf-8")
    (root / "01-Inwestycje").mkdir()
    (root / "99-Archiwum").mkdir()
    (root / ".obsidian").mkdir()
    return root


def _settings(vault) -> ObsidianSettings:
    return ObsidianSettings(vault=vault)


def _base(vault, settings=None):
    return vault / (settings or _settings(vault)).folder


# -- naming -----------------------------------------------------------------


def test_safe_name_strips_polish_letters_and_reserved_characters():
    assert safe_name("Spółka (Test), Ltd.") == "Spolka Test Ltd"
    assert safe_name("Hon Hai Precision (Foxconn)") == "Hon Hai Precision Foxconn"
    assert safe_name("Żółć #1 [x] {y} a/b") == "Zolc 1 x y a b"
    assert safe_name("   ") == "bez nazwy"


# -- note primitives --------------------------------------------------------


def test_replace_block_appends_when_absent_and_replaces_when_present():
    block = f"{BLOCK_START}\nnew\n{BLOCK_END}"
    appended = replace_block("# Title\n\nowner text\n", block)
    assert appended.startswith("# Title\n\nowner text\n")
    assert appended.count(BLOCK_START) == 1

    replaced = replace_block(f"# T\n{BLOCK_START}\nold\n{BLOCK_END}\n\n## Mine\nkeep\n", block)
    assert "old" not in replaced
    assert "new" in replaced
    assert replaced.endswith("## Mine\nkeep\n")


def test_previous_history_rows_drops_today_and_sorts_newest_first():
    block = "\n".join(
        [
            "| Data | X |",
            "| 2026-10-05 | a |",
            "| 2026-10-12 | today |",
            "| 2026-10-19 | c |",
            "| 1 | not a date row |",
        ]
    )
    rows = previous_history_rows(block, "2026-10-12")
    assert rows == ["| 2026-10-19 | c |", "| 2026-10-05 | a |"]


def test_merge_frontmatter_keeps_owner_keys_merges_tags_and_drops_none():
    from datetime import date

    existing = {"utworzono": date(2025, 1, 1), "tags": ["watchlist"], "moja_ocena": 7, "stale": 1}
    merged = merge_frontmatter(existing, {"stale": None, "pozycja": 3}, ["screener"], date(2026, 10, 12))

    assert merged["utworzono"] == date(2025, 1, 1)
    assert merged["zaktualizowano"] == date(2026, 10, 12)
    assert merged["tags"] == ["watchlist", "screener"]
    assert merged["moja_ocena"] == 7
    assert "stale" not in merged
    assert merged["pozycja"] == 3


# -- settings ---------------------------------------------------------------


def test_from_config_requires_a_vault(config):
    with pytest.raises(ObsidianError, match="obsidian.vault"):
        ObsidianSettings.from_config(config)


def test_from_config_accepts_an_override(config, vault):
    settings = ObsidianSettings.from_config(config, str(vault))
    assert settings.vault == vault
    assert settings.folder == "01-Inwestycje/Screener robotyka"
    assert "inwestycje" in settings.tags


def test_missing_vault_raises(universe, config, tmp_path):
    with pytest.raises(ObsidianError, match="nie istnieje"):
        export_obsidian(_result(universe, config), ObsidianSettings(vault=tmp_path / "nope"))


# -- full export ------------------------------------------------------------


def test_export_creates_hub_run_and_company_notes(universe, config, vault):
    result = _result(universe, config)
    summary = export_obsidian(result, _settings(vault), config)
    base = _base(vault)

    assert (base / f"{HUB_TITLE}.md").exists()
    assert (base / RUNS_DIR / f"{run_title('2026-10-12')}.md").exists()
    assert len(summary.created) == 2 + result.screened_count
    assert summary.updated == [] and summary.unchanged == []

    hub_fm, hub_body, _ = read_note(base / f"{HUB_TITLE}.md")
    assert hub_fm["ostatni_przebieg"].isoformat() == "2026-10-12"
    assert "screener" in hub_fm["tags"]
    assert BLOCK_START in hub_body and BLOCK_END in hub_body
    assert "[[START]]" in hub_body

    ranked = result.ranked.iloc[0]
    fm, body, _ = read_note(base / COMPANIES_DIR / f"{company_title(ranked)}.md")
    assert fm["status"] == "w rankingu"
    assert fm["pozycja"] == 1
    assert isinstance(fm["wynik_laczny"], int)
    assert fm["ticker"] == ranked["ticker"]
    assert f"[[{HUB_TITLE}]]" in body
    assert "### Historia wyników" in body

    rejected = result.rejected.iloc[0]
    fm, _, _ = read_note(base / COMPANIES_DIR / f"{company_title(rejected)}.md")
    assert fm["status"] == "odrzucona"
    assert fm["powod_odrzucenia"]
    assert "wynik_laczny" not in fm


def test_start_gets_one_link_under_the_investments_heading(universe, config, vault):
    result = _result(universe, config)
    first = export_obsidian(result, _settings(vault), config)
    assert first.start_status == "dodano link w sekcji Inwestycje"

    text = (vault / "START.md").read_text(encoding="utf-8")
    inv, kb = text.index("## 01 Inwestycje"), text.index("## 02 Baza wiedzy")
    link = text.index(f"- [[{HUB_TITLE}]]")
    assert inv < link < kb

    second = export_obsidian(result, _settings(vault), config)
    assert second.start_status == "link już był"
    assert (vault / "START.md").read_text(encoding="utf-8").count(f"[[{HUB_TITLE}]]") == 1


def test_start_without_investments_heading_gets_link_at_end(universe, config, vault):
    (vault / "START.md").write_text("# START\n\n## Notatki\n- [[A]]\n", encoding="utf-8")
    summary = export_obsidian(_result(universe, config), _settings(vault), config)
    assert "na końcu" in summary.start_status
    assert (vault / "START.md").read_text(encoding="utf-8").endswith(f"- [[{HUB_TITLE}]]\n")


def test_rerun_on_the_same_day_changes_nothing(universe, config, vault):
    result = _result(universe, config)
    export_obsidian(result, _settings(vault), config)
    again = export_obsidian(result, _settings(vault), config)

    assert again.created == [] and again.updated == []
    assert len(again.unchanged) == 2 + result.screened_count

    hub_body = read_note(_base(vault) / f"{HUB_TITLE}.md")[1]
    assert hub_body.count("| 2026-10-12 |") == 1


def test_unchanged_note_is_not_rewritten(universe, config, vault):
    result = _result(universe, config)
    export_obsidian(result, _settings(vault), config)

    hub = _base(vault) / f"{HUB_TITLE}.md"
    old = 1_600_000_000
    os.utime(hub, (old, old))
    export_obsidian(result, _settings(vault), config)
    assert int(hub.stat().st_mtime) == old


def test_history_accumulates_across_runs(universe, config, vault):
    export_obsidian(_result(universe, config, "2026-10-12"), _settings(vault), config)
    second = _result(universe, config, "2026-10-19")
    summary = export_obsidian(second, _settings(vault), config)
    base = _base(vault)

    # One new run note; hub and every company note updated in place.
    assert len(summary.created) == 1
    assert (base / RUNS_DIR / f"{run_title('2026-10-19')}.md").exists()
    assert (base / RUNS_DIR / f"{run_title('2026-10-12')}.md").exists()

    hub_body = read_note(base / f"{HUB_TITLE}.md")[1]
    assert hub_body.index("| 2026-10-19 |") < hub_body.index("| 2026-10-12 |")

    company = base / COMPANIES_DIR / f"{company_title(second.ranked.iloc[0])}.md"
    body = read_note(company)[1]
    assert "| 2026-10-19 |" in body and "| 2026-10-12 |" in body


def test_owner_text_and_properties_survive_a_rerun(universe, config, vault):
    first = _result(universe, config, "2026-10-12")
    export_obsidian(first, _settings(vault), config)
    path = _base(vault) / COMPANIES_DIR / f"{company_title(first.ranked.iloc[0])}.md"

    text = path.read_text(encoding="utf-8")
    text = text.replace("---\n", "---\nmoja_ocena: 7\n", 1)
    text = text.replace("tags:\n", "tags:\n- watchlist\n", 1)
    text += "\n## Moje notatki\nKupić poniżej 100.\n"
    path.write_text(text, encoding="utf-8")

    export_obsidian(_result(universe, config, "2026-10-19"), _settings(vault), config)
    fm, body, _ = read_note(path)

    assert fm["moja_ocena"] == 7
    assert "watchlist" in fm["tags"] and "screener" in fm["tags"]
    assert fm["zaktualizowano"].isoformat() == "2026-10-19"
    assert body.endswith("## Moje notatki\nKupić poniżej 100.\n")
    assert "2026-10-19" in body
    assert body.count(BLOCK_START) == 1


def test_existing_note_elsewhere_is_updated_instead_of_duplicated(universe, config, vault):
    result = _result(universe, config)
    title = company_title(result.ranked.iloc[0])
    elsewhere = vault / "01-Inwestycje" / f"{title}.md"
    elsewhere.write_text(f"# {title}\n\nMoja stara notatka.\n", encoding="utf-8")

    export_obsidian(result, _settings(vault), config)

    assert not (_base(vault) / COMPANIES_DIR / f"{title}.md").exists()
    fm, body, _ = read_note(elsewhere)
    assert "Moja stara notatka." in body
    assert BLOCK_START in body
    assert fm["ticker"] == result.ranked.iloc[0]["ticker"]


def test_archived_notes_are_not_treated_as_existing(universe, config, vault):
    result = _result(universe, config)
    title = company_title(result.ranked.iloc[0])
    archived = vault / "99-Archiwum" / f"{title}.md"
    archived.write_text("stare\n", encoding="utf-8")

    export_obsidian(result, _settings(vault), config)

    assert (_base(vault) / COMPANIES_DIR / f"{title}.md").exists()
    assert archived.read_text(encoding="utf-8") == "stare\n"


def test_unparseable_frontmatter_is_skipped_not_corrupted(universe, config, vault):
    result = _result(universe, config)
    title = company_title(result.ranked.iloc[0])
    broken = _base(vault) / COMPANIES_DIR / f"{title}.md"
    broken.parent.mkdir(parents=True)
    broken_text = "---\ntags: [unclosed\n---\n# X\n"
    broken.write_text(broken_text, encoding="utf-8")

    summary = export_obsidian(result, _settings(vault), config)

    assert broken.read_text(encoding="utf-8") == broken_text
    assert len(summary.skipped) == 1 and "YAML" in summary.skipped[0]


def test_company_notes_can_be_disabled(universe, config, vault):
    settings = ObsidianSettings(vault=vault, company_notes=False)
    result = _result(universe, config)
    summary = export_obsidian(result, settings, config)

    assert len(summary.created) == 2
    assert not (_base(vault, settings) / COMPANIES_DIR).exists()
    hub_body = read_note(_base(vault, settings) / f"{HUB_TITLE}.md")[1]
    assert f"[[{company_title(result.ranked.iloc[0])}]]" not in hub_body


def test_written_notes_are_valid_yaml_frontmatter(universe, config, vault):
    export_obsidian(_result(universe, config), _settings(vault), config)
    for path in _base(vault).rglob("*.md"):
        fm, _, raw = read_note(path)
        assert fm is not None, path
        assert raw.startswith("---\n")
        yaml.safe_load(raw.split("---\n")[1])
