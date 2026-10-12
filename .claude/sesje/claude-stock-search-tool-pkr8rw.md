# claude/stock-search-tool-pkr8rw

- **Stan:** w toku
- **Ostatnia zmiana:** 2026-10-12, chmura
- **Cel:** narzędzie online na bazie rafmall.ch: wyszukiwarka akcji/ETF/krypto, okazje (wolumen, EMA30, pullback), portfele Trumpa i inwestorów (13F, Kongres, insiderzy); publikacja na GitHub Pages.

## Zrobione
- Screener: pipeline, scoring centylowy, raport HTML, CSV, `validate`, `show`, strona `site` (5 sekcji + ETF), eksport do Obsidiana.
- Tracker: Kongres/insiderzy/13F (`scan`), `alerts` (wolumen, ruch, poziomy, konfluencja, okazje, Discord),
  `market` (cały rynek: `pullback` z przykładu ARB + `ema30`; kandydaci ze screenera TradingView), `replay`, `dump`, `hub`.
- Praca online bez komputera: `rafmall.yml` (zadania check/first_run/alerts/market/scan/screener/site/peek/dump),
  `pages.yml` (alerty + skan + strona → gałąź `gh-pages`), sesja chmurowa czyta logi przez API GitHuba.
- Pierwszy przebieg na prawdziwych danych: 7 tickerów poprawionych, SMA50 usunięte, krypto z numerycznymi id Yahoo.
- Reguła `pullback` dostrojona na prawdziwych świecach ARB (`data/samples/ARB11841-USD.csv`): odpala 2026-08-26
  (impuls 19 sie), test `tests/test_market_samples.py`; replay pokazuje jeden sygnał na impuls jak skaner.
- `data/trump.csv`: 15 z 37 spółek Trump Portfolio Trackera (reszta po podglądzie zakładek na rafmall.ch/portfel).

## Następny krok
- Użytkownik: włączyć GitHub Pages (Settings → Pages → Deploy from a branch → `gh-pages` / root) — bez tego
  https://rmalinski88-cyber.github.io/rafmall/ zwraca 404; wpisać sekrety `SEC_USER_AGENT`, `DISCORD_WEBHOOK_URL`.
- Ta sesja: dokończyć `data/trump.csv` (peek z klikaniem zakładek), przepisać `START.md`/`README.md` na wersję online,
  scalić do `main` (uruchamia `pages.yml`).

## Uwaga dla innych sesji
- `screener/report/obsidian.py` i `screener/report/views.py` są w toku — nie ruszać bez potrzeby.
- `data/samples/*.csv` to prawdziwe notowania z zadania `dump`; `ARB-USD` na Yahoo to martwy token, Arbitrum = `ARB11841-USD`.
- Decyzja o usunięciu scalonych gałęzi roboczych na GitHubie należy do użytkownika.
