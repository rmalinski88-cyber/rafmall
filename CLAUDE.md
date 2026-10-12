# rafmall — zasady pracy w tym repo

Nad tym repo pracuje **równolegle kilka sesji Claude** (Claude Code w chmurze,
Cowork na komputerze). Poniższe zasady istnieją po to, żeby sesje nie
nadpisywały sobie pracy. Każda sesja stosuje je bez pytania.

## Gałęzie

1. **Na początku każdej sesji** pobierz stan zdalny i nałóż na niego swoją gałąź:
   `git fetch origin && git pull --rebase` (na gałęzi, na której pracujesz).
   Jeśli po Twoim ostatnim pushu ktoś pchał na tę samą gałąź — scal, nie nadpisuj.
2. **Jedna sesja = jedna gałąź.** Nazwa: `<obszar>/<temat>`, np. `screener/obsidian`,
   `tracker/alerty`, `site/etf`. Nie pchaj na gałąź, na której pracuje inna sesja,
   chyba że użytkownik wyraźnie o to prosi.
3. **Gałąź integracyjna** to ta, którą GitHub pokazuje jako domyślną
   (dziś `claude/stock-search-tool-pkr8rw`; docelowo `main`). Trafiają na nią
   tylko gotowe kawałki z zielonymi testami, przez scalenie własnej gałęzi.
4. **Nigdy:** `push --force`, rebase cudzej gałęzi, usuwanie gałęzi, pomijanie testów,
   żeby „było zielone".

## Pliki wspólne — źródło konfliktów

`README.md`, `START.md`, `CLAUDE.md`, `config/default.yml`, `requirements.txt`,
`screener/cli.py`. Zmieniaj je **minimalnie i tylko w swojej sekcji**; nie
przeformatowuj cudzych fragmentów. Nową funkcję dopisuj jako osobny moduł,
a w pliku wspólnym zostaw jedną linię podpięcia.

## Przed każdym pushem

```bash
python -m pytest tests/ -q
```

Wszystkie testy muszą przechodzić. Commit opisuje **dlaczego**, nie tylko co.

## Obszary

| Katalog | Co to jest | Komenda |
|---|---|---|
| `screener/` | ranking spółek (fundamenty + technika), eksport do Obsidiana, strona `site` | `python -m screener run` |
| `tracker/` | Kongres, insiderzy, 13F, alerty, skan rynku, replay | `python -m tracker scan` |
| `tradingview/` | wskaźnik Pine Script z alertami na Discord | wklejany ręcznie w TradingView |
| `scripts/` | `first_run.py` (pierwsze uruchomienie), `publish.py` (FTP) | patrz `START.md` |
| `data/` | uniwersa spółek (CSV), listy obserwacyjne | edytowalne ręcznie |
| `tests/` | testy obu narzędzi | `python -m pytest tests/ -q` |

`START.md` to briefing dla użytkownika na pierwsze uruchomienie na komputerze.

## Dane i sieć

- Prawdziwe dane (Yahoo, SEC, TradingView) są dostępne **tylko lokalnie**.
  Środowisko chmurowe blokuje te hosty — w chmurze używaj `--provider fixture`
  i mów o tym wprost; nie udawaj wyników.
- Źródła nieoficjalne (np. skaner TradingView) mogą zniknąć bez ostrzeżenia:
  zawsze z zapasowym źródłem i bez logowania.

## Sekrety

- **Nigdy** nie proś użytkownika o wklejenie hasła, klucza API ani tokenu do czatu.
  Klucze idą do `.env` (jest w `.gitignore`) albo do sekretów środowiska.
- Nie commituj `.env`, `data/portfolio.csv`, plików z `out/`.

## Obsidian

Eksport (`python -m screener run --obsidian-vault ŚCIEŻKA`) pisze do sejfu
użytkownika. Reguły sejfu są w `screener/report/obsidian.py` (docstring) i w
`README.md` → „Eksport do Obsidiana". Źródłem prawdy co do formatu notatek jest
notatka `Zasady sejfu.md` w sejfie — jeśli sesja ma do niej dostęp, czyta ją
przed zmianą formatu eksportu.
