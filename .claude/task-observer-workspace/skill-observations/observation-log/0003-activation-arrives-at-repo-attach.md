---
id: 3
title: "Repo dołączone w trakcie sesji — CLAUDE.md i skill docierają dopiero po dołączeniu, więc protokół startowy rusza po pierwszych wywołaniach narzędzi"
status: open
type: open-source
skill: [task-observer]
proposes_skill: []
target_file: []
siblings_checked: "none — rejestru skill-families.md brak; lista skilli tej sesji (skille repo i konta) przejrzana po nazwie i po temacie, brak rodzeństwa task-observer; sweep katalogu /home/claude dał 1 skill projektowy (task-observer)"
area: "references/environments.md — Activation config (late, intermittent) i lista przyczyn pominięcia startu"
date: 2026-10-12
session_context: "Podłączenie repo do działającej sesji chmurowej na prośbę użytkownika; instrukcje repo pojawiły się w kontekście w połowie pierwszej tury. Druga instancja (sesja claude/stock-search-tool-pkr8rw, 2026-10-12): repo było w sesji od początku, ale CLAUDE.md i skill task-observer dotarły dopiero po git pull w trakcie sesji (dodała je inna sesja), po kilkudziesięciu wywołaniach narzędzi; skill pojawił się na liście dopiero po pullu, protokół wykonano wtedy"
parked_until:
resolved:
resolution:
reference:
commands_verified: none
---

**Issue:** Sesja chmurowa wystartowała bez repozytorium. Użytkownik prosił o podłączenie repo, więc dołączono je dopiero w trakcie pierwszej tury: narzędzie dołączania repo, klon do `/home/claude/rafmall`, rejestracja katalogu repo. Do tej chwili w kontekście nie było ani `CLAUDE.md` z blokiem aktywacyjnym, ani skilla `task-observer` na liście dostępnych skilli. Jedno i drugie pojawiło się dopiero po rejestracji katalogu repo, po 7 wykonanych wywołaniach narzędzi tej tury; Session Start Protocol wykonano zaraz potem (ślad w `checkpoints.log`: workspace created=observation-log/archive,last-review-date.txt,cross-cutting-principles.md; scan files=0). Hook SessionStart nie zadziałał i nie mógł: sesja już trwała, a hook nie jest wpisany do aktywnego `settings.json` (obserwacja 0002). Przyczyna pominięcia według listy z `references/environments.md` („Log the cause, not just the miss"): *absent* — konfiguracja była nieosiągalna, bo repo nie było częścią sesji, i pojawiła się w połowie tury 1. To nie opóźnienie po stronie hosta ani pominięcie z nieuwagi. Z trzech możliwych ochron w grze była tylko „zapisane w repo": nic nie było załadowane do kontekstu ani wsparte checkpointem, więc reguła „przed pierwszym wywołaniem narzędzia" była tu niewykonalna z konstrukcji.

**Suggested improvement:** (1) Skill, `references/environments.md`, sekcja „Activation config — late, intermittent, and why the guard cannot live inside it": dopisać przypadek „repozytorium dołączone do już działającej sesji" — plik instrukcji projektu, lista skilli i hooki projektu pojawiają się w chwili dołączenia, nigdy na starcie, a hook startowy nie odpala się wstecz. Reguła: za początek sesji dla protokołu uznać chwilę, w której instrukcje repo trafiają do kontekstu; wykonać wtedy Session Start Protocol w całości i zalogować przyczynę razem z liczbą wywołań narzędzi, które go wyprzedziły. (2) Po stronie adoptera: linia aktywacyjna w kanale obecnym od pierwszej tury niezależnie od repo (instrukcje lub preferencje na poziomie konta — „tier 2" z tej samej sekcji), bo `CLAUDE.md` w repo nie obejmuje sesji, które zaczynają się bez repo.

**Principle:** Konfiguracja aktywacyjna przechowywana w repozytorium chroni tylko sesje, które startują razem z nim. Gdy repozytorium dołącza w trakcie sesji, początkiem sesji dla protokołu jest chwila pojawienia się jego instrukcji w kontekście; wszystko wcześniejsze jest nieobserwowane z konstrukcji, a jedyną ochroną od pierwszej tury jest kanał niezależny od repozytorium.

**Druga instancja (2026-10-12, sesja claude/stock-search-tool-pkr8rw):** ta sama przyczyna *absent*, inny mechanizm — repo było częścią sesji od startu, lecz `CLAUDE.md` z blokiem aktywacyjnym i katalog `.claude/skills/task-observer` powstały później w innej sesji i dotarły do tej dopiero z `git pull` (ok. 40 wywołań narzędzi po starcie). Lista skilli sesji zaktualizowała się dopiero po pullu; protokół startowy (probe, scan, review trigger) wykonano w tym momencie. Wniosek do tej samej poprawki: „początek sesji dla protokołu" to także chwila, w której pull wnosi konfigurację aktywacyjną do istniejącego klonu — nie tylko dołączenie repo.
