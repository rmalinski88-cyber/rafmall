# Notatki sesji — jak sesje Claude przekazują sobie pracę

Sesje Claude (aplikacja Claude w chmurze, Claude Code na komputerze) nie rozmawiają
ze sobą bezpośrednio i nie pamiętają siebie nawzajem. Jedyne, co mają wspólne, to to
repo. Dlatego każda sesja zostawia tu krótką notatkę, a następna zaczyna od jej
przeczytania.

## Zasady

1. **Jedna gałąź = jeden plik.** Nazwa pliku to nazwa gałęzi z `-` zamiast `/`,
   np. gałąź `tracker/alerty` → `.claude/sesje/tracker-alerty.md`. Każda sesja pisze
   tylko do swojego pliku, więc notatki nigdy nie powodują konfliktów przy scalaniu.
2. **Na początku sesji** (po `git pull --rebase`) przeczytaj wszystkie pliki w tym
   katalogu. Dowiesz się, kto nad czym pracuje i czego nie ruszać.
3. **Przed każdym pushem** zaktualizuj swój plik według szablonu poniżej.
4. **Po scaleniu gałęzi** ustaw `Stan: scalone`. Pliku nie usuwaj — zostaje jako ślad.
5. Notatka ma być krótka: stan i następny krok, bez opowiadania historii. Historia
   jest w commitach.
6. Żadnych sekretów ani ścieżek z dysku użytkownika — repo jest publiczne.

## Szablon

```markdown
# <nazwa gałęzi>

- **Stan:** w toku | czeka na użytkownika | gotowe do scalenia | scalone
- **Ostatnia zmiana:** RRRR-MM-DD, <chmura | komputer>
- **Cel:** jedno zdanie, co ta gałąź ma dać.

## Zrobione
- …

## Następny krok
- … (konkretnie: który plik, która komenda)

## Uwaga dla innych sesji
- Pliki, których teraz nie ruszać, i decyzje czekające na użytkownika.
```
