# setup/wtyczki

- **Stan:** scalone
- **Ostatnia zmiana:** 2026-10-12, chmura
- **Cel:** podpiąć do repo wtyczki Claude Code z rolki matkowski.ai (po weryfikacji) i Task Observera jako skill.

## Zrobione
- Weryfikacja 5 pozycji, wynik w `.claude/PLUGINS.md`; OmniRoute pominięty celowo.
- `.claude/settings.json`: marketplace'y, wtyczki claude-code-setup, claude-mem, headroom
  oraz hook SessionStart Task Observera (plik proponowany zastosowany, obserwacja 0002 `actioned`).
- Skill `.claude/skills/task-observer` (v3.6.0), workspace `.claude/task-observer-workspace`,
  hook `.claude/hooks/task-observer-session-start.sh` przetestowany na 4 scenariuszach.

## Następny krok
- Na komputerze użytkownika: `uv tool install "headroom-ai[all]"`, `headroom doctor`,
  decyzja o `headroom wrap claude`; pierwszy start claude-mem (logowanie lub
  `CLAUDE_MEM_ONLINE_OPTIN=false`); sprawdzenie w `/plugin`, że trzy wtyczki są włączone,
  i w nowej sesji, że hook startowy wstrzykuje przypomnienie task-observer.

## Uwaga dla innych sesji
- `.claude/settings.json` jest teraz docelowy; nie dopisywać ponownie wpisu
  `task-observer@one-skill-to-rule-them-all` (skill jest w repo).
- Sesje w chmurze nie ładują wtyczek z `settings.json`; to ograniczenie Claude Code, nie błąd.
