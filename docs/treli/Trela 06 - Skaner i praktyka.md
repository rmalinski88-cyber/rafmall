---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 6. Skaner i praktyka (spotkanie live 6), 15 kwietnia 2026, ok. 2 h"
status: do przejrzenia
---
# Trela 06 – Skaner i praktyka: filtry i punktowanie wyceny (spotkanie 6)

## W skrócie
Spotkanie bez nowej teorii: Trela pokazuje, skąd brać spółki do analizy (skaner w Scrab), ustawia na żywo filtry i zawęża ok. 560 spółek do ok. 50, a potem ręcznie punktuje w Excelu pięć z nich (ServiceNow, Axon, Datadog, DoorDash, AppLovin). Po raz pierwszy wypełnia filar wyceny (P/S, P/E, P/CFO, Upside, Target Price). Główny wniosek: skaner ma dać listę **dobrych** spółek, a wycena i upside mówią tylko o **momencie** zakupu; spadający Price Target potrafi przekreślić nawet bardzo tanią spółkę.

## Najważniejsze koncepty

### Dwie drogi do listy spółek (00:01:16)
- **Top-down** („romantyczna"): czytasz o trendach i branżach, szukasz beneficjentów, dopiero potem liczysz ich w modelu. Wg Treli lepsza, bo daje kontekst.
- **Bottom-up** (skaner): najpierw liczby – filtr wyłapuje spółki spełniające warunki brzegowe, dopiero potem czytasz, czym się zajmują. Szybsza.
- Wada sztywnych filtrów: spółka przekraczająca próg o 0,1 znika z listy i nigdy się o niej nie dowiesz (przykłady: MercadoLibre, Cloudflare odpadły na Ohlsonie) (00:28:36).

### Po co w ogóle zyskowność (00:06:08)
- Od 1 kwietnia do 14 kwietnia 2026 rynek odbijał cały, ale spółki z najwyższą oceną zyskowności odbiły najmocniej (ALAB ok. +40%, META ok. +12–14%, NVO ok. +7%, MSFT ok. +5%, TSLA ok. −5%).
- Działa to w obie strony: najlepsze spółki mocniej też spadają (większa zmienność).

### Skaner ≠ wycena (00:26:26)
- **Upside** (potencjał wzrostu do ceny docelowej analityków) mówi, czy to dobry moment, a nie czy spółka jest dobra. Dlatego nie jest filtrem odcinającym, najwyżej kolumną do sortowania.
- Zwroty z kursu (np. „1 Month Price Returns") – nie używać w skanerze; kurs wyrwany z kontekstu nie jest informacją.
- Filtra na wzrost EPS (zysk na akcję) Trela nie dodaje: wyrzuciłby młode spółki, którym model potrafi „wybaczyć" brak zysków przy świetnych przychodach i gotówce (00:22:21).

### Punktowanie przez porównanie
- Punkt odniesienia: ETF **SPY** (S&P 500) albo ostrzejszy **QQQ** (Nasdaq 100) oraz grupa „topowych" spółek (NVDA, AVGO, AMD, ARM, TSM). Poziom benchmarku ≈ połowa punktów, poziom topu ≈ maksimum (00:43:26).
- Kary: za trend spadkowy prognoz, za niestabilność (skoki), za start z ujemnych wartości (procenty liczone od straty są mylące – najpierw sprawdź linię zera) (01:39:54).
- Dokładna liczba punktów jest mniej ważna niż **ta sama surowość dla wszystkich spółek** – liczy się kolejność w rankingu (01:07:08).
- Kolejność: zyskowność → fundamenty → wycena. Słaba zyskowność lub słabe fundamenty = koniec analizy, wyceny się nie liczy.

### Wycena: tanio względem własnej historii
- Każdy wskaźnik wyceny ogląda się na wykresie 5- i 10-letnim wraz z medianą (w legendzie „3Y Median") i ocenia, gdzie jest dzisiejszy odczyt.
- Dodatkowo wskaźnik „zdyskontowany" o prognozowany wzrost: własne (custom) metryki Treli **PS 2y / Rev Growth** i **PE 2y / EPS Growth** (P/E podzielone przez „EPS Average Estimated Annual Growth in Next 2 Years"). W Scrab pojawił się wbudowany **PEG Ratio (2-Year Forward)**; Trela nie jest pewien, czy „2-Year Forward" dotyczy tam P/E, czy wzrostu – ma to wyjaśnić (00:56:31).

### Price Target jako warunek „być albo nie być" (01:00:28)
- Wysoki upside może zniknąć na dwa sposoby: kurs dojdzie do celu albo analitycy obniżą cel. Spadający Price Target (cena docelowa) = czerwona strefa.
- Lepszy mały upside przy rosnącym celu niż ogromny upside przy celu ciętym. Hasło: „lepiej stracić okazję niż pieniądze".
- Najważniejszy w modelu jest jednak wzrost (growth); przy przytłaczających argumentach można zrobić wyjątek (01:14:55).

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| P/S Forward 2y (PS Ratio (2-Year Forward)) | najniżej od 10 lat / w historii | 10/10 | slajd 01:47:33 (NOW) + nagranie 00:53:41 |
| P/S Forward 2y | odczyt lekko powyżej mediany (APP: 11,32 vs mediana 9,49) | 5–6; po uwzględnieniu PS 2y / Rev Growth poniżej mediany → 7 | slajd 01:50:36, nagranie 01:48:35–01:51:20 |
| P/S Forward 2y | 8–10 dopiero przy dołkach z dłuższej historii | 8–10 | nagranie 01:50:45 |
| P/E Forward 2y (PE Ratio (2-Year Forward)) | najniżej od 10 lat | 10/10 | slajd 01:47:33, nagranie 00:55:50 |
| P/E Forward 2y | wyraźnie pod kanałem z 5 lat, ale nie historyczne minimum (APP) | ok. 9,5 (niepewne); 10 przy P/E ok. 12 | nagranie 01:51:23–01:53:12 (niepotwierdzone slajdem) |
| P/CFO (Price to CFO Per Share) | najniżej w historii | 10/10 | slajd 01:47:33, nagranie 01:00:09 |
| P/CFO | okolice mediany, dolny zakres z 2 lat (APP) | 6–6,5 | nagranie 01:53:32 (niepotwierdzone slajdem) |
| Upside (Price Target Upside) | najwyższy w historii spółki (NOW 100,75%) | 20/20 | slajd 00:35:27, nagranie 01:00:30 |
| Upside | ok. 70–75% typowego zakresu, anomalie odrzucone (APP 50,56%) | 15/20 | slajd 00:35:27, nagranie 01:54:14 |
| Target Price (trend Price Target) | cel ścięty ok. 25% od początku 2026 i dalej spada (NOW) | 0/10 + spółka „nie do portfela" | nagranie 01:01:04 |
| Target Price | cel obniżony po spadku kursu, ale od lutego stoi (APP) | 7/10 | slajd 01:56:51 (komórka W13 = 7) |
| Target Price – reguła twarda | spadek celu do ok. 5% od szczytu tolerowany; więcej = nie kupować / sprzedać | must-have | slajd 01:12:18 (rysunek „−5%") |
| TOTAL Value | suma S:W / 60 | % | Excel X2 |
| Wynik łączny | średnia z trzech procentów (growth, funds, value) | % | Excel Y2 |
| Rev. est. growth 2y (10 pkt) | 19–20% → 7,5; 22% rosnące → 8; ok. 30% → 8; 33,7% rosnące → 9; 10 dla poziomu NVDA/AVGO | 7,5–10 | slajdy 00:42:27, 01:20:12, 01:41:03 |
| EPS 2y growth (5 pkt) | poziom S&P (17,9%) → 2,5; 20% → 3,5; 27% → 4; 40% → 4,5 | 2,5–4,5 | slajdy 00:45:12, 01:22:00, 01:41:33 |
| EPS 5y growth (5 pkt) | 3% → 0; 4,65% → 1; 19,5% spadające → 3; 33% → 4,5; 38% rosnące → 5 | 0–5 | slajdy 00:43:39, 01:21:00, 01:30:39, 01:35:06 |
| CFO 2y est. (5 pkt) | 7% → 1; ok. 15–17% → 2; poziom S&P → 2,5; lekko ponad → 3; 41% → 4; top to 50–60% | 1–4 | slajdy 00:46:09, 00:46:51; nagranie 01:37:43, 01:43:36 |
| EBITDA Margin (10 pkt) | ok. 0–2% → 1; 11,6% rosnąca → 2; 19,6% rosnąca → 7; 75,7% rosnąca → 10 | 1–10 | slajdy 00:47:21, 01:31:21, 01:37:54, 01:43:57 |
| Ohlson (10 pkt) | ok. 0% → 10; ok. 1% → 8 | 8–10 | slajd 01:25:09, 01:26:12 |
| Altman (10 pkt) | > 3–3,5 bezpiecznie; < 1,5 źle; 2,04 → 5; 3,3 spadający → 7 | 5–7 | slajd 01:06:48, nagranie 01:06:38 |
| Debt/Assets (5 pkt) | ok. 9% → 4; 27% rosnące → 2; > 30% → 1; ok. 40% i więcej → 0 | 0–4 | slajdy 00:53:06, 01:26:12; nagranie 01:26:12 |
| Interest Coverage (5 pkt) | ujemne → 0; 20 lub 84 → 5 | 0/5 | slajd 00:52:51, 01:27:27 |
| CFO/Debt (5 pkt) | 0,11 → 2; 0,3 → 5; > 1 → 5 | 2–5 | nagranie 00:53:02, 01:26:58, 01:47:27 |
| Quick Ratio (5 pkt) | ok. 1 → 4,5; 2,29 → 5 | 4,5–5 | slajdy 00:53:30, 01:27:15 |
| Próg „top 20" zyskowności | 75% – na granicy; 68% i mniej – poza | – | nagranie 00:47:06, 01:25:00 |

## Filtry skanera krok po kroku

Widok: Scrab → **Screener** → „New Screener" → „Add Criteria" → „Find Stocks". Pole z lewej to minimum, z prawej maksimum.

| Krok | Metryka (jak na ekranie) | Warunek | Po co | Źródło |
|---|---|---|---|---|
| 1 | Company Countries | puste (bez ograniczeń) | perełki spoza USA (Tajwan, Holandia) i tak są notowane w USA | slajd 00:20:18 |
| 2 | Exchanges | = USA (opcjonalnie dodać giełdę niemiecką) | tylko spółki notowane w USA, w tym ADR-y (kwity depozytowe na zagraniczne akcje); brak ADR = mało prognoz i analiz. Odcina ok. 30 tys. spółek | slajd 00:20:18, nagranie 00:12:49 |
| 3 | Sectors, Industries | puste | jak najszersza lista | slajd 00:20:18 |
| 4 | Market Cap (USD) | ≥ 20B (20 mld USD) → **560 spółek** | płynność, pokrycie analityków, kurs bliżej fundamentów. Próg ruchomy: 10–15 mld po bessie, wyżej po wzrostach; z latami rośnie | slajd 00:20:18 |
| 5 | Revenue Average Estimated Annual Growth in Next 2 Years | ≥ 15% → **87 spółek** | warunek twardy: przychody mają rosnąć wyraźnie szybciej niż S&P 500 (SPY dziś 12,28%; w 2023 było ok. 6%) – próg ustawiać nad aktualnym odczytem SPY | slajdy 00:20:48, 00:21:54 |
| 6 | Revenue Number Estimates for 2 Fiscal Years Ahead | ≥ 5 → **74 spółki** | średnia prognoz ma pochodzić od co najmniej 5 analityków | slajd 00:23:18 |
| 7 | Ohlson Score Bankruptcy Probability (TTM) | ≤ 2% → ok. 51 spółek; złagodzone do ≤ 3% → **53 spółki** | odcięcie ryzyka bankructwa. Próg uznaniowy (w materiałach Trela podawał 10%); można filtr pominąć i ocenić Ohlsona, Altmana i dług w Excelu | slajd 00:26:12; liczba dla 2% z nagrania 00:23:26 |
| 8 | Price Target Upside | ≥ −10% → **49 spółek** (próba ≥ 15% dała 33) | nie filtr jakości, tylko kolumna do sortowania malejąco = kolejność analizy (najpierw najpilniejsze okazje) | slajdy 00:34:00, 00:35:27 |
| – | EPS growth, Price Returns | nie dodawać | patrz „Skaner ≠ wycena" | nagranie 00:22:21, 00:26:04 |

Dodatkowe zasady: przy analizie ręcznej progi ostrzejsze, przy automacie luźniejsze (00:24:25). Gdy lista za krótka – najpierw obniżyć Market Cap (ok. 25% spółek więcej). Skaner uruchamiać przy rebalansowaniu: nie częściej niż co miesiąc, nie rzadziej niż co kwartał (00:31:05). Duplikaty klas akcji (GOOGL/GOOG) to ta sama firma – w backtestach usuwać ręcznie.

## Przykłady z lekcji
- **ServiceNow (NOW)**: zyskowność 75%, fundamenty 84%, wycena 83% (10+10+10+20+0), razem ok. 81%. Wszystkie mnożniki najniżej od lat, upside ok. 100%, ale cel analityków cięty → Trela by nie kupował, a posiadając – raczej uciekał.
- **Axon (AXON)**: zyskowność 68% (niestabilna gotówka, marża EBITDA ok. 0 i spada), fundamenty 60% (dług 27% aktywów i rośnie, ujemne pokrycie odsetek) → wyceny nie liczono.
- **Datadog (DDOG)**: 59% zyskowności – prognozy EPS słabsze niż S&P i spadające, marża 2,3% → koniec na zyskowności.
- **DoorDash (DASH)**: 55% – zyski dopiero od roku, prognoza EPS 5-letnia tylko 3% → odpada.
- **AppLovin (APP)**: zyskowność 93%, fundamenty 88%, wycena ok. 75%, razem 85%. Debt/Assets 48% dał 0 pkt i automat by spółkę skreślił, ale Interest Coverage ok. 20 i CFO/Debt 1,12 pokazują, że dług jest bezpieczny – argument za tym, by progu zadłużenia nie traktować jako twardego veta. Trela woli APP (droższa, dużo wyższa zyskowność) niż NOW.

## Narzędzia
- **Screener**: jak w tabeli filtrów; wyniki w „Matching Companies", sortowanie kliknięciem w nagłówek kolumny.
- **Master Chart**: zaznaczasz spółkę i metrykę z listy; kilka spółek naraz (np. NOW + SPY/QQQ + top) do porównań. Porównania kursów – skala procentowa („Price % Change"); pojedyncza spółka – logarytmiczna; liniowa tylko dla wielkości już w procentach (00:10:51).
- Metryki do punktowania: Annual Actual Revenue + Revenue Estimates (Current / Next / 2 Fiscal Years Ahead), analogicznie EPS i CFO per Share, EPS Long Term (5 Years) Growth Estimates, Cash from Operations (TTM), EBITDA Margin (TTM), Altman Z-Score – Nonmanufacturers (TTM), Debt to Assets (Annual), Interest Coverage (TTM), CFO to Debt (Annual), Quick Ratio (Annual), Price Target oraz metryki z tabel wyżej.
- „Dowożenie" prognoz: czy faktyczne przychody (zielona linia) po roku dochodzą do wcześniejszej prognozy (00:39:15).
- **Excel „Model-2026"**: kolumny S–W to wycena, X = suma/60, Y = średnia trzech filarów. Annual = ostatni zamknięty rok fiskalny, TTM = ostatnie 4 kwartały.

## Co z tego zastosuję w skanerze
1. Filtr wstępny: giełda USA ∧ Market Cap ≥ 20 mld USD ∧ prognozowany wzrost przychodów 2y ≥ 15% ∧ liczba prognoz ≥ 5 ∧ Ohlson ≤ 3% → lista ok. 50 spółek.
2. Próg wzrostu przychodów liczyć dynamicznie: odczyt SPY + margines (dziś 12,28% → 15%).
3. W automacie progi luzować (np. Ohlson pominąć, Market Cap niżej) i zostawić selekcję punktacji; twarde odcięcia tracą dobre spółki tuż za progiem.
4. Upside nie jest filtrem – tylko klucz sortowania kolejki do analizy.
5. Punkty wyceny = pozycja bieżącego mnożnika w jego własnym zakresie z 5–10 lat: minimum → 10, okolice mediany → 5–6, z korektą +1 gdy mnożnik podzielony przez wzrost jest pod medianą.
6. Upside → 0–20 pkt wg pozycji w typowym historycznym zakresie upside'u danej spółki (po odrzuceniu anomalii).
7. Veto: Price Target spadł > 5% od szczytu → 0 pkt i flaga „nie kupować / sprzedać"; cel stabilny po jednorazowym cięciu → 7.
8. Wczesne wyjście: zyskowność poniżej progu top 20 (ok. 70–75%) albo słabe fundamenty → nie licz wyceny. Debt/Assets > 40% łagodzić, gdy Interest Coverage i CFO/Debt są wysokie.

## Pytania powtórkowe
1. Jakie pięć filtrów i z jakimi progami zawęża listę z 560 do ok. 53 spółek?
2. Dlaczego Trela nie filtruje po upside ani po wzroście EPS?
3. Skąd wziąć próg wzrostu przychodów i dlaczego nie jest stały?
4. Za co ServiceNow dostał 0 pkt przy 83% za wycenę i co z tego wynika?
5. Jak zamienić odczyt P/S lub P/E na punkty?
6. Dlaczego 48% zadłużenia nie przekreśliło AppLovin?

## Niepewne – do sprawdzenia
- Liczba spółek po Ohlson ≤ 2% (ok. 51) i „cztery więcej" po złagodzeniu – tylko z nagrania (00:23:26–00:24:08); slajd pokazuje 53 przy progu 3%.
- Do jakiej wartości Trela obniżył Market Cap, pokazując „25% więcej spółek" (00:25:01) – nie padło wyraźnie (możliwe 15 mld).
- Punkty APP za P/E (8 → 9 → „połówki", przyjęte 9,5) i P/CFO (6–6,5) – niewidoczne na slajdach; 9,5 i 6,5 zgadzają się z łącznym wynikiem 85% (01:51:23–01:54:09).
- Średnia marża EBITDA dla S&P „37%" (01:38:03) i zadłużenie SPY 26% / 22% (00:52:31, 01:25:54) – tylko z nagrania.
- Debt/Assets NOW: Trela wpisał 4, mówiąc, że maksimum jest dla spółek prawie bez długu (00:52:36) – transkrypcja niejasna co do skali.
- Liczba analityków wyceniających NOW: pada 38 i 48 (01:02:16, 01:03:27).
- Nagłówek Excela „TOTAL of TOTALS (209 pkt)" nie zgadza się z sumą 55+40+60; formuła liczy średnią trzech procentów.

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
