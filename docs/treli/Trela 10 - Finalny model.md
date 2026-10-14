---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 10. Finalny model (spotkanie 10), 13 maja 2026, ok. 2 h 13 min"
status: do przejrzenia
---
# Trela 10 – Finalny model punktowy (spotkanie 10)

## W skrócie
Trela ogłasza, że model punktowy z końca spotkania 8 jest finalny: reguły i wagi zostają bez zmian (Growth 55, Fundamentals 30, Value 41, Must-Have 3 = 129 pkt). Zmieniło się tylko otoczenie: spółki wyłącznie z giełd USA, a w Scrab portfel 20 spółek ważony ryzykiem (bez Scraba: 25 spółek po równo). „Meta-backtesty" (średnia z 10 okresów startu) dają 24,12% rocznie, średnio 11,7 pkt proc. powyżej S&P 500. Druga połowa to procedura („framework"): screener → model → ręczny przegląd → portfel → alerty → rebalans co 3 miesiące.

## Najważniejsze koncepty

### Meta-backtest zamiast jednego backtestu (00:09:49–00:17:15)
- Wynik testu mocno zależy od momentu startu, więc Trela liczy ten sam model dla 10 różnych dat startu i uśrednia.
- CAGR (Compound Annual Growth Rate – średnioroczna stopa zwrotu z procentem składanym) sam nic nie znaczy; liczy się różnica względem S&P 500 w tym samym okresie. Trela nazywa ją w uproszczeniu „alfą" (bez odejmowania stopy wolnej od ryzyka).

### Zarzut „survivorship bias" (00:18:04–00:21:20)
- Survivorship bias = błąd przeżywalności: test na dzisiejszej liście spółek pomija te, które zniknęły. Dwa testy kontrolne: (1) tylko spółki będące w danym kwartale w składzie S&P 500, (2) Historical Screener (screener odtwarzany kwartał po kwartale). W obu model bije indeks, choć słabiej.

### Trzy uwagi do czytania wyniku (00:24:15–00:33:30)
1. 24% to średnia z wielu lat – w żadnym pojedynczym roku portfel nie zrobił „około 24%"; bywało ok. −20% i ok. +40%.
2. Długie obsunięcia (drawdown – spadek od szczytu do dołka) są pewne: w teście najgłębsze −33,41%, 543 dni od szczytu do odrobienia. Bez zarządzania ryzykiem Trela każe liczyć się z −40/−50%.
3. Przez pierwsze lata portfel jest prawie nieodróżnialny od indeksu; przewagę widać dopiero po wielu latach procentu składanego. Stąd hasło „zostań w autobusie": nie zmieniać strategii po kwartale czy roku.

### Dlaczego nie optymalizować dalej (00:40:28–00:44:30)
- Trela nie wierzy w metodę bez opcji i dźwigni dającą trwale więcej niż ok. 20–23% rocznie. Model „dokręcony" do historii (np. premiowanie ujemnego EPS: ponad 30% w testach, potem lata strat) nie ma uzasadnienia ekonomicznego.
- Upraszczanie pomagało bardziej niż dokładanie reguł. Upside = potencjał wzrostu kursu do ceny docelowej analityków.

### Rola fundamentów i wyceny (01:54:31–01:55:15)
- Zyskowność najważniejsza; z fundamentów zostaje tylko Altman jako filtr bezpieczeństwa; wskaźniki wyceny (P/S, P/E, P/CF) wyrzucone.

### Uznaniowość (01:03:10–01:07:20)
- Zasady są dla większości; dla stylu Treli (ok. 10 spółek, analiza miękka) nie ma gotowego schematu – jedyny stały warunek to zyskowność.

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Giełdy | tylko USA (w tym ADR-y – kwity depozytowe spółek zagranicznych notowane w USA) | filtr | slajd 00:38:25 |
| Nowa spółka z ujemnym lub bardzo niskim upside | nie kupować teraz, wziąć kolejną z listy; ustawić alert | – | slajd 01:33:54 (MU −20,83%, SQM −14,92%); nagranie 01:32:04 |
| Alert wejścia | Price Target Upside ≥ próg dobrany z historii danej spółki (MU: 10, SQM: 20) | – | slajd 01:39:30 |
| Alert wyjścia (opcjonalny) | Price Target Upside ≤ 0 | – | slajd 01:47:39 (AVGO) |
| Zakup przed terminem rebalansu | upside ok. 10% → czekać; ok. 30% i 2 mies. do rebalansu → raczej kupić; ok. 50% → kupić | – | z nagrania, niepotwierdzone slajdem – sprawdź 01:36:43–01:37:58 |
| Termin rebalansu | po sezonie wyników: min. ok. 3 tygodnie publikacji, wyniki dla min. 80% spółek | – | z nagrania, niepotwierdzone slajdem – sprawdź 01:06:15 |
| Kontrola między rebalansami | raz w miesiącu przejrzeć rewizje cen docelowych spółek z portfela; żadnych transakcji | – | nagranie 01:38:11, 02:00:09 |
| Spadająca cena docelowa | spółki nie kupować mimo wysokiej punktacji; zastąpić kolejną z rankingu | – | slajd 01:17:30 (ONON); nagranie 01:17:44 |
| Kolory wyniku w Scrab | zielony ≥ 70%, czerwony < 40% | – | slajd 01:41:33 |

## Finalny model punktowy – pełna konfiguracja

Model w Scrab: „Uniwersytet 2026 (US Only)" – kopia modelu ze spotkania 8, **bez zmian reguł i wag** (slajdy 01:41:33, 02:05:12; nagranie 00:45:18, 01:41:24). Punktacja liniowa między Worst (0 pkt) a Best (maks.). Wynik końcowy w Scrab = suma punktów / 129 (dopisek Claude'a: sprawdzone na PLTR i LLY ze slajdu 01:13:57). Ustawienia modelu: Required Years Since IPO 3,0; Tolerance for Low Scores & Missing Data: Full.

Na tym spotkaniu pokazano tylko nazwy reguł, wagi i okno reguły PT Revisions; pozostałe progi pochodzą z notatek 07 i 08.

| Metryka (reguła → wskaźnik w Scrab) | Filar | Maks. punktów | Progi lub przedziały (Worst → Best) | Kierunek | Źródło |
|---|---|---|---|---|---|
| Revenue TTM → Revenue (TTM), zmiana w 5 lat | Growth | 5 | 50% → 100% | wyżej = lepiej | waga: slajd 02:05:12; progi: notatka 07 |
| Revenue Estimates → Revenue Average Estimated Annual Growth in Next 2 Years | Growth | 10 | 10% → 30% | wyżej = lepiej | jw. |
| EPS TTM → EPS Basic (TTM), zmiana w 5 lat | Growth | 5 | 100% → 250% | wyżej = lepiej | jw.; progi tylko z nagrania 07 |
| EPS Estimates 2y → EPS Average Estimated Annual Growth in Next 2 Years | Growth | 5 | 15% → 40% | wyżej = lepiej | jw. |
| EPS Estimates 5y → EPS Long Term (5 Years) Growth Estimates | Growth | 5 | 15% → 30% | wyżej = lepiej | jw. |
| CFO TTM → Cash from Operations (TTM), zmiana w 5 lat | Growth | 10 | 100% → 250% | wyżej = lepiej | jw.; progi tylko z nagrania 07 |
| CFO Estimates → prognoza wzrostu CFO na 2 lata (?) | Growth | 5 | 15% → 30% | wyżej = lepiej | jw.; progi tylko z nagrania 07 |
| EBITDA Margin → EBITDA Margin (TTM) | Growth | 10 | 20% → 40% | wyżej = lepiej | jw. |
| Altman Score → Altman Z-Score – Nonmanufacturers (TTM) | Fundamentals | 30 | 1,0 → 4,0 | wyżej = lepiej | waga: slajd 02:05:12; progi: notatka 08 |
| PT Revisions → Price Target, Maximum Drawdown, 45 dni | Value | 1, must-have | −5,00% → −4,90% (spadek o 5% lub więcej = flaga) | mniejszy spadek = lepiej | **slajd 01:59:03** |
| PT Change over year → Price Target, zmiana w 180 dni | Value | 10 | 10% → 20% | wyżej = lepiej | waga: slajd 02:05:12; progi: notatka 07 |
| Upside → Price Target Upside, Historical Range, 4 lata, kanał poziomy | Value | 30 | poniżej kanału 0 → powyżej kanału maks. | wyżej = lepiej | waga: slajd 02:05:12; nazwa wskaźnika: slajdy 01:31:57, 01:39:30; ustawienia kanału: notatka 07 |
| Market Cap → Market Cap (USD) | Must-Have | 1, must-have | 10 mld → 10,1 mld USD | wyżej = lepiej | waga: slajd 02:05:12; próg: notatki 07/08 |
| EPS Number → EPS Number Estimates for 2 Fiscal Years Ahead | Must-Have | 1, must-have | 3,0 → 3,1 | wyżej = lepiej | jw. |
| EPS > 0.50 → EPS Basic (TTM) | Must-Have | 1, must-have | Worst 0,5 USD | wyżej = lepiej | jw. |

Sumy filarów (slajd 02:05:12): Growth 55,0; Fundamentals 30,0; Value 41,0; Must-Have 3,0.

**Wersje Excel rozdane po lekcji** (punkty wpisuje się ręcznie; progów w arkuszu nie ma):

| Arkusz | Kolumny (maks. pkt) | Wynik |
|---|---|---|
| Model-2026-mini (odpowiednik Scraba) | Growth 55: Revenue TTM 5, Revenue Est. 10, EPS TTM 5, EPS 2y Growth 5, EPS 5y Growth 5, Cash from Op. 10, CFO 2y Est 5, EBITDA Margin 10. Funds 30: Altman 30. Value 40: Upside 30, Target Price 10 | TOTAL = średnia trzech filarów (każdy jako ułamek swojego maksimum) |
| Model-2026 (pełny, do analizy ręcznej) | Growth 55 jw. Funds 40: Ohlson 10, Altman 10, Debt/Assets 5, Interest Coverage 5, CFO/Debt 5, Quick Ratio 5. Value 60: P/S Forward 2y 10, P/E Forward 2y 10, P/CFO Forward 2y 10, Upside 20, Target Price 10 | jw. |

Uwaga: Excel daje każdemu filarowi wagę 1/3, a Scrab liczy sumę punktów / 129 (Growth ok. 43%) – w skanerze trzeba wybrać jeden wzór.

**Zmiany względem spotkania 8:**
- Reguły, wagi i progi modelu: bez zmian.
- Nowe: tylko giełdy USA; portfel 20 spółek + Equal Risk (zamiast 25 + równe wagi) jako wariant „ze Scrabem".
- Rozstrzygnięte niewiadome: (1) wskaźnik reguły Upside nazywa się **Price Target Upside**; (2) progi PT Revisions (−5,00% → −4,90%, 45 dni, must-have, 1 pkt) potwierdzone slajdem; (3) zapowiadany test „tylko USA" wykonany – pomaga.
- Nierozstrzygnięte: Momentum i dodatkowe wskaźniki fundamentów nie zostały dodane do modelu Scrab; nazwa wskaźnika CFO Estimates nadal niewidoczna.

**Odrzucone i dlaczego:**
- P/S, P/E, P/CF – wg Treli nie wpływają na wynik testów, więc usunięte dla prostoty (01:54:51). W notatce 08 slajdy pokazywały pogorszenie.
- Ohlson i rozbudowane fundamenty – zastąpione samym Altmanem (00:23:55).
- Giełdy spoza USA – ich usunięcie podniosło wynik (00:46:06).
- Rebalans co miesiąc – gorszy; spółki z wysokim upside nie mają czasu odbić (01:00:17).
- Alerty odchyleń wagi w Scrab – Trela ich nie włącza (01:23:04).
- Tear Sheet portfela w Scrab – symuluje wstecz obecny skład, nie pokazuje realnej historii; do pominięcia (02:03:07).
- Polska giełda – niska jakość i ciągłość prognoz analityków (02:09:32). Duże spółki chińskie, koreańskie, japońskie mają dane poprawne (02:12:23).

## Warunki Must-Have i filtry wstępne

**W modelu (flaga i koniec listy):** Market Cap ≥ 10 mld USD; min. 3 analityków z prognozą EPS na 2 lata fiskalne; EPS Basic (TTM) ≥ 0,50 USD; cena docelowa nie spadła o 5% lub więcej w 45 dni; min. 3 lata od IPO.

**Screener sugerowany na start** (celowo luźniejszy niż model; kryteria z nagrania 01:07:46–01:10:24, na slajdzie 01:07:39 widać tylko kolumny wyników):
- Exchanges: US.
- Market Cap (USD) od 10 mld.
- Marża: w tabeli wyników kolumna „EBIT Margin (TTM)", Trela mówi o marży EBITDA; próg nie padł.
- Revenue Average Estimated Annual Growth in Next 2 Years ≥ 5% oraz EPS Average Estimated Annual Growth in Next 2 Years ≥ 5% (obniżone, bo przy zmianie roku fiskalnego prognozy chwilowo spadają).
- EPS Basic (TTM) ≥ 0,10 USD (odcina „penny stocks").
- Altman Z-Score – Nonmanufacturers (TTM) ≥ 2.
- Wynik: 203 spółki (slajd 01:07:39: „1–100 of 203"); po poluzowaniu 229.

Do modelu dodaje się wszystkie spółki ze screenera, także słabe (mogą się poprawić) – rygor jest w modelu.

## Ustawienia portfela i backtesty

**Ustawienia docelowe** (slajd 00:38:25; nagranie 00:47:06–00:50:14):

| Parametr | Ze Scrabem | Bez Scraba |
|---|---|---|
| Liczba spółek | 20 | 25 |
| Wagi | Equal Risk (im większa zmienność spółki, tym mniejsza waga; uwzględnia korelacje) | Equal Weights (po równo) |
| Rebalans | co 3 miesiące | co 3 miesiące |
| Giełdy | tylko USA | tylko USA |

- 20 spółek pomaga tylko razem z Equal Risk (ważenie ryzykiem tłumi większe wahania). Różnica wobec 25 + równe wagi to ok. 1 pkt proc., być może przypadek (00:57:14); dla prostoty Trela sam wybrałby równe wagi (01:02:20).
- Ustawienia portfela w Scrab (z nagrania 01:19:48–01:24:35, okno niewidoczne na slajdach): liczba spółek 22 (demo), gotówka 100 000 USD, Allocation: Equal Risk, Rebalancing frequency: 3 mies., Suggest top companies: tak, próg rebalansu 5% (mniejsze odchylenie od wagi docelowej = brak transakcji), Reduce portfolio turnover 1% (spółka spoza portfela wchodzi dopiero, gdy ma wynik lepszy o ponad 1%).
- Testy: jednorazowa wpłata, bez dopłat, bez kosztów transakcyjnych (00:51:53, 01:06:01). W bessie rebalansuje się normalnie (00:44:32).

**Meta-backtest finalnego modelu** (slajd 00:10:10) – CAGR modelu / S&P 500:

| Okres | Model | S&P 500 |
|---|---|---|
| 2022–2026 | 31,59% | 14,78% |
| 2021–2026 | 24,73% | 10,93% |
| 2020–2026 | 27% | 15,15% |
| 2019–2026 | 28,5% | 14,53% |
| 2018–2026 | 25,04% | 12,65% |
| 2017–2026 | 21,6% | 12,35% |
| 2016–2026 | 26% | 12,95% |
| 2006–2026 | 16,54% | 8,87% |
| 2008–2026 | 17,68% | 9,38% |
| 2009–2026 | 22,56% | 12,6% |
| **Średnia (meta-CAGR)** | **24,12%** | średnia przewaga 11,7 pkt proc. (slajd 00:16:15) |

Inne wyniki:
- Model z edycji 2025 w tej samej metodzie: 23,12% (slajd 00:28:22).
- Tylko USA: okres 2016–2026 z ok. 23% na 26% (nagranie 00:46:06; 26% na slajdzie 00:10:10).
- 20 spółek + Equal Risk: ok. +1,5 pkt proc. w meta-testach (z nagrania, niepotwierdzone slajdem – sprawdź 00:47:14).
- Historical Screener, 10 lat: 18,11% rocznie wobec 12,95%; łącznie 406,82% wobec 227,67%; maks. obsunięcie −32,22% wobec −33,92%; zmienność 0,23 wobec 0,18; Sharpe 0,80 wobec 0,75 (slajd 00:20:06).
- Tylko historyczny skład S&P 500, 10 lat: 16,4% wobec 12,9% (z nagrania, niepotwierdzone slajdem – sprawdź 00:19:23).
- Najdłuższy test: 100 tys. → 3,02 mln; S&P 500 → 729,57 tys. (slajd 00:29:50; w mowie start 2006, oś wykresu od ok. 2010).
- Najgorsze obsunięcia (slajd 00:26:28): −33,41% (16.11.2021 → 14.10.2022, odrobione 14.12.2023, 543 dni); −29,84% (2020, 66 dni); −23,29% (2025, 64 dni).

## Przykłady z lekcji
- **ONON (On Holding)** – trafił do pierwszej dwudziestki mimo spadającej ceny docelowej (w modelu monitorującym portfela Price Target Revisions 19%). Trela usuwa go ręcznie i wstawia ARM. Dowód, że ręczny przegląd jest konieczny (slajd 01:17:30).
- **MU (Micron)** i **SQM** – wysoko w rankingu, ale upside −20,83% i −14,92%: dobra spółka, zły moment; alerty na upside ≥ 10 i ≥ 20 (slajdy 01:33:54, 01:39:30).
- **AVGO (Broadcom)** – alerty „Price Target Upside ≤ 0" i „Price Target ≤ 450" (slajd 01:58:36).

## Narzędzia
- **Screener** → Find Stocks → Rows: All (inaczej tylko 100) → zaznacz wszystkie → Add to → model (Quick Score) → ponownie Add to, żeby dodać na stałe. Duplikaty (różne serie akcji) usuwać ręcznie.
- **My Portfolios → „+"**: nazwa i model → dodać 20 najlepszych z modelu albo Add Companies ręcznie → Settings.
- Tabela portfela: Planned Allocation (ile kupić, także ułamki akcji), Current Allocation, Difference. Po transakcji u brokera: Buy / Sell (Ticker, Quantity, Price) albo Connect Brokerage (SnapTrade). Dopłata: edycja Available Cash.
- **Rebalancing** → lista To Sell / To Buy → Make All Transactions.
- **Alerts → New Alert**: typy Scoring Model, Company Score, Metric Value (Company, Financial Metric, Condition, Threshold Value). Dla spadku ceny docelowej alert tylko kwotowy; procentowy wymaga osobnego modelu z regułą Maximum Drawdown.
- Wystarcza plan Standard.

## Co z tego zastosuję w skanerze
1. Uniwersum: tylko spółki notowane w USA (z ADR-ami) → luźny filtr wstępny (kapitalizacja ≥ 10 mld USD, prognozowany wzrost przychodów i EPS ≥ 5%, EPS ≥ 0,10 USD, Altman ≥ 2) → wszystkie do punktacji.
2. Punktacja: 15 reguł z tabeli; wynik = suma punktów / 129. Niespełnienie reguły must-have → flaga i koniec rankingu.
3. Portfel: top 25 po równo (albo top 20 z wagami odwrotnie proporcjonalnymi do ryzyka), przegląd co 3 miesiące, ok. 3 tygodnie po starcie sezonu wyników.
4. Przed rebalansem odświeżyć listę ze screenera i dopisać nowe spółki do już ocenianych (stare zostają).
5. Histereza: wymiana spółki tylko, gdy kandydat ma wynik lepszy o ponad 1%; korekta wagi tylko przy odchyleniu ponad 5%.
6. Flaga „nie kupuj teraz": spółka z top listy z upside ≤ 0 lub wyraźnie poniżej własnej historii → pominąć, wziąć następną, dodać alert na próg upside.
7. Lista „do ręcznego przeglądu" przed każdą transakcją: cena docelowa i rewizje prognoz każdej spółki z propozycji kupna/sprzedaży.
8. Comiesięczny raport: zmiana ceny docelowej spółek z portfela.

## Pytania powtórkowe
1. Czym meta-backtest różni się od zwykłego backtestu i jaki dał wynik?
2. Co zmieniło się względem spotkania 8, a co zostało bez zmian?
3. Kiedy wybrać 20 spółek, a kiedy 25, i z jakimi wagami?
4. Jakie warunki must-have ma model i czym różni się od nich screener?
5. Co zrobić ze spółką z top 20, która ma ujemny upside? A ze spółką, której cena docelowa spada?

## Niepewne – do sprawdzenia
- Progi reguł Growth, Altmana, PT Change, Market Cap i ustawienia kanału Upside nie były pokazane na tym spotkaniu – przeniesione z notatek 07/08. Trela mówi, że model w Scrab zostanie skopiowany uczestnikom po 10 czerwca; wtedy sprawdzić wartości Worst/Best.
- Że reguła Upside używa wskaźnika Price Target Upside – wniosek z alertów i kolumn; okna reguły nie pokazano.
- Dlaczego ONON przeszedł mimo must-have na PT Revisions – Trela sam nie wie (01:17:51).
- Kryteria screenera (progi) tylko z nagrania; próg marży nie padł; kolumna wyników to EBIT Margin, a w mowie „EBITDA".
- Efekt „tylko USA": Trela mówi raz o podciągnięciu z 23% do 26%, raz o „jednym punkcie procentowym" (00:46:06–00:46:23).
- Excel: nagłówki „TOTAL of TOTALS (125 pkt)" i „(209 pkt)" nie zgadzają się z formułą (średnia trzech filarów); w wersji pełnej filary sumują się do 155 pkt. Trela zapowiadał „te same wagi" co w Scrab – w mini brak reguły PT Revisions i must-have.

## Powiązane
- [[Trela 07 - Automatyzacja modelu]]
- [[Trela 08 - Automatyzacja modelu cz 2]]
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
