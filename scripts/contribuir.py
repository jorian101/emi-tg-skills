#!/usr/bin/env python3
"""Arma la contribución saneada de lo que registraste en tu catálogo local y, si lo pedís, la abre como issue.

Uso:
  contribuir.py [--docente <slug>]                 # muestra y guarda contribucion.md (no envía nada)
  contribuir.py --enviar [--repo owner/nombre] [--si]   # abre el issue con `gh` (pide confirmación salvo --si)

Cualquiera con cuenta de GitHub puede aportar: el issue se abre en el repo PÚBLICO de las skills (sin invitación). El catálogo
público es generado: no se le hacen PR; el mantenedor integra el aporte en el catálogo privado y lo republica.

Qué incluye: por docente (su CÓDIGO), criterios nuevos y ocurrencias nuevas (criterio general, capítulo, fuente por
INICIALES), filas nuevas del historial de roles y, si el docente es nuevo, su rol, qué revisa y las HUELLAS de su nombre.
NUNCA el nombre del docente, el informe ni nombres de estudiantes. Se niega si en lo que se enviaría aparece el nombre de
alguno de TUS docentes (los de `wiki/docentes/_nombres.local.yaml` del vault: --vault o $VAULT) o una fuente trae un
nombre completo; además pasa por auditar-pii.sh.
Cada contribución se compara contra origin/main del catálogo (o contra vacío si no tiene remoto).
El mantenedor la integra con aplicar_contribucion.py.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

from catalogo_lib import (
    ARBOL_VACIO,
    base_remota,
    catalogo_default,
    commit_local,
    es_repo,
    filas_criterios,
    filas_historial,
    frontmatter,
    git,
    leer_nombres,
    nombres_en,
    normalizar,
    rama_local,
    sin_nombres_completos,
)

REPO = Path(__file__).resolve().parent.parent


def texto_en(cat: Path, ref: str, ruta: str) -> str:
    r = git(cat, "show", f"{ref}:{ruta}")
    return r.stdout if r.returncode == 0 else ""


def cambios_de(cat: Path, base: str, slug: str) -> dict | None:
    ruta = f"docentes/{slug}.md"
    antes, ahora = texto_en(cat, base, ruta), (cat / ruta).read_text(encoding="utf-8")
    if antes == ahora:
        return None
    fm_a, fm_n = frontmatter(antes) if antes else {}, frontmatter(ahora)
    out: dict = {"docente": slug, "cambios": []}
    if not antes:
        out["nuevo"] = {**{k: str(fm_n.get(k, "")) for k in ("rol", "revisa", "alcance")}, "claves": list(fm_n.get("claves") or [])}
    elif any(fm_a.get(k) != fm_n.get(k) for k in ("revisa", "alcance")):
        out["meta"] = {k: str(fm_n.get(k, "")) for k in ("revisa", "alcance")}
    previas, nuevas = filas_criterios(antes), filas_criterios(ahora)
    for id_, fila in nuevas.items():
        fuente = fila.get("Fuente") or fila.get("Evidencia") or ""
        if id_ not in previas:
            out["cambios"].append({"tipo": "criterio", "criterio": fila.get("Criterio", ""), "estado": fila.get("Estado", "inferido"),
                                   "capitulo": fila.get("Capítulo", "—"), "ocurrencias": int((re.search(r"\d+", fila.get("Ocurrencias", "1")) or ["1"])[0]),
                                   "fuente": fuente})
        else:
            o_a = int((re.search(r"\d+", previas[id_].get("Ocurrencias", "0")) or ["0"])[0])
            o_n = int((re.search(r"\d+", fila.get("Ocurrencias", "0")) or ["0"])[0])
            f_a = previas[id_].get("Fuente") or previas[id_].get("Evidencia") or ""
            if o_n > o_a:
                out["cambios"].append({"tipo": "ocurrencia", "id": id_, "suma": o_n - o_a,
                                       "fuente": fuente.replace(f_a, "").strip("; ").strip()})
    for rol, quien, desde in set(filas_historial(ahora)) - set(filas_historial(antes)):
        out["cambios"].append({"tipo": "historial", "rol": rol, "estudiante": quien, "desde": desde})
    return out if out["cambios"] or "nuevo" in out or "meta" in out else None


def cuerpo(docentes: list[dict]) -> str:
    md = ["## Contribución de criterios", ""]
    for d in docentes:
        md.append(f"### {d['docente']}" + (" (docente nuevo)" if "nuevo" in d else ""))
        if "nuevo" in d:
            md.append(f"- rol: {d['nuevo']['rol']}; revisa: {d['nuevo']['revisa']}; alcance: {d['nuevo']['alcance']}; huellas: {len(d['nuevo']['claves'])}")
        for c in d["cambios"]:
            if c["tipo"] == "criterio":
                md.append(f"- **Criterio nuevo** ({c['capitulo']}): {c['criterio']} — _{c['fuente']}_")
            elif c["tipo"] == "ocurrencia":
                md.append(f"- **Ocurrencia +{c['suma']}** de {c['id']}: _{c['fuente']}_")
            else:
                md.append(f"- **Rol**: {c['rol']} de {c['estudiante']} ({c['desde']})")
    md += ["", "```yaml", yaml.safe_dump({"docentes": docentes}, allow_unicode=True, sort_keys=False, width=110).rstrip(), "```", "",
           "_Generado por `contribuir.py`: sin informes ni nombres de estudiantes (iniciales)._"]
    return "\n".join(md)


def revisar(cuerpo_md: str, docentes: list[dict], vault: Path | None) -> list[str]:
    problemas = []
    if vault:  # los nombres de TUS docentes no pueden aparecer en lo que se publica
        tokens = {t for n in leer_nombres(vault).values() for t in re.findall(r"[a-z]{4,}", normalizar(n))}
        for palabra in nombres_en(cuerpo_md, tokens):
            problemas.append(f"el aporte contiene «{palabra}», parte del nombre de uno de tus docentes")
    for d in docentes:
        for c in d["cambios"]:
            for nombre in sin_nombres_completos(c.get("fuente", "") + " " + c.get("estudiante", "")):
                problemas.append(f"{d['docente']}: la fuente nombra a «{nombre}»; usá iniciales")
    with tempfile.TemporaryDirectory() as t:
        Path(t, "contribucion.md").write_text(cuerpo_md, encoding="utf-8")
        deny = REPO / ".pii-denylist.local"
        if deny.is_file():
            shutil.copy(deny, Path(t) / ".pii-denylist.local")
        r = subprocess.run(["bash", str(REPO / "scripts/auditar-pii.sh"), t], capture_output=True, text=True, check=False)
        if r.returncode != 0:
            problemas.append("auditar-pii.sh: " + " ".join(r.stdout.split("\n")[:3]))
    return problemas


UPSTREAM = "jorian101/emi-tg-skills"  # repo público de las skills: ahí se abren los issues de aportes


def repo_issues(explicito: str | None) -> str:
    return explicito or os.environ.get("EMI_APORTES_REPO") or UPSTREAM


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docente")
    ap.add_argument("--repo")
    ap.add_argument("--enviar", action="store_true")
    ap.add_argument("--si", action="store_true", help="no pedir confirmación (el usuario ya la dio)")
    ap.add_argument("--vault", type=Path, default=Path(os.environ["VAULT"]) if os.environ.get("VAULT") else None)
    ap.add_argument("--salida", type=Path, default=Path("contribucion.md"))
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    a = ap.parse_args()
    cat = a.catalogo
    if not es_repo(cat):
        sys.exit("El catálogo local no es un repo git: no hay con qué comparar (instalá con install.sh).")
    rama_local(cat)
    commit_local(cat, "docs(docentes): cambios locales")
    base = base_remota(cat) or ARBOL_VACIO
    slugs = [a.docente] if a.docente else sorted(p.stem for p in (cat / "docentes").glob("*.md")
                                                  if frontmatter(p.read_text(encoding="utf-8")).get("type") == "docente")
    docentes = [d for s in slugs if (d := cambios_de(cat, base, s))]
    if not docentes:
        print("Nada nuevo para contribuir respecto de la base del catálogo.")
        return 0
    md = cuerpo(docentes)
    problemas = revisar(md, docentes, a.vault)
    if problemas:  # no se deja escrito un archivo con el dato que no debe salir
        a.salida.unlink(missing_ok=True)
        print("NO SE PUEDE ENVIAR (no se guardó nada). Corregí en tu catálogo local:\n  " + "\n  ".join(problemas))
        return 1
    a.salida.write_text(md, encoding="utf-8")
    print(md, "\n", f"\n(guardado en {a.salida})")
    if not a.enviar:
        print("\nNo se envió nada. Revisá el texto y, si querés abrir el issue: contribuir.py --enviar")
        return 0
    repo = repo_issues(a.repo)
    if not shutil.which("gh"):
        sys.exit(f"Para enviar hace falta `gh` con sesión. Podés pegar {a.salida} a mano en un issue nuevo de https://github.com/{repo}/issues/new/choose")
    if not a.si and input(f"¿Abrir un issue en {repo} con este contenido? [s/N] ").strip().lower() not in ("s", "si", "sí", "y"):
        print("Cancelado.")
        return 0
    titulo = "Criterios: " + ", ".join(d["docente"] for d in docentes)
    cmd = ["gh", "issue", "create", "--repo", repo, "--title", titulo, "--body-file", str(a.salida)]
    r = subprocess.run([*cmd, "--label", "aporte-criterio"], capture_output=True, text=True, check=False)
    if r.returncode:  # la etiqueta puede no existir en ese repo: se reintenta sin ella
        r = subprocess.run(cmd, capture_output=True, text=True, check=False)
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
