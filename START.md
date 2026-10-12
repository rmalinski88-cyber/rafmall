# Narzędzie rafmall — jak działa i co zrobić raz

> Zasady wspólnej pracy sesji Claude na tym repo (gałęzie, pliki wspólne, testy
> przed pushem): **`CLAUDE.md`**. Każda sesja czyta go na starcie.

Stan: **narzędzie działa online, bez Twojego komputera.** Dane liczą się na
serwerach GitHuba (GitHub Actions) na prawdziwych notowaniach — Yahoo Finance,
SEC EDGAR, screener TradingView — a wynik to zestaw stron i plików JSON
publikowanych na GitHub Pages. Rafmall.ch (Lovable) osadza je jedną podstroną.
Pierwsze przebiegi na prawdziwych danych już były: 230 tickerów sprawdzonych,
reguła wejścia dostrojona na prawdziwych świecach ARB z sierpnia 2026 (test
w repo), skan rynku USA przez TradingView zwraca kandydatów.

## 1. Dwie rzeczy, które robi narzędzie

| | Strona | Co pokazuje | Źródło |
|---|---|---|---|
| **A. Wyszukiwanie akcji, ETF, krypto** | `szukaj.html` | wyszukiwarka po nazwie lub tickerze: kurs, trend, EMA30/SMA200, RSI, zwroty 1–12M, odległość od szczytu, iskierka; etykiety list (robotyka, surowce, energia, inne, ETF, krypto, okazje, obserwowane, Portfel Trumpa) | Yahoo |
| **B. Okazje handlowe** | `okazje.html` | nagłe wzrosty wolumenu (≥3× średnia 20 sesji), ruchy ≥2,5×ATR, wybicia 52 tyg., przebicia SMA200, poziomy, konfluencja (≥2 sygnały jednego dnia); **setupy na całym rynku USA + krypto**: `pullback` (impuls z wolumenem przez EMA30 → korekta do EMA30 → pierwsza świeca w górę; wzorzec: ARB, wejście 26 sie 2026) i `ema30` (przebicie + 3 sesje nad linią); okazje zakupowe (spadki od szczytu: MU, ASML, NBIS, NTNX, NVDA, TSLA, KOID) | Yahoo, TradingView |
| **B. Inwestorzy** | `inwestorzy.html` | Kongres (STOCK Act, Quiver), insiderzy (SEC Form 4), fundusze 13F (Buffett, Burry, Ackman, Dalio, Wood…), **Portfel Trumpa** (37 spółek z Twojego Trackera, z kursami) | SEC, Quiver, `data/trump.csv` |
| Robotyka | `roboty.html` | ranking spółek z list (fundamenty + technika), 5 sekcji, ETF-y | Yahoo |
| Start | `index.html` | dzisiejsze alerty, setupy, sygnały inwestorów, Portfel Trumpa, największe ruchy | wszystko wyżej |
| Dane | `api/instruments.json`, `api/alerts.json`, `api/market.json`, `api/signals.json`, `api/meta.json` | to samo w JSON — do użycia bezpośrednio w Lovable | — |

Powiadomienia: Discord (webhook) z przebiegów `alerts` i `market`. TradingView
Premium: wskaźnik `tradingview/rafmall_konfluencja.pine` z tymi samymi regułami
i alertem webhook → Discord w czasie rzeczywistym (`tradingview/README.md`).

Adres narzędzia: **https://rmalinski88-cyber.github.io/rafmall/**
(podstrony: `/szukaj.html`, `/okazje.html`, `/inwestorzy.html`, `/roboty.html`).

## 2. Trzy kliknięcia, które musisz zrobić sam (nie mam do nich dostępu)

1. **Włącz GitHub Pages** — bez tego adres wyżej zwraca 404, choć strony są już
   zbudowane na gałęzi `gh-pages`:
   https://github.com/rmalinski88-cyber/rafmall/settings/pages →
   *Build and deployment* → *Source*: **Deploy from a branch** → *Branch*:
   **gh-pages**, folder **/ (root)** → **Save**. Po 1–2 minutach strona działa.
2. **Wpisz klucze** (raz, tylko tam — nigdy w czacie):
   https://github.com/rmalinski88-cyber/rafmall/settings/secrets/actions →
   *New repository secret*:
   - `DISCORD_WEBHOOK_URL` — Discord → ustawienia kanału → Integracje → Webhooki →
     Nowy webhook → *Kopiuj adres URL webhooka*. Bez tego alerty tylko na stronie.
   - `SEC_USER_AGENT` — tekst `Imię Nazwisko adres@email` (SEC wymaga podpisu
     w zapytaniach). Bez tego brak insiderów i 13F; reszta działa.
   - `QUIVER_API_KEY` — opcjonalnie, do transakcji Kongresu (darmowy klucz na quiverquant.com).
3. **Osadź narzędzie w rafmall.ch** — w czacie projektu Lovable wklej prompt
   z sekcji 4.

## 3. Rytm (wszystko na GitHubie)

| Kiedy (UTC) | Co | Plik |
|---|---|---|
| co godzinę 14–21, pn–pt | `alerts --discord` na Twoich listach | `rafmall.yml` |
| 21:40 pn–pt | `market --discord` — setupy na całym rynku | `rafmall.yml` |
| 21:50 pn–pt | `scan` — nowi inwestorzy (Kongres, insiderzy, 13F) | `rafmall.yml` |
| 22:20 pn–pt i 06:20 pn–sb | pełna przebudowa stron i JSON → GitHub Pages | `pages.yml` |
| po każdym pushu do `main` | j.w. | `pages.yml` |

Ręcznie: GitHub → **Actions** → `rafmall` lub `pages` → *Run workflow*.
Zadania `rafmall`: `check`, `first_run`, `alerts`, `market`, `scan`, `screener`,
`site`, `peek` (podgląd strony WWW do logu), `dump` (notowania do logu).
Sesja Claude w chmurze uruchamia je sama przez API GitHuba i czyta logi — tak
właśnie powstały poprawki tickerów i reguł.

## 4. Prompt dla Lovable (skopiuj w całości)

```
Dodaj do nawigacji pozycję „Narzędzie” (ścieżka /narzedzie), obok „Portfel Trumpa”.
Strona ma nagłówek i stopkę jak reszta serwisu. Nad treścią umieść cztery przyciski-zakładki
w stylu serwisu: „Start”, „Szukaj”, „Okazje”, „Inwestorzy”, „Robotyka”. Pod nimi iframe
na całą szerokość, wysokość min. calc(100vh - 160px), bez ramki, z atrybutem loading="lazy".
Zakładki ustawiają src iframe na kolejno:
https://rmalinski88-cyber.github.io/rafmall/index.html
https://rmalinski88-cyber.github.io/rafmall/szukaj.html
https://rmalinski88-cyber.github.io/rafmall/okazje.html
https://rmalinski88-cyber.github.io/rafmall/inwestorzy.html
https://rmalinski88-cyber.github.io/rafmall/roboty.html
Domyślnie otwarta jest „Start”. Na stronie /portfel, pod Trump Portfolio Trackerem, dodaj
sekcję „Kursy portfela” która pobiera JSON z
https://rmalinski88-cyber.github.io/rafmall/api/instruments.json, bierze pole items,
filtruje elementy, których tablica keys zawiera "trump", i pokazuje tabelę: symbol, name,
last (kurs, 2 miejsca po przecinku), ret_1m (zwrot 1M w %, zielony gdy dodatni, czerwony
gdy ujemny), rsi (zaokrąglone), trend. Nad tabelą pokaż datę z pola generated. Gdy pobranie
się nie uda, pokaż tekst „Dane chwilowo niedostępne”. Użyj istniejących kolorów, czcionek
i komponentów serwisu; nic więcej nie zmieniaj.
```

Strony narzędzia są już w kolorach i czcionkach rafmall.ch (ciemne tło,
Inter + Space Grotesk, akcent bursztynowy), więc w ramce wyglądają jak część serwisu.

## 5. Decyzje, które podjąłem za Ciebie

Każdą zmienisz jednym zdaniem.

| Temat | Decyzja | Gdzie zmienić |
|---|---|---|
| Hosting narzędzia | GitHub Pages (za darmo, publikuje się samo). Twój hosting FTP zostaje jako opcja (`scripts/publish.py`, sekrety `FTP_*`) | `.github/workflows/pages.yml` |
| Reguła skanu | główna `pullback` (jak ARB 26 sie); zapasowa `ema30` (przebicie + dokładnie 3 sesje); wolumen 2× średniej 20 sesji; strefa korekty 3% nad EMA, dla zmiennych instrumentów do 0,6×ATR, maks. 6% | `config/tracker.yml → market_rules` |
| Zasięg skanu | USA przez screener TradingView (ok. 70 kandydatów dziennie) + krypto z listy `data/crypto.csv` (screener TV nie zwraca par krypto) | `market_tv_market`, `data/crypto.csv` |
| Jeden alert na setup | skaner pamięta klucz (reguła, symbol, dzień impulsu); kolejne dni tej samej korekty nie powtarzają alertu | `.cache/tracker_seen.json` |
| Alerty | wolumen ≥3× średniej, ruch ≥2,5×ATR, wybicie 52 tyg., SMA200 (SMA50 usunięte — same szumy), poziomy, okazje, konfluencja | `config/tracker.yml → alert_rules` |
| Portfel Trumpa | kopia Twojego Trackera z rafmall.ch (ticker, kategoria, notatka) — Trump nie zgłasza transakcji, więc to lista obserwacyjna z kursami, nie strumień transakcji | `data/trump.csv` |
| Jakość list | spółki z Twoich screenów zostały, jeśli dane je bronią; TON i TIA wykreślone (brak wiarygodnych notowań), `ARB-USD` na Yahoo to martwy token — Arbitrum to `ARB11841-USD` | CSV w `data/` |
| Portfel prywatny | repo jest publiczne, więc `data/portfolio.csv` nie trafia do GitHuba; sygnały „pod portfel” liczą się tylko lokalnie | `data/portfolio.csv` |
| Handel | narzędzie **nie składa zleceń**. Pokazuje, Ty decydujesz | — |

## 6. Na komputerze (opcjonalnie)

Nie jest potrzebny do codziennej pracy. Przydaje się do portfela prywatnego
i do eksportu do Obsidiana:

```bash
git clone https://github.com/rmalinski88-cyber/rafmall.git && cd rafmall
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
cp .env.example .env                                    # klucze jak w sekcji 2
cp data/portfolio.example.csv data/portfolio.csv        # Twoje pozycje (ticker,quantity,avg_price)
python -m tracker check                                 # co działa, czego brakuje
python -m tracker alerts --discord                      # alerty teraz
python -m tracker market                                # setupy na całym rynku teraz
python -m tracker replay ARB11841-USD --rule pullback   # kiedy reguła odpaliłaby w historii
python -m tracker hub --site out/site                   # strony lokalnie: out/site/index.html
python -m screener run --obsidian-vault ŚCIEŻKA         # notatki do sejfu Obsidian
```

## 7. Pliki, które edytujesz sam

| Plik | Co | Kolumny |
|---|---|---|
| `data/watchlist.csv` | obserwowane akcje/ETF/krypto | ticker, note |
| `data/okazje.csv` | spółki do kupienia na spadkach, z progiem % | ticker, name, max_drawdown_pct, note |
| `data/trump.csv` | Portfel Trumpa (jak w Trackerze) | ticker, name, group, note |
| `data/universe_humanoid_global.csv` | lista główna (robotyka) | ticker, name, market, segment, confidence, notes |
| `data/universe_surowce.csv`, `_infrastruktura.csv`, `_inne.csv` | sekcje poboczne | j.w. |
| `data/etf.csv` | ETF-y na stronie i w alertach | ticker, name, group, notes |
| `data/crypto.csv` | krypto do skanu i wyszukiwarki | ticker, name |
| `data/funds_13f.csv` | śledzone fundusze | key, fund, manager, cik |
| `config/tracker.yml` | progi alertów i skanu, okna czasowe, wagi | — |
| `data/portfolio.csv` | Twoje pozycje (prywatny, poza gitem) | ticker, quantity, avg_price, note |

Linie zaczynające się od `#` w CSV są ignorowane. Po pushu do `main` strona
przebudowuje się sama. Lista kandydatów i notatki ze screenów: `data/kandydaci.md`.

## 8. Ograniczenia, o których warto wiedzieć

- Świeca dzienna w trakcie sesji jest niepełna: alerty w ciągu dnia pokazują
  stan „do tej godziny”; miarodajny jest przebieg po 22:00 CET.
- Opóźnienia w danych o inwestorach: Kongres do 45 dni, 13F do 45 dni po
  kwartale, Form 4 do 2 dni roboczych.
- Yahoo limituje zapytania; pojedynczy krok może paść — strona buduje się z tego,
  co się udało (`continue-on-error`), a następny przebieg uzupełnia.
- Screener TradingView to nieoficjalny endpoint: dla akcji USA działa, dla krypto
  nie zwraca par — stąd lista zapasowa.
- Pine Script był pisany bez kompilatora: jeśli Pine Editor pokaże błąd,
  przyślij treść komunikatu.
