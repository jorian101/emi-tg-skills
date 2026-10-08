"""Utilidades del catálogo de docentes (perfiles `docentes/<slug>.md`): lo usan asignar_evaluador, registrar_criterio,
nuevo_docente, contribuir y aplicar_contribucion. Sin datos propios: solo leer, editar y commitear perfiles.

Ubicación del catálogo: `$DOCENTES_EMI` o `~/.local/share/tg-docentes`. Los cambios de un estudiante van a una rama
`local/<usuario>` del catálogo; el repo principal solo cambia por issue/PR (contribuir.py / aplicar_contribucion.py).
"""

from __future__ import annotations

import getpass
import os
import re
import subprocess
from pathlib import Path

import yaml

ARBOL_VACIO = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
PLANTILLA_CALLOUT = """> [!important] Cómo se usa este perfil
> Es el perfil **compartido** del docente (catálogo `emi-docentes`). Solo lo lee el vault de un estudiante que lo tiene
> como **evaluador identificado** (tutor, revisor o docente de TG): ahí sus criterios se aplican como `inferido
> (predicción)` en los capítulos que suele revisar, y lo que ese docente le corrige al estudiante (`confirmado`) vive en
> su vault. Para quien no lo tiene como evaluador, este perfil **no existe**: no se mezclan docentes.
> Las fuentes son informes y sesiones con varios estudiantes (por iniciales); los crudos quedan en el vault de quien los recibió."""
ENCABEZADO_CRITERIOS = "| ID | Criterio | Estado | Ocurrencias | Fuente |\n|---|---|---|---|---|\n"
NOMBRE_COMPLETO = re.compile(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,} [A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}\b")


def catalogo_default() -> Path:
    return Path(os.environ.get("DOCENTES_EMI") or Path.home() / ".local/share/tg-docentes")


def frontmatter(texto: str) -> dict:
    m = re.match(r"---\n(.*?)\n---\n", texto, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m[1]) or {}
    except yaml.YAMLError:
        simples = (re.match(r"([A-Za-z_]\w*):\s*(.*)$", ln) for ln in m[1].splitlines())
        return {k[1]: k[2].strip().strip('"') for k in simples if k and k[2]}


# ------------------------------------------------------------------ git (rama local del estudiante)
def git(cat: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(cat), *args], capture_output=True, text=True, check=False)


def es_repo(cat: Path) -> bool:
    return (cat / ".git").exists()


def usuario() -> str:
    return re.sub(r"[^a-z0-9]+", "-", getpass.getuser().lower()).strip("-") or "estudiante"


def rama_local(cat: Path) -> str | None:
    """Pasa el catálogo a su rama `local/<usuario>` (la crea desde donde esté). None si no es un repo git."""
    if not es_repo(cat):
        return None
    destino = f"local/{usuario()}"
    actual = git(cat, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if actual != destino:
        existe = git(cat, "rev-parse", "--verify", "-q", destino).returncode == 0
        git(cat, "checkout", "-q", destino if existe else "-b", *([] if existe else [destino]))
    return destino


def commit_local(cat: Path, mensaje: str) -> bool:
    """Commit de lo que cambió en docentes/ (si es un repo). Devuelve True si hizo commit."""
    if not es_repo(cat):
        return False
    git(cat, "add", "-A", "docentes")
    if git(cat, "diff", "--cached", "--quiet").returncode == 0:
        return False
    nombre = git(cat, "config", "user.name").stdout.strip() or usuario()
    correo = git(cat, "config", "user.email").stdout.strip() or f"{usuario()}@localhost"
    r = git(cat, "-c", f"user.name={nombre}", "-c", f"user.email={correo}", "commit", "-q", "-m", mensaje)
    return r.returncode == 0


def base_remota(cat: Path) -> str | None:
    for rama in ("origin/main", "origin/master"):
        if git(cat, "rev-parse", "--verify", "-q", rama).returncode == 0:
            return rama
    return None


# ------------------------------------------------------------------ tabla de criterios
def seccion(texto: str, titulo: str) -> tuple[int, int]:
    i = texto.find(f"## {titulo}")
    if i < 0:
        return -1, -1
    j = texto.find("\n## ", i + 5)
    return i, len(texto) if j < 0 else j


def cabecera(lineas: list[str]) -> tuple[int, list[str]]:
    for k, ln in enumerate(lineas):
        if ln.startswith(("| ID", "| #")):
            return k, [c.strip() for c in ln.strip().strip("|").split("|")]
    return -1, []


def celdas(fila: str) -> list[str]:
    return [c.strip() for c in fila.strip().strip("|").split("|")]


def fila_de(cols: list[str], valores: dict[str, str]) -> str:
    alias = {"Fuente": ("Fuente", "Evidencia"), "Criterio": ("Criterio", "Ítem", "Regla")}
    out = []
    for c in cols:
        v = valores.get(c)
        if v is None:
            for k, nombres in alias.items():
                if c in nombres:
                    v = valores.get(k)
        out.append(v if v is not None else ("transversal-metodológico" if c == "Tipo" else "—"))
    return "| " + " | ".join(out) + " |"


def prefijo_id(texto: str, slug: str) -> str:
    ids = re.findall(r"^\| ([A-Z]{2,}[A-Z]*)\d+ \|", texto, re.MULTILINE)
    return ids[0] if ids else (re.sub(r"[^a-z]", "", slug.lower())[:3].upper() or "DOC")


def siguiente_id(texto: str, prefijo: str) -> str:
    nums = [int(n) for n in re.findall(rf"^\| {prefijo}(\d+) \|", texto, re.MULTILINE)]
    return f"{prefijo}{max(nums, default=0) + 1}"


def sin_nombres_completos(valor: str) -> list[str]:
    """Nombres y apellidos pegados en un texto que debe llevar iniciales (se ignora lo citado entre comillas)."""
    sin_citas = re.sub(r"[\"«“].*?[\"»”]", "", valor)
    return NOMBRE_COMPLETO.findall(sin_citas)


def agregar_criterio(texto: str, slug: str, c: dict) -> tuple[str, str]:
    """Agrega un criterio a «Criterios de fondo» y devuelve (texto, id). c: criterio, estado, capitulo, fuente, ocurrencias."""
    i, j = seccion(texto, "Criterios de fondo")
    if i < 0:
        base = texto.find("\n## Historial de roles")
        base = len(texto) if base < 0 else base
        texto = texto[:base] + "\n## Criterios de fondo\n\n" + ENCABEZADO_CRITERIOS + texto[base:]
        i, j = seccion(texto, "Criterios de fondo")
    bloque = texto[i:j]
    lineas = bloque.split("\n")
    k, cols = cabecera(lineas)
    if k < 0:
        bloque = bloque.rstrip("\n") + "\n\n" + ENCABEZADO_CRITERIOS
        lineas = bloque.split("\n")
        k, cols = cabecera(lineas)
    nuevo_id = c.get("id") or siguiente_id(texto, prefijo_id(texto, slug))
    fila = fila_de(cols, {"ID": nuevo_id, "Criterio": c["criterio"], "Estado": c.get("estado", "confirmado"),
                          "Ocurrencias": str(c.get("ocurrencias", 1)), "Fuente": c["fuente"],
                          "Capítulo": c.get("capitulo", "—")})
    ultima = max(n for n, ln in enumerate(lineas) if ln.startswith("|"))
    lineas.insert(ultima + 1, fila)
    return texto[:i] + "\n".join(lineas) + texto[j:], nuevo_id


def sumar_ocurrencia(texto: str, id_: str, suma: int, fuente: str) -> str:
    """Ocurrencias +suma en la fila `id_` y la fuente nueva agregada a su celda de fuente."""
    i, j = seccion(texto, "Criterios de fondo")
    lineas = texto[i:j].split("\n")
    _, cols = cabecera(lineas)
    for n, ln in enumerate(lineas):
        if ln.startswith(f"| {id_} |"):
            cs = celdas(ln)
            if "Ocurrencias" in cols:
                k = cols.index("Ocurrencias")
                m = re.search(r"\d+", cs[k])
                cs[k] = re.sub(r"\d+", str(int(m[0]) + suma), cs[k], count=1) if m else str(suma)
            f = next((cols.index(x) for x in ("Fuente", "Evidencia") if x in cols), None)
            if f is not None and fuente and fuente not in cs[f]:
                cs[f] = f"{cs[f]}; {fuente}"
            lineas[n] = "| " + " | ".join(cs) + " |"
            return texto[:i] + "\n".join(lineas) + texto[j:]
    raise KeyError(f"No existe el criterio {id_}")


def historial_texto(s: str, rol: str, quien: str, fecha: str) -> str:
    if f"| {rol} | {quien} |" in s:
        return s
    if "## Historial de roles" not in s:
        base = s.find("\n## Relaciones")
        base = len(s) if base < 0 else base
        s = s[:base] + "\n## Historial de roles\n\n| Rol | Estudiante | Desde |\n|---|---|---|\n" + s[base:]
    i = s.index("## Historial de roles")
    j = s.find("\n\n## ", i + 1)
    j = len(s) if j < 0 else j
    bloque = s[i:j].replace("| — | — | — |\n", "").replace("| — | — | — |", "")
    return s[:i] + bloque.rstrip("\n") + f"\n| {rol} | {quien} | {fecha} |" + s[j:]


def aplicar_cambio(texto: str, slug: str, cambio: dict) -> tuple[str, str]:
    """Aplica un cambio estructurado (criterio | ocurrencia | historial) y devuelve (texto, descripción)."""
    tipo = cambio["tipo"]
    if tipo == "criterio":
        texto, nuevo = agregar_criterio(texto, slug, cambio)
        return texto, f"criterio {nuevo}"
    if tipo == "ocurrencia":
        return sumar_ocurrencia(texto, cambio["id"], int(cambio.get("suma", 1)), cambio.get("fuente", "")), f"ocurrencia {cambio['id']}"
    if tipo == "historial":
        return historial_texto(texto, cambio["rol"], cambio["estudiante"], cambio.get("desde", "")), "historial"
    raise ValueError(f"tipo de cambio desconocido: {tipo}")


# ------------------------------------------------------------------ MOC del catálogo
def regenerar_moc(cat: Path) -> None:
    filas = []
    for p in sorted((cat / "docentes").glob("*.md")):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") != "docente":
            continue
        n = len(re.findall(r"^\| [A-Z]{2,}[A-Z0-9]*\d+ \|", p.read_text(encoding="utf-8"), re.MULTILINE))
        filas.append(f"| [[{p.stem}]] | {fm.get('rol', '')} | {fm.get('revisa', '')} | {fm.get('alcance', '')} | {n} |")
    moc = cat / "docentes/_moc-docentes.md"
    texto = moc.read_text(encoding="utf-8") if moc.is_file() else (
        "---\ntitle: Catálogo de docentes EMI\ntype: moc\nstatus: activo\n---\n\n# Catálogo de docentes EMI\n\n")
    cab = "| Docente | Rol habitual | Suele revisar | Alcance | Criterios |\n|---|---|---|---|---|\n"
    i = texto.find("| Docente |")
    if i >= 0:
        j = texto.find("\n\n", i)
        texto = texto[:i] + cab + "\n".join(filas) + (texto[j:] if j >= 0 else "\n")
    else:
        texto = texto.rstrip("\n") + "\n\n" + cab + "\n".join(filas) + "\n"
    moc.write_text(texto, encoding="utf-8")


def docente_nuevo(slug: str, nombre: str, rol: str, revisa: str, alcance: str, fecha: str) -> str:
    return f"""---
title: {nombre}
type: docente
created: {fecha}
updated: {fecha}
status: activo
revisa: "{revisa}"
alcance: {alcance}
nombre: {nombre}
rol: {rol}
tags:
  - docentes
  - trabajos-grado
---

# {nombre}

{PLANTILLA_CALLOUT}

## Criterios de fondo

{ENCABEZADO_CRITERIOS}
## Historial de roles

| Rol | Estudiante | Desde |
|---|---|---|

## Relaciones
- [[_moc-docentes]] · [[jerarquia-autoridad]]
"""


# ------------------------------------------------------------------ lectura de tablas (para contribuir)
def filas_criterios(texto: str) -> dict[str, dict[str, str]]:
    i, j = seccion(texto, "Criterios de fondo")
    if i < 0:
        return {}
    lineas = texto[i:j].split("\n")
    k, cols = cabecera(lineas)
    filas = {}
    for ln in lineas[k + 2:] if k >= 0 else []:
        if ln.startswith("|"):
            cs = celdas(ln)
            if len(cs) == len(cols):
                filas[cs[0]] = dict(zip(cols, cs, strict=True))
    return filas


def filas_historial(texto: str) -> list[tuple[str, str, str]]:
    i, j = seccion(texto, "Historial de roles")
    if i < 0:
        return []
    out = []
    for ln in texto[i:j].split("\n"):
        cs = celdas(ln) if ln.startswith("|") else []
        if len(cs) == 3 and cs[0] not in ("Rol", "—") and not cs[0].startswith("-"):
            out.append((cs[0], cs[1], cs[2]))
    return out


def poner_campo(texto: str, clave: str, valor: str) -> str:
    m = re.match(r"---\n(.*?)\n---\n", texto, re.DOTALL)
    cab, linea = m[1], f'{clave}: "{valor}"' if clave == "revisa" else f"{clave}: {valor}"
    cab = re.sub(rf"^{clave}:.*$", linea, cab, count=1, flags=re.MULTILINE) if re.search(rf"^{clave}:", cab, re.MULTILINE) \
        else cab + "\n" + linea
    return f"---\n{cab}\n---\n" + texto[m.end():]
