# claude/stock-search-tool-pkr8rw

- **Stan:** w toku
- **Ostatnia zmiana:** 2026-10-14, chmura (model Treli: rynek USA)
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
- Dostawca TradingView (`screener/providers/tradingview.py`): domyślne źródło; fundamenty + wskaźniki
  w jednym zapytaniu, mapowanie tickerów na giełdy, FX, samonaprawa przy odrzuconym polu.
  Nazwy pól TradingView zweryfikowane dopiero przez przebieg GitHub Actions (stąd sieć zablokowana).
- Model Treli (`python -m screener trela`, `config/trela.yml`, `screener/trela/`): 15 reguł / 129 pkt z notatek
  `docs/treli` (gałąź `docs/treli`); dane Yahoo zweryfikowane zadaniem `probe`; przebieg Actions 14.10 OK (73 spółki).
- Model Treli po przeglądzie (agent za/przeciw, 14.10): uniwersum = cały rynek USA >= 10 mld (TradingView,
  `screener/trela/universe.py`) + filtr wstępny Treli (`prefiltr` w `config/trela.yml`), humanoidy oznaczone
  (ADR-y: TSM, SONY, TM, HMC, STM, XPEV); stałe maksimum (`aktywna: false`), must-have 0/1, ceny docelowe
  korygowane o splity, spadek 45 dni liczony na stałym zbiorze firm; ostrzeżenia „nie kupuj teraz” i brak danych;
  Discord; cron `13 13 7 * *` (zadanie `trela`), stara lista globalna jako `trela_lista`.
- Przebieg Actions 14.10 (run 38583174329): 913 spółek z TradingView, filtr wstępny odciął 485, w rankingu 428,
  0 błędów pobierania (2 wątki + ponowienia; przy 4 wątkach Yahoo blokowało po ~375). Strona:
  https://claude.ai/artifact/YGXgrcgCH3L8Ca1psUCKjs. Sesja w chmurze nie pobiera artefaktów: CSV idzie do logu,
  raport odtwarza `python -m screener trela --z-csv PLIK`.
- Azja w modelu Treli: cele analityków z TradingView (`screener/trela/targets.py`, pola `price_target_*` —
  nazwy niepotwierdzone, provider odrzuca nieznane i zgłasza), historia w `.cache/trela_cele.csv` (cache Actions),
  zadanie `trela_cele` w dni robocze 9:23 UTC, `trela_lista` 7. dnia miesiąca. Linki TradingView w raportach
  (`tradingview_url` w `screener/providers/tradingview.py`). Apify: `scripts/probe_apify.py` + zadania
  `apify_szukaj` (darmowe: sklep, cenniki, schematy wejścia) i `apify_test` (limit 20 rekordów / 0,50 USD);
  czeka na sekret `APIFY_TOKEN` od użytkownika (14.10 zalogował się do Apify).

## Następny krok
- Użytkownik: włączyć GitHub Pages (Settings → Pages → Deploy from a branch → `gh-pages` / root) — bez tego
  https://rmalinski88-cyber.github.io/rafmall/ zwraca 404; wpisać sekrety `SEC_USER_AGENT`, `DISCORD_WEBHOOK_URL`;
  wkleić prompt z `START.md` §4 do Lovable (podstrona /narzedzie z iframe + kursy Portfela Trumpa z `api/instruments.json`).
- Scalone do `main` 2026-10-12 (39c9ee4); `pages.yml` buduje stronę po każdym pushu do `main` i 2× dziennie.
- Stan 14.10: Pages nadal 404, sekrety puste, /narzedzie w Lovable nie istnieje — czeka na użytkownika.
- Potem: ocena szumu alertów po tygodniu przebiegów (progi w `config/tracker.yml`), Pine Script do sprawdzenia w Pine Editorze.

## Uwaga dla innych sesji
- Gałąź domyślna na GitHubie to nadal `claude/stock-search-tool-pkr8rw`, nie `main` (wbrew `CLAUDE.md`):
  harmonogram Actions bierze workflowy i kod z tej gałęzi. Zmiana ustawienia wymaga zgody użytkownika
  (sesja dostała odmowę). Do tego czasu ta sesja trzyma `main` == swoja gałąź (fast-forward).
- Harmonogram GitHuba gubi przebiegi o pełnej godzinie (13.10: 2 z 8 alertów) i opóźnia resztę o 3–8 h;
  alerty przesunięte na minutę 17.
- `screener/report/obsidian.py` i `screener/report/views.py` są w toku — nie ruszać bez potrzeby.
- `data/samples/*.csv` to prawdziwe notowania z zadania `dump`; `ARB-USD` na Yahoo to martwy token, Arbitrum = `ARB11841-USD`.
- Decyzja o usunięciu scalonych gałęzi roboczych na GitHubie należy do użytkownika.
