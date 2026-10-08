#!/usr/bin/env python3
"""Vigila ANEXOS-QR/anexos-qr.docx: al guardarlo, corre el pipeline
(PDF -> dividir -> subir a Drive -> actualizar QR-ANEXOS.docx).

Uso: python3 scripts/watch_anexos.py [--every 20] [--once]
Queda como servicio systemd --user (watch-anexos.service).
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

_CFG = config.cargar()
BASE = config.clave(_CFG, "anexos.dir", "Es la carpeta de los anexos con QR (manifiesto, documento y salidas).")
DOCUMENTO = BASE / _CFG["anexos"].get("documento", "anexos-qr.docx")
DOCX = DOCUMENTO
PDF = DOCX.with_suffix(".pdf")
PIPELINE = Path(__file__).resolve().parent / "anexos_pipeline.py"


def mtime(p: Path) -> float | None:
    try:
        return p.stat().st_mtime
    except OSError:
        return None


def correr() -> None:
    time.sleep(3)  # deja que Word termine de escribir
    subprocess.run(["python3", str(PIPELINE), "--dir", str(config.carpeta())], check=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--every", type=int, default=20)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--dir", help="carpeta de defensa (la lee config.py)")
    args = ap.parse_args()

    print(f"Vigilando {DOCX} (cada {args.every}s)", flush=True)
    visto = mtime(DOCX)
    if args.once:
        if visto is not None and (mtime(PDF) is None or mtime(PDF) < visto):
            correr()
        return
    while True:
        time.sleep(args.every)
        m = mtime(DOCX)
        if m is not None and m != visto:
            print(f"[{time.strftime('%H:%M:%S')}] cambio detectado en {DOCX.name}", flush=True)
            visto = m  # antes de correr: un guardado durante la corrida dispara otra
            correr()


if __name__ == "__main__":
    main()
