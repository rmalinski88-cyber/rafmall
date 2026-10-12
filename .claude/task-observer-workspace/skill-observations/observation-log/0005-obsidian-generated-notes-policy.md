---
id: 5
title: "Skill sejfu nie mówi, jak traktować notatki generowane maszynowo (dziennik przebiegów, notatka per spółka) wobec reguły „jedna notatka = jeden temat”"
status: open
type: internal
skill: [sejf-obsidian]
proposes_skill: []
target_file: []
siblings_checked: "none — skill sejf-obsidian nie należy do żadnej rodziny; rejestru skill-families.md brak w tym workspace"
area: "Zasady treści (jedna notatka = jeden temat) i zasady techniczne (edycja w miejscu, nie odtwarzać z pamięci)"
date: 2026-10-12
session_context: "Budowa eksportu screenera do sejfu Rafmal1 (screener/report/obsidian.py): hub tematu, notatka per przebieg z datą, notatka per spółka z właściwościami; sesja chmurowa bez dostępu do sejfu i do Zasady sejfu.md"
parked_until:
resolved:
resolution:
reference: "screener/report/obsidian.py (docstring modułu) i README.md → „Eksport do Obsidiana”"
commands_verified: none
---

**Issue:** Eksport screenera pisze do sejfu notatki, których nie tworzy użytkownik, tylko program — i robi to wielokrotnie (co przebieg). Skill zna tylko notatki pisane ręcznie: reguła „jedna notatka = jeden temat, nie trzymaj kilku wersji” nie mówi, czy datowany dziennik przebiegów to „kilka wersji” czy osobne tematy, a reguła „edytuj w miejscu, nie odtwarzaj z pamięci” nie mówi, jak program ma współistnieć z ręcznymi dopiskami użytkownika w tej samej notatce. Sesja musiała to rozstrzygnąć sama: (1) hub tematu aktualizowany w miejscu + datowane notatki przebiegów jako osobne tematy, (2) treść generowana zamknięta między znacznikami `<!-- screener:start -->` / `<!-- screener:end -->`, wszystko poza nimi i nieznane właściwości należą do użytkownika, (3) istniejąca notatka o tej samej nazwie gdziekolwiek w sejfie (poza `99-Archiwum`) jest aktualizowana zamiast dublowana, (4) plik bez zmian nie jest zapisywany (iCloud). Decyzje są rozsądne, ale nie wynikają ze skilla, więc inna sesja mogłaby podjąć inne.

**Suggested improvement:** Dopisać do skilla krótką sekcję „Notatki generowane przez programy”: dziennik z datą w nazwie to osobny temat per data (nie „wersja”); treść generowana żyje w oznaczonym bloku i tylko ten blok wolno nadpisać; właściwości dopisane ręcznie i tagi użytkownika zostają; przed utworzeniem notatki sprawdzić, czy notatka o tej nazwie już istnieje poza archiwum, i wtedy dopisać blok do niej; nie zapisywać pliku, jeśli treść się nie zmieniła. Ostateczna wersja do uzgodnienia z `Zasady sejfu.md`, której sesja chmurowa nie widzi.

**Principle:** Reguły pisane z myślą o ręcznych notatkach milczą tam, gdzie pisze program: o powtarzalności, o własności fragmentów i o kolizjach nazw. Skill opisujący bazę wiedzy powinien wprost powiedzieć, jak generowana treść współistnieje z ręczną, bo inaczej każda sesja rozstrzyga to inaczej.
