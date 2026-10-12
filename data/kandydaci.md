# Kandydaci ze screenów — lista kontrolna

Zbierane z telefonu, do sprawdzenia na komputerze (`python -m screener validate`).
Status: `dodać` → `w CSV` → `ticker OK` → `na stronie`

## Spółki — humanoidy i podzespoły (główna lista, pełna waga)

| # | Spółka | Ticker (do sprawdzenia) | Segment | Dlaczego interesuje | Źródło | Status |
|---|---|---|---|---|---|---|
| 1 | Moog | MOG-A (NYSE; jest też klasa B: MOG-B) | komponenty | precyzyjne sterowanie ruchem, aktuatory, serwonapędy | reel „7 ETF-ów” (B. Kucia), nr 1 | dodać |
| 2 | Symbotic | SYM | integrator | roboty magazynowe; ekspozycja pośrednia | reel „7 ETF-ów” | w CSV |

## Spółki — surowce (osobny segment, mniejsza waga: tło dla humanoidów)

Związek z humanoidami: **miedź** (silniki, okablowanie) i **metale ziem rzadkich** (magnesy) — bezpośredni.
Złoto, srebro, uran — makro/inflacja, nie humanoidy; na stronie z adnotacją.

| # | Spółka | Ticker | Metal | Uwagi | Źródło | Status |
|---|---|---|---|---|---|---|
| 1 | Freeport-McMoRan | FCX | miedź | największy producent miedzi notowany w USA | Portfel Tradera, „Spółki miedziowe” + „AI w praktyce” | dodać |
| 2 | Southern Copper | SCCO | miedź | | j.w. | dodać |
| 3 | KGHM Polska Miedź | KGH.WA | miedź, srebro | GPW; na slajdzie „KGH”, u Yahoo sufiks .WA | Portfel Tradera | dodać |
| 4 | Boliden | BOL.ST | miedź, cynk | Sztokholm; na slajdzie „BOL” | Portfel Tradera | dodać |
| 5 | MP Materials | MP | ziemie rzadkie | **już w CSV** (segment komponenty) | slajd „AI w praktyce”, warstwa 1 | w CSV |
| 6 | US Rare Earths / USA Rare Earth | ? | ziemie rzadkie | na slajdzie bez tickera; sprawdzić, czy notowana i pod jakim symbolem | slajd „AI w praktyce” | sprawdzić |
| 7 | Cameco | CCJ | uran | paliwo jądrowe (energia dla AI/datacenter) | slajd „AI w praktyce” | dodać (makro) |
| 8 | Newmont | NEM | złoto | 10,89% GDX | TOP10 GDX | dodać (makro) |
| 9 | Agnico Eagle Mines | AEM | złoto | 10,87% GDX | TOP10 GDX | dodać (makro) |
| 10 | Barrick Mining | B | złoto | 7,42% GDX; dawniej GOLD, zmiana nazwy/tickera — sprawdzić | TOP10 GDX | dodać (makro) |
| 11 | Wheaton Precious Metals | WPM | złoto/srebro (streaming) | 5,96% | TOP10 GDX | dodać (makro) |
| 12 | AngloGold Ashanti | AU | złoto | 5,01% | TOP10 GDX | dodać (makro) |
| 13 | Franco-Nevada | FNV | złoto (royalty) | 4,91% | TOP10 GDX | dodać (makro) |
| 14 | Kinross Gold | KGC | złoto | 4,16% | TOP10 GDX | dodać (makro) |
| 15 | Gold Fields | GFI | złoto | 4,12% | TOP10 GDX | dodać (makro) |
| 16 | Pan American Silver | PAAS | srebro | 2,59% | TOP10 GDX | dodać (makro) |
| 17 | Northern Star Resources | NST.AX | złoto | 2,43%; Australia, na slajdzie „NST” | TOP10 GDX | dodać (makro) |

## Spółki — AI / infrastruktura (ze slajdu „Jak podejść do inwestowania w AI”)

Warstwy 2–3 pasują do segmentu **platforma/AI** i do „infrastruktury fizycznej” (energia, chłodzenie).
Warstwy 4–6 (cyberbezpieczeństwo, chmura) nie dotyczą humanoidów — zapisane tylko jako kontekst.

| Warstwa | Spółki | Tickery (do sprawdzenia) | Co z tym zrobić |
|---|---|---|---|
| 3 półprzewodniki | Nvidia, Broadcom, ASML, Lam Research, Applied Materials, KLA, TSMC | NVDA, AVGO, ASML, LRCX, AMAT, KLAC, TSM / 2330.TW | NVDA i TSMC już są; reszta to sprzęt do produkcji chipów — do segmentu platforma/AI jako `medium` |
| 2 infrastruktura fizyczna | Vertiv, Vistra, GE Vernova, Quanta Services | VRT, VST, GEV, PWR | energia i chłodzenie dla datacenter — osobny segment „infrastruktura AI”? Do decyzji |
| 4 cyberbezpieczeństwo | Palo Alto, CrowdStrike, Fortinet, Cloudflare | PANW, CRWD, FTNT, NET | nie dotyczy humanoidów — pomijamy |
| 5–6 platformy / AI | Google, Amazon, Microsoft, Meta | GOOGL, AMZN, MSFT, META | są w watchliście trackera, nie na stronie |

## ETF-y (osobna sekcja na stronie, bez scoringu fundamentalnego)

### Humanoidy i robotyka

| ETF | Ticker | Emitent | Uwagi | Źródło | Status |
|---|---|---|---|---|---|
| KraneShares Global Humanoid & Embodied Intelligence Index ETF | KOID (Nasdaq) | KraneShares | 35,27 USD na 17 wrz 2026 wg screenu | reele B. Kucia, finanse_na_sterydach | dodać |
| Roundhill Humanoid Robotics ETF | HUMN (BATS) | Roundhill | 29,33 USD na 17 wrz 2026 | reel finanse_na_sterydach | dodać |
| Global X Robotics & AI ETF | BOTZ | Global X | — | z mojej wiedzy, nie ze screenów; do weryfikacji | kandydat |
| iShares Automation & Robotics / Global Robotics | RBOT | iShares | na slajdzie „AI w praktyce”, warstwa 2 | Portfel Tradera | dodać |
| ETF WIRE | WIRE | ? | na slajdzie warstwa 2 „infrastruktura fizyczna”; emitent i pełna nazwa do sprawdzenia | Portfel Tradera | sprawdzić |
| VanEck Semiconductor | SMH | VanEck | warstwa 3 | Portfel Tradera | dodać (tło) |

### Surowce (tło)

| ETF | Ticker | Ekspozycja | Status |
|---|---|---|---|
| Global X Copper Miners | COPX | spółki miedziowe | dodać |
| Sprott Junior Copper Miners | COPJ | mniejsze spółki miedziowe | dodać |
| Sprott Physical Copper Trust | COP.UN (Toronto) / SCOP | fizyczna miedź | dodać (ticker Yahoo do sprawdzenia) |
| VanEck Rare Earth & Strategic Metals | REMX | metale ziem rzadkich | dodać |
| Sprott Uranium Miners (URNU na slajdzie) | URNM / URNU | spółki uranowe; URNU to wersja europejska (UCITS) — sprawdzić, która ma być | sprawdzić |
| Global X Uranium | URA | uran + sektor nuklearny | dodać (makro) |
| Sprott Junior Uranium Miners | URNJ | małe spółki uranowe | dodać (makro) |
| Sprott Physical Uranium Trust | U.UN (Toronto) / SRUUF | fizyczny uran | dodać (makro) |
| VanEck Gold Miners | GDX | duże kopalnie złota | dodać (makro) |
| VanEck Junior Gold Miners | GDXJ | mniejsze kopalnie złota/srebra | dodać (makro) |
| Global X Silver Miners | SIL | kopalnie srebra | dodać (makro) |
| Amplify Junior Silver Miners | SILJ | małe kopalnie srebra | dodać (makro) |
| Sprott Physical Gold Trust | PHYS | złoto fizyczne | dodać (makro) |
| Sprott Physical Silver Trust | PSLV | srebro fizyczne | dodać (makro) |
| Sprott Physical Gold and Silver Trust | CEF | złoto + srebro | dodać (makro) |
| abrdn Physical Platinum | PPLT | platyna | dodać (makro) |
| abrdn Physical Palladium | PALL | pallad | dodać (makro) |
| Sprott Physical Platinum and Palladium | SPPP | platyna + pallad | dodać (makro) |
| abrdn Precious Metals Basket | GLTR | złoto, srebro, platyna, pallad | dodać (makro) |
| SPDR S&P Global Natural Resources | GNR | surowce rolne + energetyczne + metale; NAV 77,03 USD, AUM 5,27 mld, TER 0,40% (22 wrz 2026) | dodać (makro) |

### Pozostałe ze slajdów (kontekst, nie na stronę)

CIBR (cyberbezpieczeństwo).

## Notatki ze slajdów (kontekst makro, do ewentualnego opisu na stronie)

- BofA Fund Manager Survey, wrzesień 2026: najbardziej zatłoczona pozycja to „long global semiconductors” (53%), dalej short obligacje USA (18%), long Magnificent 7 (7%). Wniosek: półprzewodniki są dziś konsensusem, więc ryzyko korekty jest wyższe niż w niszy humanoidów.
- Teza Portfela Tradera: surowce są historycznie tanie względem akcji (BCOM/SPX najniżej od lat 90.), a deglobalizacja, zbrojenia i inflacja mają je wspierać. To argument za segmentem „Surowce” na stronie jako tłem, nie jako głównym tematem.

## Pytania do Rafała

- [ ] Screen nr 4 z pierwszej paczki (z „1”): czy to Moog, czy inna firma?
- [ ] Czy spółki wydobywcze mają mieć własny ranking (proponuję: tak, osobny segment „Surowce” na końcu strony)?
- [ ] Czy dodawać warstwę „infrastruktura AI” (Vertiv, Vistra, GE Vernova, Quanta)? Pośredni związek z humanoidami.
- [ ] Czy rafmall.ch jest nadal publikowana przez Lovable?
- [ ] HTML strony z Lovable (do dopasowania wyglądu)
- [ ] Które spółki są w portfelu, a które tylko obserwowane?

## Do zrobienia na komputerze (wymaga internetu)

- [ ] `python -m screener --universe data/universe_humanoid_global.csv validate`
- [ ] `python -m screener --universe data/universe_surowce.csv validate`
- [ ] poprawić tickery ze statusem BŁĄD (szczególnie: KGH.WA, BOL.ST, NST.AX, B, COP.UN, U.UN, MOG-A)
- [ ] pobrać pełny skład KOID (kraneshares.com) i HUMN (roundhillinvestments.com) — spółki obecne w obu ETF-ach, a nieobecne na naszej liście, to kandydaci nr 1
- [ ] odszukać pozostałe ETF-y z reela „Te 7 ETF-ów prawdopodobnie przebije S&P500” (Bartosz Kucia) — na screenach był tylko KOID (nr 3)
- [ ] sprawdzić: ticker „US Rare Earths”, pełna nazwa ETF „WIRE”, URNM vs URNU
- [ ] wygenerować `roboty.html` i obejrzeć

## Do zrobienia w kodzie (mogę z telefonu)

- [x] lista spółek surowcowych jako osobny plik `data/universe_surowce.csv`
- [ ] sekcja „ETF-y” na stronie: kurs, zwroty, trend, bez C/Z i marż
- [ ] sekcja „Surowce” na stronie: osobny ranking, na końcu, z adnotacją o mniejszej wadze
- [ ] KOID jako dodatkowy benchmark siły względnej dla spółek z listy
