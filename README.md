# Screener robotyki humanoidalnej — rynki azjatyckie

Narzędzie CLI, które ocenia spółki z sektora robotyki humanoidalnej notowane
w Tokio, Seulu, Tajpej, Hongkongu i na giełdach kontynentalnych Chin —
jednocześnie **fundamentalnie** i **technicznie** — a następnie układa je
w ranking i generuje raport HTML.

```
python -m screener run
```

---

## Jak to działa

Przebieg jednego screeningu:

```
uniwersum (CSV)  →  pobranie danych  →  wskaźniki  →  filtry  →  scoring  →  ranking
                    (dostawca+cache)    fund.+tech.   twarde     centyle      CSV + HTML
```

### 1. Uniwersum

`data/universe_humanoid_asia.csv` — ręcznie kuratorowana lista ok. 40 spółek
z ekspozycją na robotykę humanoidalną, podzielona na segmenty:

| Segment | Czym jest | Przykłady z listy |
|---|---|---|
| `komponenty` | Podzespoły: przekładnie, serwonapędy, prowadnice, pneumatyka | Harmonic Drive, Nabtesco, Hiwin, Inovance |
| `integrator` | Producenci gotowych robotów i automatyki | FANUC, Yaskawa, Estun, Doosan Robotics |
| `humanoid` | Bezpośrednie programy humanoidalne | Honda, Hyundai (Boston Dynamics), UBTech, XPeng |
| `platforma/AI` | Układy scalone, percepcja, moc obliczeniowa | TSMC, Samsung, Horizon Robotics |
| `dywersyfikat` | Konglomeraty z istotnym segmentem robotyki | Hitachi |

Plik jest zwykłym CSV — dopisuj, usuwaj i zmieniaj segmenty swobodnie.

> **Zweryfikuj tickery przed pierwszym użyciem.** Lista została złożona ręcznie
> i część symboli (szczególnie KOSDAQ i STAR Market) mogła się zmienić. Służy
> do tego osobna komenda:
>
> ```
> python -m screener validate
> ```
>
> Wypisze każdy ticker z liczbą pobranych sesji i liczbą dostępnych pól
> fundamentalnych. Wiersze ze statusem `BŁĄD` popraw w pliku CSV.

### 2. Ocena fundamentalna

Wzrost (przychody, zysk), rentowność (marża brutto/operacyjna/netto, ROE, ROA),
przepływy (marża FCF), bilans (dług/kapitał, płynność, gotówka netto) i wycena
(E/P, C/P, C/WK, EV/EBITDA, PEG).

Dwie zasady obowiązują w całym module:

- **Ujemne C/Z jest odrzucane, nie odwracane.** Spółka ze stratą nie jest
  „tania" — jej C/Z po prostu nie istnieje. Znaczna część tego sektora jest
  jeszcze nierentowna, więc to nie jest przypadek brzegowy.
- **Nic nie jest imputowane.** Brakujący wskaźnik pozostaje brakujący,
  a wagi są renormalizowane po tych, które spółka faktycznie raportuje.

### 3. Ocena techniczna

Trend (cena vs SMA50/SMA200, SMA50 vs SMA200), momentum (RSI(14) wg Wildera,
histogram MACD, stopy zwrotu 1/3/6/12M), **siła względna wobec indeksu
macierzystego** (Nikkei, KOSPI, TAIEX, Hang Seng, Shanghai, Shenzhen — dobierany
automatycznie po sufiksie tickera), pozycja w zakresie 52 tygodni, trend
wolumenu oraz miary ryzyka (ATR%, maksymalne obsunięcie).

### 4. Filtry

Twarde bramki odcinają spółki przed scoringiem, żeby nie zaburzały pozycji
centylowych pozostałych: minimalna kapitalizacja i płynność (w USD, po
przewalutowaniu), minimalna długość historii notowań, maksymalne zadłużenie
i minimalne pokrycie danymi fundamentalnymi.

**Brak danej nigdy nie powoduje odrzucenia** — brak to problem pokrycia,
raportowany osobno, a nie dowód, że spółka jest za mała.

### 5. Scoring — i co on naprawdę znaczy

Każdy wskaźnik jest zamieniany na **pozycję centylową wewnątrz badanego
uniwersum**, nie porównywany z progiem bezwzględnym. To celowa decyzja:
próg „C/Z poniżej 20" nie ma sensu jednocześnie dla Tokio, Seulu i Shenzhenu,
ani jednocześnie dla rentownego producenta przekładni i przedprzychodowego
producenta humanoidów.

Konsekwencje, które trzeba rozumieć, czytając wynik:

- **Wyniki są względne.** 90 punktów w słabym zbiorze to wciąż słaba spółka.
- **Zmiana uniwersum zmienia każdy wynik.** Dopisanie 10 spółek przestawia cały ranking.
- **Wskaźnik raportowany przez mniej niż 3 spółki jest pomijany** — ranking
  dwóch spółek względem siebie daje 100 i 0, czyli szum.
- Kolumna **Pokrycie** mówi, jaka część wag fundamentalnych była faktycznie
  dostępna. Wynik 85 przy pokryciu 40% znaczy dużo mniej niż przy 100%.

Profile scoringu (`config/default.yml`) ustalają wagi:

| Profil | Nastawienie | Podział fund./tech. |
|---|---|---|
| `growth` (domyślny) | Wzrost przychodów i marże; wycena waży mało | 45 / 55 |
| `value` | Rentowność, przepływy, wycena | 70 / 30 |
| `balanced` | Kompromis | 50 / 50 |

---

## Instalacja

```bash
git clone https://github.com/rmalinski88-cyber/rafmall.git
cd rafmall
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Python 3.10 lub nowszy.

## Użycie

```bash
# Pełny screening z domyślnym profilem
python -m screener run

# Inny profil, tylko 15 najlepszych w konsoli
python -m screener run --profile value --top 15

# Sprawdzenie, czy wszystkie tickery działają u dostawcy
python -m screener validate

# Komplet wskaźników dla jednej spółki
python -m screener show 6324.T

# Przebieg offline na danych syntetycznych (bez sieci)
python -m screener --provider fixture run

# Strona WWW z listą spółek - do wgrania na rafmall.ch
python -m screener --universe data/universe_humanoid_global.csv site --out out/site/roboty.html
# ...z kolumną "Insiderzy" z ostatniego skanu trackera:
python -m screener --universe data/universe_humanoid_global.csv site --signals out/signals_2026-10-12.json
```

`site` tworzy jeden samodzielny plik HTML (bez zależności zewnętrznych) z
wyszukiwarką, filtrem rynku i segmentami: Humanoidy / Podzespoły /
Integratorzy / Platforma i AI. `data/universe_humanoid_global.csv` to lista
azjatycka plus USA i Europa (Tesla, NVIDIA, Teradyne, ABB, Siemens, Schaeffler,
Infineon, producenci silników, LiDAR-ów i magnesów). Spółki oznaczone
`confidence=medium` mają na stronie etykietę „do weryfikacji".

Wyniki trafiają do `out/`:

- `screen_RRRR-MM-DD.csv` — pełny zestaw wskaźników i wyników, do arkusza
- `report_RRRR-MM-DD.html` — raport z wykresem, rankingiem i listą odrzuconych

Raport HTML jest samowystarczalny: otwiera się z pliku, bez internetu,
z obsługą trybu ciemnego.

### Najczęstsze zmiany w konfiguracji

Wszystko istotne siedzi w `config/default.yml`:

```yaml
filters:
  min_market_cap_usd: 150000000    # podnieś, żeby odciąć małe spółki
  min_avg_turnover_usd: 500000     # płynność — ważne dla KOSDAQ i ChiNext

profiles:
  growth:
    group_weights:
      fundamental: 0.45            # przesuń w stronę fundamentów
      technical: 0.55
    fundamental:
      revenue_growth: {weight: 3.0, direction: high}
```

Wagi są względne — liczy się ich stosunek, nie suma.

## Dane

Domyślnie **Yahoo Finance** przez `yfinance`: za darmo, bez klucza API,
z pokryciem wszystkich potrzebnych giełd. Odpowiedzi są cache'owane w `.cache/`
(domyślnie 12 h), bo darmowe źródła szybko wprowadzają limity zapytań.

Jakość danych fundamentalnych z Yahoo jest nierówna: dobra dla dużych spółek
japońskich i tajwańskich, słabsza dla małych spółek z KOSDAQ i giełd
kontynentalnych. Dlatego pokrycie jest raportowane, a nie ukrywane.

### Podmiana na źródło płatne

Warstwa dostawcy jest odizolowana. Żeby przejść na FMP, EODHD czy inne API:

1. Napisz `screener/providers/twoje_api.py` z klasą dziedziczącą po
   `DataProvider` (`get_prices`, `get_fundamentals`, `get_fx_to_usd`).
2. Dopisz jedną linię do `_REGISTRY` w `screener/providers/__init__.py`.
3. Ustaw `provider:` w konfiguracji albo podaj `--provider twoje_api`.

Reszta pipeline'u nie wymaga zmian.

## Testy

```bash
pip install pytest
python -m pytest tests/ -q
```

Testy obu narzędzi (screener + tracker). RSI i ATR są porównywane z niezależnymi implementacjami pętlowymi
napisanymi wprost z definicji — zgodność wersji zwektoryzowanej z naiwną na
losowych danych to najtańszy mocny dowód, że wektoryzacja jest poprawna.
Cały pipeline jest testowany end-to-end przez deterministycznego dostawcę
`fixture`, bez dostępu do sieci.

## Ograniczenia

- **To nie jest rekomendacja inwestycyjna ani system transakcyjny.** Narzędzie
  porządkuje publicznie dostępne dane i liczy pozycje względne.
- Uniwersum jest kuratorowane ręcznie — jego skład jest założeniem, nie wynikiem.
  Screener nie odkryje spółki, której nie ma na liście.
- Dane z darmowych źródeł bywają niekompletne, opóźnione lub błędne.
- Wskaźniki fundamentalne pochodzą z ostatnich raportowanych okresów i mogą być
  nieaktualne o kilka miesięcy.
- Scoring nie uwzględnia ryzyka walutowego, ładu korporacyjnego, ograniczeń
  w dostępie do rynku dla inwestorów zagranicznych (istotne na giełdach
  kontynentalnych) ani kosztów transakcyjnych.

Każdą spółkę zweryfikuj w jej sprawozdaniach finansowych przed jakąkolwiek
decyzją.


---

# Tracker Wall Street — Kongres, insiderzy, fundusze, akcje/ETF/krypto

Drugie narzędzie w repo (`python -m tracker`). Śledzi, czym handlują ludzie
z dostępem do lepszej informacji, i zestawia to z Twoim portfelem:

| Co | Skąd | Koszt |
|---|---|---|
| Transakcje członków Kongresu USA (STOCK Act) | Quiver Quantitative API | wymaga klucza `QUIVER_API_KEY` |
| Transakcje insiderów spółek (Form 4) | SEC EDGAR | za darmo, bez klucza |
| Portfele funduszy: Buffett, Dalio, Ackman, Wood, Burry (13F) | SEC EDGAR | za darmo, bez klucza |
| Notowania akcji, ETF i krypto | Yahoo Finance (jak screener) | za darmo |

```
Quiver / SEC  →  transakcje  →  sygnały per spółka  →  dopasowanie do portfela  →  konsola + HTML + JSON
```

## Konfiguracja

```bash
pip install -r requirements.txt
export SEC_USER_AGENT="Imię Nazwisko twoj@email.pl"   # SEC tego wymaga
export QUIVER_API_KEY="..."                           # opcjonalnie: bez niego Kongres jest pomijany
cp data/portfolio.example.csv data/portfolio.csv      # wpisz swoje pozycje (plik nie trafia do gita)
python -m tracker check                               # sprawdza klucze i dostęp do źródeł
```

Pliki do edycji: `data/portfolio.csv` (Twoje pozycje), `data/watchlist.csv`
(obserwowane akcje/ETF/krypto), `data/funds_13f.csv` (śledzone fundusze),
`config/tracker.yml` (okna czasowe i wagi sygnałów).

## Komendy

```bash
python -m tracker find nvidia               # znajdź ticker po nazwie
python -m tracker quote NVDA SPY BTC        # karta: kurs, trend, RSI, zwroty + kto handlował
python -m tracker congress --days 30        # co kupowali i sprzedawali kongresmeni
python -m tracker congress --member pelosi  # transakcje jednej osoby
python -m tracker insiders NVDA TSLA        # zakupy/sprzedaże zarządu i dyrektorów
python -m tracker funds berkshire ark       # co zmienił Buffett i Cathie Wood w ostatnim kwartale
python -m tracker scan                      # wszystko naraz + sygnały pod portfel + raport HTML
python -m tracker --feed fixture scan       # to samo na danych syntetycznych, bez sieci i kluczy
```

`scan` zapisuje `out/tracker_RRRR-MM-DD.html` (raport do przeglądarki)
i `out/signals_RRRR-MM-DD.json` (do dalszej automatyzacji).

## Jak liczony jest sygnał

Każda osoba lub fundusz liczy się **raz na spółkę i kierunek** — tłum
kupujących waży więcej niż jedna duża transakcja. Wagi (`config/tracker.yml`):

| Zdarzenie | Waga | Dlaczego |
|---|---|---|
| Zakup na rynku przez CEO/CFO/prezesa | +3 | najlepiej udokumentowany sygnał w zgłoszeniach |
| Zakup na rynku przez innego insidera | +2 | |
| Nowa pozycja funduszu (13F) | +2 | |
| Zwiększenie pozycji funduszu | +1 | |
| Kupno przez członka Kongresu | +1 | zgłoszenie bywa spóźnione nawet 45 dni |
| Sprzedaż przez członka Kongresu | −1 | |
| Zmniejszenie / sprzedaż całości (13F) | −1 / −2 | |
| Sprzedaż insidera | −0,5 | zwykle podatki i dywersyfikacja |
| Sprzedaż insidera wg planu 10b5-1 | 0 | zaplanowana z góry, nic nie mówi |

Ocena: ≥ +3 *silny popyt*, ≥ +1 *popyt*, ≤ −1 *podaż*, ≤ −3 *silna podaż*.
Pozycja z Twojego portfela z wynikiem ≤ −1 dostaje **alert portfela** i trafia
na górę listy.

Pomijane celowo: przydziały akcji, realizacja opcji, podatki i darowizny
(Form 4 kody A/M/F/G) — to ruchy mechaniczne, nie decyzje inwestycyjne.

## Alerty: anomalie i okazje zakupowe

```bash
python -m tracker alerts                 # co nowego od ostatniego sprawdzenia
python -m tracker alerts --all           # wszystkie bieżące alerty
python -m tracker alerts --discord       # ...i wyślij na Discord
```

Sprawdza wszystkie listy z `config/tracker.yml` (`alerts_universes`) plus
portfel, obserwowane i `data/okazje.csv`. Sześć reguł:

| Alert | Warunek |
|---|---|
| okazja | spółka z `data/okazje.csv` spadła o swój próg poniżej szczytu 52T albo jest pod SMA200 |
| wolumen | wolumen dnia ≥ 3× średnia 20 sesji |
| ruch | zmiana dnia ≥ 2,5× ATR(14) — próg skaluje się ze zmiennością spółki |
| wybicie | nowy szczyt lub dołek 52 tygodni |
| trend | kurs przebija SMA50 lub SMA200 |
| smart money | nowe zgłoszenia insiderów / Kongresu dla portfela i okazji |
| poziom | kurs przebija lokalny szczyt (opór) lub dołek (wsparcie) z ostatnich 90 sesji; poziom gaśnie po przebiciu |
| **konfluencja** | ≥ 2 różne alerty na jednej spółce tego samego dnia — najmocniejszy sygnał, idzie na górę |

Alerty z portfela idą pierwsze, potem okazje, potem konfluencje, potem reszta według nietypowości.
Każdy alert zgłaszany jest raz (stan w `.cache/tracker_alerts_seen.json`).

**Discord:** w ustawieniach kanału → Integracje → Webhooki → Nowy webhook →
skopiuj adres i ustaw `export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."`.
Bez tej zmiennej `--discord` tylko informuje, że nic nie wysłał.

**Czego nie wykryje:** reeli influencerów. Instagram nie ma API. Ślad po nich
to zwykle skok wolumenu bez wyników i bez komunikatu spółki — to wyłapie reguła „wolumen”.

## Skan całego rynku: kto właśnie zaczyna ruch

```bash
python -m tracker market                  # cały rynek USA (lista SEC, ~3 tys. płynnych spółek)
python -m tracker market --discord        # ...i na Discord
python -m tracker market --symbols data/universe_inne.csv   # własna lista
```

Inaczej niż `alerts`, które pilnują Twoich list, `market` przegląda **wszystkie
spółki notowane w USA** (spis SEC, za darmo) **i krypto** i pokazuje te,
które właśnie spełniły regułę. Główna reguła, `pullback`, to setup Rafała
z przykładu Arbitrum (wejście 26 sierpnia 2026):

1. **impuls**: w ostatnich 15 sesjach kurs przebija EMA30 od dołu na wolumenie
   ≥ 2× średniej i świecy ≥ 1,5× średniego zakresu,
2. **korekta**: kurs cofa się do rosnącej EMA30 (dołek ≤ 3% nad nią), zamknięcia
   zostają nad nią, wolumen korekty niższy niż impulsu,
3. **wejście**: pierwsza świeca zamykająca wyżej niż poprzednia — tu pada sygnał.

Wejście po korekcie, nie na szczycie impulsu: bliżej średniej, mniejsze ryzyko.
Druga, prostsza reguła `ema30` (`--rule ema30`):

1. kurs przebija EMA30 od dołu (świece dzienne),
2. zamyka się nad nią przez **3 kolejne sesje**,
3. w dniu przebicia lub podczas utrzymania wolumen ≥ **2× średnia** z 20 sesji sprzed przebicia.

Każdy sygnał pojawia się raz. Odfiltrowane są spółki poniżej 2 USD i z obrotem
poniżej 2 mln USD dziennie (krypto: tylko obrót). Progi w `config/tracker.yml`
→ `market_rules`. Krypto: screener TV `crypto` (pary USD/USDT, jedna na monetę),
zapas `data/crypto.csv`; świece dobowe, 3 sesje = 3 doby.

**Skąd kandydaci.** Domyślnie z nieoficjalnego screenera TradingView
(`market_source: tradingview`): jedno zapytanie zwraca spółki z wolumenem
≥ 2× i kursem nad EMA30, także z Europy i Azji (`--tv-market global`).
Nasz kod potwierdza na danych Yahoo warunek 3 sesji. Gdy screener nie
odpowie, skan sam przechodzi na pełny spis SEC (`--source sec`): pewniej,
ale pierwszy przebieg pobiera kilka tysięcy symboli z Yahoo (30–60 minut).
TradingView nie ma oficjalnego API; ten endpoint może się zmienić bez
ostrzeżenia, dlatego SEC zostaje jako zapas. Uruchamiaj raz dziennie po sesji USA (ok. 23:00 CET).
Kolejne reguły to jedna funkcja w `tracker/market.py` i jeden wpis w `RULES`.

## TradingView

Wskaźnik `tradingview/rafmall_konfluencja.pine` rysuje na wykresie te same
reguły co `tracker alerts` i wysyła alerty TradingView prosto na Discord przez
webhook — w czasie rzeczywistym, bez komputera. Instrukcja: `tradingview/README.md`.

## Rutyna co godzinę

`scan --new-only` pokazuje tylko to, co pojawiło się od poprzedniego
przebiegu (stan w `.cache/tracker_seen.json`). Przykład dla `cron`
(dni robocze, 9–16 czasu nowojorskiego):

```cron
CRON_TZ=America/New_York
0 9-16 * * 1-5  cd ~/rafmall && python -m tracker scan --new-only --no-quotes >> out/scan.log 2>&1
30 9-16 * * 1-5 cd ~/rafmall && python -m tracker alerts --discord >> out/alerts.log 2>&1
0 17 * * 1-5    cd ~/rafmall && python -m tracker market --discord >> out/market.log 2>&1
```

Ten sam przebieg może uruchamiać rutyna Claude — wystarczy prompt w stylu:
*„Uruchom `python -m tracker scan --new-only`, przeczytaj `out/signals_*.json`
z dzisiaj i streść mi nowe transakcje oraz alerty portfela.”* Środowisko
rutyny musi mieć dostęp sieciowy do `sec.gov`, `data.sec.gov`,
`api.quiverquant.com` i Yahoo Finance.

**Tracker nie składa zleceń.** Pokazuje, kto handlował — decyzję i zlecenie
składasz sam u swojego brokera.

## Ograniczenia trackera

- **Opóźnienia są wbudowane w dane:** Kongres do 45 dni, 13F do 45 dni po
  końcu kwartału, Form 4 do 2 dni roboczych. Kopiowanie cudzych transakcji po
  fakcie nie daje ich wyników.
- 13F pokazuje tylko długie pozycje w akcjach USA na koniec kwartału — bez
  shortów, gotówki i transakcji w trakcie kwartału.
- Tickery w 13F są dopasowywane po CUSIP (`data/cusip_tickers.csv`) i po
  nazwie emitenta; niedopasowane pozycje mają tylko nazwę.
- Format API Quiver bywa zmieniany — wiersze, których nie da się odczytać,
  są pomijane i raportowane w ostrzeżeniach, nigdy zgadywane.
- To nie jest rekomendacja inwestycyjna.
