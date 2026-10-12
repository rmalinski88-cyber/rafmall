# Wtyczki Claude Code w tym repo

Stan weryfikacji: 2026-10-12. Źródło listy: rolka matkowski.ai z 6.09.2026.

| Wtyczka | Źródło | Licencja | Popularność | Jak jest podpięta |
|---|---|---|---|---|
| claude-code-setup | anthropics/claude-plugins-official | Anthropic, oficjalna | 195 067 instalacji | `enabledPlugins` w `settings.json` (lokalnie) |
| claude-mem | thedotmack/claude-mem | Apache-2.0 | ~100k gwiazdek | `enabledPlugins` w `settings.json` (lokalnie) |
| headroom | headroomlabs-ai/headroom | Apache-2.0 | ~75k gwiazdek | `enabledPlugins` w `settings.json` (lokalnie) + CLI |
| task-observer | rebelytics/one-skill-to-rule-them-all | CC-BY-4.0 | ~3,3k gwiazdek | skopiowany do `.claude/skills/task-observer` (działa lokalnie i w chmurze) |
| OmniRoute | diegosouzapw/OmniRoute | MIT | ~75k gwiazdek | nie dodano, patrz niżej |

## Jak to działa

`.claude/settings.json` rejestruje marketplace'y i włącza trzy wtyczki dla każdego, kto
otworzy to repo lokalnie w Claude Code (po zaakceptowaniu dialogu zaufania folderu).
Sesje w chmurze (claude.ai/code) nie ładują wtyczek z tego pliku. To ograniczenie Claude Code.
Ładują za to skille z `.claude/skills/`, dlatego Task Observer jest wgrany jako skill.

Task Observer:

- skill: `.claude/skills/task-observer/` (wersja 3.6.0, commit 56e8907 z repo autora, CC-BY-4.0,
  autor Eoghan Henn, rebelytics.com). Aktualizacja: skopiuj `SKILL.md`, `references/`, `scripts/`.
- workspace: `.claude/task-observer-workspace/` (log obserwacji, propozycje zmian skilli).
  Autor zaleca ścieżkę poza repo, ale tu obserwacje mają wędrować z gitem.
- aktywacja: blok w `CLAUDE.md` plus hook SessionStart `.claude/hooks/task-observer-session-start.sh`,
  który wstrzykuje przypomnienie, liczbę otwartych obserwacji i datę ostatniego przeglądu.
- opcjonalnie: hook Stop z `references/environments.md` (blokuje zakończenie sesji bez wpisu w logu).
  Nie dodano, bo jest inwazyjny.

## Co trzeba zrobić raz na własnym komputerze

claude-mem: przy pierwszym starcie instalator proponuje logowanie w przeglądarce (30-dniowy trial
hostowanej pamięci, potem wraca na plan Anthropic). Pominięcie: `CLAUDE_MEM_ONLINE_OPTIN=false`.
Instalator dociąga Bun i uv. Wymaga Node.js 20+.

headroom: sama wtyczka to tylko hooki startowe. Kompresję daje CLI:

```
uv tool install --python 3.13 "headroom-ai[all]"
headroom wrap claude
```

Telemetria anonimowa jest domyślnie włączona. Wyłączenie: `HEADROOM_BEACON=off`.
`headroom wrap claude` dopisuje serwer MCP Serena do `~/.claude.json` (pominięcie: `--code-memory none`).

Jeśli `/plugin` pokaże "enabled in project settings but isn't installed", uruchom:

```
claude plugin install <nazwa>@<marketplace> --scope project
```

## Pominięte: OmniRoute

OmniRoute nie jest wtyczką Claude Code. To lokalna bramka AI, która przekierowuje ruch Claude Code
do innych dostawców modeli, w tym darmowych tierów. Sam projekt oznacza część dostawców flagą
`tos: avoid`. Jedyna wtyczka do Claude Code to projectsaibg/omniroute-claude-plugin od firmy
trzeciej (Enlace Enterprises): rejestruje serwer MCP pod `http://localhost:20128` i bez
działającego OmniRoute nic nie robi. Jeśli chcesz: `npm i -g omniroute`, potem `omniroute run claude`.
