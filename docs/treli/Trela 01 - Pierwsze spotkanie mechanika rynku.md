---
utworzono: 2026-10-13
tags:
  - nauka
  - inwestycje
  - akcje
  - kurs-trela
zrodlo: "Uniwersytet Inwestycyjny 2026 – Tomasz Trela – Pierwsze spotkanie Uniwersytetu Inwestycyjnego, 11 marca 2026, ok. 2 h"
status: do przejrzenia
---
# Trela 01 – Pierwsze spotkanie: mechanika rynku i konto brokerskie

## W skrócie
Spotkanie wprowadzające, bez wskaźników. Trela pokazuje, kto naprawdę handluje na giełdach w USA (algorytmy, ukryte parkiety, wymuszone transakcje) i wyciąga wniosek: w horyzoncie dni–miesięcy nikt nie wie, dlaczego kurs rośnie lub spada, więc nie wolno oceniać decyzji po krótkim wyniku. Jedyna przewaga inwestora indywidualnego to długi horyzont, ostra selekcja spółek i spokój. Na koniec praktyczna ściąga o koncie brokerskim.

## Najważniejsze koncepty

### Po co ta wiedza (00:07:00–00:11:20)
- Wskaźników może się nauczyć każdy. Trudne jest trzymanie się poprawnych decyzji, gdy przez miesiące przynoszą stratę (przykład: bessa 2022, ok. 14 miesięcy spadków).
- Definicje Treli: krótki horyzont = miesiące do kwartałów; długi = lata, od roku–dwóch w górę (00:11:00).

### „Mit Wall Street" (00:11:23)
- Nie ma jednej giełdy. Akcje spółki notowanej na giełdzie macierzystej są jednocześnie handlowane na kilkudziesięciu parkietach.
- Kurs, który widzimy, to po prostu ostatnia cena transakcji zawartej na którymś z nich (00:19:40).

### HFT (00:13:00)
- HFT (high frequency trading) = handel wysokiej częstotliwości, prowadzony przez algorytmy. Firmy ze slajdu: Citadel, Virtu, Jane Street, Two Sigma Securities.
- Reagują w mikrosekundach (milionowe części sekundy), a Citadel dzięki układom FPGA (obliczenia na poziomie sprzętu) nawet w nanosekundach.
- Zarabiają na ułamkach centa: wyłapują różnice cen między parkietami i wskakują przed zlecenia inwestorów indywidualnych, bo mogą kwotować z dokładnością do 4 i więcej miejsc po przecinku, a my zwykle do 2.
- Wniosek Treli: gra pod newsy i wyniki kwartalne oraz day trading (handel w ciągu dnia) są z góry przegrane.

### Payment for Order Flow (00:22:40)
- PFOF = opłata za przepływ zleceń. Broker często nie wysyła zlecenia na giełdę publiczną, tylko do firmy HFT, która mu za to płaci. Część tej kwoty wraca do klienta jako niższa prowizja.

### Dark poole (00:27:00)
- Dark pool = prywatny parkiet, na którym zleceń nie widać w czasie rzeczywistym. Ze slajdu: SigmaX (Goldman Sachs), MS Pool (Morgan Stanley).
- Skoro około połowy obrotu jest ukryte, analiza wolumenu i świec na bieżąco to wg Treli czytanie książki z co drugą stroną wyrwaną (00:28:10).

### Dlaczego cena akcji się zmienia? (00:30:50)
Fundamenty zmieniają się raz na kwartał (raport), a kurs waha się codziennie. Trzy mechanizmy ze slajdu:
1. **Algo wars i pair trading** (00:34:00). Algorytmy skanują newsy pod kątem słów kluczowych i sprzedają, zanim człowiek przeczyta nagłówek. Pair trading = handel parami: algorytm pilnuje korelacji dwóch podobnych spółek i gra na jej powrót. Algo wars = algorytmy kopiujące inne algorytmy lub grające przeciw nim. Nawet autorzy nie potrafią wyjaśnić ich pojedynczej decyzji.
2. **Hedging i short covering** (00:40:00). Short = gra na spadek: pożyczam akcje od brokera, sprzedaję, liczę na tańszy odkup. Gdy kurs rośnie, strata jest nieograniczona, więc grający zamykają pozycje, odkupując akcje (short covering), co dodatkowo podbija kurs. Stąd gwałtowne wzrosty bez newsa.
3. **ETF rebalancing** (00:43:00). ETF = fundusz kupujący wszystkie spółki spełniające kryterium (branża, wielkość), dobre i złe. Przy kwartalnym dostosowaniu składu dokupuje to, co urosło, i sprzedaje to, co spadło. Efekt: spółki ruszają się całymi grupami bez uzasadnienia.

### Margin call i „pętla zagłady" (00:45:29)
- Margin = pożyczka od brokera pod zastaw akcji (dźwignia). Wg Treli sama dźwignia nie jest zła.
- Margin call = wezwanie do dopłaty albo spłaty. Gdy kurs spada, broker każe sprzedać akcje lub sprzedaje je sam.
- Pętla zagłady: wymuszona sprzedaż obniża kurs, to uruchamia kolejne margin calle. Gdy zabraknie sprzedających, następuje ostre odbicie w kształcie litery V (V-shape), bez powodu fundamentalnego (00:51:20).
- Większość krachów trwających dni–miesiące to wg Treli czyszczenie pozycji na kredyt, nie zmiana fundamentów.

### Wniosek i „old-school investing" (00:51:48–00:59:00)
Slajd: „Nikt nie wie, dlaczego akcje rosną i spadają". Odpowiedź Treli to trzy zasady:
- **Wydłużenie horyzontu.** Algorytmy wygrywają w skali milisekund–miesięcy; w skali ok. 5 lat o kursie decydują przychody i zyski firmy.
- **Selekcja ponad spekulację.** Zamiast ETF-ów i rozkładania na branże: tylko najlepsze spółki z najlepszych branż (największa zdolność generowania gotówki, zysków, przychodów).
- **Quiet luxury.** Brak nadmiernego handlu i gwałtownych ruchów; reagować tylko na fundamenty, nie na szum. Trela nazywa to przewagą behawioralną (behavioral advantage).
- Ostrzeżenie: nie dokupować tylko dlatego, że spadło 20% (01:00:46).

### Plan zajęć (00:59:18)
Podstawy (zyskowność, wycena, budowa portfela) → system (kryteria, scoring, ranking spółek, procedury) → narzędzia i modele. Proces ma być sprowadzony do liczb, żeby dało się go kalibrować (01:02:26).

## Reguły i progi liczbowe
Lekcja nie zawiera progów wskaźnikowych ani punktów modelu. Liczby kontekstowe i brokerskie:

| Wskaźnik / kryterium                                 | Reguła lub próg                                                               | Punkty w modelu | Źródło                                                 |
| ---------------------------------------------------- | ----------------------------------------------------------------------------- | --------------- | ------------------------------------------------------ |
| Udział dark pooli w handlu                           | 51% w ukryciu                                                                 | –               | slajd 00:12:59                                         |
| Udział HFT w wolumenie akcji w USA                   | ok. 50–60%                                                                    | –               | z nagrania, niepotwierdzone slajdem – sprawdź 00:13:25 |
| Opóźnienie zleceń („speed bump") na giełdzie IEX (?) | 350 mikrosekund                                                               | –               | z nagrania, niepotwierdzone slajdem – sprawdź 00:15:14 |
| Horyzont oceny decyzji                               | lata (od 1–2 w górę), nie miesiące i kwartały                                 | –               | z nagrania 00:11:00; slajd 00:53:40 bez liczby         |
| Prowizja LYNX vs Interactive Brokers                 | 5 USD vs < 1 USD                                                              | –               | slajd 01:18:38                                         |
| Prowizja „Fixed" w IB                                | minimum 1 USD za transakcję                                                   | –               | z nagrania, niepotwierdzone slajdem – sprawdź 01:23:26 |
| Ankieta IB                                           | doświadczenie Extensive > 10y; majątek > 100k USD; cele: hedging i spekulacja | –               | slajd 01:24:07                                         |
|                                                      |                                                                               |                 |                                                        |

## Przykłady z lekcji
- **Coca-Cola / Pepsi** (00:34:09): zły news o prezesie Coca-Coli, a spada też Pepsi, bo algorytm gra na powrót korelacji. Dowód, że ruch kursu może nie mieć związku ze spółką.
- **Short na 100 akcji po 100 USD** (00:40:25): spadek do 90 daje 1000 USD zysku, wzrost do 120 to już 20% straty.
- **Margin** (00:47:30): 100 tys. spada do 80 tys., pożyczam drugie 80 tys. (ekspozycja 160 tys.); przy dalszym spadku do „60" portfel jest wart 120 tys. przy 80 tys. długu i broker wymusza sprzedaż.
- **ETF na półprzewodniki** (00:57:11): zawiera spółki wybitne i beznadziejne naraz.

## Narzędzia
- **Scrab** – przeglądarkowy system analityczny, główne narzędzie kursu. Uczestnicy mieli pakiet Advanced do 10 czerwca (m.in. własne wskaźniki). Model scoringowy da się też prowadzić w darmowym Excelu (01:07:29, 01:51:10).
- **Konto brokerskie – ściąga** (co Trela porównuje; to jego opinie):
  - Do samych akcji broker jest wg niego sprawą drugorzędną. Jedno zastrzeżenie: unikać brokerów automatycznie przewalutowujących każdą transakcję (01:17:49).
  - Do opcji (semestr jesienny) wskazuje Interactive Brokers (IB). LYNX to ta sama platforma: droższe prowizje, dobre polskie wsparcie, brak akcji ułamkowych. IB: tańszy, słabe wsparcie po angielsku, akcje ułamkowe (np. 1/10 akcji za 1200 USD) – ważne przy małym portfelu.
  - Typy kont (slajd 01:20:14): Single (jedna osoba), Joint (wspólne – druga osoba zachowuje dostęp po śmierci pierwszej), Company (firma lub fundacja rodzinna). Różnią się prowizjami, dokumentami i księgowością.
  - Ustawienia w IB: włączyć wszystkie giełdy w „Trading Permissions"; zaznaczyć „Trade in Fractions"; system prowizji „Tiered" zamiast „Fixed"; odpowiedzi w ankiecie zawyżone, żeby odblokować opcje i ETF-y lewarowane.
  - IB to konto wielowalutowe: wpłata w dowolnej walucie, wymiana po kursach międzybankowych (01:43:07, 01:48:45).
  
## Co z tego zastosuję w skanerze
- Wejście: zmiana kursu z dni/tygodni → nie używać jako sygnału kupna ani sprzedaży.
- Wejście: wolumen i świece → nie budować na nich reguł (ok. połowa obrotu jest niewidoczna).
- Wejście: spadek kursu o X% → sam w sobie nie daje sygnału „dokup"; potrzebne potwierdzenie fundamentami.
- Ocena trafności wskazań skanera → liczona w horyzoncie lat, nie kwartału.
- Uniwersum: pojedyncze spółki zagraniczne (głównie USA); bez ETF-ów, bez GPW (01:56:45), bez świeżych IPO, czyli debiutów bez historii danych (01:55:09).
- Wynik skanera: ranking/scoring spółek według liczbowych kryteriów „musi spełniać / nie może spełniać" (szczegóły w kolejnych lekcjach).

## Pytania powtórkowe
1. Dlaczego wg Treli nie da się wygrać z HFT w krótkim terminie?
2. Co to jest dark pool i jaki wniosek płynie z tego dla analizy wolumenu?
3. Jak pair trading sprawia, że spada spółka, której news nie dotyczy?
4. Jak margin call tworzy pętlę zagłady i czemu kończy się odbiciem w kształcie V?
5. Jakie są trzy zasady „old-school investing"?

## Niepewne – do sprawdzenia
- Ankieta IB: slajd mówi „Extensive > 10y" i „> 100k USD", a Trela w mowie podaje 6–10 lat, ok. 20 transakcji rocznie i majątek „powyżej 10 tysięcy" (01:22:10, 01:24:07). Przyjąłem slajd.
- Nazwa giełdy ze „speed bumpem" (transkrypcja: „International Exchange"; prawdopodobnie IEX) – 00:14:39.
- Slajd wymienia „MRS Pool"; z nagrania nie wynika, czyj to parkiet (00:27:05).
- Liczba parkietów „27" i dzienne wolumeny (ok. 20 mld akcji + ok. 10 mld w dark poolach) – tylko z mowy (00:12:42, 00:29:53).
- Próg „Tiered, chyba że 10 mln na koncie" – tylko z mowy (01:23:17).
- W przykładzie margin transkrypcja mówi o spadku „o 80%"; z rachunku wynika spadek do 80 (00:47:31).

## Powiązane
- [[Kurs Treli - mapa]]
- [[Kurs Treli - reguly wyceny pod skaner]]
- [[START]]
