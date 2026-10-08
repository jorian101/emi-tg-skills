#!/usr/bin/env python3
"""Reconoce a TU docente en el catálogo, sin que su nombre salga de tu máquina.

Uso:
  resolver_docente.py "Nombre Apellido" [--catalogo carpeta] [--vault carpeta --guardar [--codigo d-xxxxxx]]
Calcula las huellas (SHA-256 con sal pública) de los pares de nombres y apellidos que escribiste y las busca en `claves` de
los perfiles del catálogo. Muestra código, rol, qué suele revisar y cuántos criterios tiene; con --guardar anota
código→nombre en `wiki/docentes/_nombres.local.yaml` de tu vault (ignorado por git) para ver el nombre en tus notas.
Cuantos más nombres y apellidos escribas, más segura la coincidencia (3 o más pares en común = coincidencia fuerte).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from catalogo_lib import (
    MIN_COINCIDENCIAS_AUTO,
    catalogo_default,
    claves_de_nombre,
    claves_del_catalogo,
    coincidencias,
    frontmatter,
    guardar_nombre,
)


def resumen(cat: Path, codigo: str) -> str:
    texto = (cat / "docentes" / f"{codigo}.md").read_text(encoding="utf-8")
    fm = frontmatter(texto)
    n = len(re.findall(r"^\| [A-Z]{2,}[A-Z0-9]*\d+ \|", texto, re.MULTILINE))
    return f"{codigo}  {fm.get('rol', '?')}  revisa: {fm.get('revisa', '?')} ({fm.get('alcance', '?')})  criterios: {n}"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("nombre")
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    ap.add_argument("--vault", type=Path)
    ap.add_argument("--guardar", action="store_true")
    ap.add_argument("--codigo")
    ap.add_argument("--huellas", action="store_true", help="solo imprime las huellas del nombre (para aportar un docente nuevo sin dar el nombre)")
    a = ap.parse_args()
    if a.huellas:
        print("\n".join(claves_de_nombre(a.nombre)))
        return 0
    if not (a.catalogo / "docentes").is_dir():
        sys.exit(f"No encuentro el catálogo en {a.catalogo}: instalalo con ./install.sh --catalogo-publico")
    cand = coincidencias(a.nombre, claves_del_catalogo(a.catalogo))
    if not cand:
        print("Sin coincidencias: ese docente todavía no está en el catálogo (se crea con nuevo_docente.py).")
        return 1
    for codigo, n in cand[:5]:
        fuerza = "fuerte" if n >= MIN_COINCIDENCIAS_AUTO else "débil"
        print(f"  {n} par(es), coincidencia {fuerza}: {resumen(a.catalogo, codigo)}")
    elegido = a.codigo or (cand[0][0] if len(cand) == 1 or cand[0][1] > cand[1][1] else None)
    if a.guardar:
        if not a.vault:
            sys.exit("--guardar necesita --vault")
        if not elegido:
            sys.exit("Hay empate entre varios: repetí con --codigo <código> o escribí más nombres y apellidos.")
        guardar_nombre(a.vault.resolve(), elegido, a.nombre)
        print(f"  ok    {elegido} = «{a.nombre}» guardado en tu vault (solo local)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
