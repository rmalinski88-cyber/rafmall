---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 8. Automatyzacja modelu, cz. 2 (spotkanie 8), 29 kwietnia 2026, ok. 2 h 06 min"
status: do przejrzenia
---
# Trela 08 – Automatyzacja modelu cz. 2: kalibracja i backtesty (spotkanie 8)

## W skrócie
Trela dalej testuje model „Uniwersytet 2026" w Scrab (Scoring Models – modele punktowe). Sprawdza backtestami (symulacjami na danych historycznych), czy warto dodać fundamenty i wskaźniki wyceny. Wynik: ryzyko bankructwa wg Ohlsona szkodzi, wskaźnik Altmana pomaga (zostaje z wagą 30 pkt), a P/S, P/E i PEG pogarszają wynik i wylatują. Rebalansowanie co 3 miesiące, 25 spółek i równe wagi zostają bez zmian. Filar Growth nie był na tym spotkaniu ruszany.

## Najważniejsze koncepty

### Decyzji nie ocenia się po wyniku (00:00:37–00:04:22)
- Poprawna decyzja może przynieść stratę, a zła – zysk. Liczy się ogół decyzji przez lata.

### Do czego służy backtest (00:04:27–00:15:52)
- Wysokość CAGR (średnioroczna stopa zwrotu) z backtestu nie ma wartości prognostycznej – zależy od zestawu spółek i dat startu/końca.
- Jedyna rola testu: sprawdzić, czy zmiana jednego parametru na wejściu poprawia, czy pogarsza wynik, i czy różnica jest wyraźna. Ok. pół pkt proc. rocznie może być przypadkiem; 2–4 pkt proc. już nie (00:36:49, 00:44:14).
- Zestaw spółek musi być stały między testami (Trela: dzisiejszy screener). Analizy miękkiej nie da się testować; zmiana musi mieć logiczne uzasadnienie (01:02:33).
- Jedyny trwały wniosek z lat testów: spółki o wysokiej zyskowności radzą sobie lepiej niż przeciętne (00:08:50).
- Okres testu: 10 lat, nie 5 (00:35:10). Docelowo „meta-backtesty": kroczące okna 10-letnie i średnia (00:37:53).

### Model Portfolios – drugi rodzaj testu (00:16:00–00:29:55)
- Ręcznie wpisana lista spółek, sprawdzana od faktycznej daty rekomendacji – do weryfikacji własnych lub cudzych typów.
- Portfel wybrany pod wysoki upside (potencjał wzrostu do ceny docelowej analityków) trzeba oceniać w horyzoncie rebalansowania, bo upside się dezaktualizuje.
- Rada: zapisywać historyczne oceny swoich spółek – po 2–3 latach powstaje własny test z analizą miękką.

### Fundamenty w modelu (00:31:08–00:47:20, 01:06:02–01:08:13)
- Dowartościowanie „hamulców" (bezpieczeństwa) automatycznie zmniejsza względną wagę zyskowności i upside.
- Altman Z-Score: Working Capital/Total Assets, Retained Earnings/Total Assets, EBIT/Total Assets, Market Value of Equity/Book Value of Total Liabilities, Sales/Total Assets (slajd 00:45:18). Wg Treli mierzy głównie efektywność obracania kapitałem, nie samo bezpieczeństwo – stąd pomaga.
- Bankructwo zyskownej spółki to margines: wcześniej psują się zyskowność i ceny docelowe (wyjątki: oszustwa typu Enron, Wirecard).

### Wycena: nie jako kryterium zakupu (00:49:06–01:27:05)
- Historical Range: Scrab rysuje kanał z historii wskaźnika danej spółki; poniżej kanału maks. punktów, powyżej 0 (przy „niżej = lepiej").
- Kupowanie „tanich" obniża wynik; premiowanie „drogich" daje to samo co „tanich" – parametr do pominięcia.
- Pułapka automatu: jednorazowa anomalia (P/E w dziesiątkach tysięcy u MDB) rozciąga kanał i spółka dostaje niesłusznie maks. punktów (01:09:14).
- Jak Trela sam używa wyceny: ekstremalnie wysoka wycena + niski upside → redukcja lub przeniesienie kapitału do równie zyskownej, tańszej spółki; atrakcyjna wycena spółki już posiadanej → zwiększenie ekspozycji (np. opcjami).

### Zmienność i liczba spółek (00:54:14–00:57:14, 01:11:27–01:14:35, 01:53:27–02:04:40)
- Większe obsunięcie wymaga większego odbicia: −10% → +11%; −30% → ok. +42% (wg Treli).
- Dla inwestora indywidualnego zmienność to głównie problem psychologiczny.
- Im mniej wiemy o spółkach, tym więcej ich trzeba. Trela ma ok. 10, ale po własnej analizie miękkiej; bez niej rekomenduje ok. 25 (1 z 25 = 4% portfela, 1 z 10 = 10%).

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Rebalansowanie | co 3 miesiące; dopuszczalne 1–3 mies.; 6 mies. za długo (dwa kwartały wyników) | – | nagranie 01:34:33–01:37:32 |
| Przegląd ostrzegawczy | co miesiąc sprawdzić rewizje ceny docelowej | – | nagranie 01:36:45 |
| Liczba spółek | 25 | – | slajdy 01:38:24, 01:42:42; nagranie 01:44:27 |
| Wagi w portfelu | równe (Equal Weights) | – | slajdy 01:56:45, 01:59:06 |
| Staż na giełdzie | 3 lata od IPO; 1 rok nie zmienia wyniku | filtr | slajd 01:27:03; nagranie 02:01:03 |
| Altman Z-Score (opis w słowniku Scrab) | ≥3 zdrowa; 1,8–3 szara strefa; <1,8 ryzyko bankructwa w 2 lata | – | slajd 00:45:18 |
| Kanał Historical Range | ok. 70% odczytów w kanale, po 15% nad i pod | – | z nagrania, niepotwierdzone slajdem – sprawdź 00:51:10; Trela niepewny |
| Limit backtestu | maks. 1000 spółek; historyczny screener tnie listę alfabetycznie | – | z nagrania, niepotwierdzone slajdem – sprawdź 00:38:39 |

## Konfiguracja modelu punktowego w Scrab (stan po spotkaniu 8)

Punktacja liniowa między Worst (0 pkt) a Best (maks.). Stan końcowy: slajd 01:27:03. Razem 129 pkt: Growth 55, Fundamentals 30, Value 41, Must-Have 3.

| Metryka (reguła → wskaźnik, typ) | Filar | Waga / maks. pkt | Progi (Worst → Best) | Kierunek | Źródło |
|---|---|---|---|---|---|
| Revenue TTM → Revenue (TTM), Change Over Time 5 lat | Growth | 5 | 50% → 100% | wyżej = lepiej | punkty: slajd 01:27:03; progi z cz. 1 |
| Revenue Estimates → Revenue Average Estimated Annual Growth in Next 2 Years, Static Range | Growth | 10 | 10% → 30% | wyżej = lepiej | jw. |
| EPS TTM → EPS Basic (TTM), Change Over Time 5 lat | Growth | 5 | 100% → 250% | wyżej = lepiej | jw.; progi tylko z nagrania cz. 1 |
| EPS Estimates 2y → EPS Average Estimated Annual Growth in Next 2 Years, Static Range | Growth | 5 | 15% → 40% | wyżej = lepiej | jw. |
| EPS Estimates 5y → EPS Long Term (5 Years) Growth Estimates, Static Range | Growth | 5 | 15% → 30% | wyżej = lepiej | jw. |
| CFO TTM → Cash from Operations (TTM), Change Over Time 5 lat | Growth | 10 | 100% → 250% | wyżej = lepiej | jw.; progi tylko z nagrania cz. 1 |
| CFO Estimates → prognoza wzrostu CFO (?) | Growth | 5 | 15% → 30% | wyżej = lepiej | jw.; progi tylko z nagrania cz. 1 |
| EBITDA Margin → EBITDA Margin (TTM), Static Range | Growth | 10 | 20% → 40% | wyżej = lepiej | jw. |
| **Altman Score → Altman Z-Score – Nonmanufacturers (TTM), Static Range** – NOWE | Fundamentals | 30 | 1,0 → 4,0; bez must-have | wyżej = lepiej | slajd 00:41:15 |
| PT Revisions → Price Target, Maximum Drawdown 45 dni | Value | 1, must-have | −5% → −4,9% | mniejszy spadek = lepiej | punkty: slajd 01:27:03; progi tylko z nagrania (cz. 1 i 00:31:17) |
| PT Change over year → Price Target, Change Over Time 180 dni | Value | 10 | 10% → 20% | wyżej = lepiej | punkty: slajd 01:27:03; progi z cz. 1 |
| **Upside** → Historical Range, 4 lata, kanał poziomy – ZMIANA WAGI | Value | **30** (w cz. 1: 15) | poniżej kanału 0 → powyżej maks. | wyżej = lepiej | punkty: slajd 00:34:24 i 01:27:03; ustawienia z cz. 1 |
| Market Cap → Market Cap (USD) | Must-Have | 1, must-have | 10 mld → 10,1 mld USD (wg cz. 1) | wyżej = lepiej | punkty: slajd 01:27:03 |
| EPS Number → EPS Number Estimates for 2 Fiscal Years Ahead | Must-Have | 1, must-have | 3,0 → 3,1 | wyżej = lepiej | jw. |
| EPS > 0.50 → EPS Basic (TTM) | Must-Have | 1, must-have | Worst 0,5 USD | wyżej = lepiej | jw. |

**Testowane i odrzucone (nie ma ich w modelu):**

| Reguła → wskaźnik | Ustawienia | Efekt | Źródło |
|---|---|---|---|
| Ohlson Score → Ohlson Score Bankruptcy Probability (TTM), Static Range, must-have | 1 pkt; Worst 2,00% → Best 1,99% (powyżej 2% wyklucza) | z 21,4% na 17,62% | slajdy 00:34:24, 00:35:18 |
| Ohlson Score jako waga | 30 pkt; 3% → 0%, bez must-have | 17,58% | wynik: slajd 00:46:33; ustawienia: z nagrania, niepotwierdzone slajdem – sprawdź 00:35:58–00:36:34 |
| PS Ratio 2y → PS Ratio (2-Year Forward), Historical Range | 20 pkt, 5 lat, kanał poziomy, niżej = lepiej | z 23,31% na 19,5% | slajdy 00:58:09 (20 pkt, 5 lat), 00:57:51 |
| PS Ratio 2y, kanał skośny, niżej = lepiej | Horizontal Channel odznaczony | lepiej niż poziomy, gorzej niż bez reguły; liczba nie padła | slajd 00:58:09; nagranie 01:01:23 |
| PS Ratio 2y, kanał skośny, wyżej = lepiej | Higher Values Preferred zaznaczone | łącznie 519,36% – „to samo" co tanie | slajdy 01:08:33, 01:08:57 |
| PE Ratio 2y → PE Ratio (2-Year Forward), Historical Range | 20 pkt, 5 lat, poziomy, niżej = lepiej | 20,67% | slajdy 01:15:57, 01:15:18 |
| PEG Ratio (2-Year Forward), Historical Range | 20 pkt, 5 lat, poziomy, niżej = lepiej | łącznie 474,71% | slajdy 01:17:18, 01:20:54 |

Zmiany względem cz. 1: (1) Fundamentals z 0 na 30 pkt (Altman); (2) Upside 15 → 30 pkt (Value 26 → 41) – to wyjaśnia niewiadomą z notatki 07; (3) Growth i Must-Have bez zmian; (4) koniec testów przesunięty na 22.04.2026.

## Backtesty

Wspólne: model „Uniwersytet 2026", 689 spółek ze screenera, 01.06.2016–22.04.2026 (wynik liczony do 1.03.2026), opcja Reduce turnover, Tolerance Full. S&P 500: 12,95% rocznie, łącznie 227,67%, maks. obsunięcie −33,92%, zmienność 0,18 (slajd 01:57:48). Jeśli nie podano inaczej: 25 spółek, rebalans 3 mies., równe wagi, 3 lata od IPO.

| Wariant | CAGR | Łącznie | Uwagi | Źródło |
|---|---|---|---|---|
| Punkt wyjścia z cz. 1 | 21,4% | 562,44% | – | slajd 00:47:48 |
| + Ohlson must-have (2%) | 17,62% | 386,45% | odrzucone | slajd 00:35:18 |
| + Ohlson 30 pkt | 17,58% | 384,93% | odrzucone | slajd 00:46:33 |
| **+ Altman 30 pkt (nowa baza)** | **23,31%** | **671,55%** | obsunięcie −33,40%, zmienność 0,23, Sharpe 1,01 | slajdy 00:47:36, 01:57:48 |
| baza + P/S (poziomy, tanie) | 19,5% | 467,8% | odrzucone | slajd 00:57:51 |
| baza + P/S (skośny, drogie) | ok. 20,6% (dopisek Claude'a: wyliczone z zysku łącznego) | 519,36% | odrzucone | slajd 01:08:33 |
| baza + P/E | 20,67% | 524,81% | odrzucone | slajd 01:15:18 |
| baza + PEG | ok. 19,6% (dopisek Claude'a: wyliczone) | 474,71% | odrzucone | slajd 01:20:54 |
| baza, rebalans 6 mies. | 21,87% | 554,61% | gorzej (okres do 1.12.2025) | slajd 01:31:15 |
| baza, rebalans 2 mies. | ok. 21,8% (?) | – | gorzej | lista przebiegów 01:41:57 (nieostre); nagranie 01:34:31 |
| baza, rebalans 1 mies. | ok. 18,8% (?) | – | gorzej, także po poprawce na 3 lata od IPO | lista przebiegów 01:52:48 (nieostre); nagranie 01:47:58 |
| baza, 10 spółek | 18,85% | 438,61% | gorzej | slajd 01:38:24 |
| baza, 20 spółek | 21,61% | 573,74% | gorzej | slajd 01:42:42 |
| baza, 35 spółek | ok. 21,8% (?) | – | gorzej niż 25 | lista 01:52:48 (nieostre) |
| baza, 50 spółek | ok. 20,8% (?) | – | obsunięcie ok. 31%, zmienność 21% – nie warte ok. 200 pkt proc. zysku | lista 01:41:57 (nieostre); z nagrania, niepotwierdzone slajdem – sprawdź 01:40:26 |
| wagi Proportional to Metric (Upside), z Correlation Adjusted i bez | bez poprawy | – | odrzucone | nagranie 01:52:39, 01:55:29 |
| wagi Equal Risk | 23,27% | 668,63% | obsunięcie −34,09%, zmienność 0,22 – bez znaczenia | slajdy 01:56:45, 01:57:06 |
| wagi Hierarchical Risk Parity | 22,05% | 597,78% | gorzej | slajd 01:59:06 |
| 1 rok od IPO | ok. 23,4% (?) | – | bez wpływu | lista 02:01:12 (nieostre) |

## Przykłady z lekcji
- **Portfel AI z 12.02.2026** (12 spółek z 15; VRT, MU, AMAT pominięte przez niski upside): +26% wobec +10% Nasdaq (z nagrania, niepotwierdzone slajdem – sprawdź 00:22:17–00:23:10).
- **„2025 Top 20 Ideas"** (20 spółek o najwyższym upside z końca 2024, bez rebalansowania): do kwietnia 2026 przegrywa z SPY; w pierwszym kwartale −0,81% wobec −4,05% SPY (slajd 00:28:15). Dowód, że taki portfel ocenia się w horyzoncie rebalansowania.
- **MDB** – skok P/E psuje kanał (slajd 01:15:57). **Broadcom** – niska wycena w kwietniu 2025 jako okazja do zwiększenia pozycji (01:25:20).

## Narzędzia
- **Model Portfolios → New Model Portfolio**: tickery, Rebalancing Frequency (No Rebalancing), Asset Allocation → Save → Master Chart, Custom Range od daty rekomendacji, porównanie z SPY/QQQ.
- **Add Rule → Build Your Own → Historical Range**: pola Higher Values Preferred, Years for Channel, Horizontal Channel, Must-have.
- **Backtests → New Backtest → Calculate Data → Modify**: Rebalancing Frequency (miesiące; częściej niż co 1 mies. się nie da), Portfolio Size, Asset Allocation (Equal Risk / Equal Weights / Hierarchical Risk Parity / Proportional to Metric z polami Metric, Higher Values Preferred, Correlation Adjusted), Required Years Since IPO → Run Backtest → Open Tear Sheet.
- Wskaźników własnych (Custom Metrics, plan Advanced) Trela celowo nie dodaje do modelu publicznego (01:41:15).

## Co z tego zastosuję w skanerze
1. Dodać filar Fundamentals: Altman Z-Score (wersja Nonmanufacturers, TTM) → ≤1,0 = 0 pkt, ≥4,0 = 30 pkt, liniowo pomiędzy; bez wykluczania.
2. Nie wykluczać ani nie punktować spółek za prawdopodobieństwo bankructwa Ohlsona.
3. Podnieść wagę Upside do 30 pkt; PT Change 10 pkt; spadek ceny docelowej o 5% lub więcej → wykluczenie.
4. Nie punktować P/S, P/E, PEG. Ewentualnie osobna flaga ostrzegawcza: wycena skrajnie wysoka na tle własnej historii + upside bliski zera → „rozważ redukcję/zamianę" (decyzja ręczna).
5. Wynik końcowy = suma punktów / 129; ranking → 25 najlepszych, równe wagi, przegląd co 3 miesiące, min. 3 lata od IPO.
6. Co miesiąc alert: spadek ceny docelowej w spółkach z portfela.
7. Zapisywać historyczne oceny każdej spółki z datą.
8. Testując zmianę: ten sam zestaw spółek i okres, jedna zmiana naraz; różnice poniżej ok. 0,5 pkt proc. traktować jako szum.

## Pytania powtórkowe
1. Dlaczego wysokość CAGR z backtestu nie mówi nic o przyszłości i co w takim razie z testu odczytujemy?
2. Jak zadziałał Ohlson (must-have i jako waga), a jak Altman? Jak Trela tłumaczy różnicę?
3. Co wyszło z testów P/S, P/E i PEG i do czego Trela mimo to używa wyceny?
4. Jakie ustawienia portfela zostały po testach (rebalans, liczba spółek, wagi, staż od IPO)?
5. Dlaczego portfela dobranego pod upside nie wolno oceniać po półtora roku bez rebalansowania?

## Niepewne – do sprawdzenia
- Wyniki oznaczone (?) odczytane z małej, nieostrej listy „Previous Runs" – przypisanie do wariantów po godzinach przebiegów.
- Ohlson jako waga (30 pkt, 3% → 0%) – tylko z nagrania (00:35:58).
- Wynik P/S z kanałem skośnym „tanie" – liczba nie padła (01:01:23). Trela mówi, że PEG „utrzymuje wyniki bez zmian" (01:20:45), a slajd pokazuje 474,71% wobec 671,55% bazy.
- Progi Growth, PT Revisions, Market Cap i ustawienia Upside nie były pokazane na tym spotkaniu – przeniesione z notatki 07; nadal nieznana dokładna nazwa wskaźnika Upside i CFO Estimates.
- „2025 Top 20 Ideas" za cały okres: ok. 16% wobec ok. 21% SPY (?) – slajd 00:27:42 nieczytelny.
- Zapowiedziane, niewykonane: test „tylko giełda USA" (01:27:39), dodanie Momentum (01:58:35), inne wskaźniki fundamentów (Current Ratio, Quick Ratio, Debt to Assets, CFO to Debt – 00:46:44).

## Powiązane
- [[Trela 07 - Automatyzacja modelu]]
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
