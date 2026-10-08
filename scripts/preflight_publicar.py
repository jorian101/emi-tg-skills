#!/usr/bin/env python3
"""Puerta antes de publicar (push o PR): busca datos sensibles en las líneas que se van a publicar.

Uso:
  preflight_publicar.py [repo] [--base origin/main] [--catalogo carpeta] [--sin-docentes] [--permitir termino ...]

Mira SOLO las líneas agregadas respecto de la base (`git diff base..HEAD`) y de los archivos nuevos, **sin distinguir
mayúsculas** (auditar-pii.sh es sensible a mayúsculas a propósito; esta puerta es la red más ancha). Busca:
  - cada término de `.pii-denylist.local` del repo (apellidos, nombres de pila, siglas de tu proyecto);
  - los apellidos y slugs de los docentes del catálogo (`docentes/*.md`), salvo con --sin-docentes (el propio catálogo);
  - correos reales (no noreply ni de ejemplo), rutas personales /home/<usuario>, enlaces de notebook y UUID.
Sale 1 si hay algún hallazgo; cada uno se revisa a mano y, si es un falso positivo (p. ej. «terceros» como palabra común),
se pasa con --permitir. También corre auditar-pii.sh y auditar-rutas.sh si el repo los tiene.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

from catalogo_lib import ARBOL_VACIO, catalogo_default, frontmatter

TITULOS = {"ing", "lic", "msc", "cnl", "daen", "dr", "dra", "mcal", "sr", "sra"}
GENERICOS = [r"[\w.+-]+@(?!users\.noreply\.github\.com|example\.|localhost|x\b|t\b)[\w-]+\.[\w.]+",
             r"/home/[a-z][\w-]+/", r"notebooklm\.google\.com|notebook\.google\.com",
             r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b"]


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, check=False).stdout


def terminos_denylist(repo: Path) -> list[str]:
    f = repo / ".pii-denylist.local"
    return [ln.strip() for ln in f.read_text(encoding="utf-8").splitlines() if ln.strip() and not ln.startswith("#")] if f.is_file() else []


def terminos_docentes(catalogo: Path) -> list[str]:
    out: set[str] = set()
    for p in (catalogo / "docentes").glob("*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") != "docente":
            continue
        out.update(p.stem.split("-"))
        out.update(re.findall(r"[^\W\d_]{4,}", str(fm.get("nombre", ""))))
    return sorted(t for t in out if len(t) >= 4 and t.lower() not in TITULOS)


def lineas_agregadas(repo: Path, base: str) -> list[tuple[str, int, str]]:
    ref = base if git(repo, "rev-parse", "--verify", "-q", base).strip() else ARBOL_VACIO
    salida, archivo, n, out = git(repo, "diff", "-U0", "--no-color", f"{ref}..HEAD"), "", 0, []
    for ln in salida.splitlines():
        if ln.startswith("+++ "):
            archivo = ln[6:] if ln.startswith("+++ b/") else ""
        elif ln.startswith("@@"):
            m = re.search(r"\+(\d+)", ln)
            n = int(m[1]) - 1 if m else 0
        elif ln.startswith("+") and archivo:
            n += 1
            out.append((archivo, n, ln[1:]))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("repo", nargs="?", type=Path, default=Path.cwd())
    ap.add_argument("--base", default="origin/main")
    ap.add_argument("--catalogo", type=Path, default=catalogo_default())
    ap.add_argument("--sin-docentes", action="store_true")
    ap.add_argument("--permitir", nargs="*", default=[])
    a = ap.parse_args()
    repo = a.repo.resolve()
    permitidos = {t.lower() for t in a.permitir}
    nombres = terminos_denylist(repo) + ([] if a.sin_docentes else terminos_docentes(a.catalogo))
    patrones = [(re.compile(rf"\b{re.escape(t)}\b" if re.fullmatch(r"\w+", t) else t, re.IGNORECASE), t) for t in nombres
                if t.lower() not in permitidos]
    patrones += [(re.compile(g, re.IGNORECASE), "dato personal") for g in GENERICOS]
    if git(repo, "status", "--porcelain", "--untracked-files=no").strip():
        print("  aviso hay cambios sin commitear: la puerta mira lo commiteado (base..HEAD)")
    hallazgos = []
    for archivo, n, texto in lineas_agregadas(repo, a.base):
        if archivo.startswith(".husky/") or archivo.endswith(".pii-denylist.example"):
            continue
        for rx, termino in patrones:
            if rx.search(texto):
                hallazgos.append(f"{archivo}:{n}: «{termino}» → {texto.strip()[:110]}")
                break
    rc = 0
    for script in ("auditar-pii.sh", "auditar-rutas.sh"):
        if (repo / "scripts" / script).is_file():
            r = subprocess.run(["bash", str(repo / "scripts" / script)], capture_output=True, text=True, cwd=repo, check=False)
            if r.returncode:
                hallazgos.append(f"{script}: " + " | ".join(r.stdout.strip().splitlines()[:3]))
    if hallazgos:
        print(f"PREFLIGHT: {len(hallazgos)} hallazgo(s) antes de publicar:\n  " + "\n  ".join(hallazgos))
        rc = 1
    else:
        print(f"ok preflight: 0 hallazgos en las líneas a publicar ({a.base}..HEAD, {len(patrones)} patrones)")
    return rc


if __name__ == "__main__":
    sys.exit(main())
