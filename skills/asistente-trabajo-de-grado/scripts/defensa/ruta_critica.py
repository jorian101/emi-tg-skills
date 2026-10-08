#!/usr/bin/env python3
"""Ruta crítica en Excalidraw (motor de carriles, LEGADO: el principal es diagrama_flujo.py): carriles por
rol, una columna por tarea en orden, y debajo de cada tarea cómo la asiste el producto del TG. Todo sale de ruta-critica.yaml (que cita sus fuentes del TG).

Uso:
  uv run --with pyyaml --with pillow --with cairosvg python ruta_critica.py crear     <spec.yaml>  # .excalidraw
  uv run --with pyyaml --with pillow --with cairosvg python ruta_critica.py exportar  <spec.yaml>  # .png y .pdf
  uv run --with pyyaml --with pillow --with cairosvg python ruta_critica.py verificar <spec.yaml>  # textos dentro
La salida queda junto a la spec. Modelo comentado: assets/defensa/ruta-critica.example.yaml.
Reusa diagrama_animado.py (texto, elementos y exportación con Excalidraw real en Chrome headless).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagrama_animado as da  # noqa: E402
from PIL import Image  # noqa: E402

SPEC = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("ruta-critica.yaml").resolve()
AQUI = SPEC.parent
COLOR = {  # trazo, relleno, rótulo del tipo de tarea
    "analisis": ("#1971c2", "#e7f0fb", "ANÁLISIS"),
    "redaccion": ("#2f9e44", "#ebf7ee", "REDACCIÓN"),
    "fuera": ("#868e96", "#f1f3f5", "FUERA DEL {PRODUCTO}"),
    "total": ("#032154", "#e9ecef", ""),
}
ASISTE = ("#6741d9", "#f3f0ff")
COL_W, GAP, IZQ = 300, 22, 170
T_TAREA, T_TIEMPO, T_ASISTE, T_ROT = 26, 32, 25, 22
ALTO_TAREA, ALTO_ASISTE, PAD = 330, 330, 14


def _bloque(els, x, y, w, h, trazo, relleno, **kw):
    els.append(da._base("rectangle", x, y, w, h, strokeColor=trazo, backgroundColor=relleno,
                        roundness={"type": 3}, strokeWidth=3, **kw))


def crear() -> Path:
    sp = da.leer(SPEC)
    tareas = sp["tareas"]
    n = len(tareas)
    W = IZQ + n * COL_W + (n - 1) * GAP + 40
    els = []
    titulo = da._texto(40, 30, W - 80, sp["titulo"], 54, da.AZUL_OSCURO, True)
    sub = da._texto(40, titulo["y"] + titulo["height"] + 8, W - 80, sp["subtitulo"], 32, da.GRIS)
    els += [titulo, sub]
    arriba = sub["y"] + sub["height"] + 40
    alto_carril = ALTO_TAREA + 20 + ALTO_ASISTE + 2 * PAD
    y_carril = {c: arriba + i * (alto_carril + 20) for i, c in enumerate(sp["carriles"])}
    for c, y in y_carril.items():  # fondo y nombre de cada carril
        _bloque(els, 20, y, W - 40, alto_carril, "#ced4da", "#fbfcfd")
        nombre = da._texto(24, y + alto_carril / 2 - 40, IZQ - 40, c, 34, da.AZUL_OSCURO, True)
        els.append(nombre)
    cajas = {}
    for i, t in enumerate(tareas):
        x = IZQ + i * (COL_W + GAP)
        trazo, relleno, rot = COLOR[t["tipo"]]
        rot = rot.replace("{PRODUCTO}", sp.get("producto", "sistema").upper())
        if t["carril"] == "ambos":
            y0 = y_carril[sp["carriles"][0]] + PAD
            alto = y_carril[sp["carriles"][-1]] + alto_carril - PAD - y0
            h_tarea = alto - ALTO_ASISTE - 20
        else:
            y0, h_tarea = y_carril[t["carril"]] + PAD, ALTO_TAREA
        _bloque(els, x, y0, COL_W, h_tarea, trazo, relleno, customData={"tarea": t["id"]})
        e_rot = da._texto(x + 10, y0 + 12, COL_W - 20, rot, T_ROT, trazo, True)
        e_tiempo = da._texto(x + 10, e_rot["y"] + e_rot["height"] + 4, COL_W - 20, t["tiempo"], T_TIEMPO, trazo, True)
        e_tarea = da._texto(x + 10, e_tiempo["y"] + e_tiempo["height"] + 8, COL_W - 20, t["tarea"], T_TAREA,
                            da.AZUL_OSCURO, True, customData={"dentro": t["id"]})
        els += [e_rot, e_tiempo, e_tarea]
        y_a = y0 + h_tarea + 20
        _bloque(els, x, y_a, COL_W, ALTO_ASISTE, *ASISTE, customData={"asiste": t["id"]})
        e_cab = da._texto(x + 10, y_a + 12, COL_W - 20, "CÓMO ASISTE", T_ROT, ASISTE[0], True)
        e_as = da._texto(x + 10, e_cab["y"] + e_cab["height"] + 6, COL_W - 20, t["asiste"], T_ASISTE, "#343a40",
                         customData={"dentro_asiste": t["id"]})
        els += [e_cab, e_as]
        els.append(da._base("line", x + COL_W / 2, y0 + h_tarea, 0, 20, strokeColor=ASISTE[0], strokeWidth=3,
                            strokeStyle="dashed", points=[[0, 0], [0, 20]], lastCommittedPoint=None,
                            startBinding=None, endBinding=None, startArrowhead=None, endArrowhead=None))
        cajas[t["id"]] = (x, y0, COL_W, h_tarea)
    for a, b in zip(tareas, tareas[1:]):  # camino crítico: la secuencia completa, en trazo grueso
        ax, ay, aw, ah = cajas[a["id"]]
        bx, by, bw, bh = cajas[b["id"]]
        p0 = (ax + aw + 2, ay + min(ah, ALTO_TAREA) / 2)
        p3 = (bx - 2, by + min(bh, ALTO_TAREA) / 2)
        xm = (p0[0] + p3[0]) / 2
        pts = [[0, 0], [xm - p0[0], 0], [xm - p0[0], p3[1] - p0[1]], [p3[0] - p0[0], p3[1] - p0[1]]]
        els.append(da._base("arrow", p0[0], p0[1], abs(p3[0] - p0[0]), abs(p3[1] - p0[1]) or 1,
                            strokeColor="#c92a2a", strokeWidth=5, points=pts, lastCommittedPoint=None,
                            startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow",
                            elbowed=False))
    y = max(y_carril.values()) + alto_carril + 40
    ancho = (W - 80 - 2 * 30) / 3
    for i, r in enumerate(sp["resumen"]):
        x = 40 + i * (ancho + 30)
        trazo, relleno, _ = COLOR[r["tipo"]]
        _bloque(els, x, y, ancho, 170, trazo, relleno)
        c = da._texto(x + 20, y + 22, ancho - 40, r["cifra"], 52, trazo, True)
        els += [c, da._texto(x + 20, c["y"] + c["height"] + 8, ancho - 40, r["rotulo"], 30, da.AZUL_OSCURO)]
    y += 200
    prod = sp.get("producto", "sistema")  # cómo nombra el TG a su producto
    ley = (f"Rojo: camino crítico (orden de las tareas). Azul: análisis. Verde: redacción. Gris: fuera del {prod}. "
           f"Violeta: cómo asiste el {prod}.")
    e_ley = da._texto(40, y, W - 80, ley, 30, da.AZUL_OSCURO, True)
    e_nota = da._texto(40, e_ley["y"] + e_ley["height"] + 12, W - 80, sp["nota"], 28, da.GRIS)
    els += [e_ley, e_nota]
    H = e_nota["y"] + e_nota["height"] + 40
    els.insert(0, da._base("rectangle", 0, 0, W, H, id="lienzo", strokeColor="transparent",
                           backgroundColor="#ffffff", strokeWidth=1))
    doc = {"type": "excalidraw", "version": 2, "source": "ruta_critica.py", "elements": els,
           "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None, "exportScale": sp.get("escala_export", 1)},
           "files": {}}
    out = AQUI / f"{sp['slug']}.excalidraw"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok {out.name} ({W:.0f}×{H:.0f})")
    return out


def exportar() -> None:
    sp = da.leer(SPEC)
    da.FUENTE = AQUI  # el exportador busca <slug>.excalidraw en FUENTE
    png = da.exportar(str(SPEC))
    final = AQUI / f"{sp['slug']}.png"
    png.replace(final)
    img = Image.open(final).convert("RGB")
    img.save(AQUI / f"{sp['slug']}.pdf", resolution=200)
    print(f"ok {final.name} {img.size} y {sp['slug']}.pdf")


def verificar() -> int:
    sp = da.leer(SPEC)
    doc = json.loads((AQUI / f"{sp['slug']}.excalidraw").read_text(encoding="utf-8"))
    els = doc["elements"]
    k = sp.get("escala_export", 1)
    cajas = {(e["customData"].get("tarea") or e["customData"].get("asiste"), "tarea" if "tarea" in e["customData"] else "asiste"): e
             for e in els if e["type"] == "rectangle" and e.get("customData")}
    fallos = []
    for e in els:
        if e["type"] != "text":
            continue
        if e["fontSize"] * k < 40:
            fallos.append(f"letra chica en la cartulina ({e['fontSize'] * k} px): {e['text'][:40]!r}")
        cd = e.get("customData") or {}
        for clave, tipo in (("dentro", "tarea"), ("dentro_asiste", "asiste")):
            if clave in cd:
                c = cajas[(cd[clave], tipo)]
                if e["y"] + e["height"] > c["y"] + c["height"] - 6:
                    fallos.append(f"el texto se sale de la caja {cd[clave]} ({tipo}): {e['text'][:40]!r}")
    print("\n".join(fallos) or "ok ruta-critica: textos dentro de sus cajas y legibles en la cartulina")
    return 1 if fallos else 0


if __name__ == "__main__":
    r = {"crear": crear, "exportar": exportar, "verificar": verificar}[sys.argv[1]]()
    sys.exit(r if isinstance(r, int) else 0)
