# Kandydaci ze screenów — lista kontrolna

Zbierane z telefonu, do sprawdzenia na komputerze (`python -m screener validate`).
Status: `dodać` → `w CSV` → `ticker OK` → `na stronie`. Tickery z sufiksami giełd (.WA, .ST, .AX) i klasy akcji (MOG-A) to moje domysły — do sprawdzenia.

## Zasada porządkowania: warstwy robota humanoidalnego

Układ z piramidy Portfela Tradera („Jak podejść do inwestowania w AI”), dopasowany do humanoidów.
Waga na stronie maleje od środka piramidy w obie strony:

| Waga | Warstwa | Co to jest | Plik / segment |
|---|---|---|---|
| **główna** | Humanoidy | spółki z własnym robotem | `universe_humanoid_global.csv` → `humanoid` |
| **główna** | Podzespoły mechaniczne | przekładnie, aktuatory, serwonapędy, łożyska, czujniki, magnesy | `universe_humanoid_global.csv` → `komponenty` |
| **główna** | Integratorzy | producenci robotów i automatyki, kontraktowi producenci humanoidów | `universe_humanoid_global.csv` → `integrator` |
| średnia | 3 — Półprzewodniki i AI | chipy do sterowania i percepcji, sprzęt do produkcji chipów | `universe_humanoid_global.csv` → `platforma/AI` |
| mniejsza | 2 — Infrastruktura fizyczna | energia, chłodzenie, sieci, transformatory (bez tego nie ma AI, więc nie ma humanoidów) | **nowy plik** `universe_infrastruktura.csv` — do decyzji |
| mniejsza | 1 — Surowce krytyczne | miedź, ziemie rzadkie, uran; złoto/srebro jako makro | `universe_surowce.csv` |
| osobna sekcja | Inne tematy — cyberbezpieczeństwo, chmura, fintech, obronność, cokolwiek ciekawego | **zasada Rafała: ciekawe spółki z każdego sektora trafiają na stronę**, w osobnej sekcji z własnym rankingiem | `universe_inne.csv` |

---

## Warstwa główna — humanoidy, podzespoły, integratorzy

| # | Spółka | Ticker (do sprawdzenia) | Segment | Dlaczego interesuje | Źródło | Status |
|---|---|---|---|---|---|---|
| 1 | Moog | MOG-A (jest też MOG-B) | komponenty | precyzyjne sterowanie ruchem, aktuatory, serwonapędy; 367,51 USD na 9 wrz (−10% w miesiąc) | reel „7 ETF-ów” (B. Kucia) nr 1; reel inwestycjezradkiem „3 spółki na boom humanoidów” | dodać |
| 2 | Symbotic | SYM | integrator | roboty magazynowe; ekspozycja pośrednia; 42,62 USD na 9 wrz | reel „7 ETF-ów”; reel inwestycjezradkiem | w CSV |
| 3 | Palantir | PLTR | platforma/AI? | oprogramowanie AI; związek z humanoidami słaby — raczej watchlista trackera | portfel finanse_na_sterydach | w `universe_infrastruktura.csv` |

### Łańcuch dostaw humanoida podzespół po podzespole (film YouTube, polski lektor — tytuł do ustalenia)

Film idzie przez robota element po elemencie i przy każdym wymienia dostawców Zachód / Wschód. Większość już była na liście; nowe oznaczone **NOWA**.

| Podzespół | Zachód | Wschód | Status |
|---|---|---|---|
| Przekładnie falowe / reduktory | Harmonic Drive (6324.T, w CSV) | Nabtesco (6268.T, w CSV); Leaderdrive 绿的谐波 (688017.SS, w CSV) | — |
| Prowadnice liniowe, śruby kulowe | — | THK (6481.T) **NOWA**, NSK (6471.T) **NOWA**; Best Drive / Jinxu (Chiny, nie znam tickerów) | THK „najbardziej skoncentrowana i agresywna opcja” wg filmu |
| Łożyska | Schaeffler (SHA0.DE, w CSV), SKF (SKF-B.ST) **NOWA**, Timken (TKR) **NOWA** | NSK (j.w.) | cały segment łożysk był pominięty — dodany |
| Silniki, napędy, aktuatory | Regal Rexnord (RRX, w CSV), Moog (MOG-A, w CSV) | Inovance 汇川 (300124.SZ, w CSV, „chiński gigant automatyki i napędów bezszczotkowych”); Leili 雷利 (Chiny, ticker nieznany) | — |
| Magnesy ziem rzadkich | MP Materials (MP, w CSV, „perełka”) | JL MAG 金力永磁 (300660.SZ) **NOWA** | — |
| Baterie | QuantumScape (QS) **NOWA**, „Ampus Technologies” (?), Tesla | BYD (1211.HK) **NOWA**, „potężna baza R&D z pilotażowymi liniami solid state” | „Ampus Technologies” — nie znam takiej spółki, możliwy błąd lektora; sprawdzić |

Nieznane tickery do sprawdzenia na komputerze: Best Drive, Jinxu, Leili (chińskie spółki z prowadnic i silników — mogą być notowane w Szanghaju/Shenzhen albo prywatne).

## Warstwa 3 — półprzewodniki i AI (segment `platforma/AI`, średnia waga)

| # | Spółka | Ticker | Co robi | Źródło | Status |
|---|---|---|---|---|---|
| 1 | NVIDIA | NVDA | **w CSV** | wiele | w CSV |
| 2 | TSMC | 2330.TW (ADR: TSM) | **w CSV** | wiele | w CSV |
| 3 | Broadcom | AVGO | układy custom AI, sieci | slajd „AI w praktyce”, portfel finanse_na_sterydach | dodać |
| 4 | Micron | MU | pamięci HBM do AI | portfel finanse_na_sterydach | dodać |
| 5 | Marvell | MRVL | układy do datacenter | portfel finanse_na_sterydach | dodać |
| 6 | ASML | ASML | litografia — sprzęt do produkcji chipów | slajd „AI w praktyce” | dodać (medium) |
| 7 | Lam Research | LRCX | sprzęt do produkcji chipów | j.w. | dodać (medium) |
| 8 | Applied Materials | AMAT | sprzęt do produkcji chipów | j.w. | dodać (medium) |
| 9 | KLA | KLAC | kontrola jakości w produkcji chipów | j.w. | dodać (medium) |
| 10 | Intel | INTC | największa pozycja rządu USA (8,9 mld USD); produkcja chipów w USA | slajd „USA walczą o swoje surowce” (CATO) | dodać (medium) |
| 11 | GlobalFoundries | GFS | 675 mln USD od rządu USA; produkcja chipów | j.w. | dodać (medium) |
| 12 | Qualcomm, Ambarella | QCOM, AMBA | **w CSV** | | w CSV |
| — | SPCX | SPCX | z portfela finanse_na_sterydach; nie wiem, co to za spółka — sprawdzić na komputerze | reel | sprawdzić |

## Warstwa 2 — infrastruktura fizyczna (mniejsza waga, do decyzji czy na stronę)

Teza ze slajdów: centra danych pochłaniają prąd, budowa sieci trwa lata, brakuje dużych transformatorów, OZE nie rozwiąże problemu. Hyperscalerzy (Microsoft, Meta, Alphabet, Amazon, Oracle) wydają w 2026 ok. 600+ mld USD na infrastrukturę AI (Bloomberg).

| # | Spółka | Ticker | Co robi | Źródło | Status |
|---|---|---|---|---|---|
| 1 | Vertiv | VRT | chłodzenie i zasilanie datacenter | slajd „AI w praktyce”, warstwa 2 | w `universe_infrastruktura.csv` |
| 2 | Vistra | VST | energetyka (w tym jądrowa) | j.w. | w `universe_infrastruktura.csv` |
| 3 | GE Vernova | GEV | turbiny, sieci, transformatory | j.w. | w `universe_infrastruktura.csv` |
| 4 | Quanta Services | PWR | budowa sieci przesyłowych | j.w. | w `universe_infrastruktura.csv` |
| 5 | Cameco | CCJ | uran — paliwo dla energetyki jądrowej | j.w. | w `universe_surowce.csv` |
| 6 | Constellation Energy | CEG | największa flota jądrowa w USA; umowy z hyperscalerami | karuzela Neuralka „AI pożera energię”, #1 | w `universe_infrastruktura.csv` |
| 7 | NRG Energy | NRG | elektrownie gazowe szczytowe, sprzedaż detaliczna (Teksas/ERCOT) | Neuralka #2 | w `universe_infrastruktura.csv` |
| 8 | Talen Energy | TLN | elektrownia jądrowa Susquehanna obok kampusu datacenter Amazona | Neuralka #3 | w `universe_infrastruktura.csv` |
| 9 | NextEra Energy | NEE | OZE + magazyny energii + regulowana spółka na Florydzie | Neuralka #5 | w `universe_infrastruktura.csv` |
| 10 | Eaton | ETN | rozdzielnice, zasilanie awaryjne, dystrybucja energii w datacenter | Neuralka #6 | w `universe_infrastruktura.csv` |

GE Vernova (GEV) występuje u obu źródeł (Portfel Tradera i Neuralka #4). Karuzela Neuralki miała 8 slajdów — brakuje #7 i #8.

## Warstwa 1 — surowce krytyczne (`universe_surowce.csv`, osobny ranking, mniejsza waga)

Związek bezpośredni z humanoidami: **miedź** (silniki, okablowanie), **metale ziem rzadkich** (magnesy neodymowe w aktuatorach).
Slajd EUISS: Chiny dominują w wydobyciu ziem rzadkich (ok. 70% światowego wydobycia w 2025), stąd rząd USA finansuje własne źródła.

| # | Spółka | Ticker | Metal | Uwagi | Źródło | Status |
|---|---|---|---|---|---|---|
| 1 | Freeport-McMoRan | FCX | miedź | | Portfel Tradera | w CSV |
| 2 | Southern Copper | SCCO | miedź | | Portfel Tradera | w CSV |
| 3 | KGHM Polska Miedź | KGH.WA | miedź, srebro | GPW | Portfel Tradera | w CSV |
| 4 | Boliden | BOL.ST | miedź, cynk | Sztokholm | Portfel Tradera | w CSV |
| 5 | MP Materials | MP | ziemie rzadkie | 400 mln USD od rządu USA; także na liście głównej; 54,30 USD na 9 wrz | CATO, „AI w praktyce”, reel inwestycjezradkiem | w CSV |
| 6 | USA Rare Earth | ? | ziemie rzadkie, magnesy | 1,6 mld USD od rządu USA; czy notowana i pod jakim tickerem — sprawdzić | CATO | sprawdzić |
| 7 | Korea Zinc | 010130.KS? | cynk, metale krytyczne | 1,6 mld USD od rządu USA; Seul — ticker do sprawdzenia | CATO | dodać (medium) |
| 8 | Vulcan Elements | — | magnezy ziem rzadkich (USA) | 670 mln USD od rządu; prawdopodobnie prywatna — sprawdzić | CATO | sprawdzić |
| 9 | Cameco | CCJ | uran | makro / energia | | w CSV |
| 10–19 | Newmont, Agnico Eagle, Barrick, Wheaton, AngloGold, Franco-Nevada, Kinross, Gold Fields, Pan American Silver, Northern Star | NEM, AEM, B, WPM, AU, FNV, KGC, GFI, PAAS, NST.AX | złoto / srebro | makro, TOP10 GDX | Portfel Tradera | w CSV |

Pozostałe pozycje rządu USA ze slajdu CATO (nie surowce): L3Harris (LHX, obronność, 1 mld), IBM (IBM, komputery kwantowe, 1 mld), SandboxAQ (prywatna, 500 mln), iPulse (?, 250 mln). Tylko notatka.

## Warstwy 4–6 — kontekst, nie na stronę

- Cyberbezpieczeństwo: CIBR, Palo Alto (PANW), CrowdStrike (CRWD), Fortinet (FTNT), Cloudflare (NET).
- Chmura i modele: Google (GOOGL), Amazon (AMZN), Microsoft (MSFT), Meta (META), Oracle (ORCL) — są w watchliście trackera.

---

## ETF-y (osobna sekcja na stronie, bez scoringu fundamentalnego)

### Humanoidy, robotyka, półprzewodniki

| ETF | Ticker | Emitent | Uwagi | Źródło | Status |
|---|---|---|---|---|---|
| KraneShares Global Humanoid & Embodied Intelligence Index ETF | KOID (Nasdaq) | KraneShares | 35,27 USD na 17 wrz 2026 wg screenu | reele B. Kucia, finanse_na_sterydach | dodać |
| Roundhill Humanoid Robotics ETF | HUMN (BATS) | Roundhill | 29,33 USD na 17 wrz 2026 | reel finanse_na_sterydach | dodać |
| iShares Robotics / Automation | RBOT | iShares | slajd „AI w praktyce”, warstwa 2 | Portfel Tradera | dodać |
| Global X Robotics & AI | BOTZ | Global X | z mojej wiedzy, nie ze screenów | — | kandydat |
| VanEck Semiconductor | SMH | VanEck | warstwa 3 | Portfel Tradera | dodać (tło) |
| ETF WIRE | WIRE | ? | warstwa 2; emitent i pełna nazwa do sprawdzenia | Portfel Tradera | sprawdzić |

### Surowce (tło)

| ETF | Ticker | Ekspozycja | Status |
|---|---|---|---|
| Global X Copper Miners | COPX | spółki miedziowe | dodać |
| Sprott Junior Copper Miners | COPJ | mniejsze spółki miedziowe | dodać |
| Sprott Physical Copper Trust | COP.UN (Toronto) / SCOP | fizyczna miedź | dodać (ticker Yahoo do sprawdzenia) |
| VanEck Rare Earth & Strategic Metals | REMX | metale ziem rzadkich | dodać |
| Sprott Uranium Miners | URNM (USA) / URNU (UCITS, Europa) | spółki uranowe — sprawdzić, która wersja | sprawdzić |
| Global X Uranium | URA | uran + sektor nuklearny | dodać (makro) |
| Sprott Junior Uranium Miners | URNJ | małe spółki uranowe | dodać (makro) |
| Sprott Physical Uranium Trust | U.UN (Toronto) / SRUUF | fizyczny uran | dodać (makro) |
| VanEck Gold Miners / Junior | GDX / GDXJ | kopalnie złota | dodać (makro) |
| Global X Silver Miners / Amplify Junior Silver | SIL / SILJ | kopalnie srebra | dodać (makro) |
| Sprott Physical Gold / Silver / Gold+Silver | PHYS / PSLV / CEF | metal fizyczny | dodać (makro) |
| abrdn Platinum / Palladium / Basket, Sprott Pt+Pd | PPLT / PALL / GLTR / SPPP | metale szlachetne | dodać (makro) |
| SPDR S&P Global Natural Resources | GNR | surowce rolne + energetyczne + metale; NAV 77,03 USD, AUM 5,27 mld, TER 0,40% (22 wrz 2026) | dodać (makro) |
| Invesco DB Commodity Index | DBC | szeroki koszyk surowców; +47,3% YTD 2026 wg tabeli Bilello | kandydat (benchmark surowców) |

### Klasy aktywów do porównań (z tabeli Charlie Bilello, stan 18 wrz 2026)

SPY (akcje USA), QQQ (Nasdaq 100), IWM (małe spółki), EFA (rynki rozwinięte), VWO (wschodzące), GLD (złoto), TLT (obligacje), DBC (surowce), BTC. Przydadzą się jako benchmarki na stronie: „jak humanoidy radzą sobie na tle rynku”.

---

## Notatki makro (kontekst do opisu na stronie)

- **Rynek humanoidów** (The Business Research Company, Humanoid Robot Market Report 2026): 5,44 mld USD (2025) → 8,32 mld (2026) → 39 mld (2030), CAGR 2026–2030 47,1%. Film: nawet konserwatywne instytucje dają 41–48% rocznie. Do nagłówka strony, z podaniem źródła.
- **Cykl hype → rzeczywistość → ból → smart money → odbicie** (grafika z reela, przykład NVIDIA i „SpaceX”): typowy przebieg po IPO/hypie: 1–3 mies. hype, 3–9 spadek, 9–18 dno, 12–24 akumulacja. Przydatne jako komentarz do spółek humanoidalnych po debiutach (np. UBTech, Horizon).
- **Jensen Huang** (tweet F. Curzio): CEO NVIDIA zachęca do spółek energii zrównoważonej — potwierdza tezę warstwy 2.

- **BofA Fund Manager Survey, wrz 2026**: najbardziej zatłoczona pozycja „long global semiconductors” (53%). Nisza humanoidów jest mniej wyeksploatowana niż chipy.
- **Surowce vs akcje**: BCOM/SPX najniżej od lat 90.; Fidelity i Incrementum pokazują początek nowej hossy surowcowej. Portfel Tradera: deglobalizacja, zbrojenia, inflacja.
- **2026 YTD** (Bilello): surowce DBC +47,3%, US Value +20,9%, Nasdaq +17,7%, S&P +12,6%, złoto +1,2%, obligacje na minusie, BTC −7,6%.
- **Hyperscalerzy**: capex na AI rośnie z ~200 mld USD (2024) do ~600+ mld (2026). Wąskie gardło to prąd i transformatory, nie chipy.
- **Rząd USA** inwestuje bezpośrednio w spółki (Intel 8,9 mld, Korea Zinc 1,6 mld, USA Rare Earth 1,6 mld, MP Materials 400 mln) — państwowe wsparcie dla łańcucha dostaw ziem rzadkich i chipów.

## Okazje zakupowe (`data/okazje.csv`) — spółki do kupienia na spadkach

Reel finanse_na_sterydach „4 spółki, które dokupuję na spadkach” (4 czerwca): Micron, ASML + dwa loga: „N” na żółtym (prawdopodobnie Nebius), białe „X” (niepewne: Nutanix?). Komenda `tracker alerts` zgłosi, gdy kurs spadnie o próg z pliku poniżej szczytu 52T albo przebije SMA200 w dół.

## Pomysły z reela grimkrit „Mam swojego tradera 24/7”

Zbudował w Claude Code: wskaźnik Pine Script na TradingView (wolumen względny + poziomy ze szczytów/dołków gasnące po przebiciu), alerty na Telegram, automatyczne pozycje na OKX.

- [x] poziomy ze szczytów i dołków gasnące po przebiciu → reguła „poziom” w `tracker alerts`
- [x] konfluencja (kilka sygnałów naraz) → reguła „konfluencja”
- [x] wskaźnik Pine Script na TradingView → `tradingview/rafmall_konfluencja.pine` (Rafał ma Premium; test na komputerze)
- [ ] **nie bierzemy**: automatycznego składania zleceń. Narzędzie pokazuje, Rafał decyduje.

## Portfele twórców (tylko jako sygnał, co jest popularne)

- **finanse_na_sterydach**, „3 spółki, które obserwuję w sierpniu”: SoFi (SOFI, fintech), Zeta Global (ZETA, martech AI), CoreWeave (CRWV, chmura GPU). Tylko CoreWeave ma związek z AI-infrastrukturą; SoFi i Zeta nie dotyczą naszego tematu — pomijam.
- **finanse_na_sterydach**, story po wynikach NVIDIA: NVDA, Nebius (NBIS, chmura GPU), Sandisk (SNDK, pamięci), Micron (MU). Nebius i Sandisk → kandydaci do warstwy 3 jako `medium`, tylko jeśli chcemy rozszerzać o pamięci/chmurę GPU — na razie nie dodaję.

- **inwestycjezradkiem** „3 spółki, którymi rozegrałbym boom na humanoidy”: Symbotic, MP Materials, Moog. Ten sam zestaw co u B. Kuci — popularna narracja, nie niezależne potwierdzenie.

- **finanse_na_sterydach** (po 4 mies.): AVGO, SPCX, MU, PLTR, MRVL. Dwie z pięciu to pamięci/układy dla datacenter.

---

## Pytania do Rafała

- [x] Screen z „1” (pierwsza paczka): tak, Moog — potwierdzone drugim reelem
- [x] Warstwa 2: domyślnie NA STRONIE jako sekcja „Energia” (do odwołania)
- [x] Sprzęt do chipów i pamięci: domyślnie W platforma/AI jako medium (do odwołania)
- [x] ETF-y złoto/srebro/uran: domyślnie NA STRONIE w grupie „makro” (do odwołania)
- [x] Hosting rafmall.ch: własny hosting → strona jako plik `roboty.html` do wgrania
- [ ] HTML strony z Lovable (do dopasowania wyglądu)
- [ ] Które spółki są w portfelu, a które tylko obserwowane?

## Zasady od Rafała

- **Ciekawe spółki z każdego sektora** trafiają na stronę, w osobnej sekcji z własnym rankingiem.
- **Jakość, nie ilość.** To, co wrzuca ze screenów, to kandydaci do sprawdzenia; po weryfikacji część odpada.
- **Powiadomienia: Discord** (webhook). Rutyna Claude ewentualnie osobno, do streszczeń.

## Do zrobienia na komputerze (wymaga internetu)

- [ ] przegląd jakościowy wszystkich list po `validate` — wykreślić, co się nie broni

- [ ] `python -m screener --universe data/universe_humanoid_global.csv validate`
- [ ] `python -m screener --universe data/universe_surowce.csv validate`
- [ ] poprawić tickery ze statusem BŁĄD (szczególnie: KGH.WA, BOL.ST, NST.AX, B, COP.UN, U.UN, MOG-A, Korea Zinc)
- [ ] sprawdzić: tickery Best Drive, Jinxu, Leili (Chiny); tytuł filmu z łańcuchem dostaw (polski lektor, logo firm na ekranie)
- [ ] sprawdzić: co to SPCX; ticker USA Rare Earth; czy Vulcan Elements jest notowana; pełna nazwa ETF WIRE; URNM vs URNU
- [ ] pobrać pełny skład KOID (kraneshares.com) i HUMN (roundhillinvestments.com) — spółki obecne w obu ETF-ach, a nieobecne na naszej liście, to kandydaci nr 1
- [ ] odszukać pozostałe ETF-y z reela „Te 7 ETF-ów prawdopodobnie przebije S&P500” (Bartosz Kucia) — na screenach był tylko KOID (nr 3)
- [ ] wygenerować `roboty.html` i obejrzeć

## Do zrobienia w kodzie (mogę z telefonu)

- [x] lista spółek surowcowych jako osobny plik `data/universe_surowce.csv`
- [x] dopisać warstwę 3 do `universe_humanoid_global.csv` (Moog, AVGO, MU, MRVL, ASML, LRCX, AMAT, KLAC, INTC jako medium)
- [x] sekcja „ETF-y” na stronie (`data/etf.csv`)
- [x] sekcje „Surowce” i „Energia” na stronie: osobne rankingi (`site --extra`)
- [ ] KOID jako dodatkowy benchmark siły względnej dla spółek z listy
- [ ] porównanie „humanoidy vs klasy aktywów” (KOID/HUMN vs SPY, QQQ, DBC, GLD) na stronie
