---
id: 4
title: "Użytkownik chce, żeby sesja decydowała sama, gdy czegoś nie wie — zamiast dopytywać lub wystawiać opcje"
status: open
type: internal
skill: []
proposes_skill: []
target_file: ["CLAUDE.md"]
siblings_checked: "none — cel to plik instrukcji repo, nie skill; rejestru skill-families.md brak"
area: "CLAUDE.md — zasady pracy, sposób podejmowania decyzji przez sesje"
date: 2026-10-12
session_context: "Konfiguracja wtyczek Claude Code (gałąź setup/wtyczki); po serii komunikatów z opcjami i pytaniami użytkownik napisał: zrób to tak, jak ty byś zrobił, i ogólnie tę zasadę zachowaj — jak czegoś nie wiesz, zrób tak, jak ty byś zrobił"
parked_until:
resolved:
resolution:
reference:
commands_verified: none
---

**Issue:** W trakcie konfiguracji wtyczek sesja kilka razy zatrzymywała się z pytaniem lub listą opcji (logowanie do claude-mem tak/nie, flaga `--code-memory none` dla Headrooma, karta instalacji zamiast decyzji). Użytkownik odebrał to jako przerzucanie decyzji na niego i wprost poprosił, żeby sesja rozstrzygała sama według własnego osądu, gdy brakuje jej informacji. Prośba dotyczy ogólnie stylu pracy, nie jednego zadania.

**Suggested improvement:** Dopisać w `CLAUDE.md` (sekcja zasad pracy) jedną regułę, po zatwierdzeniu przez użytkownika w przeglądzie: „Gdy czegoś nie wiesz, zdecyduj sam tak, jak zrobiłby to doświadczony kolega, powiedz jedną linią, co założyłeś, i idź dalej. Pytaj tylko, gdy błędna decyzja byłaby nieodwracalna (kasowanie, wysyłka na zewnątrz, pieniądze)." Zasada nie dotyczy sekretów (sekcja „Sekrety") ani działań nieodwracalnych.

**Principle:** Dla użytkownika nietechnicznego lista opcji jest kosztem, nie wartością. Sesja ma podejmować rutynowe decyzje sama i raportować założenia, a dopytywać wyłącznie przy ryzyku nieodwracalnej szkody.
