#!/usr/bin/env python3
"""(Mantenedor) Integra una contribución de criterios al catálogo principal.

Uso:
  aplicar_contribucion.py <issue-numero|archivo.md> [--repo owner/nombre] [--commit]
Lee el bloque ```yaml``` que genera contribuir.py. El aporte trae el CÓDIGO del docente (y las huellas si es nuevo), nunca su
nombre: se identifica contra el catálogo privado por código (`d-<6hex>` del slug) o por huellas (≥3 pares en común). Si no
existe, crea un perfil con `nombre: por completar` (completalo vos) y el código como slug. Suma criterios y ocurrencias y completa
el historial de roles. Se niega si el aporte contiene el nombre de algún docente del catálogo privado (el issue es público: hay
que editarlo o borrarlo). Corré esto en `main` del catálogo privado; --commit hace el commit (sin push); --exportar regenera
catalogo-publico/ (se republica con un PR a main de skills).
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
    MIN_COINCIDENCIAS_AUTO,
    aplicar_cambio,
    catalogo_default,
    claves_del_catalogo,
    codigo_de_slug,
    coincidencias_claves,
    commit_local,
    docente_nuevo,
    frontmatter,
    git,
    nombres_en,
    nombres_privados,
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


def parsear_formulario(cuerpo: str) -> dict | None:
    """Issue creado con el formulario de GitHub (secciones `### Etiqueta`): lo traduce al mismo formato que contribuir.py."""
    campos = {m[1].strip(): m[2].strip() for m in re.finditer(r"^### (.+?)\n\n(.*?)(?=\n### |\Z)", cuerpo, re.DOTALL | re.MULTILINE)}
    docente = campos.get("Código del docente", "").strip()
    if not docente:
        return None
    tipo, crit = campos.get("Tipo de aporte", ""), campos.get("Criterio, en general", "")
    claves = [x.strip() for x in campos.get("Huellas del nombre (solo si el docente es nuevo)", "").splitlines() if re.fullmatch(r"[0-9a-f]{16}", x.strip())]
    fuente = campos.get("Fuente (iniciales y fecha)", "")
    d: dict = {"docente": docente, "cambios": []}
    if tipo == "Docente nuevo" or docente.lower() == "nuevo":
        d["docente"] = "d-nuevo"
        d["nuevo"] = {"rol": campos.get("Rol del docente con vos", "Revisor"), "revisa": campos.get("Capítulo o sección donde suele aplicarlo", "por registrar"),
                      "alcance": "por registrar", "claves": claves}
    if tipo.startswith("Confirma") and (m := re.search(r"\bCR\d+\b", crit)):
        d["cambios"].append({"tipo": "ocurrencia", "id": m[0], "suma": 1, "fuente": fuente})
    elif crit:
        d["cambios"].append({"tipo": "criterio", "criterio": crit, "estado": "confirmado", "ocurrencias": 1, "fuente": fuente,
                             "capitulo": campos.get("Capítulo o sección donde suele aplicarlo", "—")})
    d["cambios"].append({"tipo": "historial", "rol": campos.get("Rol del docente con vos", "Revisor"),
                         "estudiante": (re.findall(r"\b(?:[A-Z]\.){2,3}", fuente) or ["?"])[0], "desde": ""})
    return {"docentes": [d]}


def buscar_slug(cat: Path, codigo: str, claves: list[str]) -> str | None:
    for p in (cat / "docentes").glob("*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") == "docente" and codigo in (p.stem, codigo_de_slug(p.stem), fm.get("codigo")):
            return p.stem
    cand = coincidencias_claves(claves, claves_del_catalogo(cat)) if claves else []
    if cand and cand[0][1] >= MIN_COINCIDENCIAS_AUTO and (len(cand) == 1 or cand[0][1] > cand[1][1]):
        return cand[0][0]
    return None


def con_claves(texto: str, claves: list[str]) -> str:
    cab_fin = texto.index("\n---\n", 4)
    return texto[:cab_fin] + "\nclaves:\n" + "".join(f"  - '{c}'\n" for c in claves).rstrip("\n") + texto[cab_fin:]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("origen")
    ap.add_argument("--repo")
    ap.add_argument("--commit", action="store_true")
    ap.add_argument("--exportar", action="store_true")
    ap.add_argument("--destino", type=Path, help="con --exportar: dónde regenerar el catálogo público (por defecto catalogo-publico/ de este repo)")
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    a = ap.parse_args()
    cat = a.catalogo
    cuerpo = leer(a.origen, a.repo)
    sospechosos = nombres_en(cuerpo, nombres_privados(cat))
    if sospechosos:
        sys.exit(f"El aporte contiene nombres de docentes ({', '.join(sospechosos)}) y el issue es público: editalo o borralo y no lo apliques.")
    m = re.search(r"```yaml\n(.*?)```", cuerpo, re.DOTALL)
    datos = yaml.safe_load(m[1]) if m else parsear_formulario(cuerpo)
    if not datos:
        sys.exit("No encuentro ni el bloque ```yaml``` de contribuir.py ni los campos del formulario de aporte.")
    rama = git(cat, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if rama.startswith("local/"):
        print(f"  aviso estás en {rama}: integrá en main del catálogo para que el cambio sea el oficial")
    hoy = datetime.datetime.now().astimezone().date().isoformat()
    resumen = []
    for d in datos["docentes"]:
        n = d.get("nuevo") or {}
        slug = buscar_slug(cat, d["docente"], list(n.get("claves") or []))
        if slug is None:
            if not n:
                sys.exit(f"{d['docente']} no está en el catálogo y el aporte no lo declara como nuevo")
            slug = d["docente"]
            if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", slug):
                sys.exit(f"Código inválido: {slug}")
            nuevo = docente_nuevo(slug, "por completar", n.get("rol", "Revisor"), n.get("revisa", "por registrar"), n.get("alcance", "por registrar"), hoy)
            (cat / "docentes" / f"{slug}.md").write_text(con_claves(nuevo, list(n.get("claves") or [])), encoding="utf-8")
            resumen.append(f"{slug}: docente nuevo (completá su nombre en el perfil privado)")
        perfil = cat / "docentes" / f"{slug}.md"
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
    if a.exportar:
        destino = ["--destino", str(a.destino)] if a.destino else []
        r = subprocess.run([sys.executable, str(Path(__file__).with_name("exportar_publico.py")), "--origen", str(cat), *destino],
                           capture_output=True, text=True, check=False)
        print(r.stdout.strip() or r.stderr.strip())
    if a.commit:
        print("  ok    commit" if commit_local(cat, f"feat(docentes): contribución {a.origen}") else "  ya    sin cambios")
    else:
        print(git(cat, "diff", "--stat").stdout.strip() + "\n(revisá y commiteá, o repetí con --commit)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
