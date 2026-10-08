#!/usr/bin/env python3
"""Vincula a un evaluador del estudiante (tutor, revisor o docente de TG) con su perfil del catálogo de docentes.

Uso:
  python3 scripts/asignar_evaluador.py <vault> --rol tutor|revisor_1|revisor_2|docente_tg --docente <slug> [--iniciales D.P.]
  python3 scripts/asignar_evaluador.py <vault> --rol revisor_2 --por-asignar
  python3 scripts/asignar_evaluador.py <vault> --check
  python3 scripts/asignar_evaluador.py <vault> --desde-tg     # vincula al tutor que nombra proyecto.yaml, si está en el catálogo
  python3 scripts/asignar_evaluador.py <vault> --sync         # rehace scripts/, los enlaces de wiki/docentes y config.md

Qué hace al asignar:
- escribe `docente:` y `asignado:` en el perfil del rol (`wiki/revisores/Revisor_N.md`, `Tutor.md` o `Docente_TG.md`;
  lo crea desde la plantilla si falta) y lo agrega a `evaluadores:` del config si es el de este vault;
- enlaza en `wiki/docentes/` SOLO a ese docente (symlink a su perfil del catálogo y a sus notas `<slug>-*.md`) y
  desenlaza al anterior de ese rol si ya no evalúa en ningún otro: un estudiante nunca ve a quien no lo evalúa;
- suma la fila al historial de roles del docente en el catálogo (estudiante por iniciales);
- rehace la tabla de `wiki/docentes/_moc-docentes.md` e imprime la predicción inicial (sus criterios y qué revisa).
`--sync` es el paso de «cloné mi vault en otra máquina»: los enlaces (rutas absolutas de ESTA máquina) no se versionan, se
regeneran desde el `docente:` de cada perfil. `--check` lista roles sin vincular, enlaces rotos, docentes en `wiki/docentes/` que no evalúan, y docentes del
catálogo cuyo nombre aparece en `proyecto.yaml`. Catálogo: `--catalogo`, `$DOCENTES_EMI` o `~/.local/share/tg-docentes`.
"""

from __future__ import annotations

import argparse
import datetime
import os
import re
import sys
import unicodedata
from pathlib import Path

import yaml

from catalogo_lib import commit_local, historial_texto, rama_local

REPO = Path(__file__).resolve().parent.parent
PLANTILLA = REPO / "skills/perfil-revisor-tg/assets/Revisor_N.md"
ROLES = {"tutor": ("Tutor.md", "Tutor"), "revisor_1": ("Revisor_1.md", "Revisor 1"),
         "revisor_2": ("Revisor_2.md", "Revisor 2"), "docente_tg": ("Docente_TG.md", "Docente de TG")}
LOCALES = {"_moc-docentes.md", "_plantilla-docente.md", "jerarquia-autoridad.md"}
INICIO, FIN = "<!-- evaluadores:inicio -->", "<!-- evaluadores:fin -->"


def norm(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.casefold()) if unicodedata.category(c) != "Mn")


def frontmatter(texto: str) -> dict:
    """Frontmatter como dict. Vaults viejos traen YAML inválido (listas con «: » y líneas continuadas): en ese caso
    se leen solo las claves simples de primer nivel, que son las que usa este script."""
    m = re.match(r"---\n(.*?)\n---\n", texto, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m[1]) or {}
    except yaml.YAMLError:
        simples = (re.match(r"([A-Za-z_]\w*):\s*(.*)$", ln) for ln in m[1].splitlines())
        return {k[1]: k[2].strip().strip('"') for k in simples if k and k[2]}


def poner_campo(texto: str, clave: str, valor: str) -> str:
    """Reemplaza o agrega `clave: valor` dentro del frontmatter, sin tocar el resto."""
    m = re.match(r"---\n(.*?)\n---\n", texto, re.DOTALL)
    cabeza = m[1]
    linea = f'{clave}: "{valor}"' if valor.startswith("[[") else f"{clave}: {valor}"
    if re.search(rf"^{clave}:.*$", cabeza, re.MULTILINE):
        cabeza = re.sub(rf"^{clave}:.*$", linea, cabeza, count=1, flags=re.MULTILINE)
    else:
        cabeza += "\n" + linea
    return f"---\n{cabeza}\n---\n" + texto[m.end():]


def docente_de(perfil: Path) -> str | None:
    if not perfil.is_file():
        return None
    d = str(frontmatter(perfil.read_text(encoding="utf-8")).get("docente") or "")
    return d.strip("[]") or None


def iniciales(vault: Path) -> str:
    py = vault / "proyecto.yaml"
    nombre = (yaml.safe_load(py.read_text(encoding="utf-8")) or {}).get("tg", {}).get("estudiante", "") if py.is_file() else ""
    partes = [p for p in str(nombre).split() if p.isalpha()]
    if len(partes) < 2:
        return "?"
    return f"{partes[0][0]}.{partes[2 if len(partes) >= 4 else 1][0]}.".upper()


def enlazar(vault: Path, catalogo: Path, slug: str) -> list[str]:
    destino_dir = vault / "wiki/docentes"
    destino_dir.mkdir(parents=True, exist_ok=True)
    hechos = []
    for origen in [catalogo / "docentes" / f"{slug}.md", *sorted((catalogo / "docentes").glob(f"{slug}-*.md"))]:
        link = destino_dir / origen.name
        if link.exists() and not link.is_symlink():
            sys.exit(f"{link} es una copia local: pasá su contenido al catálogo y borrala antes de vincular.")
        if link.is_symlink():
            link.unlink()
        link.symlink_to(origen)
        hechos.append(origen.name)
    return hechos


def desenlazar(vault: Path, slug: str) -> None:
    for link in (vault / "wiki/docentes").glob(f"{slug}*.md"):
        if link.is_symlink() and (link.stem == slug or link.stem.startswith(f"{slug}-")):
            link.unlink()


def sumar_historial(catalogo: Path, slug: str, rol: str, quien: str, fecha: str) -> None:
    perfil = catalogo / "docentes" / f"{slug}.md"
    antes = perfil.read_text(encoding="utf-8")
    despues = historial_texto(antes, rol, quien, fecha)
    if despues != antes:
        rama_local(catalogo)
        perfil.write_text(despues, encoding="utf-8")
        commit_local(catalogo, f"docs(docentes): {rol} de {quien} en {slug}")


def rehacer_moc(vault: Path) -> None:
    moc = vault / "wiki/docentes/_moc-docentes.md"
    if not moc.is_file() or INICIO not in moc.read_text(encoding="utf-8"):
        return
    filas = []
    for archivo, nombre in ROLES.values():
        perfil = vault / "wiki/revisores" / archivo
        d = docente_de(perfil)
        if d:
            fm = frontmatter(perfil.read_text(encoding="utf-8"))
            celda = "por asignar (solo clases SEM)" if d == "por-asignar" else f"[[{d}]]"
            filas.append(f"| {nombre} | {celda} | {fm.get('asignado', '—')} |")
    tabla = "| Rol | Docente | Desde |\n|---|---|---|\n" + ("\n".join(filas) or "| — | sin evaluadores vinculados todavía | — |")
    s = moc.read_text(encoding="utf-8")
    s = s[: s.index(INICIO) + len(INICIO)] + "\n" + tabla + "\n" + s[s.index(FIN):]
    moc.write_text(s, encoding="utf-8")


def prediccion(catalogo: Path, slug: str) -> str:
    s = (catalogo / "docentes" / f"{slug}.md").read_text(encoding="utf-8")
    fm = frontmatter(s)
    i = s.find("## Criterios de fondo")
    seccion = s[i: s.find("\n## ", i + 1) if s.find("\n## ", i + 1) > 0 else None] if i >= 0 else ""
    filas = [f for f in seccion.splitlines() if f.startswith("|") and not re.match(r"\|\s*-", f)][1:]
    cabeza = f"Predicción inicial de {fm.get('title', slug)} — revisa: {fm.get('revisa', '?')} ({fm.get('alcance', '?')})"
    return cabeza + "\n" + ("\n".join(filas) if filas else "  (todavía sin criterios en el catálogo)")


def asignar(vault: Path, catalogo: Path, rol: str, slug: str | None, quien: str | None, fecha: str) -> None:
    archivo, nombre = ROLES[rol]
    perfil = vault / "wiki/revisores" / archivo
    if not perfil.is_file():
        perfil.parent.mkdir(parents=True, exist_ok=True)
        texto = PLANTILLA.read_text(encoding="utf-8").replace("Revisor N", nombre).replace("n_revisor: N\n", "")
        perfil.write_text(texto, encoding="utf-8")
        print(f"  ok    perfil nuevo {archivo}")
    if slug and not (catalogo / "docentes" / f"{slug}.md").is_file():
        sys.exit(f"El catálogo no tiene docentes/{slug}.md: crealo desde la plantilla de docente y volvé a correr.")
    anterior = docente_de(perfil)
    texto = poner_campo(perfil.read_text(encoding="utf-8"), "docente", f"[[{slug}]]" if slug else "por-asignar")
    perfil.write_text(poner_campo(texto, "asignado", fecha if slug else "por-asignar"), encoding="utf-8")
    otros = {docente_de(vault / "wiki/revisores" / a) for r, (a, _) in ROLES.items() if r != rol}
    if anterior and anterior not in ("por-asignar", slug) and anterior not in otros:
        desenlazar(vault, anterior)
        print(f"  ok    {anterior} ya no te evalúa: desenlazado")
    if slug:
        print(f"  ok    {nombre} = {slug}; enlazado: {', '.join(enlazar(vault, catalogo, slug))}")
        sumar_historial(catalogo, slug, nombre, quien or iniciales(vault), fecha[:7])
        escribir_config(vault, [a for a, _ in ROLES.values() if docente_de(vault / "wiki/revisores" / a)])
    else:
        print(f"  ok    {nombre} por asignar: hasta entonces solo valen las clases SEM de la matriz")
    rehacer_moc(vault)
    if slug:
        print(prediccion(catalogo, slug))


def check(vault: Path, catalogo: Path) -> int:
    problemas = []
    vinculados = set()
    for archivo, nombre in ROLES.values():
        d = docente_de(vault / "wiki/revisores" / archivo)
        if not d:
            problemas.append(f"{nombre}: sin vincular (asignar_evaluador.py … --rol … --docente <slug> | --por-asignar)")
        elif d != "por-asignar":
            vinculados.add(d)
    for f in sorted((vault / "wiki/docentes").glob("*.md")):
        if f.name in LOCALES:
            continue
        if f.is_symlink() and not f.exists():
            problemas.append(f"enlace roto: wiki/docentes/{f.name}")
        elif not any(f.stem == v or f.stem.startswith(f"{v}-") for v in vinculados):
            problemas.append(f"wiki/docentes/{f.name} no te evalúa: se quita (no se mezclan docentes)")
        elif not f.is_symlink():
            problemas.append(f"wiki/docentes/{f.name} es una copia local: pasala al catálogo y vinculala")
    py = vault / "proyecto.yaml"
    if py.is_file():
        texto = norm(py.read_text(encoding="utf-8"))
        for p in sorted((catalogo / "docentes").glob("*.md")):
            n = str(frontmatter(p.read_text(encoding="utf-8")).get("nombre") or "")
            if n and norm(n) in texto and p.stem not in vinculados:
                problemas.append(f"proyecto.yaml nombra a {n} ({p.stem}): ¿es tu evaluador? vinculalo")
    print("\n".join(problemas) or "ok: cada rol vinculado y solo tus evaluadores en wiki/docentes")
    return 1 if problemas else 0


def sync(vault: Path, catalogo: Path) -> int:
    """Regenera lo que no se versiona: vault/scripts, los enlaces a los docentes propios y config.md de este vault."""
    hechos = []
    destino = vault / "scripts"
    if destino.is_symlink() or not destino.exists():
        destino.unlink(missing_ok=True)
        destino.symlink_to(REPO / "scripts")
        hechos.append("scripts/")
    vinculados = []
    for archivo, _ in ROLES.values():
        d = docente_de(vault / "wiki/revisores" / archivo)
        if d and d != "por-asignar":
            if (catalogo / "docentes" / f"{d}.md").is_file():
                enlazar(vault, catalogo, d)
                hechos.append(f"wiki/docentes/{d}")
            else:
                print(f"  aviso {archivo}: el catálogo no tiene a {d} (¿catálogo sin acceso o desactualizado?)")
        if d:
            vinculados.append(archivo)
    escribir_config(vault, vinculados)
    rehacer_moc(vault)
    print("  ok    sync: " + (", ".join(hechos) or "nada que rehacer"))
    return 0


def escribir_config(vault: Path, evaluadores: list[str]) -> None:
    """config.md del clon (una instalación = un estudiante). No pisa el de otro vault."""
    cfg = Path(os.environ.get("TG_CONFIG") or REPO / "skills/perfil-revisor-tg/config.md")
    if cfg.is_file() and f"data_dir: {vault}/wiki/revisores" not in cfg.read_text(encoding="utf-8"):
        print(f"  aviso {cfg.name} apunta a otro vault: no lo toco (un clon = un estudiante)")
        return
    py = vault / "proyecto.yaml"
    estudiante = ((yaml.safe_load(py.read_text(encoding="utf-8")) or {}).get("tg", {}).get("estudiante", "")
                  if py.is_file() else "") or "Nombre Apellido"
    lineas = "\n".join(f"  - {e}" for e in evaluadores) or "  - Revisor_1.md"
    texto = (REPO / "skills/perfil-revisor-tg/config.example.md").read_text(encoding="utf-8")
    texto = re.sub(r"^data_dir: .*$", f"data_dir: {vault}/wiki/revisores", texto, flags=re.MULTILINE)
    texto = re.sub(r"^estudiante: .*$", f"estudiante: {estudiante}", texto, flags=re.MULTILINE)
    texto = re.sub(r"^evaluadores:\n(  - .*\n)+", f"evaluadores:\n{lineas}\n", texto, flags=re.MULTILINE)
    texto = re.sub(r"^docentes_en: .*$", f"docentes_en: {vault}/wiki/docentes", texto, flags=re.MULTILINE)
    texto = re.sub(r"^informes_en: .*$", f"informes_en: {vault}/sources/informes-revisores", texto, flags=re.MULTILINE)
    cfg.write_text(texto, encoding="utf-8")


def desde_tg(vault: Path, catalogo: Path, fecha: str) -> int:
    """El tutor sale de la carátula (proyecto.yaml): si su nombre está en el catálogo, se vincula solo."""
    py = vault / "proyecto.yaml"
    tutor = norm(str((yaml.safe_load(py.read_text(encoding="utf-8")) or {}).get("tg", {}).get("tutor", ""))) if py.is_file() else ""
    for p in sorted((catalogo / "docentes").glob("*.md")):
        n = norm(str(frontmatter(p.read_text(encoding="utf-8")).get("nombre") or ""))
        if n and tutor and n in tutor:
            asignar(vault, catalogo, "tutor", p.stem, None, fecha)
            return 0
    print("  aviso el tutor de proyecto.yaml no está en el catálogo: crealo desde _plantilla-docente y vinculalo")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vault", type=Path)
    ap.add_argument("--rol", choices=ROLES)
    ap.add_argument("--docente")
    ap.add_argument("--por-asignar", action="store_true")
    ap.add_argument("--iniciales")
    ap.add_argument("--fecha", default=datetime.datetime.now().astimezone().date().isoformat())
    ap.add_argument("--catalogo", type=Path,
                    default=Path(os.environ.get("DOCENTES_EMI") or Path.home() / ".local/share/tg-docentes"))
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--desde-tg", action="store_true")
    ap.add_argument("--sync", action="store_true")
    a = ap.parse_args()
    vault, catalogo = a.vault.expanduser().resolve(), a.catalogo.expanduser()
    if not (catalogo / "docentes").is_dir():
        sys.exit(f"No encuentro el catálogo de docentes en {catalogo} (--catalogo o $DOCENTES_EMI).")
    if a.check:
        return check(vault, catalogo)
    if a.sync:
        return sync(vault, catalogo)
    if a.desde_tg:
        return desde_tg(vault, catalogo, a.fecha)
    if not a.rol or bool(a.docente) == a.por_asignar:
        ap.error("indicá --rol y una de --docente <slug> o --por-asignar")
    asignar(vault, catalogo, a.rol, a.docente, a.iniciales, a.fecha)
    return 0


if __name__ == "__main__":
    sys.exit(main())
