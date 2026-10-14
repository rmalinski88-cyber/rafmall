---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 9. Zarządzanie ryzykiem, cz. 2 (spotkanie live nr 9), 6 maja 2026, ok. 1 h 57 min"
status: do przejrzenia
---
# Trela 09 – Zarządzanie ryzykiem cz. 2: wielkość pozycji i Czarny Excel (spotkanie 9)

## W skrócie
Model punktowy mówi, KTÓRE spółki kupić; drugi arkusz („Czarny Excel") mówi, ILE każdej. Zasada: nie wyrównujemy kwot, tylko ryzyko – spółka bardziej zmienna (wyższy VaR) dostaje mniejszą pozycję, do tego korekta za korelację i za „deltę upside", a wynik jest przycinany limitami min/max. Trela pokazuje mechanikę, po czym sam ją podważa: wg niego dla inwestora indywidualnego zmienność to problem psychologiczny, a nie finansowy, więc 90% wysiłku ma iść w wybór dobrych spółek, a 10% w wagi.

## Najważniejsze koncepty

### Wycena jako ostrzeżenie (dygresja, 00:07:57–00:25:30)
- Nowość w Scrab Master Chart: wstęgi ±2 odchylenia standardowe (2σ, „sigma") oraz kanał regresji liniowej wokół dowolnego wskaźnika. Wg Treli wskaźnik przebywa w kanale ok. 95% czasu; wyjście górą = anomalia, po której zwykle następuje powrót do średniej.
- Backtesty (testy strategii na danych historycznych) pokazują, że wycena nie wpływa na wynik, ale wg Treli to złudzenie: krachy zdarzają się średnio raz na 10 lat, więc giną w średniej (00:11:56).
- Niski lub ujemny upside (potencjał wzrostu = cena docelowa analityków vs kurs) nie jest sygnałem „sprzedaj", tylko informacją, że spadek o kilkadziesiąt procent jest prawdopodobny. Zamiast uciekać do gotówki – przesuwać kapitał do spółek z wyższym upside, pozostając zainwestowanym w 100% (00:18:11).

### Nie ma jednej definicji ryzyka (00:28:09–00:38:30)
- VaR (Value at Risk, „wartość zagrożona"): strata, której miesięcznie nie przekroczymy z 95% prawdopodobieństwem. Expected Shortfall (ES, inaczej CVaR): średnia strata w tych najgorszych 5% przypadków.
- Ten sam wskaźnik dla tej samej spółki zmienia się w czasie (Nvidia: ok. 12,5% dziś, ok. 22% dwa kwartały wcześniej), a średnia, mediana i różne okresy dają różne liczby. Każdy wybór jest uznaniowy.
- Wniosek praktyczny: ryzyko pozycji = wskaźnik ryzyka × wartość pozycji. Żeby je zrównać, spółki o 3× wyższym ryzyku kupujemy 3× mniej (00:36:10).

### Trzy składniki wielkości pozycji (01:15:55)
1. **Ryzyko (VaR)** – im wyższe względem „benchmarku" (średniego VaR naszych spółek), tym mniejsza pozycja.
2. **Korelacja** – ręczny mnożnik; spółka mocno skorelowana z resztą portfela dostaje mniej, słabo skorelowana więcej.
3. **Delta upside** – bieżący upside minus średni upside tej spółki z 5 lat. Goły upside jest nieporównywalny między spółkami (dla jednej 10% to dno, dla innej dużo), dlatego odnosi się go do własnej historii (01:01:25).

### Limity min/max (00:47:49)
Bez limitów spółka „bezpieczna" mogłaby ważyć 3–6× więcej niż ryzykowna; jedna pomyłka na dużej pozycji ściąga cały portfel mimo dobrej skuteczności wyboru. Stąd Min Cap i Max Cap (cap = ograniczenie). Poziomy są uznaniowe.

### „Plot twist" – po co to wszystko? (01:17:34–01:53:00)
- Zmienność działa w obie strony: ograniczając ją, ograniczamy zyski. Rozbijanie korelacji w rosnącej branży = gorszy wynik.
- Instytucje pilnują VaR, bo mają dźwignię i bieżące zobowiązania; inwestor indywidualny bez dźwigni – nie.
- Za Howardem Marksem: ryzyko to **bezpowrotna utrata kapitału**, nie zmienność (01:37:07). Stąd nacisk na jakość spółek.
- Miara bliższa odczuciom inwestora: **underwater period / recovery time** – jak długo portfel odrabia stratę, a nie jak głęboko spadł (01:40:13).
- Model wolno świadomie łamać dla 1–3 spółek z bardzo mocną tezą z analizy miękkiej, o ile reszta portfela jest ułożona (01:51:08).

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Liczba spółek → % na pozycję | 25 spółek = 4%; 20 = 5%; 10 = 10% (100% / liczba spółek) | – | nagranie 00:41:44; slajd 00:42:21 |
| Procent na jedną pozycję w przykładzie | 5% z 1 000 000 USD = 50 000 USD | – | slajd 00:42:48 |
| Benchmark VaR | 17% = zaokrąglona średnia VaR spółek z listy (pasek stanu: 17,38%); w arkuszu „VaR Simple" mediana | – | slajd 00:47:48 + arkusz |
| Min Cap | 3% portfela | – | slajd 00:51:12 + arkusz |
| Max Cap | 6% portfela (na początku na ekranie 7%, Trela zmienił na 6%) | – | slajd 00:51:12 + arkusz |
| Mnożnik korelacji | 1,00 = neutralnie; >1 (np. 1,20) zmniejsza pozycję; <1 (np. 0,80; 0,50) zwiększa | – | slajd 01:15:57 + arkusz |
| Delta upside | upside bieżący − średni upside 5 lat + 1 (mnożnik pozycji) | – | slajd 00:52:30 + arkusz |
| Wstęgi 2σ na wskaźniku wyceny | wskaźnik w kanale ok. 95% czasu; poza górną wstęgą = anomalia | – | nagranie 00:08:40; slajd 00:22:27 |
| Rebalansowanie (przywracanie wag) | co 1–3 miesiące | – | (z nagrania, niepotwierdzone slajdem – sprawdź 01:16:28) |
| Alerty | lista obserwowanych: upside powyżej progu, np. +20%; spółki w portfelu: upside < 0 | – | (z nagrania – sprawdź 00:05:17) |
| Podział wysiłku | 90% wybór spółek i analiza miękka, 10% wagi | – | (z nagrania – sprawdź 01:53:32) |
| Liczba spółek w portfelu | nie 5, tylko 15–25 | – | (z nagrania – sprawdź 01:53:50) |
| Wyjątki od modelu | najwyżej 1–3 spółki | – | (z nagrania – sprawdź 01:51:21) |

## Jak liczyć wielkość pozycji krok po kroku

Arkusz **VaR-Full** (główny). Ręcznie wpisuje się tylko czerwone komórki; pomarańczowe to formuły.

**Parametry (góra arkusza):**
- `C2` wartość portfela w USD (D2 przelicza na PLN kursem z arkusza Currencies),
- `C3` procent na jedną pozycję, `C4 = C2*C3` bazowa wartość pozycji,
- `C5` benchmark VaR (0,17), `E3` Min Cap (0,03), `F3` Max Cap (0,06).

**Kroki dla każdej spółki (wiersz n):**
1. Wpisz spółkę (B) i jej VaR miesięczny (C) – ze Scraba: „Monthly Value at Risk (VaR) 5% (3Y Lookback)".
2. Wpisz mnożnik korelacji (D) na podstawie macierzy korelacji.
3. Wpisz bieżący upside (P) i średni upside 5 lat (R). Arkusz liczy deltę: `S = Q − R + 1` (Q to kopia P).
4. Wartość pozycji przed limitami:
   `G = ((C4 / (C / C5)) / D) * S`
   czyli: bazowa kwota × (benchmark VaR / VaR spółki) ÷ korelacja × delta upside.
5. Limity: `H = JEŻELI(G > F3*C2; F3*C2; JEŻELI(G < E3*C2; E3*C2; G))` – przycięcie do przedziału 3–6% portfela.
6. Docelowa liczba akcji: `I = H / kurs (F)`.
7. Ryzyko kwotowe pozycji: `J = C * H`; docelowy udział: `K = H / C2`.
8. Rebalans: wpisz posiadane akcje (L). `M = I − L` (plus = dokup, minus = sprzedaj), `N = M * kurs` (kwota transakcji), `O = N / G` („Spread" – informacyjnie, skala rozjazdu).
9. Podsumowanie: suma G i H; „Gotówka" = `C2 − suma` (minus oznacza, że model chce więcej niż mamy); `J30 = suma J / C2` – ryzyko całego portfela (w przykładzie 15–17%).

**Sprawdzenie na liczbach z ekranu (00:42:48, baza 50 000 USD):**
- AMD: VaR 20%, korelacja 0,70, delta 0,82 → 50 000 × 17/20 ÷ 0,70 × 0,82 = 49 786 USD (mieści się w limitach).
- Microsoft: VaR 7%, korelacja 1,20, delta 1,20 → 121 429 USD → przycięte do Max Cap (60 000 przy 6%).
- Enphase: VaR 30%, delta 0,94 → 26 633 USD → podniesione do Min Cap 30 000.
- Po zmianie korelacji AMD na 1,20 pozycja spada do 29 042 → Min Cap 30 000 (01:15:57).

**Pozostałe arkusze:**
- **VaR Simple** – wersja uproszczona: portfel wpisany w PLN i przeliczany na USD, benchmark = mediana kolumny VaR, `G = (C4 / (VaR / C5)) / D`. Bez limitów i bez delty upside. Kolumny: liczba akcji, ryzyko, % portfela, posiadane, różnica, wartość różnicy.
- **Sortino 3y Simple** – ważenie wskaźnikiem Sortino (zysk na jednostkę zmienności spadkowej; im wyższy, tym lepiej), więc kierunek odwrotny: `G = ((Sortino / benchmark) * wartość pozycji) / D`. Benchmark 1,72; w nazwie komórki dopisek „Cap 1.5–3" (wartości Sortino wpisywane w tym przedziale). Trela zastrzega, że Sortino patrzy na przeszłe zyski, dlatego woli deltę upside (01:00:37).
- Bloki **SHORT** i **MOMENTUM** – zamiast VaR odchylenie standardowe (STD); w MOMENTUM pobierane formułą wtyczki (`monthly_standard_deviation_annualized_5y`). Nieomawiane na spotkaniu.
- **Currencies** – kursy walut (USD/PLN 3,60; EUR/USD; JPY/USD; HKD/USD; JPY/PLN); używane też dla spółek spoza USA (wiersz Softbank: liczba akcji = wartość ÷ kurs waluty ÷ cena).

## Przykłady z lekcji
- **AMD** (00:19:27–00:23:20): P/S przy górnej wstędze 2σ (16,91 vs 16,73), upside −11,97%; historycznie po takich odczytach spadki 20–70% od szczytu. Ilustracja „zabieraj żetony ze stołu".
- **Nvidia**: VaR miesięczny 12,56%, dzienny ES 6,25% (slajd 00:32:09) – ta sama spółka miała wcześniej ok. 22%: dane wejściowe są niestabilne.
- **Astera Labs vs Microsoft**: VaR 30,67% vs 8,06% (slajd 00:34:39); miesięczny ES ok. 34% vs 11% → Microsoftu 3× więcej.
- **Macierz korelacji** (01:10:18): Amazon–Synopsys 0,65; Amazon–AMD 0,68; Amazon–Webster Financial 0,22; Digital Turbine z nikim powyżej 0,40. Trela czyta 0,65 jako „65% czasu ruch w tę samą stronę" *(dopisek Claude'a: to uproszczenie – współczynnik korelacji nie jest dosłownie odsetkiem czasu)*.
- **Portfel „Full AI BET"** (10 × 10%: NVDA, AMD, ANET, AVGO, TSM, VRT, MRVL, MU, SMH, LLY; I 2019–IV 2026) vs S&P 500 (slajd 01:25:12): średniorocznie 54,53% vs 17,23%; odchylenie std. 30,78% vs 16,73%; najlepszy rok 112,89% vs 31,22%; najgorszy −31,88% vs −18,17%; maks. obsunięcie −38,96% vs −23,93%; Sortino 3,10 vs 1,42. Odrobienie strat: 8 vs 15 miesięcy. Dowód tezy „2× głębiej, ale 2× szybciej i z 3× większą nagrodą". Trela zastrzega błąd przeżywalności (dzisiejsi zwycięzcy testowani wstecz).
- **Occidental Petroleum** – VaR 34%, ok. 3× bardziej ryzykowna; przykład spółki, której można dać mniej albo świadomie więcej przy mocnej tezie.

## Narzędzia
- **Scrab → Master Chart**: „Rolling Series" (średnia/mediana krocząca), „Bands" (2σ), „Trend Channel" (regresja liniowa), „Price % Off High" (spadek od szczytu), „Monthly Value at Risk (VaR) 5% (3Y Lookback)", „Historical Monthly Expected Shortfall 5% (3Y Lookback)", „Price Target Upside" i jego „3Y Median".
- **Portfolio Visualizer** (darmowy): Tools → Asset Correlations (Correlation Basis: Monthly Returns, Rolling Correlation: 36 Months); Backtest Portfolio → Metrics, Drawdowns.
- **Excel**: kursy akcji i walut odświeżają się przy otwarciu lub przez Data → Refresh All; ceny są bieżące (00:53:40).
- Automatyzacja wag w Scrabie – odłożona na następne spotkanie.

## Co z tego zastosuję w skanerze
1. Wejście: lista spółek + VaR miesięczny 5% → benchmark = średnia (lub mediana) VaR → waga surowa = bazowa × benchmark / VaR.
2. Wejście: upside bieżący i średni 5 lat → mnożnik = upside − średnia + 1 → pomnóż wagę.
3. Wejście: macierz korelacji miesięcznych stóp zwrotu (36 mies.) → ręczny mnożnik 0,5–1,2 → podziel wagę.
4. Przytnij wagę do [Min Cap, Max Cap] = [3%, 6%] (parametry do zmiany).
5. Docelowa liczba akcji = waga × portfel / kurs; różnica vs stan posiadania → lista „kup/sprzedaj".
6. Raport ryzyka: suma (VaR × wartość pozycji) / portfel.
7. Alerty: upside > +20% dla obserwowanych; upside < 0 dla posiadanych; wskaźnik wyceny powyżej wstęgi +2σ.
8. Dodatkowo dla portfela: maks. obsunięcie i czas odrabiania strat vs S&P 500.

## Pytania powtórkowe
1. Dlaczego równe kwoty w spółkach nie oznaczają równego ryzyka?
2. Jak z VaR spółki i benchmarku VaR policzyć surową wartość pozycji?
3. Co robi mnożnik korelacji 1,2, a co 0,8?
4. Po co do upside dodaje się odniesienie do średniej 5-letniej?
5. Do czego służą Min Cap i Max Cap i jakie wartości były w przykładzie?
6. Jak Trela (za Marksem) definiuje ryzyko inwestora indywidualnego i jaką miarę uważa za najważniejszą?

## Niepewne – do sprawdzenia
- Max Cap: na ekranie najpierw 7%, potem 6% (rozdany plik: 6%). Poziomy limitów Trela nazywa uznaniowymi (00:49:00).
- Miesięczny ES: Nvidia ok. 15%, Astera ok. 34%, Microsoft ok. 11% – z nagrania, na slajdzie nieczytelne (00:35:02–00:35:44).
- Trela pomylił kierunek mnożnika korelacji i poprawił się (01:14:49–01:15:26); formuła potwierdza: większy mnożnik = mniejsza pozycja.
- Etykieta C5 „Benchmark VaR x delta upside" – w formule C5 to sam benchmark VaR.
- W blokach SHORT/MOMENTUM formuła ma dodatkowe dzielenie przez 100, a w arkuszu Sortino pojedyncze mnożniki (×1,31; ÷1,13) – nieobjaśnione.
- Underwater period „rok i 5 miesięcy vs 2 lata" – z nagrania (01:46:49).
- Dźwignie instytucji (1:10, 1:30) i „Nvidii mam 3× więcej niż innych spółek" (01:50:31, transkrypcja niewyraźna (?)) – tylko z nagrania.
- Spadek AMD o 95% po 2007 r. – z nagrania; wykres „Price % Off High" pokazuje okolice −95% (00:19:54).

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
