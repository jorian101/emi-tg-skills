#!/usr/bin/env python3
"""Herramientas genéricas para el mazo de diapositivas de la defensa (python-pptx, sin datos del proyecto).

Uso: uv run --with python-pptx --with pillow python diapositivas.py <comando> MAZO.pptx [opciones]
  texto    MAZO [--md SALIDA]            vuelca el texto de cada diapositiva (y si está oculta o tiene notas)
  cifras   MAZO --tg EXTRACCION.md       cada número del mazo debe existir en el documento; sale 1 si falta alguno
  verificar MAZO                         imágenes con menos de 150 ppp o sin descripción, cajas de texto vacías
  notas    MAZO GUION.yaml               escribe el guion en las notas del orador: {numero: "texto"} o lista de {n, texto}
  ocultar  MAZO N [N ...] [--mostrar]    oculta (o muestra) diapositivas: el contenido queda como respaldo
  imagen   MAZO N NOMBRE ARCHIVO         reemplaza una imagen conservando su caja (se centra y no se deforma)
  mover    MAZO N [N ...]                lleva esas diapositivas al final (respaldo), en ese orden
  ids      MAZO                          reasigna ids de forma repetidos (se corre solo al guardar)
  tarjetas MAZO --despues N --spec S.yaml  agrega una diapositiva con tarjetas de cifras clonando el estilo de otra
S.yaml: {titulo, base: N (diapositiva con tarjetas de la que se toma el estilo), tarjetas: [{cifra, texto}], pie}
Los números de diapositiva son los que ve el autor (1 = primera). Los cambios se guardan sobre el mismo archivo.
"""

from __future__ import annotations

import copy
import io
import re
import sys
import unicodedata
from pathlib import Path

import yaml
from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Emu, Pt

PPP_MINIMO = 150
NUMERO = re.compile(r"\d+(?:[.,]\d+)*")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.casefold())
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def _textos(forma) -> list[str]:
    if forma.has_text_frame:
        return [forma.text_frame.text]
    if getattr(forma, "has_table", False) and forma.has_table:
        return [c.text for fila in forma.table.rows for c in fila.cells]
    return []


def _es_numero_de_pagina(forma) -> bool:
    return "Marcador de contenido" in forma.name


def texto(prs: Presentation, md: Path | None) -> None:
    salida = []
    for i, s in enumerate(prs.slides, 1):
        oculta = s._element.get("show") == "0"
        notas = s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip()
        salida.append(
            f"## {i}{' (oculta)' if oculta else ''}{' · con notas' if notas else ''}"
        )
        for f in s.shapes:
            if _es_numero_de_pagina(f):
                continue
            for t in _textos(f):
                if t.strip():
                    salida.append("- " + t.strip().replace("\n", " / "))
        if notas:
            salida.append(
                "> notas: "
                + s.notes_slide.notes_text_frame.text.strip().replace("\n", " ")
            )
        salida.append("")
    cuerpo = "\n".join(salida)
    if md:
        md.write_text(cuerpo, encoding="utf-8")
        print(f"ok {md} ({len(prs.slides)} diapositivas)")
    else:
        print(cuerpo)


def cifras(prs: Presentation, tg: Path) -> int:
    doc = _norm(tg.read_text(encoding="utf-8"))
    faltan = []
    for i, s in enumerate(prs.slides, 1):
        for f in s.shapes:
            if _es_numero_de_pagina(f):
                continue
            for t in _textos(f):
                for n in set(NUMERO.findall(t)):
                    if len(n) == 1 and n.isdigit():
                        continue  # numeración de pasos y de listas
                    if not re.search(rf"(?<![\d.,]){re.escape(n)}(?![\d]|[.,]\d)", doc):
                        faltan.append(
                            f"diapositiva {i}: «{n}» no está en el documento ({t.strip()[:50]!r})"
                        )
    print("\n".join(faltan) or "ok: todas las cifras del mazo están en el documento")
    return 1 if faltan else 0


def verificar(prs: Presentation) -> int:
    fallos = []
    for i, s in enumerate(prs.slides, 1):
        for f in s.shapes:
            if f.shape_type == 13:  # imagen
                px = Image.open(io.BytesIO(f.image.blob)).size[0]
                ppp = px / max(f.width / 914400, 0.01)
                if ppp < PPP_MINIMO and f.width / 914400 > 1.2:
                    fallos.append(
                        f"diapositiva {i}: «{f.name}» a {ppp:.0f} ppp (mínimo {PPP_MINIMO})"
                    )
                if not (f._element.xpath(".//p:cNvPr/@descr") or [""])[0]:
                    fallos.append(f"diapositiva {i}: «{f.name}» sin texto alternativo")
            elif (
                f.has_text_frame
                and not f.text_frame.text.strip()
                and f.shape_type == 17
            ):
                fallos.append(f"diapositiva {i}: caja de texto vacía «{f.name}»")
    print(
        "\n".join(fallos) or "ok: imágenes nítidas y con descripción, sin cajas vacías"
    )
    return 1 if fallos else 0


def notas(prs: Presentation, guion: Path) -> None:
    datos = yaml.safe_load(guion.read_text(encoding="utf-8"))
    if isinstance(datos, list):
        datos = {d["n"]: d["texto"] for d in datos}
    for n, t in datos.items():
        prs.slides[int(n) - 1].notes_slide.notes_text_frame.text = str(t).strip()
    print(f"ok notas en {len(datos)} diapositivas")


def ocultar(prs: Presentation, numeros: list[int], mostrar: bool) -> None:
    for n in numeros:
        el = prs.slides[n - 1]._element
        if mostrar:
            el.attrib.pop("show", None)
        else:
            el.set("show", "0")
    print(f"ok {'visibles' if mostrar else 'ocultas'}: {numeros}")


def imagen(prs: Presentation, n: int, nombre: str, archivo: Path) -> None:
    s = prs.slides[n - 1]
    vieja = next(f for f in s.shapes if f.name == nombre and f.shape_type == 13)
    w, h = Image.open(archivo).size
    escala = min(vieja.width / w, vieja.height / h)
    nw, nh = int(w * escala), int(h * escala)
    x, y = vieja.left + (vieja.width - nw) // 2, vieja.top + (vieja.height - nh) // 2
    arbol = s.shapes._spTree
    orden = list(arbol).index(vieja._element)
    nueva = s.shapes.add_picture(str(archivo), x, y, Emu(nw), Emu(nh))
    nueva.name = nombre
    ids = [int(i) for i in s._element.xpath("//p:cNvPr/@id")]
    nueva._element.xpath(".//p:cNvPr")[0].set(
        "id", str(max(ids) + 1)
    )  # evita ids duplicados (Word se queja)
    arbol.remove(nueva._element)
    arbol.insert(orden, nueva._element)
    arbol.remove(vieja._element)
    print(f"ok imagen de la diapositiva {n} reemplazada ({nombre})")


def tarjetas(prs: Presentation, despues: int, spec: dict) -> None:
    base = prs.slides[spec["base"] - 1]
    nueva = prs.slides.add_slide(base.slide_layout)
    for ph in list(nueva.placeholders):
        ph._element.getparent().remove(ph._element)
    modelo = [
        f
        for f in base.shapes
        if f.shape_type == 1 and f.has_text_frame and len(f.text_frame.paragraphs) >= 2
    ]
    titulo = next(
        (f for f in base.shapes if f.is_placeholder or f.name.startswith("Título")),
        None,
    )
    for f in base.shapes:  # logo y número de página: se clonan; las tarjetas se rehacen
        if f.shape_type == 13:
            p = nueva.shapes.add_picture(
                io.BytesIO(f.image.blob), f.left, f.top, f.width, f.height
            )
            p.name = f.name
        elif (
            titulo is not None and f._element is titulo._element
        ) or _es_numero_de_pagina(f):
            nueva.shapes._spTree.append(copy.deepcopy(f._element))
    for f in nueva.shapes:
        if f.has_text_frame and f.name.startswith("Título"):
            f.text_frame.paragraphs[0].runs[0].text = spec["titulo"]
    k = len(spec["tarjetas"])
    ancho_total, x0, y0, alto = 777 * 12700, 93 * 12700, 175 * 12700, 200 * 12700
    sep = 20 * 12700
    ancho = (ancho_total - sep * (k - 1)) // k
    for j, t in enumerate(spec["tarjetas"]):
        c = copy.deepcopy(modelo[0]._element)
        nueva.shapes._spTree.append(c)
        forma = nueva.shapes[-1]
        forma.left, forma.top, forma.width, forma.height = (
            Emu(x0 + j * (ancho + sep)),
            Emu(y0),
            Emu(ancho),
            Emu(alto),
        )
        ps = forma.text_frame.paragraphs
        ps[0].runs[0].text = t["cifra"]
        for extra in ps[0].runs[1:]:
            extra._r.getparent().remove(extra._r)
        ps[1].runs[0].text = t["texto"]
        ps[1].runs[0].font.size = Pt(spec.get("texto_pt", 16))
        ps[0].runs[0].font.size = Pt(spec.get("cifra_pt", 40))
        for extra in ps[1].runs[1:]:
            extra._r.getparent().remove(extra._r)
        for extra in ps[2:]:
            extra._p.getparent().remove(extra._p)
    if spec.get("pie"):
        caja = nueva.shapes.add_textbox(
            Emu(x0), Emu(y0 + alto + 40 * 12700), Emu(ancho_total), Emu(70 * 12700)
        )
        caja.text_frame.word_wrap = True
        caja.text_frame.text = spec["pie"]
        run = caja.text_frame.paragraphs[0].runs[0]
        run.font.size = Pt(spec.get("pie_pt", 16))
        run.font.italic = True
        run.font.color.rgb = RGBColor.from_string(spec.get("pie_color", "032154"))
    lista = prs.slides._sldIdLst
    nuevo_id = lista[-1]
    lista.remove(nuevo_id)
    lista.insert(despues, nuevo_id)
    print(
        f"ok diapositiva nueva en la posición {despues + 1} con {k} tarjetas (renumerar los números escritos)"
    )


def mover_al_final(prs: Presentation, numeros: list[int]) -> None:
    lista = prs.slides._sldIdLst
    elegidos = [lista[n - 1] for n in numeros]
    for el in elegidos:
        lista.remove(el)
        lista.append(el)
    print(f"ok {numeros} al final (renumerar los números escritos)")


def renumerar(prs: Presentation) -> None:
    """Escribe en cada diapositiva su número real (cajas «Marcador de contenido»)."""
    for i, s in enumerate(prs.slides, 1):
        for f in s.shapes:
            if _es_numero_de_pagina(f) and f.has_text_frame and f.text_frame.paragraphs[0].runs:
                runs = f.text_frame.paragraphs[0].runs
                runs[0].text = str(i)
                for r in runs[1:]:
                    r._r.getparent().remove(r._r)


def ids_unicos(prs: Presentation) -> int:
    """PowerPoint no abre (ni repara) una diapositiva con dos formas del mismo id: se reasignan los repetidos."""
    cambios = 0
    for s in prs.slides:
        vistos = set()
        nodos = s._element.xpath("//p:cNvPr")
        maximo = max((int(n.get("id")) for n in nodos), default=0)
        for n in nodos:
            if n.get("id") in vistos:
                maximo += 1
                n.set("id", str(maximo))
                cambios += 1
            vistos.add(n.get("id"))
    return cambios


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    cmd, mazo = sys.argv[1], Path(sys.argv[2])
    a = sys.argv[3:]
    prs = Presentation(mazo)
    rc = 0
    if cmd == "texto":
        texto(prs, Path(a[a.index("--md") + 1]) if "--md" in a else None)
        return 0
    if cmd == "cifras":
        return cifras(prs, Path(a[a.index("--tg") + 1]))
    if cmd == "verificar":
        return verificar(prs)
    if cmd == "notas":
        notas(prs, Path(a[0]))
    elif cmd == "ocultar":
        ocultar(prs, [int(x) for x in a if x.isdigit()], "--mostrar" in a)
    elif cmd == "imagen":
        imagen(prs, int(a[0]), a[1], Path(a[2]))
    elif cmd == "ids":
        pass
    elif cmd == "mover":
        mover_al_final(prs, [int(x) for x in a if x.isdigit()])
        renumerar(prs)
    elif cmd == "tarjetas":
        tarjetas(
            prs,
            int(a[a.index("--despues") + 1]),
            yaml.safe_load(Path(a[a.index("--spec") + 1]).read_text("utf-8")),
        )
    else:
        print(__doc__)
        return 2
    if n := ids_unicos(prs):
        print(f"ok {n} ids de forma repetidos reasignados")
    prs.save(mazo)
    return rc


if __name__ == "__main__":
    sys.exit(main())
