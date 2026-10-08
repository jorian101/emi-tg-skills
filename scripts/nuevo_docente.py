#!/usr/bin/env python3
"""Crea el perfil de un docente nuevo en el catálogo local (cualquier rol: tutor, revisor o docente de TG).

Uso: nuevo_docente.py <slug> --nombre "Grado Nombre Apellido" --rol "Docente de TG" [--revisa "..."] [--alcance fondo|forma|ambos]
El perfil nace sin criterios; se llena con registrar_criterio.py y se vincula con asignar_evaluador.py.
"""

from __future__ import annotations

import argparse
import datetime
import re
import sys
from pathlib import Path

from catalogo_lib import (
    catalogo_default,
    commit_local,
    docente_nuevo,
    rama_local,
    regenerar_moc,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--rol", required=True)
    ap.add_argument("--revisa", default="por registrar")
    ap.add_argument("--alcance", default="por registrar", choices=["fondo", "forma", "ambos", "por registrar"])
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    a = ap.parse_args()
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
        sys.exit("El slug va en minúsculas, sin tildes y con guiones (p. ej. apellido-apellido).")
    destino = a.catalogo / "docentes" / f"{a.slug}.md"
    if destino.exists():
        sys.exit(f"{destino.name} ya existe en el catálogo.")
    if not (a.catalogo / "docentes").is_dir():
        sys.exit(f"No encuentro el catálogo en {a.catalogo} (instalá con install.sh).")
    rama_local(a.catalogo)
    hoy = datetime.datetime.now().astimezone().date().isoformat()
    destino.write_text(docente_nuevo(a.slug, a.nombre, a.rol, a.revisa, a.alcance, hoy), encoding="utf-8")
    regenerar_moc(a.catalogo)
    commit_local(a.catalogo, f"feat(docentes): perfil nuevo de {a.slug}")
    print(f"  ok    {destino.name} creado; vinculalo con asignar_evaluador.py --docente {a.slug}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
