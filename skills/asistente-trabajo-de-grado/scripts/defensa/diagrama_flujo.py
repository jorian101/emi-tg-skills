#!/usr/bin/env python3
"""Diagrama de flujo en Excalidraw desde YAML: inicio y fin (óvalos), pasos numerados (rectángulos),
decisiones (rombos), colores por fase con su leyenda y flechas, incluidas las de vuelta en codo.

Uso:
  uv run --with pyyaml --with pillow python diagrama_flujo.py crear     <spec.yaml>
  uv run --with pyyaml --with pillow python diagrama_flujo.py verificar <spec.yaml> [--tg extraccion.md]
  uv run --with pyyaml --with pillow python diagrama_flujo.py exportar  <spec.yaml>   # .png y .pdf
La salida queda junto a la spec. Modelo comentado: assets/defensa/flujo.example.yaml.
Cada nodo va en una celda (fila, col) de la grilla; una arista entre celdas vecinas es recta, y una con
`vuelta: arriba` sube por el pasillo entre filas o, con `vuelta: izquierda`, rodea por el margen izquierdo.
"""

from __future__ import annotations

import json
import re
import sys
import unicodedata
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import diagrama_animado as da  # noqa: E402
from PIL import Image  # noqa: E402

SPEC = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else Path("flujo.yaml").resolve()
AQUI = SPEC.parent
NW, NH, GX, GY, MX = 440, 250, 130, 170, 150  # nodo, separaciones y margen
T_TEXTO, T_DETALLE, T_ROTULO = 34, 25, 26


def _caja(n: dict, arriba: float) -> tuple[float, float, float, float]:
    return MX + n["col"] * (NW + GX), arriba + n["fila"] * (NH + GY), NW, NH


def crear() -> Path:
    global GX, GY
    sp = da.leer(SPEC)
    GX, GY = sp.get("separacion", [GX, GY])  # más pasillo si los rótulos de las flechas son largos
    cols = max(n["col"] for n in sp["nodos"]) + 1
    filas = max(n["fila"] for n in sp["nodos"]) + 1
    W = 2 * MX + cols * NW + (cols - 1) * GX
    els = []
    titulo = da._texto(40, 30, W - 80, sp["titulo"], 54, da.AZUL_OSCURO, True)
    els.append(titulo)
    arriba = titulo["y"] + titulo["height"] + 30
    if sp.get("subtitulo"):
        sub = da._texto(40, arriba, W - 80, sp["subtitulo"], 32, da.GRIS)
        els.append(sub)
        arriba = sub["y"] + sub["height"] + 40
    fases, cajas, num = sp["fases"], {}, 0
    for n in sp["nodos"]:
        x, y, w, h = _caja(n, arriba)
        trazo, relleno = fases[n["fase"]]["trazo"], fases[n["fase"]]["relleno"]
        tipo = {"inicio": "ellipse", "fin": "ellipse", "decision": "diamond"}.get(n["tipo"], "rectangle")
        forma = da._base(tipo, x, y, w, h, strokeColor=trazo, backgroundColor=relleno, strokeWidth=4,
                         roundness={"type": 3} if tipo == "rectangle" else None, customData={"nodo": n["id"]})
        els.append(forma)
        cajas[n["id"]] = (x, y, w, h)
        # zona útil del texto: el rombo y el óvalo solo admiten el rectángulo inscrito
        ix, iw = (x + w * 0.22, w * 0.56) if tipo == "diamond" else (x + w * 0.12, w * 0.76) if tipo == "ellipse" else (x + 22, w - 44)
        color = fases[n["fase"]].get("texto", da.AZUL_OSCURO)
        bloques = [(n["texto"], T_TEXTO, True)] + ([(n["detalle"], T_DETALLE, False)] if n.get("detalle") else [])
        textos = [da._texto(ix, 0, iw, t, tam, color, neg) for t, tam, neg in bloques]
        alto = sum(t["height"] for t in textos) + 10 * (len(textos) - 1)
        yy = y + (h - alto) / 2
        for t in textos:
            t["y"] = yy
            t["customData"] = {"dentro": n["id"]}
            yy += t["height"] + 10
            els.append(t)
        if n["tipo"] == "paso":  # número del paso en un círculo sobre la esquina (`numero` lo fija a mano)
            num = n.get("numero", num + 1)
            els.append(da._base("ellipse", x - 26, y - 26, 64, 64, strokeColor=trazo, backgroundColor=trazo,
                                strokeWidth=2))
            c = da._texto(x - 26, y - 26 + 12, 64, str(num), 32, "#ffffff", True)
            els.append(c)
    for a in sp["aristas"]:
        els += _flecha(cajas[a["de"]], cajas[a["a"]], a, fases)
    y_ley = arriba + filas * (NH + GY) + 10
    x_ley = MX
    for clave, f in fases.items():
        if not f.get("leyenda"):
            continue
        els.append(da._base("rectangle", x_ley, y_ley, 48, 48, strokeColor=f["trazo"], backgroundColor=f["relleno"],
                            strokeWidth=3, roundness={"type": 3}))
        t = da._texto(x_ley + 60, y_ley + 6, 900, f["leyenda"], 30, da.AZUL_OSCURO)
        t["x"] = x_ley + 60
        els.append(t)
        x_ley += 60 + t["width"] + 70
    y_fin = y_ley + 90
    if sp.get("recuadro"):  # recuadro destacado debajo de la leyenda (título y líneas)
        r = sp["recuadro"]
        f = fases[r["fase"]]
        lineas = [da._texto(MX + 30, 0, W - 2 * MX - 60, r["titulo"], 32, f["trazo"], True)]
        lineas += [da._texto(MX + 30, 0, W - 2 * MX - 60, txt, 28, da.AZUL_OSCURO) for txt in r["lineas"]]
        yy = y_fin + 24
        for t in lineas:
            t["y"] = yy
            yy += t["height"] + 14
        els.append(da._base("rectangle", MX, y_fin, W - 2 * MX, yy - y_fin + 10, strokeColor=f["trazo"],
                            backgroundColor=f["relleno"], strokeWidth=3, roundness={"type": 3}))
        els += lineas
        y_fin = yy + 50
    if sp.get("nota"):
        els.append(da._texto(40, y_fin, W - 80, sp["nota"], 28, da.GRIS))
    doc = {"type": "excalidraw", "version": 2, "source": "diagrama_flujo.py", "elements": els,
           "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None, "exportScale": sp.get("escala_export", 3)},
           "files": {}}
    out = AQUI / f"{sp['slug']}.excalidraw"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok {out.name} ({int(W)}×{int(y_fin + 70)})")
    return out


def _flecha(o, d, a, fases) -> list[dict]:
    """Recta entre celdas vecinas; `vuelta: arriba` sube por el pasillo; `vuelta: izquierda` rodea por el margen."""
    ox, oy, ow, oh = o
    dx, dy, dw, dh = d
    if a.get("vuelta") == "arriba":
        pts = [(ox + ow / 2, oy), (ox + ow / 2, oy - GY / 2), (dx + dw / 2, oy - GY / 2), (dx + dw / 2, dy + dh)]
    elif a.get("vuelta") == "izquierda":
        bajo, lado = oy + oh + GY * 0.4, MX * 0.45
        pts = [(ox + ow / 2, oy + oh), (ox + ow / 2, bajo), (lado, bajo), (lado, dy + dh / 2), (dx, dy + dh / 2)]
    elif abs(oy - dy) < 1:  # misma fila
        pts = [(ox + ow, oy + oh / 2), (dx, dy + dh / 2)] if dx > ox else [(ox, oy + oh / 2), (dx + dw, dy + dh / 2)]
    elif dy > oy:  # baja a la fila siguiente en la misma columna
        pts = [(ox + ow / 2, oy + oh), (dx + dw / 2, dy)]
    else:  # sube en la misma columna
        pts = [(ox + ow / 2, oy), (dx + dw / 2, dy + dh)]
    color = fases.get(a.get("fase", ""), {}).get("trazo", "#343a40")
    x0, y0 = pts[0]
    flecha = da._base("arrow", x0, y0, max(p[0] for p in pts) - min(p[0] for p in pts),
                      max(p[1] for p in pts) - min(p[1] for p in pts), strokeColor=color,
                      strokeWidth=4, strokeStyle="dashed" if a.get("vuelta") else "solid",
                      points=[[px - x0, py - y0] for px, py in pts], lastCommittedPoint=None,
                      startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow",
                      elbowed=False)
    out = [flecha]
    if a.get("rotulo"):
        (px, py), (qx, qy) = (pts[1], pts[2]) if len(pts) > 2 else (pts[0], pts[1])
        if abs(px - qx) < 1:  # vertical: el rótulo va al costado, a media altura
            t = da._texto(px + 16, (py + qy) / 2 - 18, 380, a["rotulo"], T_ROTULO, color, True)
            t["x"] = px + 16
        else:
            t = da._texto(min(px, qx), min(py, qy) - 50, max(abs(qx - px), 200), a["rotulo"], T_ROTULO, color, True)
        out.append(t)
    return out


def exportar() -> None:
    sp = da.leer(SPEC)
    da.FUENTE = AQUI  # el exportador busca <slug>.excalidraw en FUENTE
    da._PAGINA = da._PAGINA.replace("exportPadding: 0", "exportPadding: 60")  # la vuelta izquierda no toca el borde
    png = da.exportar(str(SPEC))
    final = AQUI / f"{sp['slug']}.png"
    png.replace(final)
    img = Image.open(final).convert("RGB")
    img.save(AQUI / f"{sp['slug']}.pdf", resolution=200)
    print(f"ok {final.name} {img.size} y {sp['slug']}.pdf")


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s.casefold())
    return re.sub(r"\s+", " ", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def verificar() -> int:
    sp = da.leer(SPEC)
    doc = json.loads((AQUI / f"{sp['slug']}.excalidraw").read_text(encoding="utf-8"))
    k = sp.get("escala_export", 3)
    formas = {e["customData"]["nodo"]: e for e in doc["elements"] if (e.get("customData") or {}).get("nodo")}
    fallos = []
    for e in doc["elements"]:
        if e["type"] != "text":
            continue
        if e["fontSize"] * k < 60:
            fallos.append(f"letra chica en la cartulina ({e['fontSize'] * k} px): {e['text'][:40]!r}")
        dentro = (e.get("customData") or {}).get("dentro")
        if dentro:
            f = formas[dentro]
            m = 0.22 if f["type"] == "diamond" else 0.12 if f["type"] == "ellipse" else 0.0
            if f["type"] == "diamond":  # el rombo solo admite su rectángulo inscrito
                y0, y1 = f["y"] + f["height"] * 0.2, f["y"] + f["height"] * 0.8
            else:
                y0, y1 = f["y"] + 6, f["y"] + f["height"] - 6
            if e["x"] < f["x"] + f["width"] * m - 2 or e["x"] + e["width"] > f["x"] + f["width"] * (1 - m) + 2 \
                    or e["y"] < y0 or e["y"] + e["height"] > y1:
                fallos.append(f"el texto se sale de {dentro}: {e['text'][:40]!r}")
    if "--tg" in sys.argv:
        tg = _norm(Path(sys.argv[sys.argv.index("--tg") + 1]).read_text(encoding="utf-8"))
        fallos += [f"término que el TG no declara: {t!r}" for t in sp.get("terminos_tg", []) if _norm(t) not in tg]
    print("\n".join(fallos) or f"ok {sp['slug']}: textos dentro de sus formas, legibles y con términos del TG")
    return 1 if fallos else 0


if __name__ == "__main__":
    r = {"crear": crear, "exportar": exportar, "verificar": verificar}[sys.argv[1]]()
    sys.exit(r if isinstance(r, int) else 0)
