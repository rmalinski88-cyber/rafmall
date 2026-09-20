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
```

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

66 testów. RSI i ATR są porównywane z niezależnymi implementacjami pętlowymi
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
