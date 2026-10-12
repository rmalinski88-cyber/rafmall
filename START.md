# Pierwsze uruchomienie na komputerze

Kolejność komend na pierwszy raz. Po każdym kroku jest napisane, czego się spodziewać.

## 1. Pobranie i instalacja (raz)

```bash
git clone https://github.com/rmalinski88-cyber/rafmall.git
cd rafmall
git checkout claude/stock-search-tool-pkr8rw
python3 -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt pytest
python -m pytest tests -q                              # oczekiwane: wszystkie testy OK, bez sieci
```

## 2. Sprawdzenie tickerów (wymaga internetu)

```bash
python -m screener --universe data/universe_humanoid_global.csv validate
python -m screener --universe data/universe_surowce.csv validate
python -m screener --universe data/universe_infrastruktura.csv validate
python -m screener --universe data/universe_inne.csv validate
python -m screener --universe data/etf.csv validate
```

Wiersze ze statusem `BŁĄD — brak notowań` to tickery, których Yahoo nie zna.
Popraw je w `data/universe_humanoid_global.csv` albo wyślij mi listę błędów,
a ja je poprawię. Spółki z `confidence=medium` sprawdź w pierwszej kolejności.

## 3. Strona z robotyką humanoidalną

```bash
python -m screener --universe data/universe_humanoid_global.csv site --out out/site/roboty.html \
  --extra "Surowce=data/universe_surowce.csv" --extra "Energia=data/universe_infrastruktura.csv" \
  --extra "Inne tematy=data/universe_inne.csv"
```

Otwórz `out/site/roboty.html` w przeglądarce. To gotowy plik do wgrania na rafmall.ch.
ETF-y z `data/etf.csv` dołączają się same. Pierwsze uruchomienie pobiera ~110 symboli z Yahoo,
może potrwać kilka minut; kolejne idą z cache.

## 4. Tracker transakcji (opcjonalnie)

```bash
export SEC_USER_AGENT="Imię Nazwisko rmalinski88@gmail.com"   # SEC wymaga identyfikacji
export QUIVER_API_KEY="..."                                   # tylko jeśli masz klucz; bez niego Kongres jest pomijany
cp data/portfolio.example.csv data/portfolio.csv              # wpisz swoje pozycje
python -m tracker check
python -m tracker scan
```

Potem strona z kolumną „Insiderzy”:

```bash
python -m screener --universe data/universe_humanoid_global.csv site --signals out/signals_$(date +%F).json
```

## 5. Alerty na Discord

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."   # z ustawień kanału → Integracje → Webhooki
python -m tracker alerts --all --discord        # pierwszy raz: wszystko, żeby zobaczyć format
python -m tracker alerts --discord              # potem: tylko nowości
```

Do crona co godzinę w godzinach sesji USA — przykład w README.

## 5a. Skan całego rynku (reguła EMA30 + wolumen)

```bash
python -m tracker market --limit 200       # pierwszy test na 200 symbolach (kilka minut)
python -m tracker market --discord         # pełny rynek USA, 30–60 min za pierwszym razem
```

## 5b. TradingView (masz Premium)

Instrukcja w `tradingview/README.md`: wklej wskaźnik w Pine Editor, ustaw alert
z webhookiem Discorda. Jeśli Pine Editor pokaże błąd, wyślij mi treść.

## 6. Przegląd jakościowy (zasada: jakość, nie ilość)

Po `validate` i pierwszej stronie z prawdziwymi danymi przejdź listy i wykreśl
spółki, które nie bronią się po sprawdzeniu (trend, wyniki, aktualność tezy
z reela). Wyślij mi tickery do wykreślenia albo zrób to sam w CSV.

## Co mi wysłać po uruchomieniu

- wynik `validate` (błędy tickerów),
- zrzut ekranu strony `roboty.html`,
- ewentualne komunikaty błędów w całości.
