#!/usr/bin/env python3
"""Vigila documentos de Office y regenera su PDF cada vez que cambian (al guardar).

Pensado para correr en segundo plano (WSL). Sondea los mtime cada --every segundos (no usa inotify
porque no es fiable sobre /mnt/*) y, cuando un archivo cambia, lo convierte a PDF con word_a_pdf.py
(Word/PowerPoint en segundo plano). Sirve para: TRABAJO-DE-GRADO.docx, el manual de usuario, los
tripticos/bipticos y la presentacion .pptx.

Uso:
    python3 watch_a_pdf.py --dir CARPETA           # vigila lo que declara su defensa.json, para siempre
    python3 scripts/watch_a_pdf.py --once          # una pasada y sale
    python3 scripts/watch_a_pdf.py --only archivo.docx [mas...]   # solo esos (ignora la lista)
    python3 scripts/watch_a_pdf.py --every 15 --outdir DIR

Dejarlo corriendo:  nohup python3 scripts/watch_a_pdf.py >/tmp/watch_a_pdf.log 2>&1 &
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from word_a_pdf import convertir, tipo  # noqa: E402

def objetivos_de_config() -> list[str]:
    """Los .docx/.pptx que declara defensa.json: el TG, el manual oficial y los archivos de cada entregable."""
    import config

    cfg = config.cargar()
    base = Path(cfg["_base"])
    rutas = [cfg["fuentes"].get("tg")] + [cfg.get("manual_oficial")]
    rutas += [a for e in cfg["entregables"] for a in e["archivos"]]
    propios = set()  # el documento de anexos lo convierte su propio pipeline (watch_anexos.py)
    if cfg.get("anexos"):
        propios.add(str(config.ruta(cfg["anexos"]["dir"], base) / cfg["anexos"].get("documento", "anexos-qr.docx")))
    return sorted({str(config.ruta(r, base)) for r in rutas if r and Path(r).suffix.lower() in (".docx", ".pptx")} - propios)


def mtime(p: Path) -> float | None:
    try:
        return p.stat().st_mtime
    except OSError:
        return None


def pdf_de(src: Path, outdir: Path | None) -> Path:
    return (outdir / (src.stem + ".pdf")) if outdir else src.with_suffix(".pdf")


def procesar(src: Path, outdir: Path | None) -> bool:
    if not src.exists() or tipo(src.suffix) is None:
        return False
    time.sleep(3)  # deja que Office termine de escribir
    try:
        return convertir(src, outdir)
    except Exception as exc:  # noqa: BLE001
        print(f"   error al convertir {src}: {exc}")
        return False


def main() -> None:
    ap = argparse.ArgumentParser(description="Regenera el PDF de un docx/pptx cuando cambia.")
    ap.add_argument("extras", nargs="*", help="archivos adicionales a vigilar")
    ap.add_argument("--every", type=int, default=20, help="segundos entre sondeos (def. 20)")
    ap.add_argument("--outdir", default=None, help="carpeta de salida (def. junto al archivo)")
    ap.add_argument("--once", action="store_true", help="una sola pasada y sale")
    ap.add_argument("--only", action="store_true", help="usar solo los archivos pasados (ignora defensa.json)")
    ap.add_argument("--dir", help="carpeta de defensa (la lee config.py)")
    args = ap.parse_args()

    outdir = Path(args.outdir) if args.outdir else None
    base = args.extras if args.only else objetivos_de_config() + args.extras
    targets = [Path(p) for p in base]

    print("Vigilando:")
    for t in targets:
        print("  -", t, "" if t.exists() else "(aun no existe)")

    vistos: dict[str, float] = {}

    def pasada(inicial: bool) -> None:
        for src in targets:
            m = mtime(src)
            if m is None:
                continue
            pdf = pdf_de(src, outdir)
            pm = mtime(pdf)
            cambio = vistos.get(str(src)) != m
            desactualizado = pm is None or pm < m
            if (inicial and desactualizado) or (not inicial and cambio):
                print(f"\n[{time.strftime('%H:%M:%S')}] cambio detectado: {src.name}")
                if procesar(src, outdir):
                    vistos[str(src)] = m
            else:
                vistos[str(src)] = m

    pasada(inicial=True)
    if args.once:
        return
    print("\nVigilando cambios… (Ctrl+C para salir)")
    while True:
        time.sleep(args.every)
        pasada(inicial=False)


if __name__ == "__main__":
    main()
