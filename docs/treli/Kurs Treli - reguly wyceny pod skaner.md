---
utworzono: 2026-10-13
tags:
  - inwestycje
  - akcje
  - kurs-trela
  - skaner
zrodlo: "Synteza notatek z kursu Uniwersytet Inwestycyjny 2026 – Tomasz Trela (semestr akcyjny, 23 nagrania)"
status: do przejrzenia
---
# Kurs Treli – reguły wyceny pod skaner

To notatka z kursu, nie porada inwestycyjna: opisuje metodę prowadzącego. Kolumna „pewność": `slajd` = potwierdzone slajdem, ekranem lub Excelem; `tylko nagranie` = padło tylko w mowie. „Skąd" = numer notatki, czas nagrania.

## W skrócie
Trela ocenia spółki w trzech filarach: zyskowność (Growth), fundamenty, czyli bezpieczeństwo finansowe (Fundamentals), i wycena (Value). Finalny model (spotkania 8, 10, 11) ma 15 reguł i 129 punktów: Growth 55, Fundamentals 30 (sam Altman), Value 41 (same reguły oparte na cenie docelowej analityków), Must-Have 3. Klasyczne wskaźniki wyceny (P/S, P/E, PEG) i Ohlson odpadły po backtestach, czyli testach reguł na danych historycznych. Portfel: 20–25 najlepszych spółek z giełd USA, przegląd co 3 miesiące. Wynik modelu to podpowiedź: przed transakcją Trela ręcznie przegląda TOP 50.

## Proces od A do Z (wersja końcowa)
0. **Przygotowanie (raz):** cel, horyzont, stałe daty rebalansu, plan na krach, własna checklista; stare przypadkowe pozycje sprzedać (slajd, 11, 00:02:32, 01:07:51).
1. **Screener** (filtr wstępny): luźne warunki, tylko giełdy USA. Wszystkie wyniki trafiają do modelu, stare spółki zostają w bazie.
2. **Model punktowy:** 15 reguł, wynik = suma punktów / 129. Niespełniony warunek Must-Have = flaga i koniec listy.
3. **Przegląd ręczny TOP 50** (na spotkaniu 10 była mowa tylko o proponowanej dwudziestce): szukać skoków, cykliczności, świeżego przejścia ze straty do zysku; czytać sprawozdanie i transkrypcję rozmowy zarządu z analitykami; odrzucać spółki ze spadającą ceną docelową.
4. **Portfel:** 20 spółek ważonych ryzykiem albo 25 po równo.
5. **Alerty:** wejście przy upside ≥ próg z historii spółki; wyjście (opcjonalnie) przy upside ≤ 0. Upside = o ile procent cena docelowa analityków (Price Target, PT) jest powyżej kursu.
6. **Co miesiąc:** wynik portfela → rewizje prognoz EPS (zysk na akcję), przychodów i PT → wiadomości. Transakcje tylko w wyjątkach (spotkanie 10 mówiło: żadnych; obowiązuje wersja z 11).
7. **Co kwartał – rebalans** (przywrócenie składu i wag): ok. 3 tygodnie po starcie sezonu wyników → kroki 1–3 → lista kupna i sprzedaży przefiltrowana przez wyjątki z sekcji „Kiedy sprzedać".

## Krok 1. Filtry wstępne (screener)
| Metryka (jak w Scrab) | Warunek | Po co | Pewność | Skąd |
|---|---|---|---|---|
| Exchanges | tylko USA (z ADR-ami, czyli kwitami na akcje spółek zagranicznych) | lepsze prognozy analityków; w teście podniosło wynik | slajd | 10, 00:38:25 |
| Market Cap (USD) – kapitalizacja | ≥ 10 mld | płynność, pokrycie analityków | tylko nagranie | 10, 01:07:46 |
| Revenue Average Estimated Annual Growth in Next 2 Years | ≥ 5% | prognozowany wzrost przychodów | tylko nagranie | 10, 01:07:46–01:10:24 |
| EPS Average Estimated Annual Growth in Next 2 Years | ≥ 5% | prognozowany wzrost zysku | tylko nagranie | jw. |
| EPS Basic (TTM) | ≥ 0,10 USD | odcina spółki groszowe | tylko nagranie | jw. |
| Altman Z-Score – Nonmanufacturers (TTM) | ≥ 2 | minimum bezpieczeństwa | tylko nagranie | jw. |
| EBIT / EBITDA Margin (TTM) | próg nie padł | – | tylko nagranie | jw. |

TTM = ostatnie 12 miesięcy. Wynik: 203 spółki (slajd, 10, 01:07:39). Progi są celowo luźne – rygor siedzi w modelu. Na spotkaniu 6 screener do analizy ręcznej był ostrzejszy (kapitalizacja ≥ 20 mld, wzrost przychodów ≥ 15%).

## Krok 2. Warunki obowiązkowe (Must-Have)
| Metryka | Warunek | Po co | Pewność | Skąd |
|---|---|---|---|---|
| Market Cap (USD) | ≥ 10 mld (Worst 10 → Best 10,1) | jw.; pierwotnie 15 mld | slajd | 07, 01:46:15 |
| EPS Number Estimates for 2 Fiscal Years Ahead | ≥ 3 analityków (3,0 → 3,1) | wiarygodność prognozy | slajd | 07, 00:59:00 |
| EPS Basic (TTM) | ≥ 0,50 USD | przy EPS bliskim zera dynamika w % jest myląca | slajd | 07, 00:33:48 |
| Price Target, Maximum Drawdown, 45 dni (reguła PT Revisions) | spadek PT od szczytu o 5% lub więcej = flaga (−5,00% → −4,90%) | spółki z obniżaną ceną docelową wypadają | slajd | 10, 01:59:03 |
| Required Years Since IPO | min. 3 lata od debiutu | potrzebna historia | slajd | 07, 00:56:21; 10, 01:41:33 |
| Tolerance for Low Scores & Missing Data | Full – brak pojedynczej danej nie wyklucza | – | slajd | 07, 00:56:21 |

Must-Have działa zero-jedynkowo: poniżej Worst spółka dostaje flagę i ląduje na końcu listy (slajd, 07, 01:00:18).

## Krok 3. Model punktowy – finalna konfiguracja
Punktacja liniowa: odczyt ≤ „najgorzej" = 0 pkt, ≥ „najlepiej" = maksimum (slajd, 07, 00:34:12 – opis skali w oknie reguły), pomiędzy proporcjonalnie (tylko nagranie, 07, 01:42:15). Wagi wszystkich reguł potwierdza slajd 10, 02:05:12; „pewność" niżej dotyczy progów.

| Filar | Metryka | Maks. pkt | Najgorzej (0) → najlepiej (maks.) | Kierunek | Pewność | Skąd |
|---|---|---|---|---|---|---|
| Growth | Revenue (TTM), zmiana w 5 lat | 5 | 50% → 100% | wyżej = lepiej | slajd | 07, 00:37:27 |
| Growth | Revenue Average Estimated Annual Growth in Next 2 Years | 10 | 10% → 30% | wyżej | slajd | 07, 00:42:00 |
| Growth | EPS Basic (TTM), zmiana w 5 lat | 5 | 100% → 250% | wyżej | tylko nagranie | 07, 00:44:16–00:44:48 |
| Growth | EPS Average Estimated Annual Growth in Next 2 Years | 5 | 15% → 40% | wyżej | slajd | 07, 00:46:03 |
| Growth | EPS Long Term (5 Years) Growth Estimates | 5 | 15% → 30% | wyżej | slajd | 07, 00:47:00 |
| Growth | Cash from Operations (TTM), zmiana w 5 lat (CFO = gotówka z działalności operacyjnej) | 10 | 100% → 250% | wyżej | tylko nagranie | 07, 00:48:15 |
| Growth | CFO Estimates – prognoza wzrostu CFO na 2 lata (okna reguły nie pokazano; prawdopodobnie „CFO per Share Average Estimated Annual Growth in Next 2 Years") | 5 | 15% → 30% | wyżej | tylko nagranie | 07, 00:49:26 |
| Growth | EBITDA Margin (TTM) – marża zysku przed odsetkami, podatkami i amortyzacją | 10 | 20% → 40% | wyżej | slajd | 07, 00:51:00 |
| Fundamentals | Altman Z-Score – Nonmanufacturers (TTM) | 30 | 1,0 → 4,0 | wyżej | slajd | 08, 00:41:15 |
| Value | PT Revisions: Price Target, Maximum Drawdown, 45 dni | 1 (must-have) | −5,00% → −4,90% | mniejszy spadek = lepiej | slajd | 10, 01:59:03 |
| Value | PT Change over year: Price Target, zmiana w 180 dni | 10 | 10% → 20% | wyżej | slajd | 07, 01:30:06 |
| Value | Upside: Price Target Upside na tle własnej historii z 4 lat (Historical Range, kanał poziomy) | 30 | poniżej kanału → powyżej kanału | wyżej | waga: slajd; ustawienia kanału: tylko nagranie | 08, 00:34:24; 07, 01:40:04–01:42:15 |
| Must-Have | Market Cap (USD) | 1 (must-have) | 10 mld → 10,1 mld | wyżej | slajd | 07, 01:46:15 |
| Must-Have | EPS Number Estimates for 2 Fiscal Years Ahead | 1 (must-have) | 3,0 → 3,1 | wyżej | slajd | 07, 00:59:00 |
| Must-Have | EPS Basic (TTM) | 1 (must-have) | Worst 0,5 USD | wyżej | slajd | 07, 00:33:48 |

Sumy filarów: Growth 55, Fundamentals 30, Value 41, Must-Have 3 = 129 (slajd, 08, 01:27:03; 10, 02:05:12). Spotkania 10 i 11 nie zmieniły ani reguł, ani wag.

**Wynik łączny – dwa różne wzory:**
- **Scrab:** suma punktów / 129. Growth waży ok. 43%. Zielony ≥ 70%, czerwony < 40% (slajd, 10, 01:41:33).
- **Excel:** każdy filar jako ułamek swojego maksimum, potem średnia trzech filarów – każdy waży 1/3 (arkusze Model-2026 i Model-2026-mini).

Przykład rachunku (dopisek Claude'a, liczby wymyślone): prognozowany wzrost przychodów 16% → (16 − 10) / (30 − 10) × 10 = 3 pkt. Altman 3,1 → (3,1 − 1) / 3 × 30 = 21 pkt. Spółka z Growth 40, Altmanem 21, Upside 18, PT Change 6 i kompletem warunków obowiązkowych: Scrab → (40 + 21 + 18 + 6 + 1 + 3) / 129 = 69,0%; Excel mini → (40/55 + 21/30 + 24/40) / 3 = 67,6%.

## Wersja ręczna w Excelu (pełna i mini)
Punkty wpisuje się ręcznie; progów w arkuszu nie ma. Growth (55 pkt) jest w obu arkuszach taki sam. **Mini** (odpowiednik Scraba): Funds = Altman 30; Value 40 = Upside 30 + Target Price 10; brak reguły PT Revisions i warunków Must-Have. **Pełny:** Funds 40, Value 60.

Trela oceniał każdą kolumnę według trendu, poziomu i porównania z najlepszymi spółkami na giełdzie: poziom indeksu S&P 500 to ok. połowa punktów, poziom liderów to maksimum (tylko nagranie, 06, 00:43:26). Odejmował za rewizje prognoz w dół, niestabilność i start z wartości ujemnych. Skale odtworzone z jego przykładów:

| Kolumna (maks.) | Przykładowe oceny | Pewność | Skąd |
|---|---|---|---|
| Revenue TTM (5) | stały wzrost 5; stoją od 2–3 lat 2; spadek 5–15% → 1–0 | slajd | 03, 01:06:42 |
| Revenue Est. (10) | ok. 40% → 8–10; ok. 20% → 7–7,5; 14% z rewizjami w dół → 3; ok. 0 → 0 | slajd | 03, 00:39:36; 06, 01:41:03 |
| EPS TTM (5) | rośnie 5; niestabilnie 4; duże wahania 3,5; 60% pod szczytem 1 | slajd | 03, 02:00:57 |
| EPS 2y Growth (5) | 17,9% (poziom S&P) → 2,5; 20% → 3,5; 27% → 4; 40% → 4,5; stale obniżana → 2 | slajd | 06, 01:41:33 |
| EPS 5y Growth (5) | ok. 40% → 5; 33% → 4,5; 14–19% → 3–3,5; 3% → 0 | slajd | 03, 00:38:51; 06, 01:30:39 |
| Cash from Op. (10) | rośnie 10; lekki spadek po drodze 8; trend spadkowy 3 | slajd | 03, 00:44:16 |
| CFO 2y Est (5) | 7% → 1; 15–17% → 2; 41% → 4 | slajd | 06, 00:46:09 |
| EBITDA Margin (10) | kilka % → 1; 11,6% → 2; ok. 20% rosnąca → 6,5–7; 75,7% → 10 | slajd | 03, 01:52:30; 06, 01:43:57 |
| Ohlson (10) | 0–0,12% → 10; 1–1,7% → 8 | slajd | 04, 01:57:45 |
| Altman (10; mini 30) | dużo ponad 3 → 10; 3,44 → 9; 2,04 → 5; 1,05 → 2 | slajd | 04, 01:58:39; 06, 01:06:48 |
| Debt/Assets (5) | 2% → 5; 9% → 4; 22% płasko 3,5; 23–31% rosnąco 2; od ok. 40% → 0 | slajd | 04, 01:04:26; 06, 01:26:12 |
| Interest Coverage (5) | od 5 stabilnie → 5; 6,61 po okresie ujemnym 4,5; ujemne 0 | slajd | 04, 01:59:15 |
| CFO/Debt (5) | ≥ 1 → 5; 0,35 → 3; 0,19 → 2 | slajd | 04, 02:00:24 |
| Quick Ratio (5) | od ok. 1,5 → 5; ok. 1 → 4,5; 0,74 → 4 | slajd | 04, 02:01:03 |
| P/S, P/E, P/CFO Forward 2y (po 10) | najniżej od 10 lat → 10; lekko nad medianą → 5–6 | slajd | 06, 01:47:33 |
| Upside (20; mini 30) | najwyższy w historii spółki → 20; 70–75% typowego zakresu → 15 | slajd | 06, 00:35:27 |
| Target Price (10) | stabilny po jednym cięciu → 7; płaski → 5; cięty dalej → 0 i spółka poza portfelem | slajd (7 i 0); tylko nagranie (5) | 06, 01:56:51; 05, 01:53:34 |

Zyskowność 75% to granica najlepszej dwudziestki, 68% i mniej – poza nią (tylko nagranie, 06, 00:47:06).

## Wycena – jak czytać wskaźniki
- **P/S** (cena do przychodów), **P/E** (cena do zysku), **P/CFO** (cena do gotówki operacyjnej) – Trela bierze wersje „forward 2y", czyli liczone od prognozy na 2 lata naprzód (slajd, 05, 00:59:12).
- Odczytu nie porównuje się między spółkami, tylko z własną historią spółki z 5–10 lat i medianą kroczącą z 3 lat („3Y Median"). Przy medianie = uczciwie, strefa dolna = tanio, górna = drogo, ponad zakres = bańka (tylko nagranie, 05, 00:14:40; mediana: slajd, 05, 00:38:54).
- **Upside** mówi o momencie zakupu, nie o jakości. Czytany względem własnej historii spółki. Upside ponad 100% to ostrzeżenie (tylko nagranie, 05, 01:53:11).
- **Price Target:** ważniejszy od poziomu jest kierunek zmian. Spadek większy niż ok. 5% od szczytu = nie kupować lub sprzedać (slajd, 06, 01:12:18). Wyjątek: cięcie „techniczne" po dużym spadku kursu, gdy prognozy się nie pogarszają (tylko nagranie, 05, 01:53:53).

**Co weszło do modelu finalnego:** Upside (30), zmiana PT w 180 dni (10), blokada przy spadku PT (must-have).
**Co odrzucono:**
- P/S, P/E, PEG forward 2y jako reguły po 20 pkt – każda pogarszała wynik bazowy 23,31% (wyniki w tabeli backtestów; slajd, 08, 00:57:51, 01:15:18, 01:20:54). Premiowanie spółek „drogich" dało to samo co „tanich".
- EV/EBITDA – brak prognoz EBITDA (tylko nagranie, 05, 01:24:26).
- Wycena zostaje jako ręczne ostrzeżenie: skrajnie wysoka wycena + upside bliski zera → rozważyć redukcję albo zamianę na równie zyskowną, tańszą spółkę (tylko nagranie, 08, 01:22:13–01:25:15).

## Fundamenty – progi bezpieczeństwa
W modelu finalnym jest tylko Altman. Reszta służy analizie ręcznej i pełnemu Excelowi.

| Wskaźnik | Próg | Pewność | Skąd |
|---|---|---|---|
| Altman Z''-Score (spółki nieprodukcyjne) | > 3 świetnie; 1,2–3 przeciętnie; < 1,2 fatalnie | slajd | 03-1, 00:23:39; 04, 01:26:01 |
| Altman – opis w słowniku Scrab | ≥ 3 zdrowa; 1,8–3 szara strefa; < 1,8 ryzyko bankructwa | slajd | 08, 00:45:18 |
| Ohlson (prawdopodobieństwo bankructwa) | < 10% granica absolutna; dobre spółki mają < 1% | slajd (10%); tylko nagranie (1%) | 04, 00:28:09, 01:10:23 |
| Debt/Assets (dług do aktywów) | < 40%, trend płaski lub spadkowy | slajd (40%); tylko nagranie (trend) | 03-1, 00:46:14 |
| Quick Ratio (płynność bez zapasów) | > 0,8; „realnie" > 1 | slajd (0,8); tylko nagranie (1) | 03-1, 00:46:14, 00:46:54 |
| Current Ratio (aktywa bieżące do zobowiązań bieżących) | > 1; „realnie" > 1,2 | slajd; tylko nagranie | 03-1, 00:46:14, 00:46:54 |
| CFO/Debt (gotówka operacyjna do długu) | > 0,2; pełne punkty powyżej 0,5 | slajd; tylko nagranie | 03-1, 00:46:14; 04, 02:00:23 |
| Interest Coverage (EBIT do odsetek) | > 3; absolutne minimum 2 | slajd; tylko nagranie | 03-1, 00:46:14, 00:44:37 |

Dane brać TTM, a gdy ich nie ma – roczne; nigdy kwartalne (tylko nagranie, 04, 00:28:47).

## Analiza miękka i branża
Checklista 25 pytań tak/nie, 1 pkt za każde: Spółka 10, Produkt 6, Otoczenie 9 (slajd, 07-1, 00:49:39; pełna lista w notatkach 06-1 i 07-1). Ok. 20 z 25 = bardzo dobra spółka (tylko nagranie, 07-1, 01:17:37). Spółek w fazie samego pomysłu (embryonic) Trela nie kupuje (slajd, 07-1, 00:08:06). Checklisty nie ma w modelu automatycznym – nie da się jej testować. Stosuje się ją przy przeglądzie TOP 50, razem z lekturą sprawozdania i transkrypcji rozmowy z analitykami (slajd, 11, 00:27:46).

## Portfel i ryzyko
| Parametr | Reguła | Pewność | Skąd |
|---|---|---|---|
| Liczba spółek i wagi | 20 + Equal Risk (większa zmienność = mniejsza waga) albo 25 po równo; różnica ok. 1–1,5 pkt proc. (raz „półtora", raz „jakiś jeden") | slajd (20); tylko nagranie (25 i różnica) | 10, 00:38:25, 00:47:22, 00:57:20 |
| Dopuszczalny zakres | 15–30 spółek z uzasadnieniem; 10 tylko dla doświadczonych | tylko nagranie | 11, 00:06:07, 01:46:22 |
| Rebalans | co 3 miesiące, min. ok. 3 tygodnie po starcie sezonu wyników (dane dla min. 80% spółek), w z góry ustalone dni | slajd (3 mies.); tylko nagranie (reszta) | 10, 00:38:25, 01:06:15; 11, 01:11:52 |
| Histereza | korekta wagi tylko przy odchyleniu ponad 5%; wymiana spółki, gdy kandydat ma wynik lepszy o ponad 1% | tylko nagranie | 10, 01:20:49–01:22:55 |

**Wielkość pozycji – Czarny Excel, arkusz VaR-Full** (slajd, 09, 00:42:48 + arkusz). VaR (Value at Risk) = strata miesięczna, której spółka nie przekroczy z 95% prawdopodobieństwem.
1. Bazowa kwota = wartość portfela × procent na pozycję (100% / liczba spółek, np. 5%).
2. Delta upside = upside bieżący − średni upside z 5 lat + 1.
3. Kwota pozycji = bazowa kwota × (benchmark VaR / VaR spółki) ÷ mnożnik korelacji × delta upside. Benchmark VaR = średnia VaR spółek z listy (w przykładzie 17%).
4. Mnożnik korelacji wpisuje się ręcznie: 1,0 neutralnie; 1,2 dla spółki mocno skorelowanej z resztą (mniejsza pozycja); 0,8 lub 0,5 dla słabo skorelowanej (slajd, 09, 01:15:57).
5. Limity: nie mniej niż 3% i nie więcej niż 6% portfela (slajd, 09, 00:51:12).
6. Liczba akcji = kwota / kurs; ryzyko portfela = suma (VaR × kwota) / portfel.

Sprawdzenie z lekcji: AMD, VaR 20%, korelacja 0,70, delta 0,82 → 50 000 × 17/20 ÷ 0,70 × 0,82 = 49 786 USD. Trela zastrzega: 90% wysiłku w wybór spółek, 10% w wagi (tylko nagranie, 09, 01:53:32).

## Kiedy sprzedać / kiedy nie słuchać modelu
**Sprzedaż zwykła:** spółka wypada przy kwartalnym rebalansie.
**Sprzedaż od razu** (slajd, 11, 00:41:53):
1. Drastycznie obniżone prognozy EPS lub przychodów i nie jest to zdarzenie jednorazowe.
2. Cena docelowa mocno redukowana z merytorycznych powodów (nie przez ogólną korektę rynku).
3. Pojawiły się argumenty ważniejsze niż punktacja.

**Nie słuchać podpowiedzi modelu** (slajd, 11, 00:18:13):
1. Różnica wyniku minimalna (np. 82% i 81%).
2. Kandydat ma wyższy wynik łączny, ale niższy Growth.
3. Wymiana nieuzasadniona podatkowo.
4. Wynik zaniżyła anomalia, np. jednorazowy odpis.
5. Wątpliwy model biznesowy lub branża kandydata (np. spółki surowcowe).

**Nowy zakup:** spółka z czołówki z ujemnym lub bardzo niskim upside – nie kupować teraz, wziąć następną i ustawić alert (tylko nagranie; na ekranie przykład MU z upside −20,83%, 10, 01:32:04–01:33:54). Spółki ze spadającą ceną docelową nie kupować mimo punktów (tylko nagranie; na ekranie przykład ONON, 10, 01:17:30).
**Dobra, ale droga:** sama wysoka wycena nie jest powodem do sprzedaży przy długim horyzoncie; osoby wypłacające z portfela mogą sprzedawać przy upside ok. zera (tylko nagranie, 11, 00:46:04, 01:09:08). Bańka = cena wzrosła absurdalnie, a prognozy wzrostu nie – progu brak (tylko nagranie, 11, 00:50:07).

## Wyniki backtestów (wg prowadzącego)
Wyniki historyczne pokazane na kursie: bez kosztów transakcyjnych, jednorazowa wpłata. Trela podkreśla, że liczy się różnica względem indeksu, a nie sam poziom. CAGR = średnioroczna stopa zwrotu.

| Test | Model | S&P 500 | Pewność | Skąd |
|---|---|---|---|---|
| Meta-backtest finalnego modelu (średnia z 10 dat startu) | 24,12% | średnio 11,7 pkt proc. mniej | slajd | 10, 00:10:10, 00:16:15 |
| Model finalny 2016–2026 | 26% | 12,95% | slajd | 10, 00:10:10 |
| Kontrola błędu przeżywalności (Historical Screener, 10 lat) | 18,11% | 12,95% | slajd | 10, 00:20:06 |
| Tylko historyczny skład S&P 500 | 16,4% | 12,9% | tylko nagranie | 10, 00:19:23 |
| Sama zyskowność (od 06.2016) | 18,06% | 12,95% | slajd | 07, 01:34:33 |
| + reguły PT i Upside | 21,4% | jw. | slajd | 07, 01:50:09 |
| jw. bez blokady spadku PT | 18,99% | jw. | slajd | 07, 01:55:33 |
| + Altman 30 pkt (baza) | 23,31% | jw. | slajd | 08, 00:47:36 |
| + Ohlson (must-have / 30 pkt) | 17,62% / 17,58% | jw. | slajd | 08, 00:35:18, 00:46:33 |
| Baza + P/S / + P/E | 19,5% / 20,67% | jw. | slajd | 08, 00:57:51, 01:15:18 |
| Baza + PEG (zysk łączny) | 474,71% wobec 671,55% bazy | – | slajd | 08, 01:20:54 |
| 10 / 20 spółek zamiast 25 | 18,85% / 21,61% | – | slajd | 08, 01:38:24, 01:42:42 |
| Najgłębsze obsunięcie modelu | −33,41%, 543 dni do odrobienia | – | slajd | 10, 00:26:28 |
| Stosowanie modelu „w ciemno" | 18–20% rocznie | – | tylko nagranie | 11, 00:13:19 |

## Czego kurs nie rozstrzygnął – do sprawdzenia
- Progi EPS TTM, CFO TTM i CFO Estimates znane tylko z nagrania (07, 00:44:16, 00:48:15, 00:49:26). Trela zapowiedział wgranie modelu na konta uczestników po 10 czerwca – tam sprawdzić wartości Worst/Best (10).
- Nazwa wskaźnika w regule CFO Estimates – okna reguły nie pokazano (07, 10). W analizie ręcznej Trela używał „CFO per Share Average Estimated Annual Growth in Next 2 Years" (slajd, 06, 00:46:09) – prawdopodobnie ten sam, do potwierdzenia.
- Ustawienia kanału Upside: 4 lata, poziomy, ok. 70% odczytów w kanale – tylko nagranie, Trela sam niepewny (07, 01:40:04).
- Że reguła Upside używa wskaźnika „Price Target Upside" – wniosek z alertów, okna reguły nie pokazano (10).
- Best w regule EPS ≥ 0,50: na slajdzie „10K"; nie widać, czy poprawiono (07, 00:33:48).
- Altman: slajd lekcji podaje dla wersji nieprodukcyjnej granicę 1,2, słownik Scrab 1,8; raz są cztery składniki, raz pięć (03-1, 00:23:39; 08, 00:45:18).
- Progi screenera tylko z nagrania; próg marży nie padł (10, 01:07:46).
- ONON wszedł do dwudziestki mimo blokady PT – Trela nie wiedział dlaczego (10, 01:17:51).
- Excel: nagłówki „125 pkt" i „209 pkt" nie zgadzają się z formułą (średnia trzech ułamków); 125 = 55 + 30 + 40, ale 209 nie jest nawet sumą maksimów (55 + 40 + 60 = 155).
- Odczyt równy dokładnie Worst: opis skali w Scrab mówi „0 pkt, gdy wskaźnik jest równy lub gorszy niż Worst" (slajd, 07, 00:34:12; 10, 01:59:03), więc przy Must-Have dokładnie 3 analityków, EPS 0,50 czy 10,0 mld dałoby flagę; Trela mówi „poniżej trzech = zero" (07, 00:58:46). Do sprawdzenia w Scrab: warunek „≥ 3" czy „> 3" (dla liczby analityków to różnica 3 wobec 4).
- Scrab i Excel liczą wynik łączny inaczej – wybrać jeden wzór.
- „Minimalna różnica", „drastycznie obniżone", „mocno redukowany" – bez progów liczbowych (11).
- Rozbieżne oceny ręczne: CFO/Debt 0,3 → 5 (06) wobec 0,35 → 3 (04); prognoza CFO 17% → 3,5 (03) wobec 2 (06).
- Momentum i dodatkowe wskaźniki fundamentów zapowiedziane, ale niedodane (08, 10).

## Jak to przenieść do mojego skanera (dopisek Claude'a)
Cała sekcja to moje propozycje, nie treść kursu. Dostępność pól w Yahoo Finance (biblioteka `yfinance`) trzeba potwierdzić na kilku tickerach przed kodowaniem.

| Reguła Treli | Potrzebne dane | Yahoo Finance? | Uwagi |
|---|---|---|---|
| Tylko USA, kapitalizacja ≥ 10 mld | giełda, kapitalizacja | tak | – |
| EPS (TTM) ≥ 0,50 | EPS z 12 miesięcy | tak | do sprawdzenia: „Basic" czy rozwodniony |
| Min. 3 lata od IPO | pierwsze notowanie | tak | z historii kursu |
| Min. 3 analityków EPS na 2 lata naprzód | liczba analityków | częściowo | drugi rok naprzód – do sprawdzenia |
| Zmiana przychodów, EPS, CFO w 5 lat | 5 lat sprawozdań | częściowo | do sprawdzenia, ile lat zwraca Yahoo; krótsze okno oznaczyć flagą |
| Prognozowany wzrost przychodów i EPS w 2 lata | prognozy analityków | częściowo | zastępnik: wzrost na bieżący i następny rok – do sprawdzenia |
| Prognoza EPS na 5 lat | prognoza długoterminowa | do sprawdzenia | brak → 0 pkt z flagą „brak danych" |
| Prognoza wzrostu CFO | prognozy CFO | raczej nie – do sprawdzenia | brak → mianownik 124 zamiast 129, z adnotacją |
| EBITDA Margin (TTM) | EBITDA, przychody | tak | – |
| Altman Z-Score | bilans, EBIT | częściowo | policzyć samemu; wzór spoza kursu, porównać ze Scrabem na kilku spółkach |
| Upside | średnia cena docelowa, kurs | tak (bieżący) | (PT − kurs) / kurs |
| Spadek PT w 45 dni, zmiana PT w 180 dni | historia ceny docelowej | nie – do sprawdzenia | zapisywać PT codziennie; reguły ruszą po 45 i 180 dniach |
| Upside na tle 4 lat | historia upside | nie | własna historia od dziś; wcześniej zastępnik z flagą „niska pewność" |
| Wielkość pozycji (VaR, korelacja) | miesięczne stopy zwrotu | tak | VaR 5% = 5. percentyl z 36 miesięcy; metoda Scraba – do sprawdzenia |
| Debt/Assets, Quick, CFO/Debt, Interest Coverage | sprawozdania roczne | tak | tylko flagi ostrzegawcze |

Kolejność pracy: (1) funkcja `punkty(odczyt, najgorzej, najlepiej, maks)` z liniową skalą; (2) lista KRYTERIA wczytana z pliku `Kurs Treli - model finalny.json`; (3) flagi Must-Have; (4) wynik w obu wersjach; (5) codzienny zapis PT i upside; (6) raport TOP 50 „do przeglądu ręcznego", bez automatycznych zleceń.

## Powiązane
- [[Kurs Treli - mapa]]
- [[Trela 01-1 - Zyskownosc spolki]]
- [[Trela 02 - Analiza zyskownosci]]
- [[Trela 03 - Analiza zyskownosci cz 2]]
- [[Trela 03-1 - Badanie fundamentow]]
- [[Trela 04 - Analiza fundamentow]]
- [[Trela 04-1 - Wycena akcji]]
- [[Trela 05 - Wskazniki wyceny akcji]]
- [[Trela 05-1 - Makroekonomia]]
- [[Trela 06 - Skaner i praktyka]]
- [[Trela 06-1 - Analiza miekka]]
- [[Trela 07 - Automatyzacja modelu]]
- [[Trela 07-1 - Ocena branzy]]
- [[Trela 08 - Automatyzacja modelu cz 2]]
- [[Trela 08-1 - Zarzadzanie ryzykiem]]
- [[Trela 09 - Zarzadzanie ryzykiem cz 2]]
- [[Trela 09-1 - Psychologia na gieldzie]]
- [[Trela 10 - Finalny model]]
- [[Trela 11 - Podsumowanie]]
- [[Skaner Rafmall - jak pracujemy]]
- [[START]]
