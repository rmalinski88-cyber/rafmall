---
id: 1
title: "CLAUDE.md przypina workspace dla chmury literalną ścieżką /home/user/rafmall, a klon sesji chmurowej leży w /home/claude/rafmall"
status: open
type: internal
skill: []
proposes_skill: []
target_file: ["CLAUDE.md"]
siblings_checked: "none — cel to plik instrukcji repo, nie skill; rejestru skill-families.md brak; przejrzano listę skilli tej sesji i katalog /home/claude (1 skill projektowy, task-observer)"
area: "aktywacja Task Observera — przypięcie ścieżki workspace w CLAUDE.md"
date: 2026-10-12
session_context: "Podłączenie repo rafmall do działającej sesji chmurowej (repo dołączone w trakcie sesji) i pierwszy Session Start Protocol w tym klonie"
parked_until:
resolved:
resolution:
reference:
commands_verified: "git rev-parse --show-toplevel — run, zwróciło /home/claude/rafmall; ls -d /home/user/rafmall — run, błąd No such file or directory"
---

**Issue:** `CLAUDE.md` (sekcja „Task Observer", wiersz „sesje w chmurze (claude.ai/code)") podaje workspace jako literalną ścieżkę `/home/user/rafmall/.claude/task-observer-workspace`. W tej sesji chmurowej repo zostało sklonowane do `/home/claude/rafmall` (`git rev-parse --show-toplevel` zwraca `/home/claude/rafmall`), a katalog `/home/user` w ogóle nie istnieje (`ls -d /home/user/rafmall` kończy się błędem). Zmienne `CLAUDE_PROJECT_DIR` i `TASK_OBSERVER_WORKSPACE` były nieustawione. Sesja, która wstawi do bloku aktywacyjnego ścieżkę z tego wiersza, dostanie nieudaną sondę i może błędnie uznać, że workspace nie istnieje. Gorszy wariant (wniosek z lektury komendy „Workspace creation", nie sprawdzany uruchomieniem): komenda zakłada brakujące katalogi, więc po cichu powstałby drugi, pusty workspace poza repo, który nie wędruje z gitem, a z wnętrza wygląda na kompletny. Tym razem użyto reguły z wiersza „lokalnie" (katalog główny repo z gita) i do rozszczepienia logu nie doszło.

**Suggested improvement:** W `CLAUDE.md`, sekcja „Task Observer": usunąć osobny wiersz z literalną ścieżką dla chmury i zostawić jedną regułę dla każdego środowiska — workspace to `<katalog główny repo>/.claude/task-observer-workspace`, gdzie katalog główny to wynik `git rev-parse --show-toplevel`, ustalany raz na początku sesji. Dopisać jedno zdanie: jeśli wyliczona ścieżka nie istnieje, to jest to błąd przypięcia — zgłosić, nie tworzyć. Skrypt hooka `.claude/hooks/task-observer-session-start.sh` już liczy ścieżkę z `CLAUDE_PROJECT_DIR` albo z własnego położenia, więc jest z tą regułą zgodny.

**Principle:** Miejsce na trwały stan przypina się regułą wyliczaną z checkoutu (katalog główny repozytorium), a nie literalną ścieżką prawdziwą w jednym środowisku uruchomieniowym. Literalna ścieżka, która nie istnieje, nie kończy się błędem: idempotentna komenda zakładająca strukturę tworzy ją i powstaje cichy, pusty odłamek logu.
