#!/usr/bin/env python3
"""Registra una corrección de un docente en el catálogo local (rama local/<usuario>), con estudiantes por iniciales.

Uso:
  registrar_criterio.py <docente> --criterio "texto" --fuente "informe a D.P., MP 15/05" [--capitulo marco práctico] [--estado confirmado]
  registrar_criterio.py <docente> --ocurrencia YAN3 --fuente "informe a J.S., MP 20/05"
Es el paso 4 de «registrar corrección» (perfil-revisor-tg). No toca el repo principal: para compartirlo, contribuir.py.
El criterio va en general (sin datos de un TG concreto); lo propio de tu TG se queda en tu vault.
"""

from __future__ import annotations

import argparse
import datetime
import sys
from pathlib import Path

from catalogo_lib import (
    aplicar_cambio,
    catalogo_default,
    commit_local,
    poner_campo,
    rama_local,
    regenerar_moc,
    sin_nombres_completos,
)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("docente")
    ap.add_argument("--criterio")
    ap.add_argument("--ocurrencia", metavar="ID")
    ap.add_argument("--fuente", required=True)
    ap.add_argument("--capitulo", default="—")
    ap.add_argument("--estado", default="confirmado", choices=["confirmado", "inferido", "abierto"])
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    a = ap.parse_args()
    if bool(a.criterio) == bool(a.ocurrencia):
        ap.error("indicá --criterio (nuevo) o --ocurrencia ID (suma una ocurrencia)")
    perfil = a.catalogo / "docentes" / f"{a.docente}.md"
    if not perfil.is_file():
        sys.exit(f"El catálogo no tiene a {a.docente}: crealo con nuevo_docente.py")
    nombres = sin_nombres_completos(a.fuente)
    if nombres:
        sys.exit(f"La fuente nombra a estudiantes completos ({', '.join(nombres)}): usá iniciales (D.P.).")
    rama_local(a.catalogo)
    cambio = ({"tipo": "criterio", "criterio": a.criterio, "estado": a.estado, "capitulo": a.capitulo,
               "fuente": a.fuente, "ocurrencias": 1} if a.criterio
              else {"tipo": "ocurrencia", "id": a.ocurrencia, "suma": 1, "fuente": a.fuente})
    try:
        texto, que = aplicar_cambio(perfil.read_text(encoding="utf-8"), a.docente, cambio)
    except KeyError as e:
        sys.exit(str(e))
    hoy = datetime.datetime.now().astimezone().date().isoformat()
    perfil.write_text(poner_campo(texto, "updated", hoy), encoding="utf-8")
    regenerar_moc(a.catalogo)
    commit_local(a.catalogo, f"feat(docentes): {que} de {a.docente}")
    print(f"  ok    {a.docente}: {que} (rama local; para compartirlo: contribuir.py --docente {a.docente})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
