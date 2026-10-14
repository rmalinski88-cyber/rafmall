---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 4. Analiza fundamentów (spotkanie live nr 4), 1 kwietnia 2026, ok. 2 h 04 min"
status: do przejrzenia
---
# Trela 04 – Analiza fundamentów: punktowanie stabilności finansowej (spotkanie 4)

## W skrócie
Do modelu punktowego (dotąd sama zyskowność, 55 pkt) dochodzi drugi filar: fundamenty, czyli stabilność finansowa spółki (40 pkt, sześć wskaźników). Trela pokazuje, skąd te wskaźniki biorą się w bilansie, jak je odczytać na wykresie w Scrabie i jak zamienić odczyt na punkty – na przykładach ALAB, META, MRVL i ORCL. Fundamenty to wg niego „hamulce": mają tylko wyłapać spółki skrajnie ryzykowne, a nie decydować o wyborze, bo kurs ciągnie zyskowność.

## Najważniejsze koncepty

### Rola fundamentów (00:03:13–00:09:16, 00:55:57)
- „Fundamenty" u Treli = stabilność finansowa, płynność, poziom zadłużenia. Nie zyskowność i nie wycena.
- Im większa waga fundamentów w modelu, tym niższy oczekiwany zysk; przy wadze 90% wynik zbliża się do S&P 500 (z nagrania, ma to pokazać na backtestach, czyli testach strategii na danych historycznych).
- Kolejność pracy: najpierw zyskowność. Spółki o słabej zyskowności w ogóle nie sprawdzamy pod kątem fundamentów, bo i tak nie trafi do portfela (00:55:57).
- Słabe fundamenty można „wybaczyć" spółce o wybitnej zyskowności; spółce przeciętnej (okolice 25.–30. miejsca listy) – nie (01:11:29).

### Bilans (balance sheet) – skąd biorą się wskaźniki (00:10:55–00:27:05)
- Total Assets (aktywa) − Total Liabilities (zobowiązania) = Total Equity (wartość netto).
- Sama wartość aktywów jest neutralna (spółki „niematerialne" rosną bez zwiększania aktywów). Ważne, żeby wartość netto nie spadała; trend spadkowy to mocny sygnał ostrzegawczy (00:13:45).
- Current assets = aktywa zamienialne na gotówkę w 12 miesięcy: gotówka i jej ekwiwalenty, receivables (należności), inventory (zapasy). Current liabilities = zobowiązania do zapłaty w 12 miesięcy. Porównanie tych dwóch pozycji mówi o płynności.
- Non-current (długoterminowe, powyżej roku): aktywa długoterminowe powinny przewyższać zobowiązania długoterminowe.
- Jeśli bieżące zobowiązania są większe od bieżących aktywów, to u małej spółki jest to czerwona lampka; u dużej, pokrywanej przez wielu analityków – nie musi blokować inwestycji (00:21:38–00:24:22).

### Sześć wskaźników i sposób czytania
- **Debt to Assets** (dług do aktywów; wzór ze slajdu: Short Term Debt + Long Term Debt / Total Assets). Oceniamy poziom i trend. Niżej = lepiej, bo zostaje pole do zadłużenia się w kryzysie. Banki dyskontują wartość aktywów (zużycie, aktywa niematerialne), więc ok. 40% to często praktyczne maksimum (00:31:26–00:34:14).
- **Interest Coverage** (pokrycie odsetek; slajd: EBIT / Interest Expenses; w nagraniu Trela mówi skrótowo o „zysku"). Ile razy roczny zysk pokrywa roczny koszt obsługi długu (same odsetki, nie cały dług – 01:21:50). Przy wysokich wartościach trendu nie oceniamy (00:37:32).
- **CFO to Debt** (slajd: CFO / Total Debt; CFO = Cash From Operations, gotówka z działalności operacyjnej). Uzupełnia poprzedni wskaźnik, bo zysk to pojęcie księgowe, a tu liczy się realna gotówka. Liczy się poziom, a przy wartościach granicznych także trend (00:42:31).
- **Quick Ratio** (slajd: (Current Assets − Inventory) / Current Liabilities). Płynność bieżąca bez zapasów, bo zapasów nie da się szybko i pewnie sprzedać. Poziom i trend (nie powinien spadać).
- **Ohlson** – w Scrabie jako prawdopodobieństwo bankructwa w 12 miesięcy, w procentach. Nie czytać dosłownie, tylko jako miarę bezpieczeństwa: niżej = lepiej (00:49:02–00:51:27).
- **Altman Z-Score** – brać wariant Nonmanufacturers (dla spółek nieprodukcyjnych); tak ocenia się też Apple, Nvidię, Broadcom, ARM, bo projektują, a produkcję zlecają (00:52:55). TSM i ASML to producenci (01:21:27). Dla uproszczenia o wariancie produkcyjnym można zapomnieć (01:38:39).

### Zasady punktowania
- Wszystkie sześć wskaźników oceniamy **bezwzględnie** (bez porównania krzyżowego do innych spółek) – 01:20:14.
- Progi są orientacyjne, nie zero-jedynkowe: 2,9 a 3,1 to nie różnica między spółką niebezpieczną i bezpieczną (00:38:13). Punkty przyznaje się „na oko", ważne jest zachowanie właściwej różnicy między spółkami, a nie dokładna liczba (02:00:33).
- Dane: TTM (trailing twelve months, ostatnie 12 miesięcy), jeśli dostępne; inaczej Annual (roczne). Kwartalnych nie używać – za duże wahania (00:28:47, 01:18:48).
- Wynik końcowy służy tylko do uszeregowania spółek; nie ma minimalnego progu punktów, bierze się 20–30 najlepszych (01:19:13).

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Ohlson Default Probability | < 10% (granica absolutna); większość dobrych spółek ma < 1%, więc ~5% Trela też by odpuścił, chyba że zyskowność wybitna | max 10; 0–0,12% → 10; 1,68% → 8 | slajd 00:28:09, 01:57:45; nagranie 01:07:34–01:12:37 |
| Altman Z''-Score (Nonmanufacturers) | > 3 świetnie; 1,2–3 przeciętnie; < 1,2 fatalnie | max 10; dużo powyżej 3 → 10; 3,44 → 9; 2,73 → ok. 9 (−1 pkt); 1,05 → 2 | slajd 01:26:01, 01:58:39; nagranie 00:55:11, 01:58:15 |
| Altman Z-Score (produkcyjne) | > 3 świetnie; 1,8–3 przeciętnie; < 1,8 fatalnie | – | slajd 01:24:33 |
| Debt to Assets | < 40%; powyżej 35–40% mocny sygnał ostrzegawczy; trend płaski lub spadkowy | max 5; 2% → 5; 22% płasko → 3,5; 23% rosnąco → 2; 31% spadkowo → 3; 31% rosnąco → 2; „totalnie zadłużona" → 0 | slajd 00:28:09, 01:04:26; nagranie 00:31:26, 01:23:19 |
| Interest Coverage | > 3 | max 5; 35–10 000 → 5; 6,61 (wcześniej ujemne) → 4,5; 5 stabilnie → 5 | slajd 00:28:09, 01:59:15 |
| CFO to Debt | > 0,2 (w nagraniu: 0,2–0,3 „wystarczająco") | max 5; ≥ 1 → 5; 0,35 → 3; 0,19 → 2; pełne 5 pkt dopiero powyżej 0,5 (z nagrania, niepotwierdzone slajdem – sprawdź 02:00:23) | slajd 00:28:09, 02:00:24 |
| Quick Ratio | > 0,8 (lub Current Ratio > 1); ≥ 1 „superbezpiecznie" | max 5; 1,58 → 5; 9,79 → 5; 0,74 → 4 | slajd 00:28:09, 02:01:03 |
| Suma fundamentów | TOTAL FUNDS = suma 6 ocen / 40 | 40 pkt | Excel, slajd 00:59:27 |
| Suma zyskowności | TOTAL GROWTH = suma 8 ocen / 55 | 55 pkt | Excel |
| Wynik łączny | TOTAL of TOTALS = (TOTAL GROWTH % + TOTAL FUNDS %) / 2 | nagłówek „95 pkt" | Excel (formuła) |
| Wariant „tylko Scrab" | zostawić Ohlsona i Altmana, każdy po 20 pkt, cztery pojedyncze wskaźniki pominąć | 20 + 20 | nagranie 00:48:48, 01:32:50 |
| Wariant zero-jedynkowy | fundamenty bez punktów, tylko test „bankrut / nie bankrut" (np. Ohlson 0,5% = przechodzi) | brak | nagranie 01:33:24 |

Uwaga: w Excelu wynik łączny to zwykła średnia dwóch procentów, więc zyskowność i fundamenty ważą po połowie mimo proporcji 55:40. Trela zapowiada, że wagi będą jeszcze zmieniane po backtestach (01:13:24). Przy zmianie liczby punktów trzeba poprawić dzielnik w formule (np. 40 → 20) – 01:34:25.

## Przykłady z lekcji

### Punkty fundamentów przyznane spółkom (Excel „Model-2026-Fundamenty")

| Spółka | Ohlson (10) | Altman (10) | Debt/Assets (5) | Int. Cov. (5) | CFO/Debt (5) | Quick (5) | FUNDS | GROWTH | Łącznie |
|---|---|---|---|---|---|---|---|---|---|
| ALAB (Astera Labs) | 10 | 10 | 5 | 5 | 5 | 5 | 100% | 85% | 92% |
| MRVL (Marvell) | 10 | 9 | 3,5 | 4,5 | 3 | 5 | 88% | 82% | 85% |
| META | 10 | 10 | 2 | 5 | 5 | 5 | 93% | 75% | 84% |
| ORCL (Oracle) | 8 | 2 | 0 | 5 | 2 | 4 | 53% | 78% | 65% |

NVO i TSLA mają w arkuszu tylko zyskowność (38% i 31%), fundamentów nie oceniano; WMT bez ocen.

Uzasadnienia z nagrania:
- **ALAB** (00:59:08–01:03:02): Ohlson 0%, Altman ok. 14, dług 2% aktywów (ok. 30 mln USD przy 1,5 mld aktywów), Interest Coverage ok. 10 000, CFO/Debt ok. 10, Quick Ratio 9,79. Wszędzie maksimum. Krótka historia giełdowa nie przeszkadza – liczy się stan dzisiejszy.
- **META** (01:03:06–01:06:30): Ohlson 0,02%, Altman ok. 5,4 (spada, ale daleko powyżej 3), Interest Coverage ok. 70, CFO/Debt powyżej 1, Quick powyżej 1. Jedyna kara: Debt to Assets 23,24% i stale rośnie → 2 pkt (poniżej połowy skali).
- **MRVL** (01:57:09–02:01:11): Ohlson 0,12% → 10; Altman 3,44 → 9 (dziesiątka dla wyraźnie wyższych); dług 22% i płasko → 3,5; Interest Coverage 6,61, ale wcześniej ujemne → 4,5; CFO/Debt 0,35 → 3; Quick 1,58 → 5.
- **ORCL**: Ohlson 1,68% (wyższy, ale spada) → 8; Altman 1,05, czyli poniżej granicy akceptacji → 2; spółka „totalnie zadłużona" → 0; Interest Coverage 5 → 5; CFO/Debt 0,19 → 2; Quick 0,74 → 4.
- **AAPL** (ilustracja czytania wskaźników, bez wpisu do arkusza): Debt to Assets 31,28% i spada (Trela dałby 3 pkt), Interest Coverage 35,87, CFO/Debt 0,99, Quick 0,86, Ohlson 0,3%, Altman 2,73.
- Porównanie Ohlsona wielu spółek (01:13:21): AMC 32,83%, HTZ 5,48%, F 5,02%, BCRX 2%, VRT 1,27%, reszta poniżej 1% – dowód, że przy takim tle 5% to już dużo.

## Narzędzia
- **Yahoo Finance** → Financials → Balance Sheet (AAPL): rozwijanie Total Assets / Total Liabilities.
- **Scrab → Master Chart** (app.scrab.com/charts/master): metryki „Ohlson Score Bankruptcy Probability (TTM)", „Altman Z-Score - Nonmanufacturers (TTM)", „Debt to Assets (Annual)", „Interest Coverage (TTM)", „CFO to Debt (Annual)", „Quick Ratio (Annual)"; pomocniczo „Total Debt (Annual)", „Total Assets (Annual)", „Net Income (Annual)", „Cash from Operations (Annual)". Kilka spółek naraz na jednym wykresie pozwala zobaczyć tło.
- **Excel „Model-2026-Fundamenty"**: kolumny L–Q (fundamenty), R = SUM(L:Q)/40, S = (K+R)/2, sortowanie malejąco po S.
- Wg Treli Ohlsona poza Scrabem praktycznie nie ma za darmo; cztery pojedyncze wskaźniki są w każdym darmowym serwisie (00:47:41).
- Rada: prowadzić kartotekę spółek – jeden plik na ticker z własnymi notatkami (01:29:15).

## Co z tego zastosuję w skanerze
1. Kolejność: najpierw wynik zyskowności; fundamenty liczyć tylko dla spółek z dobrą zyskownością.
2. Pobierać sześć wskaźników w wersji TTM, a gdy brak – Annual; nigdy kwartalnych.
3. Flagi ostrzegawcze: Ohlson ≥ 10%, Altman Z'' < 1,2, Debt/Assets > 40%, Interest Coverage < 3, CFO/Debt < 0,2, Quick Ratio < 0,8.
4. Punktacja stopniowana zamiast progu 0/1: maksimum dla wyniku wyraźnie lepszego od progu, częściowe punkty w okolicy progu, 0–2 pkt wyraźnie poniżej (kalibracja na przykładach z tabeli).
5. Debt/Assets: korekta o trend – przy tym samym poziomie spadek długu +1 pkt względem wzrostu.
6. Interest Coverage: przy wartości dużo powyżej 3 nie karać za trend.
7. Wynik: FUNDS% = suma/40; łączny = (GROWTH% + FUNDS%)/2; wagi jako parametry do zmiany. Dodać przełączniki: „Ohlson 20 + Altman 20" oraz tryb zero-jedynkowy.
8. Ranking malejąco po wyniku łącznym, bez progu minimalnego; brać czołówkę listy.

## Pytania powtórkowe
1. Co Trela rozumie przez „fundamenty" i dlaczego nie chce dawać im dużej wagi?
2. Jakie są progi dla sześciu wskaźników ze slajdu „Najlepsze wskaźniki fundamentalne"?
3. Dlaczego META dostała tylko 2 pkt za Debt to Assets, choć ma 23%, czyli dużo poniżej 40%?
4. Czym różni się Interest Coverage od CFO to Debt i po co oba?
5. Który wariant Altmana stosować do Apple lub Nvidii i dlaczego?
6. Jak liczony jest w Excelu wynik łączny i jakie są dwa uproszczone warianty oceny fundamentów?

## Niepewne – do sprawdzenia
- Liczby z bilansu Apple (current assets 147 mld vs current liabilities 165 mld; aktywa długoterminowe 211 vs zobowiązania 119; gotówka 54, należności 72) – tylko z nagrania, na arkuszach widać inny widok (00:15:47–00:25:37).
- ALAB: Altman ok. 14, Debt/Assets 2%, Interest Coverage ok. 10 000, CFO/Debt ok. 10, dług 30 mln / aktywa 1,5 mld / zysk 200 mln / CFO 300 mln – z nagrania, niepotwierdzone slajdem (00:59:39–01:02:47).
- META: Altman ok. 5,4, Interest Coverage ok. 70, CFO/Debt > 1 – z nagrania (01:03:30–01:04:54). Ohlson: w mowie „dwie dziesiąte procent", na slajdzie 0,02% – przyjęto slajd.
- ORCL: wartość Debt to Assets nie padła czytelnie i nie ma jej na arkuszach (01:58:45). Ohlson w transkrypcji zniekształcony („76%"), na slajdzie 1,68%.
- MRVL: Debt to Assets „22%" tylko z nagrania (01:58:55). CFO/Debt: Trela wahał się między 3 a 4, w Excelu zostało 3; ORCL Quick: wahanie 3,5–4, w Excelu 4.
- „0 punktów" za Altmana – Trela wskazał fragment wykresu, nie podał liczby (01:58:31); prawdopodobnie okolice zera i niżej (?).
- Próg „5 pkt za CFO/Debt dopiero powyżej 0,5" – tylko z nagrania (02:00:23).
- Ohlson: na wcześniejszych zajęciach padła granica 3%, tu 10%; Trela mówi, że nie ma jednej granicy (01:07:34).
- W nagłówku Excela literówka „EBIRDA Margin" (chodzi o EBITDA Margin).

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
