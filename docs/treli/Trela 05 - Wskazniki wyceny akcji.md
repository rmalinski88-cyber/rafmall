---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 5. Wskaźniki wyceny akcji (spotkanie live 5), 8 kwietnia 2026, ok. 2 h 08 min"
status: do przejrzenia
---
# Trela 05 – Wskaźniki wyceny akcji (spotkanie 5)

## W skrócie
Wycena to trzeci filar po zyskowności i fundamentach: sprawdza się ją tylko dla spółek, które przeszły dwa pierwsze. Wg Treli nie liczy się sama wartość wskaźnika, tylko to, gdzie jest dziś względem własnej historii tej spółki (5–10 lat, mediana krocząca z 3 lat). Trzy wskaźniki „twardej" wyceny (P/S, P/E, P/CFO – wszystkie z prognozą na 2 lata) mówią, czy jest tanio czy drogo, a upside i kierunek zmian ceny docelowej mówią, czy to dobry moment. Dokładnych progów punktowych Trela na tym spotkaniu nie podał – przykłady w Excelu przeniósł na spotkanie 6.

## Najważniejsze koncepty

### Miejsce wyceny (00:02:09)
- Kolejność: zyskowność → fundamenty (bezpieczeństwo finansowe) → dopiero wycena. Spółki niezyskownej albo zagrożonej bankructwem nie wycenia się wcale.
- DCF (discounted cash flow – wycena przez zdyskontowane przyszłe przepływy pieniężne) Trela odrzuca: wymaga zgadywania stóp procentowych na ok. 15 lat (00:03:25).

### P/S Forward 2y – wskaźnik główny (00:06:55)
- Price to Sales (P/S) = cena akcji do przychodu na akcję: ile dolarów płacisz w cenie akcji za 1 dolara przychodu.
- Wersja zwykła bierze przychody z ostatniego roku fiskalnego, więc jest spóźniona. „Forward" podstawia prognozę. Trela używa wersji z prognozą na 2 lata naprzód (w Scrabie: `PS Ratio (2-Year Forward)`, dostępna w darmowym planie Basic). Wersję na 1 rok ignoruje (01:05:05).
- P/S spada, gdy spada kurs albo gdy rośnie prognoza przychodów (00:56:34).
- Wartości nominalnej nie porównuje się między spółkami ani z branżą czy indeksem. Różne modele biznesowe mają trwale różne poziomy (ARM z opłatami licencyjnymi vs Broadcom ze sprzedażą jednorazową) (00:10:02, 00:57:47).

### Jak czytać wykres wskaźnika (00:14:40, 00:34:00)
- Okno 5 albo 10 lat; 3 lata to za mało. Wybierasz to okno, w którym widać stabilny, powtarzalny zakres (00:21:19, 00:38:51).
- „Drogo" i „tanio" to nie pojedyncze historyczne maksimum/minimum, tylko strefy, do których wskaźnik dochodził wielokrotnie. Wyznaczenie jest przybliżone i częściowo uznaniowe (00:39:25).
- Mediana krocząca z 3 lat (w Scrabie „Time Based Medians → 3Y"): dłuższa jest zbyt wygładzona, krótsza zbyt poszarpana (00:47:50, 01:52:41).
- Dotknięcie mediany = uczciwa wycena i wg Treli w praktyce dobry moment na zakup; zdarza się mniej więcej raz na kwartał. Skrajne dołki zdarzają się ok. raz na 2 lata i nie warto na nie czekać (00:35:58).
- Kanałów skośnych się nie rysuje – wycena ma górną i dolną granicę (01:06:34).
- Stale rosnąca mediana jest w porządku tylko wtedy, gdy rośnie też prognozowana dynamika przychodów. Stale spadająca mediana to zła informacja (inwestorzy płacą coraz mniej) (00:43:01, 00:59:54).

### Analiza krzyżowa – jedyny wyjątek (00:16:42, 00:38:39)
Porównanie nominalnego wskaźnika z konkurentami ma sens tylko wtedy, gdy spółka jest na giełdzie zbyt krótko (ok. roku), żeby wyznaczyć własny zakres. Wynik to „niedo-/przewartościowana względem konkurencji", a nie „tania/droga".

### Wskaźnik pomocniczy: P/S 2y ÷ dynamika przychodów (00:25:10)
- Własna metryka Treli w Scrabie (`PS 2y / Rev Growth`): P/S Forward 2y podzielone przez prognozowany średni roczny wzrost przychodów w 2 lata.
- Dodaje kontekst, gdy samo P/S jest niejednoznaczne: wysokie P/S może być uzasadnione skokiem prognozowanej dynamiki. Bez punktów w modelu (wymaga płatnego planu Advanced); bez niego można patrzeć na oba wykresy osobno (01:09:12).
- Gdy P/S mówi „drogo", a wskaźnik z dynamiką „niedrogo": pierwszeństwo wersji z dynamiką tylko wtedy, gdy znasz branżę i wiesz, że wzrost jest trwały; w przeciwnym razie zostań przy zwykłym P/S (01:02:13).

### P/E Forward 2y i P/CFO Forward 2y (01:20:07)
- P/E (cena do zysku na akcję) z prognozą na 2 lata: czytany identycznie jak P/S – względem własnej historii i mediany 3-letniej. W Scrabie `PE Ratio (2-Year Forward)`, plan Basic.
- P/CFO (cena do gotówki z działalności operacyjnej na akcję): Scrab ma tylko wersję wsteczną `Price to CFO Per Share`. Wersję forward trzeba zbudować jako własną metrykę (plan Advanced); bez tego zostaje wersja wsteczna (01:21:53).
- EV/EBITDA (wartość przedsiębiorstwa do zysku operacyjnego przed amortyzacją) Trela w tej edycji odpuszcza: brak prognozy EBITDA w danych, więc wskaźnik zawsze patrzy wstecz (01:24:26).

### Upside i Price Target – wycena „miękka" i timing (01:27:05)
- Price target = średnia cena docelowa analityków na 12 miesięcy (termin graniczny, nie konkretna data). Upside = o ile procent cena docelowa jest wyżej od kursu.
- Upside to wskaźnik timingowy: mówi, czy to dobry moment. Też czytany względem własnej historii spółki (5–10 lat), nie nominalnie między spółkami (01:31:41, 01:54:52).
- Upside spada na dwa sposoby: kurs dogania cenę docelową albo analitycy tną cenę docelową. Dlatego kierunek zmian price targetu ocenia się osobno (01:36:18, 01:40:16).
- Niski upside nie jest powodem do sprzedaży dobrej spółki, ale nowej spółki przy niskim upside się nie kupuje; upside ponad 100% to zwykle mała, zmienna spółka (01:46:47, 01:53:11).
- Dwie twarde reguły Treli: nie trzymać spółek, którym spadają prognozy przychodów, ani tych, którym spada cena docelowa (01:36:40).
- Wyjątek: „techniczne" cięcie ceny docelowej po dużym spadku kursu, gdy fundamenty i prognozy się nie pogarszają, a upside wyskoczył na poziom niewidziany w historii. Długi spadek (miesiące) to już trend, nie cięcie techniczne (01:53:53, 02:02:53).

### Trzy kwestie do przemyślenia (slajd 02:04:54)
1. Czy fundamenty nie powinny być zero-jedynkowe (bezpieczna / nie)?
2. Czy wycena powinna być częścią modelu punktowego, czy osobnym testem „czy to dobry moment" po wyborze top 30?
3. Czy przy horyzoncie wieloletnim bieżąca wycena w ogóle ma duże znaczenie?
Odpowiedzi mają dać backtesty (testy reguł na danych historycznych) na kolejnych spotkaniach.

## Reguły i progi liczbowe
Trela nie podał progów liczbowych przeliczających odczyt na punkty; poniżej wszystko, co padło.

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu | Źródło |
|---|---|---|---|
| P/S Forward 2y | Pozycja względem własnego zakresu z 5–10 lat i mediany kroczącej 3Y: nisko = tanio, przy medianie = uczciwie, przy górnej strefie = drogo, ponad zakres = bańka | maks. 10 | slajd Excel 00:59:12; reguła z nagrania 00:14:40 |
| P/E Forward 2y | Tak samo jak P/S | maks. 10 | slajd Excel 01:26:36; nagranie 01:20:20 |
| P/CFO Forward 2y | Tak samo; cena ÷ prognoza CFO na akcję za 2 lata | maks. 10 | slajd Excel 00:59:12, slajd Scrab 01:23:03 |
| UPSIDE | Pozycja względem własnej historii; im bliżej górnej strefy, tym lepiej; blisko zera/dolnej strefy = zły moment | maks. 20 | slajd Excel 00:59:12; nagranie 01:38:09 |
| Target Price (kierunek rewizji) | Rośnie = dobrze; płaski = 5 pkt; spada = traktować zero-jedynkowo, spółka do usunięcia, chyba że cięcie techniczne | maks. 10 (na czerwono – do dyskusji) | slajd Excel 00:59:12; „5 za płaski" z nagrania, niepotwierdzone slajdem – sprawdź 01:53:34 |
| TOTAL Value | Suma pięciu kolumn ÷ 60 | 60 pkt | Excel: X = SUM(S:W)/60 |
| Wynik łączny | Średnia z trzech filarów w procentach: (Growth + Funds + Value) ÷ 3 | – | Excel: Y = (K+R+X)/3 |
| Upside ujemny / przy dolnej granicy | Nie kupować teraz, wziąć kolejną spółkę z rankingu | – | nagranie 02:00:44 |
| Spadek price targetu przez miesiące | Sygnał wyjścia (Oracle: ponad 5 miesięcy = trend) | – | nagranie 01:57:08, 02:02:53 |
| Częstotliwość sprawdzania price targetu | Raz na 2 tygodnie do raz na miesiąc; wcześniej pada też „raz na kwartał wystarczy" | – | z nagrania, niepotwierdzone slajdem – sprawdź 01:44:35 |

## Przykłady z lekcji
- **ARM** – P/S 2y Fwd 20,36, mediana 3Y 21,81 (slajd 00:39:33). Trela: drogo ok. 28–30, bardzo tanio ok. 16; uczestnik proponował 20 i Trela to przyjął – dowód, że strefy są przybliżone.
- **Astera Labs (ALAB) vs Broadcom (AVGO), Marvell** – ALAB 9,03 wobec AVGO 8,2 (slajd 00:19:18); ilustracja analizy krzyżowej przy krótkiej historii.
- **Micron (MU)** – P/S 2y Fwd 2,69 przy medianie 2,62; w 10 latach max 5,09, min 0,68 (slajd 00:34:51). Odczyt ok. 5 = bańka. Prognozowany wzrost przychodów 79,92%, więc `PS 2y / Rev Growth` = 0,03, najniżej w historii. Upside 44,35%, cena docelowa 545,05 przy kursie 406,94, 41 analityków (slajdy 01:41:24, 01:42:09).
- **Broadcom** – P/S 8,2 poniżej mediany 10,56; P/E 2y Fwd 15,16 przy medianie 21 (slajdy 00:45:45, 01:22:15): tanio na obu.
- **Microsoft** – cena docelowa ok. 7,7% poniżej szczytu przy kursie ok. 31% poniżej szczytu, upside 57,14% (slajd 01:48:36): przykład cięcia prawdopodobnie technicznego.
- **Oracle, GameStop** – Oracle: cena docelowa spada od listopada 2025, czyli trend, nie technika. GameStop: wzrost bez podstaw przy małej kapitalizacji, stąd wymóg dużych spółek i pomijanie momentum (01:12:59, 02:01:53).

## Narzędzia
- **Scrab → Master Chart**: metryki `PS Ratio (2-Year Forward)`, `PE Ratio (2-Year Forward)`, `Price to CFO Per Share`, `Price Target`, `Price Target Upside`, `Revenue Average Estimated Annual Growth in Next 2 Years`. Zakresy 5Y/10Y lub własny zakres dat (tak wycina się anomalie w danych, 00:28:04). Scrab ma wkrótce dodać odchylenie standardowe i regresję liniową (00:48:09).
- Trzy kropki przy metryce → `Time Based Medians` → `3Y`. Opcje `Max`/`Min` i `Horizontal Channel` Trela uznaje za mało przydatne (01:16:52).
- **Custom Metrics** (plan Advanced, limit 5 metryk): `New Metric`, Display Format = Number, formuła `A / B`.
  - `PS 2y / Rev Growth`: A = PS Ratio (2-Year Forward), B = Revenue Average Estimated Annual Growth in Next 2 Years (00:31:39).
  - `P/CFO 2y Forward`: A = Price, B = CFO per Share Estimates for 2 Fiscal Years Ahead (slajd 01:23:03).

## Co z tego zastosuję w skanerze
1. Bramka: filar wyceny liczony tylko dla spółek, które przeszły zyskowność i fundamenty.
2. Dla P/S, P/E i P/CFO (forward 2y): pobierz 5–10 lat historii → policz medianę kroczącą 3Y i pozycję bieżącego odczytu w historycznym rozkładzie (np. percentyl – dopisek Claude'a, Trela mówi o „strefach") → etykieta tanio / uczciwie / drogo / bańka → punkty 0–10. Skalę progów trzeba ustalić samemu lub po spotkaniu 6.
3. Historia krótsza niż ok. 1–2 lata → zamiast historii porównanie nominalne z 2–3 konkurentami, z flagą „niska pewność".
4. Wskaźnik pomocniczy P/S 2y ÷ wzrost przychodów 2y: liczony jako kontekst (bez punktów); flaga, gdy rozjeżdża się z P/S.
5. Upside: pozycja w historii własnej spółki → 0–20 pkt; upside ujemny lub przy dolnej strefie → blokada „nie kupuj teraz"; upside > 100% → ostrzeżenie.
6. Price target: trend rosnący = 10, płaski = 5, spadający = 0 i flaga „do usunięcia"; wyjątek do ręcznego sprawdzenia, gdy kurs spadł mocno, prognozy przychodów/zysków nie spadają, a upside jest na historycznym maksimum.
7. Twardy filtr: spadające prognozy przychodów → spółka poza portfelem.
8. Wynik: Value = suma ÷ 60; łączny = średnia z trzech filarów w procentach.

## Pytania powtórkowe
1. Dlaczego Trela używa P/S z prognozą na 2 lata, a nie zwykłego P/S?
2. Kiedy wolno porównywać P/S między spółkami?
3. Z ilu lat liczy się medianę i dlaczego ma być krocząca?
4. Na jakie dwa sposoby może spaść P/S, a na jakie dwa upside?
5. Czym różni się informacja z upside od informacji z kierunku zmian price targetu?
6. Kiedy spadek ceny docelowej można uznać za techniczny?

## Niepewne – do sprawdzenia
- Brak konkretnych progów punktowych dla kolumn wyceny – Trela przesunął przykłady w Excelu na spotkanie 6 (02:02:28).
- Nagłówek Excela „TOTAL of TOTALS (209 pkt)" nie zgadza się z sumą filarów 55 + 40 + 60 = 155; formuła to średnia z trzech procentów.
- Astera Labs: „raz było 26, dziś 9" – 26 tylko z mowy (00:18:34); 9,03 potwierdza slajd.
- Skuteczność prognoz analityków „ponad 70%, 75–77%" – tylko z mowy (01:43:49).

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
