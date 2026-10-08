#!/usr/bin/env python3
"""(Mantenedor, una vez) Renumera los IDs de criterio de un catálogo a `CR<n>`, sin prefijos que delatan al docente.

Uso: migrar_ids_neutros.py <catalogo> [--dry-run]
Recorre `docentes/*.md`; cada fila de tabla cuyo primer campo es un ID con prefijo (YAN3, MAG2, TERF1…) pasa a `CR<n>`
en orden de aparición, y se reemplazan también las menciones sueltas en el texto («ver NAR1»). Idempotente: lo que ya es
`CR<n>` no se toca. Imprime el mapeo para que quede en el commit del mantenedor.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ID = re.compile(r"^\| ([A-Z]{2,}[A-Z0-9]*\d+) \|", re.MULTILINE)


def migrar(texto: str) -> tuple[str, dict[str, str]]:
    ids: list[str] = []
    for m in ID.finditer(texto):
        if m[1] not in ids:
            ids.append(m[1])
    nuevos = [i for i in ids if not re.fullmatch(r"CR\d+", i)]
    n = max((int(i[2:]) for i in ids if re.fullmatch(r"CR\d+", i)), default=0)
    mapa = {}
    for i in nuevos:
        n += 1
        mapa[i] = f"CR{n}"
    for viejo, nuevo in mapa.items():
        texto = re.sub(rf"\b{viejo}\b", nuevo, texto)
    return texto, mapa


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("catalogo", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    for p in sorted((a.catalogo / "docentes").glob("*.md")):
        texto, mapa = migrar(p.read_text(encoding="utf-8"))
        if mapa:
            print(f"  {p.name}: " + ", ".join(f"{v}←{k}" for k, v in mapa.items()))
            if not a.dry_run:
                p.write_text(texto, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
