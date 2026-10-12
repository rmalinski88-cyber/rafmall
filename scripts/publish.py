#!/usr/bin/env python3
"""Wgraj stronę na hosting przez FTP (dane z .env: FTP_HOST, FTP_USER, FTP_PASS, FTP_DIR).

    python scripts/publish.py                       # out/site/roboty.html -> FTP_DIR/roboty.html
    python scripts/publish.py --dry-run             # tylko pokaż, co by zrobił
    python scripts/publish.py inny.html --as index.html

Używa wyłącznie biblioteki standardowej (ftplib), działa na Windows/macOS/Linux.
FTP_TLS=1 (domyślnie) próbuje połączenia szyfrowanego, z powrotem do zwykłego FTP, gdy serwer go nie ma.
"""

from __future__ import annotations

import argparse
import os
import sys
from ftplib import FTP, FTP_TLS, error_perm
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from tracker.env import load_dotenv  # noqa: E402


def connect(host: str, user: str, password: str, use_tls: bool):
    if use_tls:
        try:
            ftp = FTP_TLS(host, timeout=30)
            ftp.login(user, password)
            ftp.prot_p()
            return ftp, "FTPS"
        except Exception as exc:  # fall back to plain FTP
            print(f"FTPS nie zadziałało ({exc}); próbuję zwykłego FTP.", file=sys.stderr)
    ftp = FTP(host, timeout=30)
    ftp.login(user, password)
    return ftp, "FTP"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("file", nargs="?", default="out/site/roboty.html")
    parser.add_argument("--as", dest="remote_name", help="nazwa pliku na serwerze (domyślnie jak lokalnie)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv()
    host, user, password = os.environ.get("FTP_HOST"), os.environ.get("FTP_USER"), os.environ.get("FTP_PASS")
    remote_dir = os.environ.get("FTP_DIR", "/")
    use_tls = os.environ.get("FTP_TLS", "1") not in ("0", "false", "no")
    local = Path(args.file)
    remote_name = args.remote_name or local.name

    if not local.exists():
        print(f"Brak pliku {local}. Najpierw: python -m screener ... site", file=sys.stderr)
        return 1
    if not (host and user and password):
        print("Brak FTP_HOST / FTP_USER / FTP_PASS w .env — wgraj plik ręcznie przez panel hostingu.", file=sys.stderr)
        return 2

    print(f"{local} ({local.stat().st_size // 1024} KB) -> {host}:{remote_dir}/{remote_name}")
    if args.dry_run:
        return 0

    ftp, mode = connect(host, user, password, use_tls)
    try:
        try:
            ftp.cwd(remote_dir)
        except error_perm:
            print(f"Katalog {remote_dir} nie istnieje na serwerze — sprawdź FTP_DIR.", file=sys.stderr)
            return 3
        with local.open("rb") as handle:
            ftp.storbinary(f"STOR {remote_name}", handle)
        print(f"Wgrano przez {mode}. Sprawdź: https://rafmall.ch/{remote_name}")
    finally:
        ftp.quit()
    return 0


if __name__ == "__main__":
    sys.exit(main())
