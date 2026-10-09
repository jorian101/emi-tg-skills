#!/usr/bin/env python3
"""Arma $VAULT/proyecto.yaml con lo que el TG extraído dice de sí mismo, sin inventar nada.

Lee `sources/<slug>.md` (salida de extraer-doc-tesis) y saca solo lo determinístico: carátula
(título, caso, estudiante, tutor, ciudad y año), secciones clave con su texto literal (antecedentes
institucionales, problema, objetivos), lista de anexos y el índice de figuras y tablas. Lo que no
encuentra queda como PENDIENTE para el modo inicializar de asistente-trabajo-de-grado, que completa
el resto (causa y efecto, convenciones, entregables) citando la sección del TG.

Uso:
  python3 scripts/inicializar_desde_tg.py <vault> [<slug>] [--force]
Sin <slug> usa el único `sources/*.extraction.json` del vault. No pisa un proyecto.yaml existente
salvo con --force. También completa `estudiante:` en config.md y el nombre en Tutor.md si siguen
con el texto de la plantilla.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

PENDIENTE = "PENDIENTE"
TITULO_MD = re.compile(r"^(#{1,6})\s+(.*)$")
FIG_TAB = re.compile(r"^(?:#{1,6}\s+)?\**(Figura|Tabla)\s+(\d+)\s*[:.]\s*(.+?)\**\s*$")
ANEXO = re.compile(r"^(?:#{1,6}\s+)?\**ANEXO\s+([A-Z]{1,2})\b\s*[:.\-–]?\s*(.*?)\**\s*$")
SECCIONES = {  # clave -> patrón del título de sección (sin numeración)
    "antecedentes_institucionales": r"antecedentes institucionales",
    "identificacion_problema": r"identificaci[oó]n del problema",
    "formulacion_problema": r"formulaci[oó]n del problema",
    "objetivo_general": r"objetivo general",
    "objetivos_especificos": r"objetivos espec[ií]ficos",
    "mision": r"misi[oó]n",
    "vision": r"visi[oó]n",
}


def limpio(t: str) -> str:
    t = re.sub(r"<[^>]+>", "", t)
    return re.sub(r"[*_]+", "", t).strip(" >\t“”\"")


def caratula(lineas: list[str]) -> dict:
    """La carátula: líneas de texto antes de DEDICATORIA/ÍNDICE (con o sin negrita). La segunda trae el tutor."""
    neg = []
    for ln in lineas:
        t = limpio(re.sub(r"^#{1,6}\s+", "", ln.strip()))
        if re.match(r"^(DEDICATORIA|AGRADECIMIENTOS?|RESUMEN|ÍNDICE)\b", t.upper()):
            break
        if t and not ln.lstrip().startswith("<img"):
            neg.append(t)
    c = {"titulo": PENDIENTE, "caso": PENDIENTE, "estudiante": PENDIENTE, "tutor": PENDIENTE,
         "ciudad_anio": PENDIENTE}
    for i, t in enumerate(neg):
        if t.upper().startswith("CASO"):
            c["caso"] = t.split(":", 1)[-1].strip()
            if i > 0 and c["titulo"] == PENDIENTE:
                c["titulo"] = neg[i - 1]
            if i + 1 < len(neg) and c["estudiante"] == PENDIENTE:
                c["estudiante"] = re.sub(r"^(EST|UNIV|SBTTE|SGTO)\.?\s+", "", neg[i + 1], flags=re.IGNORECASE)
        elif t.upper().startswith("TUTOR"):
            c["tutor"] = t.split(":", 1)[-1].strip()
        elif re.match(r"^[A-ZÁÉÍÓÚÑ ]+,\s*\d{4}$", t):
            c["ciudad_anio"] = t
    return c


# misión y visión suelen venir como viñeta («- Misión institucional: La misión … es …»), no como título
VINETA_INSTITUCIONAL = {
    "mision": re.compile(r"^[-*]\s*\**misi[oó]n[^:]*:\**\s*(.+)$", re.IGNORECASE),
    "vision": re.compile(r"^[-*]\s*\**visi[oó]n[^:]*:\**\s*(.+)$", re.IGNORECASE),
}


def secciones(lineas: list[str]) -> dict:
    """Primera aparición de cada sección clave fuera del índice: título literal + texto hasta el siguiente título."""
    out = {}
    for i, ln in enumerate(lineas):
        m = TITULO_MD.match(ln)
        if not m:
            continue
        titulo = limpio(m.group(2))
        sin_num = re.sub(r"^[\d.]+\s*", "", titulo).lower()
        for clave, patron in SECCIONES.items():
            if clave in out or not re.fullmatch(patron, sin_num):
                continue
            cuerpo = []
            for sig in lineas[i + 1:]:
                if TITULO_MD.match(sig):
                    break
                cuerpo.append(sig)
            texto = "\n".join(cuerpo).strip()
            if texto:  # el índice repite títulos sin cuerpo: se saltea
                out[clave] = {"seccion": titulo, "texto": texto}
    for ln in lineas:
        for clave, patron in VINETA_INSTITUCIONAL.items():
            m = patron.match(ln.strip())
            if m and clave not in out:
                out[clave] = {"seccion": f"viñeta «{clave}»", "texto": limpio(m.group(1))}
    return out


def objetivos_especificos(texto: str) -> list[str]:
    items = [limpio(re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", ln)) for ln in texto.splitlines()]
    return [t for t in items if len(t) > 15 and not t.endswith(":")]  # fuera la frase que presenta la lista


def indices(lineas: list[str]) -> tuple[list, list, list]:
    figs, tabs, anexos = {}, {}, {}
    for ln in lineas:
        s = ln.strip()
        if m := FIG_TAB.match(s):
            (figs if m.group(1) == "Figura" else tabs).setdefault(int(m.group(2)), limpio(m.group(3)))
        elif (m := ANEXO.match(s)) and m.group(2):
            anexos.setdefault(m.group(1), limpio(m.group(2)))
    return ([{"n": n, "titulo": t} for n, t in sorted(figs.items())],
            [{"n": n, "titulo": t} for n, t in sorted(tabs.items())],
            [{"letra": k, "titulo": v, "qr": False} for k, v in sorted(anexos.items(), key=lambda kv: (len(kv[0]), kv[0]))])


def armar(md: Path) -> dict:
    lineas = md.read_text(encoding="utf-8").splitlines()
    sec = secciones(lineas)
    figs, tabs, anexos = indices(lineas)
    oe = sec.get("objetivos_especificos", {})
    cara = caratula(lineas)
    return {
        "_nota": "Generado por inicializar_desde_tg.py desde el TG extraído. PENDIENTE = no estaba en el TG o "
                 "no se pudo leer sin interpretar: lo completa el modo inicializar citando la sección.",
        "tg": {
            "slug": md.stem,
            **cara,
            "revisores": [],
            "institucion_caso": {
                "nombre": cara.get("caso", PENDIENTE), "sigla": PENDIENTE,  # el caso de la carátula es la institución
                "antecedentes": sec.get("antecedentes_institucionales", PENDIENTE),
                "mision": sec.get("mision", PENDIENTE), "vision": sec.get("vision", PENDIENTE),
                "funcion": PENDIENTE,
            },
            "problema": {
                "identificacion": sec.get("identificacion_problema", PENDIENTE),
                "formulacion": sec.get("formulacion_problema", PENDIENTE),
                "causa": PENDIENTE, "efecto": PENDIENTE,
            },
            "objetivo_general": sec.get("objetivo_general", PENDIENTE),
            "objetivos_especificos": ({"seccion": oe["seccion"], "items": objetivos_especificos(oe["texto"])}
                                      if oe else PENDIENTE),
            "anexos": anexos,
            "figuras": figs,
            "tablas": tabs,
        },
        "convenciones": {
            "producto": PENDIENTE, "hilo_conductor": PENDIENTE, "terminologia": {},
            "terminos_prohibidos": [], "terminos_dificiles": [], "paleta_uml": {},
            "contenedores": {"red": "", "postgres": ""},
        },
        "entregables": {"seccion_desarrollo": PENDIENTE, "fases": [], "calendario": {}, "mapa": []},
    }


def completar_plantillas(vault: Path, tg: dict) -> None:
    """Solo reemplaza el texto de la plantilla: nunca pisa un dato que el usuario ya escribió."""
    cfg = Path(__file__).resolve().parent.parent / "skills/perfil-revisor-tg/config.md"
    if cfg.is_file() and tg["estudiante"] != PENDIENTE:
        s = cfg.read_text(encoding="utf-8")
        if "estudiante: Nombre Apellido" in s and f"data_dir: {vault}/" in s:  # solo el config de ESTE vault
            cfg.write_text(s.replace("estudiante: Nombre Apellido", f"estudiante: {tg['estudiante']}"), encoding="utf-8")
            print(f"  ok    config.md: estudiante = {tg['estudiante']}")
    tutor = vault / "wiki/revisores/Tutor.md"
    if tutor.is_file() and tg["tutor"] != PENDIENTE:
        s = tutor.read_text(encoding="utf-8")
        if "# Perfil — Tutor\n" in s and "nombre:" not in s.split("---")[1]:
            s = s.replace("status: en-elaboracion\n", f"status: en-elaboracion\nnombre: {tg['tutor']}\n", 1)
            tutor.write_text(s, encoding="utf-8")
            print(f"  ok    Tutor.md: nombre = {tg['tutor']}")


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--force"]
    if not args:
        sys.exit(__doc__)
    vault = Path(args[0]).expanduser().resolve()
    if len(args) > 1:
        md = vault / "sources" / f"{args[1]}.md"
    else:
        reportes = sorted((vault / "sources").glob("*.extraction.json"))
        if len(reportes) != 1:
            sys.exit(f"Hay {len(reportes)} extracciones en sources/: indicá el <slug>.")
        md = reportes[0].with_name(reportes[0].name.replace(".extraction.json", ".md"))
    if not md.is_file():
        sys.exit(f"No existe {md}: extraé primero el TG con extraer-doc-tesis.")
    destino = vault / "proyecto.yaml"
    if destino.exists() and "--force" not in sys.argv:
        sys.exit(f"{destino} ya existe (usá --force para regenerarlo; se pierde lo completado a mano).")
    datos = armar(md)
    destino.write_text(yaml.safe_dump(datos, allow_unicode=True, sort_keys=False, width=110), encoding="utf-8")
    tg = datos["tg"]
    faltan = [k for k in ("titulo", "caso", "estudiante", "tutor") if tg[k] == PENDIENTE]
    faltan += [k for k in ("objetivo_general", "objetivos_especificos") if tg[k] == PENDIENTE]
    print(f"  ok    {destino.name}: {len(tg['figuras'])} figuras, {len(tg['tablas'])} tablas, {len(tg['anexos'])} anexos")
    if faltan:
        print(f"  aviso PENDIENTE en el TG: {', '.join(faltan)}")
    completar_plantillas(vault, tg)


if __name__ == "__main__":
    main()
