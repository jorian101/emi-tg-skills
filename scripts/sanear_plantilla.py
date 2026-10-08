#!/usr/bin/env python3
"""Sanea una plantilla de Office (.docx/.pptx) antes de publicarla: borra autor, último editor, título y empresa de sus propiedades.

Uso: sanear_plantilla.py <entrada> <salida> [--nombres-de <catalogo-privado>]
Con --nombres-de, además falla (sin escribir) si en el texto o las propiedades queda algún nombre o apellido de un docente
del catálogo privado. Nunca modifica el archivo de entrada.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from catalogo_lib import nombres_en, nombres_privados, sanear_oficina, texto_de_oficina


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--nombres-de", type=Path)
    a = ap.parse_args()
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    sanear_oficina(a.entrada, a.salida)
    if a.nombres_de:
        hallazgos = nombres_en(texto_de_oficina(a.salida), nombres_privados(a.nombres_de))
        if hallazgos:
            a.salida.unlink()
            sys.exit(f"{a.entrada.name}: quedan nombres de docentes en el archivo ({', '.join(hallazgos)}); no se escribió la salida")
    print(f"  ok    {a.salida.name} sin propiedades de persona")
    return 0


if __name__ == "__main__":
    sys.exit(main())
