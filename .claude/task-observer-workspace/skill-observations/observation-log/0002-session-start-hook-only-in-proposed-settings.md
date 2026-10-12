---
id: 2
title: "Hook SessionStart Task Observera jest opisany jako działający, a w repo wpisano go tylko do .claude/settings.proposed.json"
status: open
type: internal
skill: []
proposes_skill: []
target_file: [".claude/PLUGINS.md", ".claude/settings.json", "CLAUDE.md"]
siblings_checked: "none — cel to pliki konfiguracji i dokumentacji repo, nie skill; rejestru skill-families.md brak; przejrzano listę skilli tej sesji i katalog /home/claude (1 skill projektowy, task-observer)"
area: "aktywacja Task Observera — hook SessionStart i jego opis w dokumentacji"
date: 2026-10-12
session_context: "Podłączenie repo rafmall do działającej sesji chmurowej i pierwszy Session Start Protocol w tym klonie; stan repo z commita ece33d6 na gałęzi domyślnej"
parked_until:
resolved:
resolution:
reference:
commands_verified: "grep -c hooks .claude/settings.json — run, zwróciło 0; grep -c hooks .claude/settings.proposed.json — run, zwróciło 3; grep -n -i proposed .claude/PLUGINS.md README.md START.md CLAUDE.md — run, brak trafień"
---

**Issue:** `.claude/PLUGINS.md` („aktywacja: blok w CLAUDE.md plus hook SessionStart…") i `CLAUDE.md` („Hook SessionStart podaje gotową ścieżkę") opisują hook `.claude/hooks/task-observer-session-start.sh` jako działającą warstwę aktywacji. W stanie wypchniętym na gałąź domyślną (commit ece33d6) aktywny `.claude/settings.json` nie ma sekcji `hooks` (`grep -c hooks .claude/settings.json` zwraca 0). Sekcja `hooks.SessionStart` jest tylko w `.claude/settings.proposed.json` (`grep -c hooks .claude/settings.proposed.json` zwraca 3), a o tym pliku nie wspomina żaden dokument (`grep -n -i proposed .claude/PLUGINS.md README.md START.md CLAUDE.md` nie daje trafień). Oba pliki różnią się też wtyczkami: aktywny nadal rejestruje marketplace `one-skill-to-rule-them-all` i włącza `task-observer@one-skill-to-rule-them-all`, proponowany już nie. Skutek: z samego repo hook nie jest podpięty, a dokumentacja opisuje stan zamierzony jako faktyczny. Nie sprawdzano konfiguracji lokalnej użytkownika — `.claude/settings.local.json` jest w `.gitignore`, więc lokalnie hook może być podpięty.

**Suggested improvement:** Decyzja użytkownika, jedna z dwóch: (a) zastąpić `.claude/settings.json` treścią `.claude/settings.proposed.json` i usunąć plik proponowany; (b) zostawić jak jest i dopisać w `.claude/PLUGINS.md` jedno zdanie, że hook czeka w `settings.proposed.json` na ręczne zastosowanie. W obu wariantach `PLUGINS.md` i `CLAUDE.md` mają opisywać hook zgodnie ze stanem faktycznym.

**Principle:** Krok konfiguracji odłożony do ręcznego zastosowania (plik „proponowany") nie jest wykonany, dopóki ktoś nie zobaczył go w działaniu. Dokumentacja ma odróżniać „zaproponowane, czeka na zastosowanie" od „działa" i wskazywać plik, który czeka — inaczej kolejne sesje liczą na ochronę, której nie ma.
