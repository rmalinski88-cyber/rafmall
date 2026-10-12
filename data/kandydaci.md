# Kandydaci ze screenów — lista kontrolna

Zbierane z telefonu, do sprawdzenia na komputerze (`python -m screener validate`).
Status: `dodać` → `w CSV` → `ticker OK` → `na stronie`

## Spółki

| # | Spółka | Ticker (do sprawdzenia) | Segment | Dlaczego interesuje | Źródło | Status |
|---|---|---|---|---|---|---|
| 1 | Moog | MOG-A (NYSE; jest też klasa B: MOG-B) | komponenty | precyzyjne sterowanie ruchem, aktuatory, serwonapędy | reel „7 ETF-ów” (B. Kucia), nr 1 | dodać |
| 2 | Symbotic | SYM | integrator | roboty magazynowe; ekspozycja pośrednia | reel „7 ETF-ów” | w CSV |

## ETF-y (osobna sekcja na stronie, bez scoringu fundamentalnego)

| # | ETF | Ticker | Emitent | Uwagi | Źródło | Status |
|---|---|---|---|---|---|---|
| 1 | KraneShares Global Humanoid & Embodied Intelligence Index ETF | KOID (Nasdaq) | KraneShares | 35,27 USD na 17 wrz 2026 wg screenu | reele B. Kucia, finanse_na_sterydach | dodać |
| 2 | Roundhill Humanoid Robotics ETF | HUMN (BATS) | Roundhill | 29,33 USD na 17 wrz 2026 wg screenu | reel finanse_na_sterydach | dodać |

## Pytania do Rafała

- [ ] Screen nr 4 (z „1”): czy to Moog, czy inna firma?
- [ ] Czy rafmall.ch jest nadal publikowana przez Lovable?
- [ ] HTML strony z Lovable (do dopasowania wyglądu)
- [ ] Które spółki są w portfelu, a które tylko obserwowane?

## Do zrobienia na komputerze (wymaga internetu)

- [ ] `python -m screener --universe data/universe_humanoid_global.csv validate`
- [ ] poprawić tickery ze statusem BŁĄD
- [ ] pobrać pełny skład KOID (kraneshares.com) i HUMN (roundhillinvestments.com) — spółki obecne w obu ETF-ach, a nieobecne na naszej liście, to kandydaci nr 1
- [ ] odszukać pozostałe ETF-y z reela „Te 7 ETF-ów prawdopodobnie przebije S&P500” (Bartosz Kucia) — na screenach był tylko KOID (nr 3); sprawdzić pozostałe 6 i dopisać te z robotyki/automatyki/AI do sekcji ETF-ów
- [ ] wygenerować `roboty.html` i obejrzeć

## Do zrobienia w kodzie (mogę z telefonu)

- [ ] sekcja „ETF-y na humanoidy” na stronie: kurs, zwroty, trend, bez C/Z i marż
- [ ] KOID jako dodatkowy benchmark siły względnej dla spółek z listy
