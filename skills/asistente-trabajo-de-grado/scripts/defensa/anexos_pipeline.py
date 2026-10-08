#!/usr/bin/env python3
"""Pipeline completo de anexos con QR:

  anexos-qr.docx  ->  PDF  ->  dividir por anexo  ->  subir a Drive  ->  QR  ->  QR-ANEXOS.docx

Uso: python3 scripts/anexos_pipeline.py
Requiere el documento de anexos (clave anexos.documento de defensa.json, en anexos.dir).
Lleva un lock para no solaparse si corre dos veces (p. ej. el vigilante + un rebuild manual).
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

_CFG = config.cargar()
BASE = config.clave(_CFG, "anexos.dir", "Es la carpeta de los anexos con QR (manifiesto, documento y salidas).")
DOCUMENTO = BASE / _CFG["anexos"].get("documento", "anexos-qr.docx")
SCRIPTS = Path(__file__).resolve().parent
LOCK = BASE / ".pipeline.lock"
LOCK_MAX_S = 900  # si el lock es mas viejo que esto, se asume colgado
UV = shutil.which("uv") or str(Path.home() / ".local/bin/uv")  # systemd no trae ~/.local/bin


def run(*cmd: str) -> None:
    print("$", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True)


def tomar_lock() -> bool:
    if LOCK.exists():
        edad = time.time() - LOCK.stat().st_mtime
        if edad < LOCK_MAX_S:
            print(f"pipeline ya en curso (lock de {edad:.0f}s); salgo")
            return False
        LOCK.unlink(missing_ok=True)
    LOCK.write_text(str(os.getpid()), encoding="utf-8")
    return True


def soltar_lock() -> None:
    LOCK.unlink(missing_ok=True)


def main() -> None:
    docx = DOCUMENTO
    d = ["--dir", str(config.carpeta())]
    if not docx.exists():
        sys.exit(f"Falta {docx}. Crealo (o pedime que lo armemos) antes de correr el pipeline.")
    if not tomar_lock():
        return
    try:
        pdf = docx.with_suffix(".pdf")
        run("python3", str(SCRIPTS / "word_a_pdf.py"), str(docx), "--outdir", str(BASE))
        run(UV, "run", "--with", "pypdf", "python", str(SCRIPTS / "anexos_dividir.py"), str(pdf), *d)
        run("python3", str(SCRIPTS / "drive_subir.py"), *d)
        run(UV, "run", "--with", "qrcode", "--with", "pillow", "--with", "python-docx",
            "python", str(SCRIPTS / "anexos_qr.py"), *d)
        print("\nListo: PDF por anexo subidos y QR-ANEXOS.docx actualizado.")
    finally:
        soltar_lock()


if __name__ == "__main__":
    main()
