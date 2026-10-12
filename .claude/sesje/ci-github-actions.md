# ci/github-actions

- **Stan:** w toku
- **Ostatnia zmiana:** 2026-10-12, chmura
- **Cel:** uruchamiać screener i tracker na prawdziwych danych bez komputera użytkownika.

## Zrobione
- Workflow `.github/workflows/rafmall.yml`: harmonogram (alerts, market, scan) i ręczne uruchamianie.
- Opis w `README.md` („Bez komputera: GitHub Actions") i jedna linia w `CLAUDE.md`.

## Następny krok
- Pierwszy ręczny przebieg `check` i `screener` na GitHubie; sprawdzić, czy Yahoo odpowiada z serwerów GitHuba.

## Uwaga dla innych sesji
- Sekrety (`SEC_USER_AGENT`, `QUIVER_API_KEY`, `DISCORD_WEBHOOK_URL`, `FTP_*`) wpisuje użytkownik na GitHubie. Nie prosić o nie na czacie.
- Workflow celowo nie używa `data/portfolio.csv`: logi publicznego repo są publiczne.
