# Wskaźnik TradingView „Rafmall konfluencja”

Te same reguły, które liczy `python -m tracker alerts`, narysowane na wykresie
i podpięte pod alerty TradingView, które same wysyłają wiadomość na Discord.
Bot skanuje szeroko (141 instrumentów co godzinę); TradingView pilnuje
w czasie rzeczywistym tych kilku, które wybierzesz.

## Instalacja (raz)

1. TradingView → na dole **Pine Editor** → wklej zawartość `rafmall_konfluencja.pine`.
2. **Zapisz** → **Dodaj do wykresu**.
3. Na wykresie pojawią się: SMA50/200, przerywane linie poziomów (czerwone =
   opór, zielone = wsparcie), żółte świece przy skoku wolumenu, różowe przy
   konfluencji, trójkąty przy przebiciu poziomu.

## Alert na Discord (raz na symbol)

1. Discord → ustawienia kanału → Integracje → Webhooki → Nowy webhook → kopiuj URL.
2. TradingView → dzwonek **Alert** → Warunek: **Rafmall konfluencja** →
   **Dowolna funkcja alert()**.
3. Zakładka **Powiadomienia** → zaznacz **Webhook URL** → wklej adres Discorda.
4. Wygaśnięcie: „Bez końca” (Premium na to pozwala). Zapisz.

Wiadomość jest już w formacie JSON, którego Discord oczekuje, więc nie trzeba
nic wpisywać w polu „Wiadomość”.

Powtórz dla każdego symbolu, który chcesz pilnować w czasie rzeczywistym.
Premium daje 400 alertów, więc portfel + okazje spokojnie się mieszczą.

## Które symbole (propozycja)

Interwał **1D**. Alert per symbol, „Dowolna funkcja alert()”, webhook Discorda:

- portfel — wszystko z `data/portfolio.csv`,
- okazje — MU, ASML, NBIS, NVDA, TSLA, KOID (+ NTNX, jeśli potwierdzisz „X” z reela),
- krypto — ARB/USDT (Binance), BTC, ETH, SOL.

Reszta list (141 instrumentów) zostaje w bocie co godzinę — tam nie trzeba
klikać alertów ręcznie.

## Co jest wspólne z botem, a co inne

| | bot (`tracker alerts`) | TradingView |
|---|---|---|
| zasięg | wszystkie listy, 141 instrumentów | tylko symbole z ustawionym alertem |
| częstotliwość | co godzinę (cron) | natychmiast, przy zamknięciu świecy |
| dane | Yahoo, opóźnienie ~15 min | czas rzeczywisty |
| reguły | wolumen, ruch, wybicie 52T, SMA, poziomy, okazje, smart money, konfluencja | wolumen, ruch, SMA, poziomy, konfluencja |
| okazje zakupowe i insiderzy | tak | nie (TradingView nie ma tych danych) |

Interwał: na dziennym (1D) wskaźnik odpowiada 1:1 regułom bota. Na 1H
działa tak samo, ale będzie głośniejszy — rozważ wyższy próg wolumenu.

## Pierwszy test

Wskaźnik był pisany bez dostępu do TradingView. Jeśli Pine Editor pokaże
błąd kompilacji, skopiuj komunikat (numer linii i treść) i wyślij mi — poprawię.
