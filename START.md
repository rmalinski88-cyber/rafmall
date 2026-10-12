# Briefing — uruchomienie na komputerze

Stan: wszystko zbudowane i przetestowane offline (143 testy). Nic nie było
jeszcze uruchomione na prawdziwych danych, bo telefon nie ma dostępu do Yahoo,
SEC ani TradingView. Pierwsze uruchomienie na komputerze to jedna komenda,
która robi wszystko po kolei i zapisuje log. Od tego logu zaczynam poprawki.

## 1. Co jest zbudowane

| Narzędzie | Komenda | Co robi | Źródło |
|---|---|---|---|
| Screener | `python -m screener run` | ranking spółek z listy: fundamenty + technika | Yahoo |
| **Strona WWW** | `python -m screener … site` | `roboty.html`: 5 sekcji, 116 spółek, 21 ETF-ów, wyszukiwarka | Yahoo |
| Tracker | `python -m tracker scan` | Kongres, insiderzy (Form 4), fundusze 13F → sygnały pod portfel | SEC, Quiver |
| Karta | `python -m tracker quote NVDA BTC` | kurs, trend, zwroty + kto handlował | Yahoo, SEC |
| **Alerty** | `python -m tracker alerts` | Twoje listy (141 instr.): wolumen, ruch, wybicia, SMA, poziomy, okazje, konfluencja | Yahoo |
| **Skan rynku** | `python -m tracker market` | cały rynek USA + krypto: setup „pullback do EMA30” (ARB) i „EMA30 + 3 dni” | TradingView → Yahoo |
| Replay | `python -m tracker replay ARB-USD` | w które dni historii reguła by odpaliła — test akceptacyjny | Yahoo |
| TradingView | `tradingview/rafmall_konfluencja.pine` | te same reguły na wykresie + alert webhook → Discord, realtime | TV Premium |
| Publikacja | `python scripts/publish.py` | wgrywa `roboty.html` na hosting przez FTP | .env |
| **Obsidian** | `python -m screener run --obsidian-vault ŚCIEŻKA` | notatki w sejfie: hub tematu, przebieg z datą, spółka z właściwościami (baza do Bases/Dataview) | sejf lokalny |

Powiadomienia: Discord (webhook). Rutyna Claude osobno, do streszczeń — później.

## 2. Pierwsze uruchomienie — jedna komenda

```bash
git clone https://github.com/rmalinski88-cyber/rafmall.git && cd rafmall
git checkout claude/stock-search-tool-pkr8rw
python3 -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
cp .env.example .env            # i uzupełnij: SEC_USER_AGENT (imię, nazwisko, e-mail) + DISCORD_WEBHOOK_URL
cp data/portfolio.example.csv data/portfolio.csv       # wpisz swoje pozycje (ticker,quantity,avg_price)
python scripts/first_run.py     # 20–40 min; --quick = kilka minut bez strony i skanu rynku
```

Skrypt przechodzi 15 kroków (testy → check → weryfikacja 7 list → replay ARB →
alerty → tracker → skan rynku → strona), nie zatrzymuje się na błędzie
i zapisuje wszystko do `out/first_run_<data>.log`.

**Wyślij mi ten log.** Resztę robię ja.

## 3. Decyzje, które podjąłem za Ciebie

Każdą zmienisz jednym zdaniem.

| Temat | Decyzja | Gdzie zmienić |
|---|---|---|
| Portfel | nieznany → do czasu wpisania tracker używa przykładu i ostrzega; **priorytet alertów nie działa bez tego** | `data/portfolio.csv` |
| Reguła skanu | główna: `pullback` (impuls → korekta do EMA30 → wejście, jak ARB 26 sie); zapasowa: `ema30` (przebicie + dokładnie 3 sesje); wolumen 2× liczony od średniej 20 sesji | `config/tracker.yml → market_rules` |
| Zasięg skanu | USA + krypto przez screener TradingView; przy awarii spis SEC / lista zapasowa | `market_tv_market`, `market_crypto` |
| TradingView realtime | portfel + okazje (MU, ASML, NBIS, NTNX?, NVDA, TSLA, KOID) + ARB-USD, interwał 1D | `tradingview/README.md` |
| Hosting | plik `roboty.html` → `rafmall.ch/roboty.html`; FTP przez `scripts/publish.py`; katalog zgaduję `/public_html` | `.env → FTP_*` |
| Rytm | alerty co godzinę w sesji USA, skan rynku raz po sesji, strona raz dziennie | sekcja 5 |
| Jakość | spółki `medium` zostają z etykietą „do weryfikacji” do pierwszego przeglądu; wykreślamy po danych, nie po nazwie | CSV w `data/` |
| Sektory | robotyka = sekcja główna; wszystko inne ciekawe → „Inne tematy”, osobny ranking | `data/universe_inne.csv` |
| Klucze | w `.env` (gitignore), nie w configu; bez SEC_USER_AGENT działa wszystko poza insiderami i 13F | `.env` |
| Handel | narzędzie **nie składa zleceń**. Pokazuje, Ty decydujesz | — |

## 4. Co zrobię po otrzymaniu logu — w tej kolejności

1. **Tickery** — poprawię te ze statusem BŁĄD. Spodziewam się 5–10, głównie: `MOG-A`, `SKF-B.ST`, `300660.SZ`, `SHA0.DE`, `KGH.WA`, `BOL.ST`, `NST.AX`, `B`, `KOID`, `HUMN`, `NTNX`, benchmark `WIG20.WA`.
2. **Replay ARB** — sprawdzę, czy `pullback` odpalił 26–27 sierpnia. Jeśli obok o >1 dzień albo wcale: stroję `pullback_pct`, `impulse_atr_multiple`, `volume_multiple`. Jeśli NVDA strzela co kilka dni: zaostrzam.
3. **Screener TradingView** — jeśli krok „skan rynku” pokazał „niedostępny”, poprawię nazwy pól albo zostawimy spis SEC.
4. **Szum alertów** — po pierwszym `alerts --all` ocenię, czy progi (3× wolumen, 2,5× ATR) dają 10 czy 100 alertów dziennie, i dostroję.
5. **Strona na prawdziwych danych** — obejrzysz `out/site/roboty.html`; razem wykreślimy to, co się nie broni (jakość nad ilość).
6. **Automatyzacja** — cron (macOS/Linux) albo Harmonogram zadań (Windows) wg sekcji 5.
7. **Pine Script** — jeśli Pine Editor pokaże błąd, przyślij treść; poprawię.
8. **Wygląd pod rafmall.ch** — gdy znajdziesz HTML z Lovable; do tego czasu strona ma własny, neutralny styl.

## 5. Rutyna po wdrożeniu (czas CET; sesja USA 15:30–22:00)

```cron
# crontab -e   (macOS/Linux; Windows: Harmonogram zadań z tymi samymi komendami)
0  16-22 * * 1-5  cd ~/rafmall && .venv/bin/python -m tracker alerts --discord          >> out/alerts.log 2>&1
40 22    * * 1-5  cd ~/rafmall && .venv/bin/python -m tracker market --discord          >> out/market.log 2>&1
50 22    * * 1-5  cd ~/rafmall && .venv/bin/python -m tracker scan --new-only --no-quotes >> out/scan.log 2>&1
0  7     * * 2-6  cd ~/rafmall && .venv/bin/python -m screener --universe data/universe_humanoid_global.csv site --out out/site/roboty.html --extra "Surowce=data/universe_surowce.csv" --extra "Energia=data/universe_infrastruktura.csv" --extra "Inne tematy=data/universe_inne.csv" --signals "out/signals_$(date +\%F -d yesterday).json" >> out/site.log 2>&1 && .venv/bin/python scripts/publish.py >> out/site.log 2>&1
```

Krypto handluje 24/7 — jeśli chcesz alerty krypto w weekend, drugi wpis `alerts` z `* * 0,6`.

## 6. Znane ryzyka — co może nie zadziałać za pierwszym razem

| Ryzyko | Skutek | Plan |
|---|---|---|
| Screener TradingView to nieoficjalny endpoint; nazwy pól niesprawdzone | skan rynku wraca do spisu SEC (wolniej, tylko USA) | poprawka pól albo zostajemy przy SEC |
| Pine Script pisany bez kompilatora | błąd przy wklejaniu | przyślij komunikat, poprawka w minutę |
| ~15 tickerów z pamięci (sufiksy giełd, klasy akcji) | `validate` pokaże BŁĄD | poprawiam z logu |
| Yahoo limituje zapytania | pierwszy pełny skan SEC 30–60 min; cache łagodzi kolejne | `--limit` w first_run; TV jako główne źródło |
| Świeca dzienna w trakcie sesji jest niepełna | alerty w ciągu dnia pokazują stan „do tej godziny”; wolumen zaniżony | ostatni przebieg po 22:00 CET jest miarodajny |
| 13F: dopasowanie CUSIP→ticker niepełne | część pozycji funduszy bez tickera, tylko nazwa | `data/cusip_tickers.csv` rozbudowujemy w miarę potrzeb |
| Kongres wymaga klucza Quiver | bez klucza sekcja Kongresu pusta | opcjonalne; Quiver ma darmowy tier do testów |
| Yahoo dla GPW/Sztokholm/ASX bywa dziurawe | braki w sekcji Surowce | widać w `validate`; wykreślamy albo zmieniamy ticker |

## 7. Pliki, które edytujesz sam

| Plik | Co | Kolumny |
|---|---|---|
| `data/portfolio.csv` | Twoje pozycje (prywatny, poza gitem) | ticker, quantity, avg_price, note |
| `data/watchlist.csv` | obserwowane akcje/ETF/krypto | ticker, note |
| `data/okazje.csv` | spółki do kupienia na spadkach, z progiem % | ticker, name, max_drawdown_pct, note |
| `data/universe_humanoid_global.csv` | lista główna (robotyka) | ticker, name, market, segment, confidence, notes |
| `data/universe_surowce.csv`, `_infrastruktura.csv`, `_inne.csv` | sekcje poboczne | j.w. |
| `data/etf.csv` | ETF-y na stronie i w alertach | ticker, name, group, notes |
| `data/crypto.csv` | krypto do skanu (zapas, gdy TV nie odpowie) | ticker, name |
| `data/funds_13f.csv` | śledzone fundusze | key, fund, manager, cik |
| `config/tracker.yml` | progi alertów i skanu, okna czasowe, wagi | — |
| `.env` | klucze i FTP | — |

Linie zaczynające się od `#` w CSV są ignorowane. Dopisuj swobodnie — testy
i `validate` wyłapią literówki. Lista kandydatów i notatki ze screenów:
`data/kandydaci.md`.
