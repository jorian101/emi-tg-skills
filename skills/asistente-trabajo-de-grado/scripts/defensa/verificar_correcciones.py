#!/usr/bin/env python3
"""Dice qué correcciones ya copió el autor al Word y cuáles faltan.

TG:     python3 verificar_correcciones.py [correcciones.md ...] [--mover]
        Lee los bloques «**Buscar**» / «**Reemplazar con**» (cada uno en un bloque ```) del archivo
        de correcciones (clave `correcciones` de defensa.json) y los compara con el texto del TG (`fuentes.tg`):
          APLICADA  el texto nuevo está y el viejo ya no
          PENDIENTE el texto viejo sigue en el Word
          REVISAR   no está ninguno (el autor lo escribió distinto)
        --mover pasa las secciones «### …» ya aplicadas debajo de «## Aplicadas».
Manual: python3 verificar_correcciones.py --manual
        Compara por título de sección el manual generado (`manual_a_copiar`) con el oficial
        (`manual_oficial`) y lista las secciones que todavía difieren.
Todas las rutas salen de defensa.json en --dir CARPETA (o $DEFENSA_DIR, o el directorio actual).
Sale con 1 si hay pendientes. Requiere pandoc.
"""

from __future__ import annotations

import difflib
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

# Se completan desde defensa.json en main(): fuentes.tg, manual_oficial, manual_a_copiar y correcciones.
TG = MANUAL_OFICIAL = MANUAL_NUEVO = CORRECCIONES = None
# «**Buscar** en «ancla»:» limita la búsqueda a los 400 caracteres que siguen al ancla (p. ej. el
# rótulo de la fila), para que una celda corta como «14,0» no se confunda con otra igual.
BLOQUE = re.compile(r"\*\*Buscar[^*\n]*\*\*([^\n]*)\n```[^\n]*\n(.*?)\n```\s*\n\*\*Reemplazar[^\n]*\n```[^\n]*\n(.*?)\n```", re.S)
ANCLA = re.compile(r"«([^»]+)»")


def texto(docx: Path, fmt: str = "plain") -> str:
    return subprocess.run(["pandoc", str(docx), "-t", fmt, "--wrap=none"], capture_output=True,
                          text=True, check=True).stdout


def norm(s: str) -> str:
    s = re.sub(r"(\d),\s+(\d)", r"\1,\2", s)  # pandoc escribe las ecuaciones de Word como «34, 98»
    return re.sub(r"\s+", " ", re.sub(r"[*_`$\\|]", "", s)).strip().lower()


def tramos(a: list[str], b: list[str]) -> tuple[list[str], list[str]]:
    """Lo que cambia entre a y b, con dos palabras de contexto a cada lado (si no, «5 %» sale en todos lados)."""
    viejos, nuevos = [], []
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == "equal":
            continue
        if i2 > i1:
            viejos.append(" ".join(a[max(0, i1 - 2):i2 + 2]))
        if j2 > j1:
            nuevos.append(" ".join(b[max(0, j1 - 2):j2 + 2]))
    return viejos, nuevos


def esta(t: str, tg: str) -> bool:
    """t aparece como palabras enteras («14,0» no está dentro de «14,04»)."""
    return re.search(rf"(?<![\w.,]){re.escape(t)}(?!\w|[.,]\d)", tg) is not None


def estado(viejo: str, nuevo: str, tg: str) -> str:
    v, n = tramos(norm(viejo).split(), norm(nuevo).split())
    hay_nuevo = all(esta(t, tg) for t in n) if n else True
    # Solo se agregó texto: el viejo sigue siendo un trozo del nuevo, así que no sirve como señal.
    hay_viejo = any(esta(t, tg) for t in v) if v else (esta(norm(viejo), tg) and not hay_nuevo)
    if len(norm(nuevo)) >= 80 and norm(nuevo) in tg:  # solo textos largos: uno corto puede existir en otro lado  # el texto nuevo entero está: el trozo viejo puede repetirse en otro lado
        return "APLICADA"
    if hay_nuevo and not hay_viejo:
        return "APLICADA"
    return "PENDIENTE" if hay_viejo else "REVISAR"


def ventana(cabecera: str, tg: str) -> str:
    """Todo el TG, o el tramo que sigue al ancla «…» de la cabecera ('' si el ancla no está)."""
    m = ANCLA.search(cabecera)
    if not m:
        return tg
    i = tg.find(norm(m.group(1)))
    return tg[i:i + 400] if i >= 0 else ""


def verificar_tg(archivos: list[Path], mover: bool) -> int:
    tg = norm(texto(TG))
    pendientes = 0
    for md in archivos:
        cuerpo = md.read_text(encoding="utf-8")
        principal, _, aplicadas = cuerpo.partition("\n## Aplicadas\n")
        secciones = re.split(r"(?m)^(?=### )", principal)
        quedan, nuevas_aplicadas = [], []
        for sec in secciones:
            bloques = [(ventana(cab, tg), v, n) for cab, v, n in BLOQUE.findall(sec)]
            estados = [estado(v, n, t) if t else "REVISAR" for t, v, n in bloques]
            titulo = sec.splitlines()[0] if sec.startswith("### ") else ""
            for (_, v, _), e in zip(bloques, estados):
                print(f"{e:9} {md.name} · {titulo[4:60] or '(sin sección)'} · {norm(v)[:70]}")
            pendientes += sum(e != "APLICADA" for e in estados)
            ya = titulo and bloques and all(e == "APLICADA" for e in estados)
            (nuevas_aplicadas if ya else quedan).append(sec)
        if mover and nuevas_aplicadas:
            resto = "".join(quedan).rstrip() + "\n\n## Aplicadas\n\n" + "".join(nuevas_aplicadas) + aplicadas
            md.write_text(resto.rstrip() + "\n", encoding="utf-8")
            print(f"  → {len(nuevas_aplicadas)} sección(es) movidas a «Aplicadas» en {md.name}")
    print(f"\n{pendientes} corrección(es) sin aplicar.")
    return 1 if pendientes else 0


def secciones_manual(docx: Path) -> dict[str, str]:
    """Texto por sección. Los títulos del manual usan los estilos propios H1-H4 (pandoc no los ve como
    títulos); los índices (TOC*) se saltan. Compara solo texto: una captura cambiada no se detecta."""
    w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
    raiz = ET.fromstring(zipfile.ZipFile(docx).read("word/document.xml"))
    secciones: dict[str, list[str]] = {}
    actual = None
    for p in raiz.iter(f"{w}p"):
        estilo = p.find(f"{w}pPr/{w}pStyle")
        estilo = estilo.get(f"{w}val") if estilo is not None else ""
        txt = "".join(t.text or "" for t in p.iter(f"{w}t")).strip()
        if not txt or estilo.startswith("TOC"):
            continue
        if re.fullmatch(r"H[1-4]", estilo):
            actual = norm(txt)
            secciones.setdefault(actual, [])
        elif actual:
            secciones[actual].append(txt)
    return {t: norm(" ".join(c)) for t, c in secciones.items()}


def verificar_manual() -> int:
    nuevo, oficial = secciones_manual(MANUAL_NUEVO), secciones_manual(MANUAL_OFICIAL)
    faltan = [t for t, c in nuevo.items() if oficial.get(t) != c]
    for t in faltan:
        print(("FALTA    " if t not in oficial else "DIFIERE  ") + t)
    print(f"\n{len(faltan)} de {len(nuevo)} secciones por copiar al MANUAL DE USUARIO OFICIAL.docx.")
    return 1 if faltan else 0


def _configurar() -> None:
    global TG, MANUAL_OFICIAL, MANUAL_NUEVO, CORRECCIONES
    cfg = config.cargar()
    TG = config.ruta(cfg["fuentes"]["tg"], Path(cfg["_base"]))
    CORRECCIONES = config.clave(cfg, "correcciones", "Es el archivo vivo de correcciones al TG.")
    if "manual_oficial" in cfg:
        MANUAL_OFICIAL = config.clave(cfg, "manual_oficial")
        MANUAL_NUEVO = config.clave(cfg, "manual_a_copiar", "Es el manual generado que se copia al oficial.")


if __name__ == "__main__":
    _configurar()
    args = config.args_sin_dir()
    if "--manual" in args:
        if MANUAL_OFICIAL is None:
            sys.exit("Este proyecto no declara manual_oficial en defensa.json.")
        sys.exit(verificar_manual())
    sys.exit(verificar_tg([Path(a) for a in args if not a.startswith("--")] or [CORRECCIONES],
                          "--mover" in args))
