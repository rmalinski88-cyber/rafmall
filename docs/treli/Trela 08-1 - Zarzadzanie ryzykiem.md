---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – 8-1. Zarządzanie ryzykiem (materiał dodatkowy po 8. spotkaniu), koniec kwietnia 2026, ok. 70 min"
status: do przejrzenia
---
# Trela 08-1 – Zarządzanie ryzykiem (materiał teoretyczny)

## W skrócie
Lekcja teoretyczna o budowie portfela: ryzyko to zmienność, a celem jest jak najlepszy stosunek zysku do ryzyka. Ryzyka rynkowego (systemowego) nie da się usunąć, ale ryzyko pojedynczych spółek można ograniczać trzema dźwigniami: dywersyfikacją geograficzną i sektorową, liczbą spółek oraz proporcjami pozycji. Trela przechodzi przez miary: beta, CAPM, Sharpe, Sortino, odchylenie standardowe, VaR, Expected Shortfall i Hierarchical Risk Parity.

## Najważniejsze koncepty

### Czym jest ryzyko (00:00:42)
- Ryzyko = niepewność przyszłego wyniku = wahania i obsunięcia kapitału = **zmienność**. Im szerszy możliwy rozrzut wyniku, tym większe ryzyko.

### Dwa rodzaje ryzyka (00:03:39)
- **Systemowe** – wynika z samego bycia na giełdzie (wojna, lockdown 2020); dywersyfikacja go nie usuwa. W teorii = ryzyko indeksu S&P 500.
- **Pozasystemowe** – dotyczy jednej spółki lub branży (słabe wyniki, oszustwo księgowe, spadek ceny ropy dla spółek naftowych). To nim da się zarządzać.

### Trzy sposoby zarządzania ryzykiem (00:07:48)
1. **Dywersyfikacja geograficzna i sektorowa** – traktowane łącznie. Liczy się nie giełda notowania, tylko to, skąd spółka ma większość przychodów (00:10:16).
2. **Odpowiednia liczba spółek** – krzywa ryzyka wypłaszcza się; przy ok. 60 spółkach zostaje już tylko ryzyko systemowe, a portfel zachowuje się jak S&P 500 (ryzyko i zysk), więc znika szansa na pobicie rynku (00:18:12).
3. **Właściwe proporcje** – dwie pozycje po 100 USD, zmienność 20% i 40%; pierwsza +20, druga −40 daje −10% mimo skuteczności 50%. Spółka bardziej zmienna powinna ważyć mniej (00:11:15).

### Beta i CAPM (00:21:19)
- **Beta** – przelicznik: o ile zmieni się kurs spółki lub portfela, gdy S&P 500 zmieni się o jednostkę. Beta 1,2: rynek +10% → spółka +12%, rynek −10% → −12%. Beta portfela = suma bet spółek pomnożonych przez wagi.
- Slajd: beta > 1 = bardziej zmienna niż rynek; < 1 = mniej; > 0 = korelacja dodatnia, < 0 = ujemna.
- **CAPM** (Capital Asset Pricing Model, model wyceny aktywów kapitałowych): `oczekiwany zwrot = rf + beta × (rm − rf)`, gdzie rf = stopa wolna od ryzyka (rentowność obligacji USA), rm = oczekiwany zwrot rynku. Na slajdzie: rm = średni zysk S&P 500 z 12 miesięcy (00:23:27).

### Sharpe i Sortino (00:29:19)
- **Sharpe Ratio** = (Rp − Rf) / σp, czyli nadwyżka zysku nad stopą wolną od ryzyka podzielona przez odchylenie standardowe. Mierzy zysk na jednostkę ryzyka; lepsze kryterium wag niż sam oczekiwany wzrost (upside).
- Wada: karze także wahania w górę.
- **Sortino Ratio** = (Rp − rf) / σd, gdzie σd = odchylenie tylko w dół (downside deviation). Według Treli lepsze dla inwestora indywidualnego w akcje (00:32:16).
- Czasem lepiej wybrać niższy zysk: 18% przy ryzyku 20% bije 20% przy ryzyku 40%.

### Odchylenie standardowe – sigma, STD (00:38:35)
- Miara odrywania się kursu od średniej; baza pozostałych wskaźników. Liczona historycznie: dziennie, miesięcznie lub rocznie.
- 1 sigma: 68% szans, że kurs zostanie w tym zakresie (po 34,1% w górę i w dół); 2 sigma: 95%; 3 sigma: 99,7% – w praktyce nieużywane.

### Value at Risk i Expected Shortfall (00:45:41)
- **VaR** (wartość zagrożona) – potencjalna strata w danym okresie z danym prawdopodobieństwem. Miesięczny VaR 5% = 20%: tylko 5% szans, że strata w miesiącu przekroczy 20%.
- VaR spółki A 20% i B 30% → B jest o 50% bardziej ryzykowna, więc powinna ważyć mniej.
- Z VaR spółek liczy się VaR portfela i porównuje z S&P 500. Jeśli poziom jest nieakceptowalny – przesunąć kapitał z najbardziej ryzykownych pozycji do mniej ryzykownych (00:49:40).
- **Expected Shortfall (ES)** – ile średnio wyniesie strata, gdy zdarzy się te 5% najgorszych przypadków. VaR podaje minimalną stratę w takim scenariuszu, ES średnią rzeczywistą. Spółka z niższym VaR może mieć dużo gorszy ES.

### Proporcje: samo ryzyko to za mało (00:58:15)
- VaR i ES oceniają, czy ryzyko portfela jest akceptowalne. Do ustalania wag lepszy jest wskaźnik zysk/ryzyko (np. Historical Sortino); powyżej 1 = zysk większy niż ryzyko.

### Hierarchical Risk Parity – HRP (01:02:11)
- Krok 1: algorytm grupuje spółki w klastry według korelacji kursów (nie według deklarowanej branży).
- Krok 2: wewnątrz klastra spółka o wyższym ryzyku dostaje mniejszą wagę (przykład: Microsoft VaR 9% i Oracle 18% → więcej Microsoftu).
- Wagi przelicza się przy każdym rebalansowaniu.
- Wg Treli HRP zwykle daje lepsze wyniki niż wagi po Sortino czy VaR, ale wymaga backtestu na własnej strategii.

## Reguły i progi liczbowe

| Wskaźnik / kryterium | Reguła lub próg | Punkty w modelu (jeśli podano) | Źródło (slajd/nagranie + czas) |
|---|---|---|---|
| Liczba spółek | Ryzyko przestaje spadać przy ok. 40 spółkach: ok. 40% (tylko USA), ok. 30% (globalnie) | – | slajd 00:15:36 |
| Liczba spółek | 20–30 spółek zostawia szansę pobicia rynku | – | nagranie 00:20:58 (z nagrania, niepotwierdzone slajdem – sprawdź 00:20:58) |
| Liczba spółek | ok. 60 = zostaje tylko ryzyko systemowe, wynik jak S&P 500 | – | slajd 00:18:12 |
| Beta | > 1 bardziej ryzykowna niż rynek; < 1 mniej | – | slajd 00:21:19 |
| Sigma | 1σ = 68%, 2σ = 95%, 3σ = 99,7% | – | slajd 00:38:35, 00:43:51 |
| Wagi wg VaR | Waga odwrotnie proporcjonalna do VaR (VaR 2× wyższy → pozycja o połowę mniejsza) | – | nagranie 00:57:26 (z nagrania, niepotwierdzone slajdem – sprawdź 00:57:26) |
| Zysk/ryzyko | > 1 = zysk większy niż ryzyko | – | nagranie 01:00:10 (z nagrania, niepotwierdzone slajdem – sprawdź 01:00:10) |

Lekcja nie podaje punktów do modelu punktowego.

## Przykłady z lekcji
- **USA vs rynki rozwinięte poza USA (MSCI EAFE), 1970–2013**: 100% S&P 500 – zmienność ok. 17%, zwrot ok. 8,5%; 100% EAFE – ok. 21,5% i ok. 9,2%; miks 16% EAFE + 84% S&P 500 miał niższą zmienność i wyższy zwrot niż samo S&P 500 (00:13:04).
- **Miesięczny VaR 5% (5 lat wstecz), Scrab**: TSLA 24,66%, MELI 20,85%, AMZN 14,86%, MSFT 9,25%, BRK-A 8,96%. Wniosek: MSFT i BRK można mieć wartościowo ok. dwa razy więcej niż Tesli przy tym samym ryzyku (00:54:53).
- **Zysk na jednostkę ryzyka**: Microsoft ok. 1,13, Berkshire ok. 0,66, Mercado Libre ok. 1 (01:00:47).

## Narzędzia
- Scrab: wykres wskaźnika `Monthly Value at Risk (VaR) 5% (5Y Lookback)` dla kilku spółek naraz.
- Wymienione bez pokazu: Historical Sortino, Sharpe, Expected Shortfall, Hierarchical Risk Parity. Klikanie odłożone do części praktycznej.

## Co z tego zastosuję w skanerze
- Spółki w portfelu → policz liczbę → ostrzeżenie poniżej 20 (koncentracja) i powyżej ok. 40–60 (portfel staje się indeksem).
- Spółka → kraj/region głównych przychodów i sektor → ostrzeżenie, gdy jeden region lub sektor dominuje.
- Spółka → miesięczny VaR 5% (5 lat) → waga wstępna odwrotnie proporcjonalna do VaR.
- Portfel → VaR ważony → porównanie z VaR S&P 500 → flaga „ryzyko wyższe niż rynek".
- Spółka → Sortino (zysk / odchylenie w dół) → wyższa waga przy wyższym wyniku; flaga przy wyniku poniżej 1.
- Wariant docelowy: klastry według korelacji kursów → wewnątrz klastra waga odwrotna do ryzyka (HRP) → porównać backtestem z wagami po Sortino i VaR.

## Pytania powtórkowe
1. Czym różni się ryzyko systemowe od pozasystemowego i które da się ograniczyć?
2. Dlaczego 60 spółek w portfelu to według Treli za dużo?
3. Co oznacza beta 1,2 przy spadku rynku o 10%?
4. Czym Sortino różni się od Sharpe'a i dlaczego jest lepszy dla inwestora w akcje?
5. Jak odczytać „miesięczny VaR 5% = 20%" i co dodaje Expected Shortfall?
6. Jakie są dwa kroki Hierarchical Risk Parity?

## Niepewne – do sprawdzenia
- Zalecany zakres 20–30 spółek pada tylko w mowie; wcześniej Trela wymienia też 20–35 i 30–40 (00:17:33–00:21:04).
- Wartości zysk/ryzyko (MSFT 1,13; BRK 0,66; MELI ok. 1) – brak kadru ze slajdem 16; nie wiadomo na pewno, czy to Historical Sortino (01:00:10–01:01:00).
- Rok publikacji HRP: transkrypcja niejasna („2016"?) (01:02:41).
- Przykład ES dla spółek A i B (średnio −80% vs −35%) jest w nagraniu poplątany; sens przyjęty według slajdu (00:52:00–00:54:30).

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
