# claude/stock-search-tool-pkr8rw

- **Stan:** w toku
- **Ostatnia zmiana:** 2026-10-12, chmura
- **Cel:** screener spółek robotyki humanoidalnej (fundamenty + technika) i eksport wyników do sejfu Obsidian.

## Zrobione
- Screener: pipeline, scoring centylowy, raport HTML, CSV, `validate`, `show`, strona `site` (5 sekcji + ETF).
- Tracker: Kongres/insiderzy/13F (`scan`), `alerts` (wolumen, ruch, poziomy, konfluencja, okazje, Discord),
  `market` (cały rynek: reguła `pullback` z przykładu ARB + `ema30`; kandydaci ze screenera TradingView, zapas SEC),
  `replay` (test reguły na historii), `.env`, `scripts/first_run.py`, `scripts/publish.py`, Pine Script.
- Eksport do Obsidiana: hub, notatka przebiegu, notatka per spółka z właściwościami;
  nie niszczy cudzych treści, nie dubluje istniejących notatek (`screener/report/obsidian.py`, 19 testów).
- `CLAUDE.md` (zasady pracy sesji, sekcja „Decyzje”), utworzenie gałęzi `main` jako integracyjnej.

## Następny krok
- Chmura (ta sesja): `first_run` przez GitHub Actions (`rafmall.yml`, zadanie `first_run`), odczyt logu
  przez API, poprawki tickerów i progów reguł, potem scalenie do `main`.
- Użytkownik: pierwsze uruchomienie na komputerze wg `START.md`, w tym
  `python -m screener run --obsidian-vault <ścieżka sejfu>`; przesłać log i wrażenia z Obsidiana.
- Po logu: poprawić tickery z `validate`, dopasować format notatek do `Zasady sejfu.md`
  (to wymaga sesji lokalnej z dostępem do sejfu).

## Uwaga dla innych sesji
- `screener/report/obsidian.py` i `screener/report/views.py` są w toku — nie ruszać bez potrzeby.
- Decyzja o usunięciu scalonych gałęzi roboczych na GitHubie należy do użytkownika.
