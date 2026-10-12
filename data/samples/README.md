Prawdziwe notowania zapisane z `python -m tracker dump SYMBOL` (GitHub Actions, zadanie `dump`).
Służą do `python -m tracker --provider samples replay SYMBOL` bez dostępu do sieci
i do testów akceptacyjnych reguł (`tests/test_market_samples.py`).

- `ARB11841-USD` — Arbitrum (przykład użytkownika: impuls 19 sie 2026, wejście 26 sie 2026). `ARB-USD` to inny, martwy token.
- `OP-USD` — Optimism; `BTC-USD`, `ETH-USD`, `SOL-USD`; akcje: KOID, MP, MU, NBIS, NVDA, QS, SPY, TSLA.

Plik zawiera tylko wiersze `data,open,high,low,close,volume`; ostrzeżenia yfinance z logu nie należą do CSV.
