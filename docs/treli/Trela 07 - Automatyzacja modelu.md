---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 7. Automatyzacja modelu (spotkanie 7), 22 kwietnia 2026, ok. 2 h 03 min"
status: do przejrzenia
---
# Trela 07 – Automatyzacja modelu punktowego w Scrab (spotkanie 7)

## W skrócie
Trela przenosi ręczny model punktowy z Excela do automatu w Scrab (zakładka Scoring Models – „modele punktowe"): na razie cały filar zyskowności (Growth, 55 pkt), trzy warunki konieczne (Must-Have) i pierwsze reguły wyceny oparte na cenie docelowej analityków. Potem puszcza backtesty (symulacje „co by było, gdybym stosował te reguły w przeszłości") i sprawdza, które dodatki poprawiają wynik względem S&P 500. Wniosek z testów: sama zyskowność bije indeks, upside i rosnąca cena docelowa pomagają, a spółki z obniżaną ceną docelową lepiej wyrzucać. Model jest „rozgrzebany" – progi są wstępne i będą kalibrowane na kolejnych dwóch spotkaniach.

## Najważniejsze koncepty

### Po co automat (00:00:36–00:05:20)
- Maszyna ocenia każdą spółkę tak samo – znika uznaniowość („lubię tę spółkę", gorszy dzień).
- Ważniejsze: zakodowany model da się przetestować na historii, zamiast czekać lata na wynik własnego portfela.
- Jeśli wynik się nie podoba, zmienia się jedną rzecz (wagę, próg, regułę) i testuje ponownie.

### Typy reguł w Scrab (00:26:44–00:28:40, slajd 00:35:03)
- **Static Range** (stały zakres) – gdy da się z góry podać liczby „źle/dobrze" jednakowe dla wszystkich spółek, np. marża, kapitalizacja, prognozowana dynamika w %.
- **Change Over Time** (zmiana w czasie) – procentowa zmiana wskaźnika w zadanym okresie; do wartości nominalnych o różnej skali (przychody, EPS, gotówka operacyjna).
- **Maximum Drawdown** (maksymalne obsunięcie od szczytu) – użyte do wykrywania obniżek ceny docelowej.
- **Historical Range** (zakres historyczny) – bieżący odczyt na tle własnej historii spółki; do upside i wskaźników wyceny, gdzie „dużo" znaczy co innego dla każdej spółki.

### Jak działa punktacja reguły (00:36:11–00:41:05)
- Każda reguła ma Maximum Score (maks. punktów = waga) i Grading Scale: wartość **Worst** (przy niej i gorzej 0 pkt) oraz **Best** (przy niej i lepiej maks.).
- Pomiędzy punkty rosną proporcjonalnie. Przykłady z podglądu reguły Revenue Estimates (10 pkt): Apple z odczytem ok. 8,4% → 0 pkt; Microsoft ok. 16% → ok. 2,3 pkt; Nvidia ok. 39% → 10 pkt.
- Progi Trela dobiera „na oko": nakłada na Master Chart (zmiana procentowa, 5 lat) spółki świetne i słabe i patrzy, gdzie się rozdzielają. Nie ma jedynych słusznych poziomów. Piąty typ reguły, Metrics Comparison (różnica dwóch wskaźników), tylko wspomniał.

### Must-have – warunek konieczny (00:25:22–00:33:40)
- Zaznaczenie pola Must-have robi z reguły filtr zero-jedynkowy: spółka poniżej Worst dostaje flagę i ląduje na końcu listy. Liczba punktów jest wtedy bez znaczenia (wpisuje 1).
- Best trzeba ustawić tylko odrobinę powyżej Worst (np. 3,0 i 3,1), inaczej spółka nie „zaświeci się" na zielono (01:05:05).
- Te same warunki co w screenerze trzeba powtórzyć w modelu: screener sprawdza stan na dziś, a model w backteście sprawdza je na każdy dzień rebalansowania w przeszłości (00:26:01, 00:31:47).

### Pułapka przeoptymalizowania (00:23:38, 01:58:39–02:01:48)
- Nie luzuje się progu po to, żeby „załapała się" lubiana spółka – to zabija sens sztywnych reguł.
- Automatyczne szukanie wag dających najlepszy wynik historyczny to zła droga: w losowych danych zawsze znajdzie się jakaś „prawidłowość". Najpierw hipoteza przyczyna–skutek, potem backtest jako weryfikacja.
- Na koniec kursu „meta-backtesty": te same ustawienia testowane na wielu okresach i horyzontach, wnioski ze średniej.

### Z omówienia testu (00:08:08–00:18:30)
- Z pary P/S i EPS mocniej skorelowany z kursem jest P/S – trzeba to sprawdzać na wykresie, nie z pamięci.
- Przy ocenie przepływów gotówkowych liczą się: dodatni cash flow operacyjny i dodatnia zmiana gotówki netto w roku. Marża, ROA, przychody i zadłużenie nie są gotówką.

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Staż na giełdzie | min. 3 lata od IPO („absolutne minimum", sugestia) | filtr | slajd 00:56:21 |
| Braki danych | Tolerance for Low Scores & Missing Data = Full | – | slajd 00:56:21 |
| Kolory wyniku | zielony od 70%, czerwony poniżej 40% (tylko wizualizacja) | – | slajd 00:56:21 |
| Liczba spółek w portfelu testowym | 25 najlepszych, równe wagi | – | slajd 01:55:33 |
| Rebalansowanie | co 3 miesiące | – | slajd 01:55:33 |
| Wymiana spółki przy rebalansowaniu | tylko gdy następna w kolejce ma wynik wyższy o min. 1 pkt proc. (opcja Reduce turnover) | – | nagranie 01:10:39; opcja widoczna na slajdzie 01:55:33 |
| Zakres historyczny (Historical Range) | ok. 70% odczytów w kanale, po ok. 15% nad i pod | – | z nagrania, niepotwierdzone slajdem – sprawdź 01:41:02; Trela sam nie był pewien |
| Quick Ratio | powyżej 0,8 zadowalające, powyżej 1 pełne bezpieczeństwo | – | z nagrania, niepotwierdzone slajdem – sprawdź 00:14:37 |
| Model Excel po lekcji | Growth 55 pkt, Funds 40 pkt, Value 60 pkt; wynik końcowy = średnia z trzech procentów | – | zrzut Excela |

Progi poszczególnych metryk – w tabeli niżej.

## Konfiguracja modelu punktowego w Scrab

Model „Uniwersytet 2026", stan na koniec lekcji. Punktacja liniowa między Worst a Best. Kierunek we wszystkich regułach: wyżej = lepiej.

| Metryka (nazwa reguły → wskaźnik w Scrab) | Filar | Waga / maks. pkt | Progi (Worst → Best) | Kierunek | Źródło |
|---|---|---|---|---|---|
| Market Cap → Market Cap (USD), Static Range | Must-Have | 1, must-have | 15 mld → 15,01 mld USD; do długich backtestów obniżone do 10 mld → 10,1 mld | wyżej = lepiej | slajd 01:00:18 i 01:46:15 |
| EPS Number → EPS Number Estimates for 2 Fiscal Years Ahead, Static Range | Must-Have | 1, must-have | 3,0 → 3,1 (min. 3 analityków) | wyżej = lepiej | slajd 00:59:00 |
| EPS > 0.50 → EPS Basic (TTM), Static Range | Must-Have | 1, must-have | Worst 0,5 USD; Best na slajdzie „10K" | wyżej = lepiej | slajd 00:33:48 |
| Revenue TTM → Revenue (TTM), Change Over Time, 5 lat | Growth | 5 | 50% → 100% | wyżej = lepiej | slajd 00:37:27 |
| Revenue Estimates → Revenue Average Estimated Annual Growth in Next 2 Years, Static Range | Growth | 10 | 10% → 30% (najpierw 12%, złagodzone) | wyżej = lepiej | slajd 00:42:00 |
| EPS TTM → EPS Basic (TTM), Change Over Time, 5 lat | Growth | 5 | 100% → 250% (najpierw 300%) | wyżej = lepiej | punkty: slajd 00:56:21; progi: z nagrania, niepotwierdzone slajdem – sprawdź 00:44:16–00:44:48 |
| EPS Estimates 2y → EPS Average Estimated Annual Growth in Next 2 Years, Static Range | Growth | 5 | 15% → 40% | wyżej = lepiej | slajd 00:46:03 |
| EPS Estimates 5y → EPS Long Term (5 Years) Growth Estimates, Static Range | Growth | 5 | 15% → 30% | wyżej = lepiej | slajd 00:47:00 |
| CFO TTM → Cash from Operations (TTM), Change Over Time, 5 lat | Growth | 10 | 100% → 250% | wyżej = lepiej | punkty: slajd 00:56:21; progi: z nagrania, niepotwierdzone slajdem – sprawdź 00:48:15 |
| CFO Estimates → prognoza wzrostu CFO na 2 lata (dokładna nazwa wskaźnika niewidoczna) (?), Static Range | Growth | 5 | 15% → 30% | wyżej = lepiej | punkty: slajd 00:56:21; progi: z nagrania, niepotwierdzone slajdem – sprawdź 00:49:26 |
| EBITDA Margin → EBITDA Margin (TTM), Static Range | Growth | 10 | 20% → 40% | wyżej = lepiej | slajd 00:51:00 |
| PT Revisions → Price Target, Maximum Drawdown, 45 dni | Value | 1, must-have | −5% → −4,9% (spadek ceny docelowej od szczytu o 5% lub więcej wyklucza spółkę) | mniejszy spadek = lepiej | nazwa i punkty: slajd 01:46:15; progi: z nagrania, niepotwierdzone slajdem – sprawdź 01:24:16–01:25:10 |
| PT Change over year → Price Target, Change Over Time, 180 dni | Value | 10 (testowane 15 i 30) | 10% → 20% | wyżej = lepiej | slajd 01:30:06, 01:36:24, 01:46:15 |
| Upside → potencjał wzrostu do ceny docelowej, Historical Range, 4 lata, kanał poziomy, „Higher values preferred" | Value | 15, potem podniesione (nowa wartość nie padła) | poniżej kanału 0 pkt → powyżej kanału maks. | wyżej = lepiej | punkty: slajd 01:46:15; ustawienia: z nagrania, niepotwierdzone slajdem – sprawdź 01:40:04–01:42:15 |
| Fundamentals | Fundamentals | 0 – kategoria pusta | brak reguł | – | slajd 01:46:15 |

Suma: Growth 55 pkt (zgodnie z Excelem), Value 26 pkt, Must-Have 3 pkt. Analiza miękka pominięta – nie da się jej testować automatem (00:21:02).

## Przykłady z lekcji

Backtesty: model „Uniwersytet 2026", 689 spółek ze screenera, 25 pozycji, równe wagi, rebalansowanie co 3 miesiące, od 1.06.2016. S&P 500 w tym okresie: 12,95% rocznie, łącznie 227,67%, maks. obsunięcie −33,92%.

| Wariant | Zwrot roczny | Łącznie | Maks. obsunięcie | Źródło |
|---|---|---|---|---|
| Sama zyskowność (Growth + Must-Have) | 18,06% | 404,74% | −32,56% | slajd 01:34:33 |
| + PT Revisions (must-have) + PT Change (15 pkt) | 18,5% | 423,22% | −32,23% | slajd 01:34:45 |
| PT Change podniesione do 30 pkt | ok. 17,6% – pogorszenie | – | – | z nagrania, niepotwierdzone slajdem – sprawdź 01:39:22 |
| PT Change 10 pkt + Upside 15 pkt | 19,16% | 452,34% | −33,79% | slajd 01:45:30 |
| Wyższa waga Upside | 21,4% | 562,44% | −32,48% | slajd 01:50:09 |
| Jak wyżej, ale bez must-have na PT Revisions | 18,99% | 444,82% | – | slajd 01:55:33 |

- Wniosek Treli: cena docelowa jest istotna, ale jej waga nie może być zbyt duża; upside wyraźnie pomaga; wyrzucanie spółek ze spadającą ceną docelową daje statystyczną przewagę (wyjątki ręczne dopuszczalne, ale nie w testach).
- Test od stycznia 2010 (sama zyskowność): 13,09% rocznie (slajd 01:30:24); łącznie ok. 638% wobec ok. 480% dla S&P 500 (z nagrania, niepotwierdzone slajdem – sprawdź 01:22:12) – przewaga mniejsza, przy nieco większym obsunięciu.
- Nie należy przywiązywać się do samej wysokości zwrotu (zależy od daty startu) – liczy się porównanie z benchmarkiem i to, czy zmiana poprawia, czy pogarsza wynik (01:43:07).
- Ranking na dziś: APP ma wysoki wynik zyskowności, ale przy progu 3 lat od IPO krótko notowane spółki (np. ALAB) spadają na koniec listy z komunikatem o zbyt krótkiej historii (01:00:44).

## Narzędzia
- **Scoring Models → + → Start from Scratch** (bez gotowych szablonów); nazwa modelu, kategorie: Growth, Fundamentals, Value, Must-Have (00:19:44–00:25:30).
- **Add Rule → Build Your Own** → typ reguły → Rule Name, Category, Maximum Score, Financial Metric, Timeframe, Grading Scale (Worst/Best), pole Must-have. Po prawej podgląd „Preview – Test before saving" z wynikiem przykładowej spółki.
- **Dodawanie spółek do modelu**: ręcznie (Add Companies, wklejenie tickerów) albo ze Screenera („Add to" → model).
- **Screener użyty w lekcji** (slajd 01:05:33): Exchanges – USA, Austria, Belgia, Dania, Finlandia, Francja, Niemcy, Włochy, Holandia, Polska, Szwajcaria, Wielka Brytania; Market Cap (USD) od 10B; EPS Number Estimates for 2 Fiscal Years Ahead od 3; Revenue Average Estimated Annual Growth in Next 2 Years od 5% → ok. 689 spółek. Do backtestów screener celowo szeroki, a rygor w modelu.
- **Backtests → New Backtest**: Scoring Model, Companies, Backtest Period → Rebalancing Frequency, Portfolio Size, Asset Allocation (Equal Weights), Required Years Since IPO, Tolerance, Buy & Sell Criteria, Advanced Settings → Run Backtest → **Open Tear Sheet** (karta wyników na tle benchmarku: Annual return, Cumulative returns, Max drawdown, Annual volatility, Sharpe ratio).
- Modele i backtesty wymagają abonamentu co najmniej Standard (00:53:03); gotowy model Trela ma wgrać uczestnikom na koniec kursu.

## Co z tego zastosuję w skanerze
1. Dwa typy funkcji punktujących: (a) wartość bieżąca w stałym zakresie, (b) zmiana procentowa w oknie czasu. Wejście: odczyt, Worst, Best, maks. punktów → wynik: 0 poniżej Worst, maks. powyżej Best, liniowo pomiędzy.
2. Filtry konieczne przed punktacją: kapitalizacja min. 15 mld USD (10 mld w długich testach), min. 3 analityków prognozujących EPS na 2 lata naprzód, EPS TTM powyżej 0,50 USD, min. 3 lata od IPO → niespełnienie = spółka na koniec listy.
3. Filar zyskowności 55 pkt według tabeli konfiguracji (8 reguł z progami).
4. Cena docelowa: spadek o 5% lub więcej od szczytu z 45 dni → wykluczenie; wzrost w 180 dni: 10% → 0 pkt, 20% → maks. (10 pkt).
5. Upside oceniany względem własnej 4-letniej historii spółki (poziomy kanał), nie stałym progiem; im wyżej w kanale, tym więcej punktów.
6. Filtry ze skanera zapisać także w modelu i liczyć je na datę oceny, żeby dało się testować wstecz.
7. Ranking → 25 najlepszych, równe wagi, przegląd co kwartał; wymiana tylko przy różnicy wyniku min. 1 pkt proc.
8. Każdą zmianę wagi lub progu oceniać backtestem względem S&P 500 na kilku okresach, a nie dopasowywać pod jeden okres.

## Pytania powtórkowe
1. Kiedy używa się reguły Static Range, a kiedy Change Over Time?
2. Dlaczego warunki ze screenera trzeba powtórzyć w modelu punktowym?
3. Co oznaczają Worst i Best i ile punktów dostaje spółka pomiędzy nimi?
4. Jakie trzy warunki Must-Have ustawił Trela i z jakimi progami?
5. Co pokazały backtesty o wadze ceny docelowej, o upside i o wyrzucaniu spółek z obniżaną ceną docelową?
6. Dlaczego automatyczne szukanie „najlepszych" wag pod historię jest błędem?

## Niepewne – do sprawdzenia
- Progi EPS TTM (100% → 250%), CFO TTM (100% → 250%), CFO Estimates (15% → 30%) – tylko z nagrania; na slajdach widać nazwy reguł i punkty (00:44:16, 00:48:15, 00:49:26).
- Dokładna nazwa wskaźnika w regule CFO Estimates i w regule Upside (prawdopodobnie „Price Target Upside" – taka pozycja jest na liście wskaźników) – niewidoczna na slajdach.
- PT Revisions: 45 dni i −5% / −4,9% tylko z nagrania; transkrypcja zniekształca liczbę dni (01:24:16, 01:37:03).
- Do ilu punktów podniesiono Upside przed wynikiem 21,4% – nie padło (01:46:16–01:50:05).
- EPS > 0.50: na slajdzie Best = „10K"; czy poprawiono na wartość tuż nad Worst, nie widać.
- Rebalansowanie w pierwszym teście: Trela waha się między 1 a 3 miesiącami; slajd wyników pokazuje 3 Months (01:09:41, 01:55:33).
- Test od 2010 r.: czy z progiem 2 czy 3 lat od IPO – niejasne (01:17:05).
- Excel: nagłówek „TOTAL of TOTALS (209 pkt)", choć suma filarów to 155 pkt; w arkuszu upside ma 20 pkt, w Scrab 15.

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
