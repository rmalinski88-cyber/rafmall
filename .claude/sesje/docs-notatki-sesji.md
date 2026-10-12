# docs/notatki-sesji

- **Stan:** scalone
- **Ostatnia zmiana:** 2026-10-12, chmura
- **Cel:** dać sesjom w chmurze i na komputerze wspólne miejsce na przekazywanie pracy.

## Zrobione
- Katalog `.claude/sesje/` z zasadami i szablonem (`README.md`).
- Sekcja „Przekazywanie pracy między sesjami" w `CLAUDE.md`.

## Następny krok
- Brak. Kolejne sesje zakładają własne pliki według szablonu.

## Uwaga dla innych sesji
- Czeka na decyzję użytkownika: `.claude/settings.proposed.json` nie jest jeszcze
  zastosowany jako `.claude/settings.json` (obserwacja 0002 w logu Task Observera).
- `CLAUDE.md` nadal podaje dla chmury ścieżkę `/home/user/rafmall` (obserwacja 0001);
  używaj wyniku `git rev-parse --show-toplevel`.
