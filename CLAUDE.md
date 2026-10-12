# rafmall

Projekt w Pythonie: screener i tracker spółek (humanoidalna robotyka i tematy pokrewne),
alerty, eksport do Obsidiana i strony. Pierwsze uruchomienie opisuje `START.md`,
szczegóły w `README.md`. Testy: `python -m pytest tests`.

Wtyczki Claude Code dla tego repo opisuje `.claude/PLUGINS.md`.

## Task Observer (skill `.claude/skills/task-observer`)

Workspace skilla jest w repo, więc obserwacje wędrują z gitem:

- sesje w chmurze (claude.ai/code): `/home/user/rafmall/.claude/task-observer-workspace`
- lokalnie: `<katalog repo>/.claude/task-observer-workspace`, gdzie katalog repo to
  wynik `git rev-parse --show-toplevel`. Ustal go raz na początku sesji i dalej używaj
  tylko tej ścieżki absolutnej. Hook SessionStart podaje gotową ścieżkę.

Poniższy blok aktywacyjny pochodzi z `references/environments.md` skilla. `[ABSOLUTE PATH]`
oznacza ścieżkę ustaloną wyżej, `[PROJECTS ROOT]` to katalog nadrzędny repo.

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
