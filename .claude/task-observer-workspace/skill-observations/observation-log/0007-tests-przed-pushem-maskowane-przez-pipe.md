---
id: 7
title: "Reguła „testy przed pushem” złamana: `pytest | tail && git commit && git push` — rura z tail maskuje błąd (brak pytest), push poszedł bez testów"
status: open
type: internal
skill: []
proposes_skill: []
target_file: ["CLAUDE.md"]
siblings_checked: "none — cel to plik instrukcji repo, nie skill; rejestru skill-families.md brak"
area: "CLAUDE.md — Przed każdym pushem"
date: 2026-10-14
session_context: "Sesja chmurowa claude/chrome-extension-claude-code-2v7o15: pytanie o wtyczkę Chrome; stop hook zażądał commita checkpoints.log, commit i push w jednym poleceniu"
parked_until:
resolved:
resolution:
reference:
commands_verified: "python -m pytest tests/ -q 2>&1 | tail -2 && git add … && git commit … ; git push — run, wypisało „No module named pytest”, a commit i push przeszły; po pip install pytest -r requirements.txt — run, 218 passed"
---

**Issue:** Reguła z CLAUDE.md („Przed każdym pushem: python -m pytest tests/ -q; wszystkie
testy muszą przechodzić”) była w kontekście, a mimo to push poszedł bez testów. Testy
i push były jednym poleceniem `pytest … | tail -2 && git commit … ; git push`. Kod
wyjścia rury to kod `tail` (0), więc brak modułu pytest w świeżym kontenerze chmurowym
nie zatrzymał łańcucha. Testy uruchomiono dopiero po pushu (218 passed), więc szkody
nie było. Ochrona była tylko spisana i wczytana do kontekstu, nie miała punktu
kontrolnego.

**Suggested improvement:** Barierą, nie zdaniem: hook PreToolUse na `git push`
(albo pre-push git hook w repo) uruchamiający `python -m pytest tests/ -q` i odmawiający
pushu przy niezerowym kodzie. Do tego zależności w kontenerze chmurowym z setup scriptu
lub hooka SessionStart, żeby pytest był zawsze dostępny.

**Principle:** Bramka jakości sklejona rurą z poleceniem filtrującym wyjście (`| tail`,
`| head`) przestaje być bramką: łańcuch `&&` widzi kod ostatniego polecenia w rurze.
Bramkę uruchamia się osobno albo z `set -o pipefail`, a regułę „X przed Y” egzekwuje
hook na Y.
