#!/usr/bin/env python3
"""Crea el perfil de un docente nuevo (cualquier rol: tutor, revisor o docente de TG).

Uso:
  nuevo_docente.py --nombre "Nombre Apellido" --rol "Docente de TG" [--revisa "..."] [--alcance fondo|forma|ambos] [--vault <vault>]
      Catálogo local/público: el perfil lleva un código y las huellas del nombre, NUNCA el nombre; con --vault, el nombre se
      guarda solo en tu vault (wiki/docentes/_nombres.local.yaml). Después: asignar_evaluador.py --docente <código>.
  nuevo_docente.py <slug> --nombre "..." --rol "..." --privado
      (Mantenedor) catálogo privado: perfil con nombre y slug.
El perfil nace sin criterios; se llena con registrar_criterio.py.
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
    docente_publico_nuevo,
    guardar_nombre,
    rama_local,
    regenerar_moc,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug", nargs="?")
    ap.add_argument("--nombre", required=True)
    ap.add_argument("--rol", required=True)
    ap.add_argument("--revisa", default="por registrar")
    ap.add_argument("--alcance", default="por registrar", choices=["fondo", "forma", "ambos", "por registrar"])
    ap.add_argument("--vault", type=Path)
    ap.add_argument("--privado", action="store_true")
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    a = ap.parse_args()
    if not (a.catalogo / "docentes").is_dir():
        sys.exit(f"No encuentro el catálogo en {a.catalogo} (instalá con install.sh).")
    hoy = datetime.datetime.now().astimezone().date().isoformat()
    if a.privado:
        if not a.slug or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", a.slug):
            sys.exit("Con --privado hace falta un slug en minúsculas, sin tildes y con guiones (p. ej. apellido-apellido).")
        codigo, texto = a.slug, docente_nuevo(a.slug, a.nombre, a.rol, a.revisa, a.alcance, hoy)
    else:
        codigo, texto = docente_publico_nuevo(a.nombre, a.rol, a.revisa, a.alcance, hoy)
    destino = a.catalogo / "docentes" / f"{codigo}.md"
    if destino.exists():
        sys.exit(f"{destino.name} ya existe en el catálogo: vinculalo con asignar_evaluador.py --docente {codigo}")
    rama_local(a.catalogo)
    destino.write_text(texto, encoding="utf-8")
    regenerar_moc(a.catalogo)
    commit_local(a.catalogo, f"feat(docentes): perfil nuevo {codigo}")
    if a.vault and not a.privado:
        guardar_nombre(a.vault.resolve(), codigo, a.nombre)
    print(f"  ok    {destino.name} creado; vinculalo con asignar_evaluador.py --docente {codigo}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
