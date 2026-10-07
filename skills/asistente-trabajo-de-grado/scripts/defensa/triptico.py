#!/usr/bin/env python3
"""Genera el tríptico (jurado) y el bíptico de la defensa en .docx desde un YAML (python-docx, sin datos del proyecto).

Uso: uv run --with python-docx --with pyyaml python triptico.py generar TRIPTICO.yaml
     uv run --with python-docx --with pyyaml python triptico.py verificar TRIPTICO.yaml --tg EXTRACCION.md
TRIPTICO.yaml (modelo: assets/defensa/triptico.example.yaml):
  colores: {oscuro: "032154", accion: "0a3a82"}      imagenes: {logo: ruta, foto: ruta}   (rutas relativas al yaml)
  salida: {triptico: nombre.docx, biptico: nombre.docx}
  solapa, contratapa, portada: lista de elementos       interior: [panel, panel, panel]      biptico: [panel, panel]
Elemento = lista: [h, texto] barra de título · [hb, texto] título sobre fondo oscuro · [p, texto] · [pb, texto] negrita
  · [pw, texto] párrafo blanco · [c, texto] centrado · [titulo, texto] · [li, texto] viñeta · [cifra, valor, rótulo]
  · [img, clave_o_ruta, ancho_cm] (clave = logo | foto) · [pie, texto] · [sep]
Paneles con fondo oscuro: portada y biptico[0] (campo `fondo: oscuro` en {fondo, elementos}); el resto, blanco.
Un panel es una lista de elementos o {fondo: oscuro, elementos: [...]}. Tríptico: A4 horizontal a doble cara
(exterior: solapa, contratapa, portada; interior: tres paneles). `verificar` falla si una cifra no está en el documento.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

import yaml
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.table import (
    WD_CELL_VERTICAL_ALIGNMENT,
    WD_ROW_HEIGHT_RULE,
    WD_TABLE_ALIGNMENT,
)
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

BLANCO = RGBColor(0xFF, 0xFF, 0xFF)
AZUL_TRIBUNAL, AZUL_ACCION = "032154", "0a3a82"  # se reemplazan con `colores` del yaml


def sombrear(celda, hex_):
    tcPr = celda._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hex_)
    tcPr.append(shd)


def sin_bordes(tabla):
    borders = OxmlElement("w:tblBorders")
    for b in ("top", "left", "bottom", "right", "insideH", "insideV"):
        e = OxmlElement(f"w:{b}")
        e.set(qn("w:val"), "nil")
        borders.append(e)
    tabla._tbl.tblPr.append(borders)


def parrafo(celda, primero, alin=None, antes=0, despues=3):
    p = celda.paragraphs[0] if primero[0] else celda.add_paragraph()
    primero[0] = False
    p.paragraph_format.space_before, p.paragraph_format.space_after = (
        Pt(antes),
        Pt(despues),
    )
    if alin:
        p.alignment = alin
    return p


def run(p, texto, tam=8.5, negrita=False, color=None, cursiva=False):
    r = p.add_run(texto)
    r.font.size, r.bold, r.italic = Pt(tam), negrita, cursiva
    if color is not None:
        r.font.color.rgb = color
    return r


def llenar(celda, fondo, elementos):
    if fondo:
        sombrear(celda, fondo)
    oscuro = fondo is not None
    texto_color = BLANCO if oscuro else None
    azul = RGBColor.from_string(AZUL_ACCION)
    primero = [True]
    C = WD_ALIGN_PARAGRAPH.CENTER
    for el in elementos:
        tipo = el[0]
        if tipo == "sep":
            parrafo(celda, primero, despues=2)
        elif tipo == "h":  # barra azul con texto blanco
            p = parrafo(celda, primero, antes=4, despues=4)
            pPr = p._p.get_or_add_pPr()
            shd = OxmlElement("w:shd")
            shd.set(qn("w:val"), "clear")
            shd.set(qn("w:fill"), AZUL_ACCION)
            pPr.append(shd)
            run(p, f" {el[1]} ", 11.5, True, BLANCO)
        elif tipo == "hb":  # título sobre fondo oscuro
            run(
                parrafo(celda, primero, antes=4),
                el[1],
                11,
                True,
                RGBColor(0xF2, 0xC9, 0x1E),
            )
        elif tipo == "titulo":
            run(parrafo(celda, primero, C), el[1], 16, True, texto_color)
        elif tipo == "c":
            run(parrafo(celda, primero, C), el[1], 11.5, True, texto_color)
        elif tipo in ("p", "pw"):
            p = parrafo(celda, primero, WD_ALIGN_PARAGRAPH.JUSTIFY)
            run(p, el[1], 10, False, texto_color)
        elif tipo == "pb":
            run(
                parrafo(celda, primero, WD_ALIGN_PARAGRAPH.JUSTIFY),
                el[1],
                10.5,
                True,
                azul,
            )
        elif tipo == "li":
            p = parrafo(celda, primero, despues=2)
            p.paragraph_format.left_indent = Cm(0.3)
            run(p, "▪ ", 10, True, azul)
            run(p, el[1], 10, False, texto_color)
        elif tipo == "cifra":
            p = parrafo(celda, primero, despues=1)
            run(p, el[1] + "  ", 16, True, azul)
            run(p, el[2], 9.5, False, texto_color)
        elif tipo == "img":
            p = parrafo(celda, primero, C, antes=4, despues=4)
            if oscuro:  # el logo es azul: sobre el fondo oscuro va en una franja blanca
                pPr = p._p.get_or_add_pPr()
                shd = OxmlElement("w:shd")
                shd.set(qn("w:val"), "clear")
                shd.set(qn("w:fill"), "FFFFFF")
                pPr.append(shd)
            p.add_run().add_picture(el[1], width=Cm(el[2]))
        elif tipo == "pie":
            run(parrafo(celda, primero, C), el[1], 8.5, False, None, True)


def hoja(doc, paneles, nueva_pagina=False):
    if nueva_pagina:
        doc.add_page_break()
    sec = doc.sections[0]
    ancho = sec.page_width.cm - sec.left_margin.cm - sec.right_margin.cm
    t = doc.add_table(rows=1, cols=len(paneles))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    sin_bordes(t)
    t.rows[0].height = Cm(
        sec.page_height.cm - sec.top_margin.cm - sec.bottom_margin.cm - 0.6
    )
    t.rows[
        0
    ].height_rule = WD_ROW_HEIGHT_RULE.EXACTLY  # cada panel ocupa el alto de la hoja
    for i, (fondo, elementos) in enumerate(paneles):
        celda = t.cell(0, i)
        celda.width = Cm(ancho / len(paneles))
        if fondo:
            celda.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        llenar(celda, fondo, elementos)


def documento():
    doc = Document()
    sec = doc.sections[0]
    sec.orientation = WD_ORIENT.LANDSCAPE
    sec.page_width, sec.page_height = Cm(29.7), Cm(21.0)
    for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(sec, m, Cm(0.8))
    return doc


def _panel(spec, imagenes, base: Path):
    fondo, elementos = (
        (AZUL_TRIBUNAL, spec["elementos"])
        if isinstance(spec, dict) and spec.get("fondo") == "oscuro"
        else (None, spec["elementos"] if isinstance(spec, dict) else spec)
    )
    out = []
    for el in elementos:
        el = list(el)
        if el[0] == "img":
            el[1] = str(base / imagenes.get(el[1], el[1]))
        out.append(tuple(el))
    return fondo, out


def generar(spec_path: Path) -> None:
    global AZUL_TRIBUNAL, AZUL_ACCION
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    AZUL_TRIBUNAL = spec.get("colores", {}).get("oscuro", AZUL_TRIBUNAL)
    AZUL_ACCION = spec.get("colores", {}).get("accion", AZUL_ACCION)
    imgs = spec.get("imagenes", {})
    paneles = lambda lista: [_panel(p, imgs, base) for p in lista]
    exterior = [
        spec["solapa"],
        spec["contratapa"],
        {"fondo": "oscuro", "elementos": spec["portada"]},
    ]
    tri = documento()
    hoja(tri, paneles(exterior))
    hoja(tri, paneles(spec["interior"]), nueva_pagina=True)
    tri.save(base / spec["salida"]["triptico"])
    bip = documento()
    hoja(bip, paneles(spec["biptico"]))
    bip.save(base / spec["salida"]["biptico"])
    print(f"ok {spec['salida']['triptico']} y {spec['salida']['biptico']}")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.casefold())
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def verificar(spec_path: Path, tg: Path) -> int:
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    doc_tg = _norm(tg.read_text(encoding="utf-8"))
    faltan = []
    for nombre in spec["salida"].values():
        d = Document(spec_path.parent / nombre)
        textos = [
            p.text for t in d.tables for c in t.rows[0].cells for p in c.paragraphs
        ]
        for t in textos:
            for n in set(re.findall(r"\d+(?:[.,]\d+)*", t)):
                if len(n) > 1 and not re.search(
                    rf"(?<![\d.,]){re.escape(n)}(?!\d|[.,]\d)", doc_tg
                ):
                    faltan.append(
                        f"{nombre}: «{n}» no está en el documento ({t.strip()[:50]!r})"
                    )
    print(
        "\n".join(sorted(set(faltan))) or "ok: todas las cifras están en el documento"
    )
    return 1 if faltan else 0


if __name__ == "__main__":
    if len(sys.argv) < 3 or sys.argv[1] not in ("generar", "verificar"):
        print(__doc__)
        sys.exit(2)
    ruta = Path(sys.argv[2]).resolve()
    if sys.argv[1] == "generar":
        generar(ruta)
    else:
        sys.exit(verificar(ruta, Path(sys.argv[sys.argv.index("--tg") + 1])))
