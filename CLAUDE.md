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

## Przekazywanie pracy między sesjami

Sesje nie widzą siebie nawzajem — łączy je tylko to repo. Na początku sesji
przeczytaj notatki w `.claude/sesje/`, a przed każdym pushem zaktualizuj notatkę
swojej gałęzi. Zasady i szablon: `.claude/sesje/README.md`.

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
- Prawdziwe dane bez komputera: workflow `.github/workflows/rafmall.yml` (GitHub Actions).
  Klucze są w sekretach repo na GitHubie; opis w `README.md` → „Bez komputera: GitHub Actions".
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

## Wtyczki Claude Code

Wtyczki Claude Code dla tego repo opisuje `.claude/PLUGINS.md`.

### Task Observer (skill `.claude/skills/task-observer`)

Workspace skilla jest w repo, więc obserwacje wędrują z gitem:

- na komputerze użytkownika (Windows): `C:\Users\RR\projekty\rafmall\.claude\task-observer-workspace`,
  katalog nadrzędny repo: `C:\Users\RR\projekty`
- sesje w chmurze i każdy inny klon: `<katalog repo>/.claude/task-observer-workspace`, gdzie
  katalog repo to wynik `git rev-parse --show-toplevel`, a katalog nadrzędny repo to jego
  rodzic. W chmurze ścieżka klonu bywa różna (`/home/user/rafmall`, `/home/claude/rafmall`),
  więc nie wpisuj jej na sztywno. Ustal ją raz na początku sesji i dalej używaj tylko tej
  ścieżki absolutnej.
- Jeśli wyliczona ścieżka nie istnieje, to błąd — zgłoś go, nie twórz drugiego workspace'u.
  Gdy repo zostało dołączone w trakcie sesji, protokół startowy wykonaj od razu po
  pojawieniu się tego pliku w kontekście.

Poniższy blok aktywacyjny pochodzi z `references/environments.md` skilla. `[ABSOLUTE PATH]`
oznacza ścieżkę roboczą z listy wyżej, `[PROJECTS ROOT]` odpowiadający jej katalog nadrzędny.

```text
Before the first tool call of any session — and before writing or
proposing a plan, not merely before executing one — invoke the
task-observer skill AND execute its Session Start Protocol (storage
check, frontmatter scan, review trigger). Loading the skill and running
the protocol are separate steps; a session that loads the file and stops
has activated nothing. Any turn that will involve a tool call counts; do
not classify the session as "too simple" from its opening message.

Select skills on the DECISION the request is about, not on the artefact it
arrived as. Name what the user is deciding, then match the installed skill
descriptions against that — a request handed over as a file to review
still needs the skill whose description names its subject.

After completing each task, list the observation records written this
session in the same turn and report a one-line summary from that listing
(ids and titles, or "none logged and why") — never from memory of
writing them. This is the activation backstop: it forces a look at the log,
so a session that silently skipped the protocol is discovered at the
first task boundary instead of never.

Loading a skill is not complete until you have queried the observation
log for OPEN observations naming it and read their bodies:
  find "[ABSOLUTE PATH]/skill-observations/observation-log" -maxdepth 1 \
    -name '*.md' -exec grep -l "skill:.*<skill-name>" {} +
(<skill-name> is the bare name: drop a plugin: prefix, up to the last
colon.)
Apply their insights to the current work — meaning: let them change what
you do in THIS task. Editing the skill file, or writing the rule into any
other file a later session reads, is acting on the observation and waits
for the review. Run this at every skill load, however many skills load
in one session.

Where scripts run, the lookup and its checkpoint line are one command:
  bash "<skill directory>/scripts/skill-load.sh" "[ABSOLUTE PATH]" <skill-name>
The Skill invocation and that call are ONE batch — emit them together,
one call per skill loaded, never the call in a later batch.

The task-observer workspace for this project is:
  [ABSOLUTE PATH]
Every path the skill uses derives from that root and nothing else:
  [ABSOLUTE PATH]/skill-observations/observation-log/   (the log)
  [ABSOLUTE PATH]/skill-observations/cross-cutting-principles.md
  [ABSOLUTE PATH]/skill-updates/                        (staging root)
  [ABSOLUTE PATH]/skill-updates/PENDING.md              (staging manifest)
Never place the workspace inside a skills-discovery directory or any path
linked into one.

The user's repositories live under:
  [PROJECTS ROOT]

A subagent dispatched by a session that already runs this protocol does
not run it again and does not write to the log. The controller observes,
because only it sees the whole task and its review.
```
