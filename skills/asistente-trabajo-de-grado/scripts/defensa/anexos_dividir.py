#!/usr/bin/env python3
"""Divide el PDF de anexos en un PDF por anexo, detectando las caratulas «ANEXO X: ...».

Uso: uv run --with pypdf python scripts/anexos_dividir.py <anexos.pdf> [outdir]
Salida: outdir/ANEXO-<X>.pdf (uno por anexo). No depende de numeros de pagina fijos.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

from pypdf import PdfReader, PdfWriter

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

_CFG = config.cargar()
BASE = config.clave(_CFG, "anexos.dir", "Es la carpeta de los anexos con QR (manifiesto, documento y salidas).")
DOCUMENTO = BASE / _CFG["anexos"].get("documento", "anexos-qr.docx")
MANIFIESTO = BASE / "manifiesto-anexos.json"


def pagina_caratula(texto: str, letra: str) -> bool:
    """True si la pagina es la portada del anexo: contiene 'ANEXO <letra>' (EN MAYUSCULAS)."""
    return re.search(rf"ANEXO\s+{re.escape(letra)}\b", texto) is not None


def main() -> None:
    args = config.args_sin_dir()
    pdf = Path(args[0])
    outdir = Path(args[1]) if len(args) > 1 else BASE / "anexos-sueltos"
    outdir.mkdir(parents=True, exist_ok=True)

    letras = [a["letra"] for a in json.loads(MANIFIESTO.read_text(encoding="utf-8"))["anexos"]]
    reader = PdfReader(str(pdf))
    textos = [(p.extract_text() or "") for p in reader.pages]

    # Portadas del PDF que el manifiesto no lista: sin esto se pegan al anexo anterior en silencio.
    en_pdf = {m.group(1) for t in textos if (m := re.match(r"\s*ANEXO\s+([A-Z]{1,2})\s*\n", t))}
    if sobran := sorted(en_pdf - set(letras)):
        sys.exit(f"ERROR: el PDF tiene portadas que el manifiesto no lista: {', '.join(sobran)}")

    inicios: list[tuple[str, int]] = []
    cursor = 0
    faltan = []
    for letra in letras:
        for i in range(cursor, len(textos)):
            if pagina_caratula(textos[i], letra):
                inicios.append((letra, i))
                cursor = i + 1
                break
        else:
            faltan.append(letra)
    if faltan:
        sys.exit(f"ERROR: no encontre la portada de los anexos {', '.join(faltan)} (¿cambio la letra en el docx?)")

    for viejo in outdir.glob("ANEXO-*.pdf"):  # que no sobreviva un PDF de otra corrida para subirlo
        viejo.unlink()

    for idx, (letra, ini) in enumerate(inicios):
        fin = inicios[idx + 1][1] if idx + 1 < len(inicios) else len(reader.pages)
        w = PdfWriter()
        for p in range(ini, fin):
            w.add_page(reader.pages[p])
        dest = outdir / f"ANEXO-{letra}.pdf"
        with open(dest, "wb") as f:
            w.write(f)
        print(f"  ANEXO {letra}: paginas {ini + 1}-{fin} -> {dest.name}")

    print(f"ok {len(inicios)} anexos en {outdir}")


if __name__ == "__main__":
    main()
