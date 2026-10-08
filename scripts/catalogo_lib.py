"""Utilidades del catálogo de docentes (perfiles `docentes/<slug>.md`): lo usan asignar_evaluador, registrar_criterio,
nuevo_docente, contribuir y aplicar_contribucion. Sin datos propios: solo leer, editar y commitear perfiles.

Ubicación del catálogo: `$DOCENTES_EMI` o `~/.local/share/tg-docentes`. Los cambios de un estudiante van a una rama
`local/<usuario>` del catálogo; el repo principal solo cambia por issue/PR (contribuir.py / aplicar_contribucion.py).
"""

from __future__ import annotations

import getpass
import hashlib
import itertools
import os
import re
import subprocess
import unicodedata
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
    """Con remoto, origin/main; en el catálogo local sembrado desde el público, la rama `main` (el último snapshot)."""
    for rama in ("origin/main", "origin/master"):
        if git(cat, "rev-parse", "--verify", "-q", rama).returncode == 0:
            return rama
    actual = git(cat, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if actual != "main" and git(cat, "rev-parse", "--verify", "-q", "main").returncode == 0:
        return "main"
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
    """Los IDs son neutros (CR1, CR2…): un prefijo con el apellido delataría al docente en el catálogo público."""
    return "CR"


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


# ------------------------------------------------------------------ seudónimos: código + huellas del nombre
# La sal es PÚBLICA a propósito: cada estudiante calcula en su máquina las huellas del nombre de SU docente y las busca en
# el catálogo público. Es seudonimización, no anonimato: quien ya sepa un nombre puede comprobarlo.
SAL = "emi-docentes/v1"
TITULOS_NOMBRE = {"ing", "lic", "msc", "cnl", "daen", "dr", "dra", "mcal", "sr", "sra", "mgr", "phd", "tcnl", "crnl", "cap",
                  "tte", "del", "los", "las", "von", "van", "docente", "tutor"}
MIN_COINCIDENCIAS_AUTO = 3  # tokens en común (3 pares) para vincular sin preguntar


def normalizar(texto: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", texto.casefold()) if unicodedata.category(c) != "Mn")


def tokens_nombre(nombre: str) -> list[str]:
    return sorted({t for t in re.findall(r"[a-z]{3,}", normalizar(nombre)) if t not in TITULOS_NOMBRE})


def claves_de_nombre(nombre: str) -> list[str]:
    """Huella de cada par no ordenado de tokens del nombre (16 hex): sirve para reconocer un nombre sin guardarlo."""
    return sorted(hashlib.sha256(f"{SAL}|{a}|{b}".encode()).hexdigest()[:16] for a, b in itertools.combinations(tokens_nombre(nombre), 2))


def codigo_de_slug(slug: str) -> str:
    return "d-" + hashlib.sha256(f"{SAL}|slug|{slug}".encode()).hexdigest()[:6]


def coincidencias_claves(mias_: list[str], perfiles: dict[str, list[str]]) -> list[tuple[str, int]]:
    mias = set(mias_)
    res = [(cod, len(mias & set(claves))) for cod, claves in perfiles.items()]
    return sorted(((c, n) for c, n in res if n), key=lambda x: -x[1])


def coincidencias(nombre: str, perfiles: dict[str, list[str]]) -> list[tuple[str, int]]:
    """[(código, pares en común)] de mayor a menor, con al menos un par en común."""
    return coincidencias_claves(claves_de_nombre(nombre), perfiles)


def claves_del_catalogo(cat: Path) -> dict[str, list[str]]:
    out = {}
    for p in (cat / "docentes").glob("*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") == "docente":
            claves = fm.get("claves") or (claves_de_nombre(str(fm.get("nombre", ""))) if fm.get("nombre") else [])
            if claves:
                out[p.stem] = [str(c) for c in claves]
    return out


# ------------------------------------------------------------------ export público (sin nombres)
CITA = re.compile(r"[\"«“][^\"»”]*[\"»”]")


def rol_generico(rol: str) -> str:
    r = normalizar(rol)
    if "tutor" in r:
        return "Tutor"
    if "docente de trabajo" in r or "docente de tg" in r or "cnl" in r:
        return "Docente de TG"
    return "Revisor"


def _limpiar_fuente(celda: str) -> str:
    sin_citas = CITA.sub("", celda)
    return re.sub(r"\s{2,}", " ", re.sub(r"\s*;\s*;", ";", sin_citas)).strip(" ;,—-")


def _tabla_limpia(bloque: str) -> str:
    """Tabla de criterios sin citas literales en la columna de fuente (se conservan iniciales, fechas y ocurrencias)."""
    lineas = bloque.split("\n")
    k, cols = cabecera(lineas)
    if k < 0:
        return bloque
    destino = next((cols.index(c) for c in ("Fuente", "Evidencia") if c in cols), None)
    for n in range(k + 2, len(lineas)):
        if lineas[n].startswith("|") and destino is not None:
            cs = celdas(lineas[n])
            if len(cs) == len(cols):
                cs[destino] = _limpiar_fuente(cs[destino]) or "—"
                lineas[n] = "| " + " | ".join(cs) + " |"
    return "\n".join(lineas)


def perfil_publico(texto: str, slug: str) -> tuple[str, str]:
    """Perfil sin nombre: (código, texto). Solo criterios (sin citas literales), forma e historial de roles."""
    fm = frontmatter(texto)
    codigo = codigo_de_slug(slug)
    claves = claves_de_nombre(str(fm.get("nombre", "")))
    partes = []
    for titulo in ("Criterios de fondo", "Criterios de forma"):
        i, j = seccion(texto, titulo)
        if i < 0:
            ip = texto.find(f"## {titulo}")  # «Criterios de forma (fuera del alcance…)»
            i, j = (-1, -1) if ip < 0 else (ip, seccion(texto[ip:], titulo)[1] + ip)
        if i >= 0:
            bloque = _tabla_limpia(texto[i:j].rstrip("\n"))
            bloque = re.sub(r"^## .*$", f"## {titulo}", bloque, count=1, flags=re.MULTILINE)
            partes.append(bloque)
    i, j = seccion(texto, "Historial de roles")
    if i >= 0:
        partes.append(texto[i:j].rstrip("\n"))
    cab = {"title": f"Docente {codigo}", "type": "docente", "codigo": codigo, "status": "activo",
           "revisa": str(fm.get("revisa", "por registrar")), "alcance": str(fm.get("alcance", "por registrar")),
           "rol": rol_generico(str(fm.get("rol", ""))), "updated": str(fm.get("updated", "")), "claves": claves}
    cuerpo = f"# Docente {codigo}\n\n{PLANTILLA_CALLOUT_PUBLICO}\n\n" + "\n\n".join(partes) + "\n\n## Relaciones\n- [[_moc-docentes]] · [[jerarquia-autoridad]]\n"
    return codigo, "---\n" + yaml.safe_dump(cab, allow_unicode=True, sort_keys=False, width=200).rstrip() + "\n---\n\n" + cuerpo


PLANTILLA_CALLOUT_PUBLICO = """> [!important] Perfil público sin nombre
> El nombre de este docente **no** está aquí: se reconoce localmente con `scripts/resolver_docente.py "Nombre Apellido"`,
> que calcula huellas del nombre en tu máquina y las compara con `claves`. Los criterios son generales y las fuentes llevan
> iniciales y fecha, sin citas. Es seudonimización, no anonimato."""


def nombres_privados(cat: Path) -> set[str]:
    """Todo lo que identificaría a un docente del catálogo privado: tokens de su nombre y partes de su slug (normalizados)."""
    out: set[str] = set()
    for p in (cat / "docentes").glob("*.md"):
        fm = frontmatter(p.read_text(encoding="utf-8"))
        if fm.get("type") != "docente":
            continue
        out.update(t for t in re.findall(r"[a-z]{4,}", normalizar(p.stem)))
        if not normalizar(str(fm.get("nombre", ""))).startswith("por completar"):
            out.update(t for t in re.findall(r"[a-z]{4,}", normalizar(str(fm.get("nombre", "")))) if t not in TITULOS_NOMBRE)
    return out


def nombres_en(texto: str, prohibidos: set[str], permitir: frozenset[str] = frozenset()) -> list[str]:
    palabras = set(re.findall(r"[a-z]{4,}", normalizar(texto)))
    return sorted((palabras & prohibidos) - permitir)


# ------------------------------------------------------------------ nombres locales (código → nombre de MIS docentes)
NOMBRES_LOCAL = "wiki/docentes/_nombres.local.yaml"  # en el vault, ignorado por git: el nombre no sale de tu máquina


def leer_nombres(vault: Path) -> dict[str, str]:
    f = vault / NOMBRES_LOCAL
    return {str(k): str(v) for k, v in (yaml.safe_load(f.read_text(encoding="utf-8")) or {}).items()} if f.is_file() else {}


def guardar_nombre(vault: Path, codigo: str, nombre: str) -> None:
    f = vault / NOMBRES_LOCAL
    f.parent.mkdir(parents=True, exist_ok=True)
    datos = leer_nombres(vault)
    datos[codigo] = nombre
    f.write_text("# Código del catálogo → nombre de TUS docentes. Solo en tu máquina (ignorado por git).\n"
                 + yaml.safe_dump(datos, allow_unicode=True, sort_keys=True), encoding="utf-8")


def codigo_de_nombre(nombre: str) -> str:
    """Código provisional de un docente nuevo creado en local (el mantenedor lo reconcilia por `claves`)."""
    return "d-" + hashlib.sha256(f"{SAL}|nombre|{'|'.join(tokens_nombre(nombre))}".encode()).hexdigest()[:6]


def docente_publico_nuevo(nombre: str, rol: str, revisa: str, alcance: str, fecha: str) -> tuple[str, str]:
    """Perfil local sin nombre (solo código y huellas): el nombre se guarda aparte, en el vault."""
    codigo = codigo_de_nombre(nombre)
    cab = {"title": f"Docente {codigo}", "type": "docente", "codigo": codigo, "status": "activo", "revisa": revisa,
           "alcance": alcance, "rol": rol_generico(rol), "updated": fecha, "claves": claves_de_nombre(nombre)}
    cuerpo = (f"# Docente {codigo}\n\n{PLANTILLA_CALLOUT_PUBLICO}\n\n## Criterios de fondo\n\n{ENCABEZADO_CRITERIOS}\n"
              "## Historial de roles\n\n| Rol | Estudiante | Desde |\n|---|---|---|\n\n## Relaciones\n- [[_moc-docentes]] · [[jerarquia-autoridad]]\n")
    return codigo, "---\n" + yaml.safe_dump(cab, allow_unicode=True, sort_keys=False, width=200).rstrip() + "\n---\n\n" + cuerpo
