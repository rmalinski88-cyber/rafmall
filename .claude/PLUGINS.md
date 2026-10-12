# Wtyczki Claude Code w tym repo

Plik `.claude/settings.json` deklaruje marketplace'y i włącza wtyczki dla każdego,
kto otworzy to repo lokalnie w Claude Code (po zaakceptowaniu dialogu zaufania folderu).
Sesje w chmurze (claude.ai/code) nie ładują wtyczek z tego pliku. To ograniczenie Claude Code.

Stan weryfikacji: 2026-10-12.

| Wtyczka | Źródło | Licencja | Popularność | Uwagi |
|---|---|---|---|---|
| claude-code-setup | anthropics/claude-plugins-official | Anthropic | 195 067 instalacji | Oficjalna. Tylko analizuje repo i proponuje hooki, skille, MCP. |
| claude-mem | thedotmack/claude-mem | Apache-2.0 | ~100k gwiazdek | Pamięć między sesjami. Hooki: SessionStart, UserPromptSubmit, PostToolUse, Stop, SessionEnd. Worker w tle, SQLite + Chroma lokalnie. |
| headroom | headroomlabs-ai/headroom | Apache-2.0 | ~75k gwiazdek | Sama wtyczka to tylko hooki startowe. Kompresję daje CLI w Pythonie (`headroom-ai`). |
| task-observer | rebelytics/one-skill-to-rule-them-all | CC-BY-4.0 | ~3.3k gwiazdek | Skill obserwujący sesje. Wymaga bloku aktywacyjnego w CLAUDE.md ze ścieżką absolutną. |

## Instalacja na własnym komputerze

Wtyczki ze źródłem relatywnym (claude-code-setup, claude-mem, headroom) ładują się same
po zaufaniu folderowi. task-observer ma źródło zewnętrzne i trzeba go dociągnąć ręcznie:

```
claude plugin install task-observer@one-skill-to-rule-them-all --scope project
```

Jeśli `/plugin` pokaże błąd "enabled in project settings but isn't installed", uruchom
analogiczną komendę dla danej wtyczki.

## Co jeszcze trzeba zrobić ręcznie

claude-mem: instalator proponuje logowanie w przeglądarce (30-dniowy trial hostowanego
"observera"). Można pominąć: `CLAUDE_MEM_ONLINE_OPTIN=false`. Instalator dociąga Bun i uv.
Wymaga Node.js 20+.

headroom: zainstaluj CLI i owiń Claude Code:

```
uv tool install --python 3.13 "headroom-ai[all]"
headroom wrap claude
```

Telemetria anonimowa jest domyślnie włączona. Wyłączenie: `HEADROOM_BEACON=off`.
`headroom wrap claude` dopisuje też serwer MCP Serena do `~/.claude.json`
(pominięcie: `--code-memory none`).

task-observer: skopiuj blok aktywacyjny z `references/environments.md` w repo autora
do CLAUDE.md i wstaw ścieżkę absolutną do folderu obserwacji. Bez tego skill rzadko się odpala.

## Pominięte: OmniRoute

OmniRoute (diegosouzapw/OmniRoute, MIT, ~75k gwiazdek) nie jest wtyczką Claude Code.
To lokalna bramka AI, która przekierowuje ruch Claude Code do innych dostawców modeli.
Jedyna "wtyczka" to projectsaibg/omniroute-claude-plugin od firmy trzeciej (Enlace Enterprises):
rejestruje serwer MCP pod `http://localhost:20128` i bez działającego OmniRoute nic nie robi.
Nie dodano. Jeśli chcesz, uruchom `npm i -g omniroute` i `omniroute run claude` na własnym komputerze.
