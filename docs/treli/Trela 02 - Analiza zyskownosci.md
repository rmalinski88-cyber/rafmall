---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 2. Analiza zyskowności (spotkanie live nr 2), 18 marca 2026, ok. 2 h"
status: do przejrzenia
---
# Trela 02 – Analiza zyskowności i pierwszy model punktowy (spotkanie 2)

## W skrócie
Lekcja pokazuje, skąd w sprawozdaniu finansowym biorą się trzy liczby, na których Trela opiera ocenę zyskowności: przychody, zysk na akcję (EPS) i gotówka z działalności operacyjnej (CFO), oraz jak je oglądać na wykresach w Scrabie razem z prognozami analityków i ich rewizjami. Każdą liczbę ocenia się trzema metodami: porównanie z innymi spółkami, trend, wartość nominalna. **Uwaga:** model punktowy w Excelu został tylko zapowiedziany – zasad przyznawania punktów w kolumnach Trela w tym nagraniu NIE podał, przełożył to na spotkanie 3 (01:45:05).

## Najważniejsze koncepty

### Trzy metody oceny każdego wskaźnika (00:01:07)
- **Analiza krzyżowa** – sama liczba (np. wzrost 17%) nic nie mówi, trzeba ją zestawić z innymi spółkami lub średnią branży.
- **Analiza trendu** – czy odczyt z roku na rok się poprawia, czy pogarsza.
- **Ocena nominalna** – niektóre wartości mówią same za siebie (marża 60% jest ogromna bez porównań); marża nie może rosnąć bez końca, więc tu liczy się poziom.
- Do tego **prognozy** na kolejne lata i **rewizje** (zmiany prognoz analityków w czasie). Wg Treli to rewizje najczęściej mówią, kiedy reagować; nie ma „kup i zapomnij" (00:03:01).

### Sprawozdanie finansowe – co z niego brać (00:08:47)
- **Income statement** (rachunek wyników): Revenue (przychody) → minus Cost of Revenue → Gross Profit → minus koszty operacyjne → Operating Income = **EBIT** (zysk przed odsetkami i podatkiem).
- **EBITDA** = EBIT z dodaną z powrotem amortyzacją i deprecjacją (koszt czysto księgowy, rozłożony zwykle na ok. 5 lat). EBITDA jest zawsze ≥ EBIT i wg Treli lepiej pokazuje kondycję operacyjną (00:12:22, 00:29:42).
- **EPS** (earnings per share) = zysk netto / liczba akcji w obiegu. Trela używa EPS jako głównej miary zysku, bo analitycy prognozują właśnie EPS (00:18:23). Diluted EPS uwzględnia zamianę opcji pracowniczych na akcje.
- Z rachunku wyników wystarczą dwa pytania: czy rosną przychody i czy rośnie zysk netto (jeśli tak, koszty rosną wolniej niż przychody) (00:19:20).
- **Cash flow** (przepływy gotówki): Operating / Investing / Financing. Liczy się jedno: **gotówka z działalności operacyjnej ma rosnąć z roku na rok** (00:21:16). CFO (Cash from Operations) i OCF to to samo.
- Duże dodatnie wpływy z działalności inwestycyjnej to zły znak (wyprzedaż majątku); minus lub okolice zera są w porządku (00:23:17).
- Skup akcji (buyback) i dywidendy są dobre tylko wtedy, gdy finansuje je gotówka operacyjna (00:25:16). Stan gotówki na koniec roku sam w sobie nic nie mówi (00:27:26). Dywidend Trela w ocenie nie bierze pod uwagę (01:48:10).

### TTM, roczne, kwartalne (00:32:35)
- **TTM** (trailing twelve months) = suma czterech ostatnich kwartałów; najświeższe dane, niezależne od roku fiskalnego spółki. Jeśli jest TTM – brać TTM.
- Danych kwartalnych nie analizować: sezonowość, więcej szumu niż sygnału.

### Prognozy i rewizje – trzy warunki (00:51:33)
1. Każda kolejna prognoza musi być wyżej: TTM < bieżący rok fiskalny < następny < dwa lata do przodu. Dla przychodów to warunek konieczny – spółka, która go nie spełnia, „wylatuje z portfela".
2. Rewizje muszą iść w górę, a nie w dół. Liczy się też historia: spółka z nawykiem rewizji w dół (Intel) jest podejrzana, nawet gdy dzisiejsze prognozy rosną.
3. Różnica między prognozami musi być znaczna w procentach, nie „na oko" z wykresu.
- Skoki na wykresach prognoz przy zmianie roku fiskalnego to nie rewizja, tylko zmiana definicji „bieżącego/następnego roku" (01:00:32).

### Stabilność ponad wszystko
- Trela woli gładki wzrost bez pojedynczych złych lat od biznesu z wahaniami (00:36:00, 00:43:37).
- Jednorazowy skok (np. CFO Apple) to anomalia; nagły boom (Micron) sugeruje cykliczność – ostrzeżenie, nie dyskwalifikacja (01:29:30, 01:33:00).
- Żaden pojedynczy wskaźnik nie dyskwalifikuje spółki ani nie każe jej sprzedać – słabszy odczyt to po prostu mniej punktów (01:13:47, 01:50:25).

### Czego Trela nie bierze do modelu (01:39:38)
- ROA (zwrot z aktywów) i ROIC (zwrot z zainwestowanego kapitału): zakłamane dla spółek bez fabryk i powielają informację o zysku netto.
- Zostaje **marża EBITDA** – im wyższa, tym większy bufor do obniżania cen (01:42:34).
- Cel: ok. 20 parametrów w całym modelu (zasada Pareto; limit 20 metryk w tańszym abonamencie Scraba).

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Revenue TTM (historia) | wzrost w horyzoncie 5–10 lat, gładki; porównać % zmiany z innymi spółkami | max 5 („Revenue (5) TTM") | nagranie 00:42:13; punkty: Excel |
| Revenue – prognozy | TTM < Current FY < Next FY < 2 FY Ahead (warunek konieczny); rewizje w górę; istotny % wzrostu (Revenue Average Est. Annual Growth in Next 2 Years) | max 10 („Revenue (10) Est.") | nagranie 00:51:33; Excel |
| EPS Basic TTM (historia) | jak przychody: trend, gładkość, porównanie | max 5 („EPS TTM (5)") | nagranie 01:26:17; Excel |
| EPS – wzrost 2 lata | EPS Average Est. Annual Growth in Next 2 Years: poziom + trend rewizji | max 5 („EPS 2y Growth (5)") | nagranie 01:30:37; Excel |
| EPS – wzrost 5 lat | EPS Long Term (5 Years) Growth Estimates: ma nie spadać; najlepiej zbieżny z dynamiką 2-letnią; niższy niż 2-letni = mniej punktów | max 5 („EPS 5y Growth (5)") | nagranie 01:55:13; Excel |
| Cash from Operations TTM | ma rosnąć rok do roku, bez anomalii i cykliczności | max 10 („Cash from Op. (10)") | nagranie 01:31:58; Excel |
| CFO – prognozy | CFO per Share Average Est. Annual Growth in Next 2 Years + kierunek rewizji | max 5 („CFO 2y Est (5)") | nagranie 01:34:52; Excel |
| EBITDA Margin | im wyższa, tym lepiej (ocena nominalna + krzyżowa) | max 10 („EBITDA Margin (10)") | nagranie 01:42:34; Excel |
| Wynik filaru | suma punktów / 55 („TOTAL GROWTH (55 pkt)") | 55 | Excel |
| Kapitalizacja | minimum 10–15 mld USD (lepsze dane, więcej analityków) | – | (z nagrania, niepotwierdzone slajdem – sprawdź 01:02:45) |
| Liczba analityków w prognozie | absolutne minimum 5; przy 2–3 prognozę wyrzucić | – | (z nagrania, niepotwierdzone slajdem – sprawdź 01:13:28) |
| Punkt odniesienia S&P 500 | zyski rosną ok. 10% rocznie, przychody ok. 6% – spółki w portfelu mają rosnąć szybciej | – | (z nagrania, „z pamięci" – sprawdź 00:54:31) |
| Częstotliwość przeglądu | aktualizacja modeli raz na miesiąc | – | (z nagrania – sprawdź 01:23:24) |

Szczegółowej skali punktów (za co 10, za co 5, za co 0) w tym nagraniu nie ma. W pliku Excel są już przykładowe oceny (ALAB, NVO, META, TSLA) – pochodzą z późniejszej wersji modelu, nie z tej lekcji.

## Przykłady z lekcji
- **Przychody 5 lat (slajd 00:44:27):** Arista (ANET) +265,78%, Apple (AAPL) +33,82%, Intel (INTC) −31,99%. Kurs w tym czasie wg Treli: ok. +600%, +100%, −30% (tylko nagranie, 00:45:32) – dowód, że zyskowność koreluje z ceną akcji.
- **Apple – prognozy przychodów (slajd 00:57:51):** TTM 435,62 mld; 463,99 / 494,84 / 523,51 mld; średni wzrost 7,98% rocznie. Rosną, ale w latach 2023–2025 bywały rewizje w dół.
- **Nvidia (slajdy 01:04:45, 01:29:09, 01:58:27):** dynamika przychodów 37,89%; prognozę robi 56 analityków; EPS TTM 4,93 → 8,25 / 10,9 / 12,6; EPS 2-letni 40,23%, 5-letni 27,01% (5 analityków).
- **Micron (MU):** świetne prognozy EPS, ale boom wygląda na cykliczny (01:29:16).
- **CFO na akcję, wzrost 2-letni (slajd 01:38:30):** AAPL 16,81%, ANET 17,5%, INTC 21,89% – Intel ma wysoki odczyt z niskiej bazy i przy złych rewizjach, więc nie jest to atut.
- **Marża EBITDA TTM (slajd 01:48:54):** NVDA 61,7%, MU 53,09%, ANET 43,63%, AAPL 35,1%, INTC 22,62%.
- **Apple w Yahoo Finance (slajdy 00:09:39–00:24:33):** przychody 435,6 mld, EBIT 141,1 mld, EBITDA 152,9 mld, Basic EPS 7,93, Operating Cash Flow 135,5 mld.

## Narzędzia
- **Yahoo Finance** → Financials → Income Statement / Cash Flow, kolumna TTM.
- **Scrab → Master Chart**: ticker na górze, metryki na dole; horyzont 5Y–10Y; przełącznik skali z `Lin` na `%` (percent change) do porównań; metryki przeciąga się na siebie, żeby były na jednym wykresie (00:50:47, 01:07:42).
- Metryki: `Revenue (TTM)`, `Revenue Estimates for Current Fiscal Year / Next Fiscal Year / 2 Fiscal Years Ahead`, `Revenue Average Estimated Annual Growth in Next 2 Years`, `Revenue Number Estimates for Next Fiscal Year` (liczba analityków), `EPS Basic (TTM)` + trzy prognozy, `EPS Average Estimated Annual Growth in Next 2 Years`, `EPS Long Term (5 Years) Growth Estimates` (+ `Number Estimates`), `Cash from Operations per Share (TTM)` + `CFO per Share Estimates…`, `CFO per Share Average Estimated Annual Growth in Next 2 Years`, `EBITDA Margin (TTM)`.
- Pułapka: `Cash from Operations` jest w dolarach łącznie, a prognozy CFO są „per Share" – do jednego wykresu brać wersję per Share (01:37:03).
- Menu „trzy kropki" → `Domestic Peers` / średnia peers; Trela korzysta rzadko, woli porównanie spółka do spółki, także między branżami (00:47:09).
- Dane prognoz w Scrabie pochodzą z FactSet, odświeżane co noc, opóźnienie 1–3 dni; pokazywana wartość to mediana (01:04:50, 01:10:46).
- TipRanks – lista konkretnych analityków; rekomendacji buy/sell Trela każe nie czytać (01:16:54).

## Co z tego zastosuję w skanerze
1. Filtr wstępny: kapitalizacja ≥ 10 mld USD; liczba analityków w prognozie ≥ 5, inaczej prognozę oznaczyć jako niewiarygodną.
2. Warunek konieczny: `Rev TTM < Rev CurrentFY < Rev NextFY < Rev 2FY` → jeśli fałsz, spółka odpada.
3. To samo sprawdzenie „schodków" dla EPS i CFO per Share → wynik jako punkty, nie jako odrzucenie.
4. Kierunek rewizji: porównać dzisiejszą prognozę z tą sprzed 3/6/12 miesięcy; rewizje w dół w historii = flaga ostrzegawcza. Pominąć skok na przełomie roku fiskalnego.
5. Gładkość trendu: policzyć, ile razy w 5–10 latach wartość TTM spadła rok do roku; jednorazowy skok oznaczyć jako anomalię zamiast liczyć go do wzrostu.
6. Ranking krzyżowy: procentowa zmiana 5-letnia i prognozowany wzrost 2-letni porównywane w całej liście spółek, nie tylko w branży.
7. Zbieżność EPS: wzrost 5-letni wyraźnie niższy niż 2-letni → mniej punktów.
8. Wagi kolumn wg Excela: 5 / 10 / 5 / 5 / 5 / 10 / 5 / 10, wynik = suma / 55. Skalę wewnątrz kolumn uzupełnić po spotkaniu 3.

## Pytania powtórkowe
1. Jakie są trzy metody oceny wskaźnika i kiedy wystarcza sama ocena nominalna?
2. Dlaczego Trela woli EBITDA od EBIT, a jako miarę zysku używa EPS?
3. Jakie trzy warunki muszą spełniać prognozy przychodów?
4. Skąd biorą się skoki na wykresach prognoz przy zmianie roku fiskalnego?
5. Dlaczego ROA i ROIC nie wchodzą do modelu, a marża EBITDA tak?
6. Ile punktów maksymalnie ma każda z ośmiu kolumn filaru zyskowności?

## Niepewne – do sprawdzenia
- Zasady punktacji w kolumnach: nie padły w tym nagraniu (zapowiedź 01:45:29) – sprawdzić w notatce ze spotkania 3.
- EPS Long Term Nvidii: w mowie „20%" (01:57:04), na slajdzie 27,01% – przyjęto slajd.
- Wzrost EPS Apple 5 lat „75–76%", Micron „270%", Arista „400%", Nvidia „2000%" (01:26:44–01:27:12) – tylko nagranie, slajdu brak.
- Apple: EPS 2-letni 11% i 5-letni 8%; Arista 20%/20% przy 2 analitykach (01:55:42–01:56:41) – tylko nagranie.
- Dynamika przychodów Aristy „20–23%", Intela „5%", inne spółki „37/50/60%" (00:59:03–01:00:06) – tylko nagranie.
- CFO per Share Micron/Nvidia na slajdzie 01:38:30 nieczytelne (ok. 50% i ok. 91%, bez pewności, która spółka).
- EPS Micron na slajdzie 01:30:30 (TTM 10,62; prognozy ok. 38,5 / 59,3 / 51,5) – drobny druk, kolejność lat niepewna.
- Przykładowe progi do screenera „przychody +10%, EPS +15%, CFO dodatni" (01:47:05) padły jako ilustracja, nie jako oficjalna reguła.
- Kursy akcji 5 lat: Nvidia „+1000%", Arista „+600%" (01:35:33) – tylko nagranie.

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
