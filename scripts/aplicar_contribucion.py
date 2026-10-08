#!/usr/bin/env python3
"""(Mantenedor) Integra una contribución de criterios al catálogo principal.

Uso:
  aplicar_contribucion.py <issue-numero|archivo.md> [--repo owner/nombre] [--commit]
Lee el bloque ```yaml``` que genera contribuir.py, crea los docentes nuevos, suma criterios y ocurrencias y completa el
historial de roles. Corré esto en `main` del catálogo; con --commit hace el commit (sin push). Revisá el diff antes.
"""

from __future__ import annotations

import argparse
import datetime
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from catalogo_lib import (
    aplicar_cambio,
    catalogo_default,
    commit_local,
    docente_nuevo,
    git,
    poner_campo,
    regenerar_moc,
    sin_nombres_completos,
)


def leer(origen: str, repo: str | None) -> str:
    if Path(origen).is_file():
        return Path(origen).read_text(encoding="utf-8")
    if not shutil.which("gh"):
        sys.exit("Para leer un issue hace falta `gh`; pasá un archivo .md.")
    cmd = ["gh", "issue", "view", origen, "--json", "body", "-q", ".body"] + (["--repo", repo] if repo else [])
    r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if r.returncode:
        sys.exit(r.stderr.strip())
    return r.stdout


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("origen")
    ap.add_argument("--repo")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    a = ap.parse_args()
    cat = a.catalogo
    m = re.search(r"```yaml\n(.*?)```", leer(a.origen, a.repo), re.DOTALL)
    if not m:
        sys.exit("No encuentro el bloque ```yaml``` de la contribución.")
    datos = yaml.safe_load(m[1])
    rama = git(cat, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if rama.startswith("local/"):
        print(f"  aviso estás en {rama}: integrá en main del catálogo para que el cambio sea el oficial")
    hoy = datetime.datetime.now().astimezone().date().isoformat()
    resumen = []
    for d in datos["docentes"]:
        slug, perfil = d["docente"], cat / "docentes" / f"{d['docente']}.md"
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
            sys.exit(f"Slug inválido: {slug}")
        if not perfil.exists():
            n = d.get("nuevo") or sys.exit(f"{slug} no existe y la contribución no lo declara como nuevo")
            perfil.write_text(docente_nuevo(slug, n["nombre"], n["rol"], n.get("revisa", "por registrar"),
                                            n.get("alcance", "por registrar"), hoy), encoding="utf-8")
        texto = perfil.read_text(encoding="utf-8")
        for k, v in (d.get("meta") or {}).items():
            texto = poner_campo(texto, k, str(v))
        for c in d["cambios"]:
            nombres = sin_nombres_completos(c.get("fuente", "") + " " + c.get("estudiante", ""))
            if nombres:
                sys.exit(f"{slug}: la fuente nombra a {nombres}; devolvé la contribución para que use iniciales")
            texto, que = aplicar_cambio(texto, slug, c)
            resumen.append(f"{slug}: {que}")
        perfil.write_text(poner_campo(texto, "updated", hoy), encoding="utf-8")
    regenerar_moc(cat)
    print("\n".join(f"  ok    {r}" for r in resumen))
    if a.commit:
        print("  ok    commit" if commit_local(cat, f"feat(docentes): contribución {a.origen}") else "  ya    sin cambios")
    else:
        print(git(cat, "diff", "--stat").stdout.strip() + "\n(revisá y commiteá, o repetí con --commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
