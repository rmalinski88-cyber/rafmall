---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 3. Analiza zyskowności, cz. 2 (spotkanie live nr 3), 25 marca 2026, ok. 2 h"
status: do przejrzenia
---
# Trela 03 – Analiza zyskowności cz. 2: punktowanie w modelu (spotkanie 3)

## W skrócie
Spotkanie warsztatowe: Trela na żywo wypełnia w Excelu filar zyskowności (8 kolumn, razem 55 pkt) dla czterech spółek z zadania domowego: ALAB, TSLA, NVO i META. Nie podaje sztywnej tabeli progów – punkty przyznaje „na oko" według trzech kryteriów (trend, wartość nominalna, porównanie z najlepszymi spółkami) i mówi wprost, że ocena jest subiektywna. Ważna jest konsekwencja: ta sama metoda dla każdej spółki daje ten sam ranking, nawet jeśli sumy punktów wyjdą inne. Skalę w tabelach poniżej odtworzyłem z jego przykładów.

## Najważniejsze koncepty

### Wagi kolumn i skąd się biorą (00:23:19)
- Prognozy przychodów ważą więcej (10) niż historia (5), bo kupując akcje, kupujemy przyszłość.
- EPS (zysk na akcję): historia 5 + prognoza 2-letnia 5 + prognoza 5-letnia 5, czyli prognozy razem 10.
- Gotówka operacyjna (CFO) odwrotnie: historia 10, prognoza tylko 5, bo wg backtestów Treli prognozy gotówki sprawdzają się najsłabiej.
- Marża EBITDA 10. Razem 55 pkt; wynik = suma / 55.
- Wagi są uznaniowe, oparte na backtestach i doświadczeniu; inna konfiguracja pasowałaby do spółek dywidendowych niż do wzrostowych (00:25:33).

### Trzy kryteria oceny jednego wskaźnika (00:28:21)
1. **Trend** – czy wykres rośnie i czy każda kolejna prognoza jest wyżej.
2. **Wartość nominalna** dynamiki – 1–3% rocznie to słabo, 40% to wybitnie.
3. **Porównanie z innymi spółkami** – gdy liczba nie jest oczywista (np. 13%).
- Porównuje się z najlepszymi spółkami na całej giełdzie, nie ze średnią sektora: celem jest top 20–30 spółek świata, a nie najlepsza spółka w słabej branży (00:54:09, 01:10:42).

### Za co Trela odejmuje punkty
- Rewizje prognoz w dół (analitycy obniżają prognozy) – najcięższa kara, ważniejsza niż sam poziom dynamiki (01:08:06).
- Brak rosnącego trendu dynamiki: −1 lub −2 pkt nawet przy wysokim poziomie (00:36:07).
- Niestabilność: wahania zysków lub marży, gorsze lata po drodze (01:48:48, 01:52:38).
- Dynamika z dolnego zakresu na tle topowych spółek (01:50:35).
- Spadek od szczytu (wskaźnik `Percent of High` w Scrabie) (01:04:54).

### Czego nie karze
- Małej skali: nominalnej wielkości przychodów się nie ocenia, liczy się dynamika i kierunek (00:45:59). Nominalnie karze się marżę i zadłużenie.
- Niskiej bazy startowej (ALAB) i krótkiej historii, jeśli obraz jest jednoznaczny (00:30:41, 00:43:32).
- Spadku dynamiki prognoz dokładnie na przełomie roku fiskalnego – to zmiana definicji „bieżącego/następnego roku", nie rewizja (00:31:49, 01:41:30).
- Wyjątek: skrajnie małe wartości (EPS z 1 na 2 centy = „+100%") trzeba wykluczyć ręcznie (00:58:29).

### TTM kontra Annual Actual (00:17:36)
- `Revenue (TTM)` zawiera zdarzenia jednorazowe (np. sprzedaż części firmy, jednorazowy kontrakt), a prognozy analityków je pomijają. Przykład: Prologis (PLD), gdzie prognozy leżały poniżej TTM.
- W Scrabie lepiej użyć `Annual Actual Revenue`, `Annual Actual EPS`, `Annual Actual CFO per Share` – liczone tak jak prognozy. Poza Scrabem zostaje TTM, bo jest dostępne wszędzie.

### Automatyzacja punktów – ostrzeżenie (00:48:12, 00:51:13)
- Progi liczbowe da się zakodować (będzie to robione w Scrabie na późniejszych spotkaniach), ale algorytm nie widzi anomalii: wzrostu z 1 na 2 centy albo wykresu ze skokiem, który człowiek wyłapuje od razu.
- Filtr typu „EPS min. 1 USD" odrzuci świetną spółkę z EPS 0,99.

### Kiedy sprzedawać (01:17:21, 01:21:00)
- Jeden spadek prognoz to może być przypadek; powtarzające się obniżki przez kolejne kwartały to reguła – uciekać. Obniżki rzadko są tymczasowe (01:36:55).
- Spółkę wyrzuca się nie dlatego, że jest zła, tylko dlatego, że znalazła się lepsza: portfel = 20–30 najlepszych, model aktualizowany co kwartał.
- To, czy mamy na pozycji zysk czy stratę, nie może wpływać na decyzję (01:35:17).
- Kurs akcji nie bierze udziału w ocenie zyskowności (00:41:29).

## Reguły i progi liczbowe

Skala punktów odtworzona z ocen czterech spółek (punkty widać na slajdach Excela; uzasadnienia pochodzą z nagrania).

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| Revenue historia (max 5) | stały wzrost → 5; rosły, ale od 2–3 lat stoją i są ok. 3% pod szczytem → 2; wyraźny spadek 5–15% → 1 lub 0 | 5 / 2 / 1–0 | slajd 01:06:42; nagranie 01:05:39 |
| Revenue Est. (max 10) | schodki w górę + dynamika ok. 40% → 10, minus 2 za spadający trend dynamiki = 8; ok. 20% i ładny trend → 7; schodki są, ale 14% i wieloletnie rewizje w dół → 3; prognoza poniżej bieżących przychodów, dynamika ok. 0 → 0 | 8 / 7 / 3 / 0 | slajdy 00:39:36, 01:49:19, 01:08:00, 01:26:21 |
| Punkt odniesienia dla przychodów | średnia prognozowana dynamika S&P 500 ok. 8–9%, w uproszczeniu 10%; powyżej 10% = dobrze, 40% = wybitnie | – | (z nagrania, niepotwierdzone slajdem – sprawdź 00:32:38) |
| EPS historia (max 5) | rośnie → 5; rośnie, ale nie od początku stabilnie → 4; długi trend dobry, lecz duże wahania → 3,5; 60% pod szczytem → 1 | 5 / 4 / 3,5 / 1 | slajdy 01:05:30, 01:50:03, 01:08:33 |
| EPS 2y Growth (max 5) | wysoka dynamika + rewizje w górę → 5; 19–36% bez rewizji w górę lub bez rosnącego trendu → 4; 30%, ale stale obniżana → 2; dużo niższa dynamika albo brak schodków → 1; dynamika ok. 0 → 0 | 5 / 4 / 2 / 1 / 0 | nagranie 01:08:33–01:08:50, 01:50:04; slajdy jw. |
| EPS 5y Growth (max 5) | ok. 40% i stabilna → 5; 14% stabilna (topowe mają 30–40%) → 3,5; trend zły → 2; prognoza bliska zera → 0 (albo 1, jeśli nie daje się zer) | 5 / 3,5 / 2 / 0 | slajdy 00:38:51, 01:50:57, 01:09:36 |
| Cash from Op. historia (max 10) | rośnie, prognozy coraz wyżej → 10; świetna historia z lekkim spadkiem po drodze → 8; trend spadkowy + rewizje w dół → 3 („ucinam 70%") | 10 / 8 / 3 | slajdy 00:44:16, 01:52:18, 01:10:17 |
| CFO 2y Est (max 5) | wysoka stabilna dynamika bez wzrostu → 4; 17% (niższy zakres) mimo rewizji w górę → 3,5; rewizje w dół → 2; prognozy poniżej, dynamika ujemna → 0 | 4 / 3,5 / 2 / 0 | slajdy jw.; nagranie 01:26:55, 01:52:18 |
| EBITDA Margin (max 10) | 50%, ale niestabilna → 7; 21% rosnąca, „przyzwoita, nie wybitna" → 6,5; 48% z drastycznym spadkiem → 6; 11% i spada → 2; 1 pkt zarezerwowany dla marż rzędu kilku procent | 7 / 6,5 / 6 / 2 | slajdy 01:13:00, 01:27:09, 01:52:30 |
| Wynik filaru | suma / 55; 75% = „bardzo dobry wynik, spokojnie do portfela" | – | slajd 02:00:57; nagranie 01:53:04 |
| Historia notowań | najlepiej 4–5 lat; 2,5 roku wystarczy przy jednoznacznym trendzie | – | (z nagrania – sprawdź 00:45:02) |
| Cena akcji | minimum kilkadziesiąt USD (bez spółek groszowych) | – | (z nagrania – sprawdź 01:03:10) |

## Przykłady z lekcji

Punkty z Excela (zgodne ze slajdem 02:00:57). Kolejność kolumn: Rev TTM (5) / Rev Est. (10) / EPS TTM (5) / EPS 2y (5) / EPS 5y (5) / CFO (10) / CFO 2y (5) / EBITDA Margin (10).

| Spółka | Rev | Rev Est | EPS | EPS 2y | EPS 5y | CFO | CFO Est | Marża | Suma | Wynik |
|---|---|---|---|---|---|---|---|---|---|---|
| ALAB (Astera Labs) | 5 | 8 | 4 | 4 | 5 | 10 | 4 | 6,5 | 46,5 | 85% |
| META | 5 | 7 | 3,5 | 4 | 3,5 | 8 | 3,5 | 7 | 41,5 | 75% |
| NVO (Novo Nordisk) | 5 | 0 | 5 | 0 | 0 | 5 | 0 | 6 | 21 | 38% |
| TSLA (Tesla) | 2 | 3 | 1 | 2 | 2 | 3 | 2 | 2 | 17 | 31% |

Pozostałe spółki z zadania (MSFT, RTX, LLY, MRVL, WMT, NFLX) nie zostały ocenione – zostały do samodzielnego przerobienia.

**ALAB (00:29:33–00:40:53, korekta 00:44:20)**
- Przychody +636% w ok. 2,5 roku od wejścia na giełdę (slajd 00:30:39) → 5.
- Prognozy przychodów: dynamika 40,82%, trzecia najwyższa na liście porównawczej (slajd 00:33:18). Najpierw 10, potem 8 – minus 2 za to, że dynamika spadła z ok. 100% i nie rośnie.
- EPS: wyjście ze straty; 5 obniżone do 4 za brak stabilności od początku.
- EPS 2y 36,31% (slajd 00:35:00), bez rewizji w dół, ale bez rosnącego trendu → 4.
- EPS 5y 40,93%, stabilne, tylko 3 analityków (slajd 00:38:51) → 5.
- CFO rośnie, każda prognoza wyżej → 10; prognoza stabilna, bez wzrostu → 4.
- Marża EBITDA 21,15%, rośnie, ale w dolnym zakresie dobrych spółek → 6,5.

**TSLA (01:04:06–01:13:16)**
- Przychody +160% w 5 lat, ale od 2023 stoją i są 3% pod szczytem → 2.
- Prognozy: schodki są, dynamika 14,89% (slajd 01:14:23), lecz spadła z ok. 40% i jest obniżana od lat → 3.
- EPS 60% pod szczytem → 1. EPS 2y 30,85%, ale stale obniżane → 2. EPS 5y lekko odbił, trend zły → 2.
- CFO spadkowy, świeże rewizje w dół → 3; prognoza → 2.
- Marża 11,6% i spada (slajd 01:13:27); przy 60% u Nvidii czy Microna → 2.
- Wg Treli do 2022 r. ta sama spółka dostałaby wysokie oceny – dowód, że „kup i trzymaj" nie działa.

**NVO (01:24:12–01:27:29)**
- Przychody i EPS (z 2 do 4 w dwa lata) wciąż rosną → po 5.
- Prognozy przychodów, EPS 2y, EPS 5y i CFO: kolejne lata poniżej bieżących, dynamika ok. 0 lub ujemna → 0.
- Marża 48,35% (slajd 01:27:09), wysoka, ale drastycznie spada → 6.
- Trela przyznał, że sam trzymał NVO za długo; sygnałem były rewizje w dół od października 2024.

**META (01:47:53–01:53:09)**
- Przychody rosną → 5. Prognozy: 19,65% (slajd 01:48:18), ładny trend, lecz niżej niż topowe → 7.
- EPS: ok. +80% w 5 lat, duże wahania → 3,5. EPS 2y ok. 19%, bez rewizji w górę → 4. EPS 5y 14,67% → 3,5.
- CFO: świetna historia, drobny spadek po drodze → 8; prognoza 17,35% → 3,5.
- Marża 50,7%, bardzo wysoka, ale bez trendu i z dużymi wahaniami → 7.

## Narzędzia
- **Scrab → Master Chart**: spółki u góry, metryki na dole; do porównań zaznaczyć kilka spółek naraz i przełączyć skalę na `%` (00:50:13).
- Metryki użyte na lekcji: `Annual Actual Revenue`, `Revenue Estimates for Current / Next Fiscal Year / 2 Fiscal Years Ahead`, `Revenue Average Estimated Annual Growth in Next 2 Years`, `Annual Actual EPS` + prognozy, `EPS Average Estimated Annual Growth in Next 2 Years`, `EPS Long Term (5 Years) Growth Estimates` (+ `Number Estimates`), `Annual Actual CFO per Share` + prognozy, `EBITDA Margin (TTM)`.
- `Percent of High` – tryb wykresu pokazujący, ile procent wskaźnik lub prognoza spadły od swojego szczytu; szybki sposób na zobaczenie rewizji w dół (01:04:54).
- Dziwny wykres (np. start z wartości ujemnych) → zmienić skalę z logarytmicznej na liniową (00:35:27).
- Dane w Scrabie zaczynają się od IPO (debiutu giełdowego) spółki (00:57:14).
- **Excel**: plik `Model-2026-Zyskownosc`, jedna spółka w wierszu, ostatnia kolumna `=SUM(C:J)/55`.

## Co z tego zastosuję w skanerze
1. Dane historyczne brać w wersji „Annual Actual" (bez zdarzeń jednorazowych), jeśli źródło ją ma; inaczej TTM z flagą „może zawierać jednorazowe".
2. Dla każdej prognozy liczyć spadek od szczytu (percent of high) → duży spadek = rewizje w dół → mocne obcięcie punktów, nawet gdy dynamika jest wysoka.
3. Historia przychodów: wzrost ciągły → 5; płasko i 0–5% pod szczytem → 2; spadek ≥ 5% → 0–1.
4. Prognozy: sprawdzić schodki, potem poziom dynamiki względem najlepszych spółek na liście (ranking), potem trend dynamiki; brak rosnącego trendu → −1 (kolumny 5-punktowe) lub −2 (10-punktowe).
5. Pomijać skok dynamiki w miesiącu zmiany roku fiskalnego spółki.
6. Marża EBITDA: punkty za poziom na tle całej listy, minus za spadek i za wahania.
7. Flagi do ręcznego przeglądu zamiast automatycznej oceny: EPS bliski zera, przejście ze straty do zysku, historia krótsza niż 4 lata, mniej niż 5 analityków.
8. Wynik filaru = suma / 55; ranking całej listy, do portfela top 20–30.

## Pytania powtórkowe
1. Dlaczego historia gotówki operacyjnej ma 10 pkt, a jej prognoza tylko 5?
2. Za co ALAB stracił 2 punkty w prognozach przychodów mimo dynamiki 40%?
3. Dlaczego Tesla dostała tylko 2 pkt za EPS 2y przy dynamice 30%?
4. Kiedy spadek dynamiki prognoz nie jest rewizją w dół?
5. Dlaczego Trela porównuje marżę Tesli z Nvidią, a nie z Fordem?
6. Czym różni się `Revenue (TTM)` od `Annual Actual Revenue`?

## Niepewne – do sprawdzenia
- META, CFO 2y Est: w mowie „ze cztery" (01:52:18), w Excelu 3,5 – przyjęto Excel.
- ALAB, wynik: slajd 00:44:16 pokazuje 86% (EPS TTM = 5), po korekcie 85% (EPS TTM = 4).
- TSLA, Revenue Est.: w mowie „trzy, cztery" (01:07:13), w Excelu 3. NVO marża: „siedem, może sześć", w Excelu 6.
- NVO, Cash from Op. = 5: Trela nie uzasadnił, dlaczego 5, a nie 10, skoro gotówka rośnie (01:26:29).
- ALAB, dynamika prognoz CFO: transkrypcja niejasna („36"/„66", 00:39:22), slajd nieczytelny.
- Przykładowe progi automatu: <10% → 0 pkt, 10–13% → 2, 13–15% → 3 (00:51:38) – tylko ilustracja z mowy, nie oficjalna skala.
- Liczby tylko z nagrania: Tesla przychody +160%/5 lat i −3% od szczytu, EPS −60% od szczytu; META EPS +80%/5 lat; ALAB EPS +1600%, strata −80 mln → zysk ok. 200 mln; marża Forda 3%; kapitalizacja ALAB ok. 20 mld USD.
- Listy porównawcze na slajdach 00:33:18, 01:13:00, 01:50:33 – drobny druk, odczyty innych spółek pominięto.

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
