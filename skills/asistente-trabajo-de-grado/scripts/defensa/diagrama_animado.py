#!/usr/bin/env python3
"""Diagramas animados para público no técnico: Excalidraw + íconos planos que se mueven en bucle.

  crear <spec.yaml>      arma fuente/<slug>.excalidraw (editable en Obsidian/Excalidraw) desde el YAML
  exportar <spec.yaml>   exporta el fondo (sin los íconos animados) con Excalidraw dentro de Chrome headless
  animar <spec.yaml>     salida/<slug>.gif + .mp4 + -final.png: el punto recorre el flujo, el paso activo
                         se ilumina y CADA ícono se mueve en bucle a la vez (más fuerte el activo)
  verificar <spec.yaml>  letra legible en el tamaño final y que no falte ningún concepto de la técnica

Uso: uv run --with pyyaml --with pillow --with cairosvg --with imageio --with imageio-ffmpeg \
       python diagrama_animado.py <comando> <spec.yaml>
Chrome: $CHROME, `chromium`/`google-chrome` en el PATH o el chrome-headless-shell de ~/.cache/puppeteer.
Íconos: SVG planos en iconos/ (Tabler, licencia MIT en iconos/LICENSE-tabler.txt).
"""

from __future__ import annotations

import base64
import glob
import io
import json
import math
import os
import random
import shutil
import subprocess
import sys
import tempfile
import threading
import unicodedata
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

AQUI = Path.cwd()  # la carpeta del diagrama del proyecto (desde donde se corre)
ICONOS = AQUI / "iconos"
FUENTE = AQUI / "fuente"
SALIDA = AQUI / "salida"

AZUL, AZUL_OSCURO, GRIS = "#0a3a82", "#032154", "#495057"
FONDO_TARJETA, BORDE = "#eef3fb", "#0a3a82"
BRILLO, PUNTO = (245, 159, 0), (215, 25, 32)
TAM = {"titulo": 48, "frase": 36, "termino": 28, "franja": 40, "paso": 30}  # px en el tamaño final
MIN_FRASE, MIN_TEXTO = 36, 28
FPS, VIAJE, PAUSA, FINAL, PERIODO = 14, 12, 22, 28, 28
FRANJA = 150
LETRA = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
LETRA_N = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def leer(spec: str) -> dict:
    return yaml.safe_load(Path(spec).read_text(encoding="utf-8"))


# ---------------------------------------------------------------- texto
def fuente(tam: int, negrita=False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(LETRA_N if negrita else LETRA, tam)


def partir(texto: str, tam: int, ancho: int, negrita=False) -> list[str]:
    f, lineas, actual = fuente(tam, negrita), [], ""
    for palabra in texto.split():
        prueba = f"{actual} {palabra}".strip()
        if f.getlength(prueba) <= ancho:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    return lineas + [actual]


# ---------------------------------------------------------------- íconos
def icono_png(nombre: str, lado: int, color: str = AZUL) -> Image.Image:
    import cairosvg

    svg = (ICONOS / f"{nombre}.svg").read_text(encoding="utf-8")
    svg = svg.replace("currentColor", color).replace('stroke-width="2"', 'stroke-width="1.6"')
    png = cairosvg.svg2png(bytestring=svg.encode(), output_width=lado, output_height=lado)
    return Image.open(io.BytesIO(png)).convert("RGBA")


def mover(img: Image.Image, mov: str, t: float, amp: float) -> tuple[Image.Image, int, int, list]:
    """Devuelve (imagen transformada, dx, dy, extras dibujables) para la fase t∈[0,1) del bucle."""
    s, lado = math.sin(2 * math.pi * t), img.width
    extras: list = []
    dx = dy = 0
    if mov == "deslizar":
        dx = int(s * 0.22 * lado * amp)
    elif mov == "apilar":
        dy = -int(abs(s) * 0.22 * lado * amp)
    elif mov in ("cortar", "balancear", "barajar"):
        ang = {"cortar": 24, "balancear": 14, "barajar": 12}[mov] * s * amp
        img = img.rotate(ang, resample=Image.BICUBIC)
        if mov == "barajar":
            dx = int(s * 0.06 * lado * amp)
    elif mov in ("crecer", "latir"):
        k = 1 + (0.24 if mov == "latir" else 0.3) * amp * (0.5 + 0.5 * s if mov == "crecer" else max(s, 0))
        nuevo = img.resize((max(1, int(lado * k)),) * 2, Image.BICUBIC)
        dx = dy = -(nuevo.width - lado) // 2
        if mov == "crecer":
            dy = -(nuevo.width - lado)  # crece desde la base
        img = nuevo
    elif mov == "girar":
        img = img.rotate(-360 * t * amp, resample=Image.BICUBIC)
    elif mov == "barrer":
        dx, dy = int(math.cos(2 * math.pi * t) * 0.1 * lado * amp), int(s * 0.1 * lado * amp)
    elif mov == "parpadear":
        a = img.getchannel("A").point(lambda v: int(v * (0.55 + 0.45 * (0.5 + 0.5 * s) if amp else 1)))
        img.putalpha(a)
    elif mov == "escanear":
        extras.append(("linea", t))
    elif mov == "escribir":
        ancho = int(lado * (0.25 + 0.75 * t)) if amp else lado
        mascara = Image.new("L", img.size, 0)
        ImageDraw.Draw(mascara).rectangle([0, 0, ancho, lado], fill=255)
        alfa = Image.composite(img.getchannel("A"), Image.new("L", img.size, 0), mascara)
        img.putalpha(alfa)
    elif mov == "filtrar":
        extras.append(("gotas", t))
    return img, dx, dy, extras


# ---------------------------------------------------------------- crear (.excalidraw)
def _base(tipo: str, x, y, w, h, **kw) -> dict:
    r = random.Random(f"{tipo}{x}{y}{w}{h}{kw.get('text', '')}")
    e = {
        "id": kw.pop("id", None) or "".join(r.choice("abcdefghijkmnpqrstuvwxyz0123456789") for _ in range(16)),
        "type": tipo, "x": x, "y": y, "width": w, "height": h, "angle": 0,
        "strokeColor": AZUL, "backgroundColor": "transparent", "fillStyle": "solid",
        "strokeWidth": 2, "strokeStyle": "solid", "roughness": 0, "opacity": 100,
        "groupIds": [], "frameId": None, "roundness": None, "seed": r.randint(1, 2**31),
        "version": 1, "versionNonce": r.randint(1, 2**31), "isDeleted": False,
        "boundElements": None, "updated": 1, "link": None, "locked": False,
    }
    e.update(kw)
    return e


def _texto(x, y, ancho_caja, texto, tam, color, negrita=False, **kw) -> dict:
    lineas = partir(texto, tam, ancho_caja, negrita)
    f = fuente(tam, negrita)
    w = max(f.getlength(linea) for linea in lineas)
    h = len(lineas) * tam * 1.25
    return _base("text", x + (ancho_caja - w) / 2, y, w, h, text="\n".join(lineas),
                 originalText="\n".join(lineas), fontSize=tam, fontFamily=2, textAlign="center",
                 verticalAlign="top", containerId=None, autoResize=True, lineHeight=1.25,
                 strokeColor=color, **kw)


def posiciones(sp: dict) -> dict[str, tuple[float, float]]:
    """Celda de cada nodo; las celdas vacías (null) quedan como `_vacia<i>` para la leyenda."""
    W, Tw, Th = sp["lienzo"]["ancho"], sp["tarjeta"]["ancho"], sp["tarjeta"]["alto"]
    cols = max(len(f) for f in sp["filas"])
    gap = (W - 2 * 60 - cols * Tw) / (cols - 1)
    arriba = 30 + len(partir(sp["titulo"], TAM["titulo"], W - 120, True)) * TAM["titulo"] * 1.25 + 30
    pos = {}
    for i, fila in enumerate(sp["filas"]):
        for j, n in enumerate(fila):
            pos[n or f"_vacia{i}{j}"] = (60 + j * (Tw + gap), arriba + i * (Th + 70))
    return pos


def crear(spec: str) -> Path:
    sp = leer(spec)
    W, H = sp["lienzo"]["ancho"], sp["lienzo"]["alto"]
    Tw, Th = sp["tarjeta"]["ancho"], sp["tarjeta"]["alto"]
    pos = posiciones(sp)
    els = [_base("rectangle", 0, 0, W, H, id="lienzo", strokeColor="transparent",
                 backgroundColor="#ffffff", strokeWidth=1)]
    els.append(_texto(60, 30, W - 120, sp["titulo"], TAM["titulo"], AZUL_OSCURO, True))
    files = {}
    for n, nd in sp["nodos"].items():
        x, y = pos[n]
        els.append(_base("rectangle", x, y, Tw, Th, backgroundColor=FONDO_TARJETA, strokeColor=BORDE,
                         roundness={"type": 3}, customData={"nodo": n}))
        lado = 130
        fid = f"icono-{nd['icono']}"
        files[fid] = {"id": fid, "mimeType": "image/png", "created": 1, "dataURL": "data:image/png;base64,"
                      + base64.b64encode(_png_bytes(icono_png(nd["icono"], lado))).decode()}
        els.append(_base("image", x + (Tw - lado) / 2, y + 22, lado, lado, fileId=fid, status="saved",
                         scale=[1, 1], crop=None, strokeColor="transparent",
                         customData={"nodo": n, "icono": nd["icono"], "movimiento": nd["movimiento"]}))
        frase = _texto(x + 20, y + 22 + lado + 14, Tw - 40, nd["frase"], TAM["frase"], AZUL_OSCURO, True,
                       customData={"nodo": n, "rol": "frase"})
        els.append(frase)
        els.append(_texto(x + 20, frase["y"] + frase["height"] + 10, Tw - 40, nd["termino"], TAM["termino"],
                          GRIS, customData={"nodo": n, "rol": "termino"}))
    for celda, (x, y) in pos.items():  # celda libre: leyenda para quien no es técnico
        if celda.startswith("_vacia") and sp.get("leyenda"):
            els.append(_texto(x + 10, y + 40, Tw - 20, sp["leyenda"], TAM["termino"] + 2, GRIS,
                              customData={"rol": "leyenda"}))
    for a, b in sp["flechas"]:
        (ax, ay), (bx, by) = pos[a], pos[b]
        if abs(ay - by) < 1:  # misma fila
            y0 = ay + Th / 2
            x0, x1 = (ax + Tw, bx) if bx > ax else (ax, bx + Tw)
            p0, p1 = (x0 + 8 * (1 if bx > ax else -1), y0), (x1 - 8 * (1 if bx > ax else -1), y0)
        else:
            x0 = ax + Tw / 2
            p0, p1 = (x0, ay + Th + 8), (x0, by - 8)
        els.append(_base("arrow", p0[0], p0[1], abs(p1[0] - p0[0]), abs(p1[1] - p0[1]), strokeWidth=4,
                         points=[[0, 0], [p1[0] - p0[0], p1[1] - p0[1]]], lastCommittedPoint=None,
                         startBinding=None, endBinding=None, startArrowhead=None, endArrowhead="arrow",
                         elbowed=False, customData={"desde": a, "hasta": b}))
    FUENTE.mkdir(exist_ok=True)
    doc = {"type": "excalidraw", "version": 2, "source": "diagrama_animado.py", "elements": els,
           "appState": {"viewBackgroundColor": "#ffffff", "gridSize": None}, "files": files}
    out = FUENTE / f"{sp['slug']}.excalidraw"
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"ok {out}")
    return out


def _png_bytes(img: Image.Image) -> bytes:
    b = io.BytesIO()
    img.save(b, "PNG")
    return b.getvalue()


# ---------------------------------------------------------------- exportar (Excalidraw real)
_PAGINA = """<!doctype html><script type="module">
const post = (r, b) => fetch('/' + r, {method: 'POST', body: b});
try {
  const {exportToBlob} = await import('https://esm.sh/@excalidraw/excalidraw@0.18.1');
  const doc = await (await fetch('/escena')).json();
  const els = doc.elements.filter(e => !e.isDeleted && !(e.customData && e.customData.icono));
  const blob = await exportToBlob({elements: els, files: doc.files, mimeType: 'image/png', exportPadding: 0,
    appState: {...doc.appState, exportBackground: true, viewBackgroundColor: '#ffffff'},
    getDimensions: (w, h) => { const s = doc.appState.exportScale || 1; return {width: w * s, height: h * s, scale: s}; }});
  await post('png', blob);
} catch (e) { await post('err', String(e) + '\\n' + e.stack); }
</script>"""


def navegador() -> str:
    for c in [os.environ.get("CHROME"), shutil.which("chromium"), shutil.which("google-chrome"),
              *sorted(glob.glob(os.path.expanduser(
                  "~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell")))[::-1]]:
        if c and Path(c).exists():
            return c
    sys.exit("No encuentro Chrome: definí CHROME o instalá chromium / chrome-headless-shell.")


def exportar(spec: str) -> Path:
    sp = leer(spec)
    doc = (FUENTE / f"{sp['slug']}.excalidraw").read_bytes()
    cuerpo, res, listo = {"/": _PAGINA.encode(), "/escena": doc}, {}, threading.Event()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(cuerpo.get(self.path, b""))

        def do_POST(self):
            res[self.path] = self.rfile.read(int(self.headers["Content-Length"]))
            self.send_response(200)
            self.end_headers()
            listo.set()

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    perfil = tempfile.mkdtemp()
    proc = subprocess.Popen([navegador(), "--headless=new", "--no-sandbox", "--disable-gpu",
                             f"--user-data-dir={perfil}", f"http://127.0.0.1:{srv.server_port}/"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    listo.wait(240)
    proc.kill()
    srv.shutdown()
    shutil.rmtree(perfil, ignore_errors=True)
    if "/png" not in res:
        raise RuntimeError(f"export falló: {res.get('/err', b'timeout').decode()[:1500]}")
    out = FUENTE / f"{sp['slug']}-fondo.png"
    out.write_bytes(res["/png"])
    print(f"ok {out} {Image.open(out).size}")
    return out


# ---------------------------------------------------------------- animar
def _escena(sp: dict):
    doc = json.loads((FUENTE / f"{sp['slug']}.excalidraw").read_text(encoding="utf-8"))
    els = [e for e in doc["elements"] if not e.get("isDeleted")]
    lienzo = next(e for e in els if e["id"] == "lienzo")
    tarjetas = {e["customData"]["nodo"]: e for e in els if e["type"] == "rectangle" and e.get("customData", {}).get("nodo")}
    iconos = {e["customData"]["nodo"]: e for e in els if e["type"] == "image" and e.get("customData", {}).get("icono")}
    flechas = {(e["customData"]["desde"], e["customData"]["hasta"]): e for e in els
               if e["type"] == "arrow" and e.get("customData", {}).get("desde")}
    return lienzo, tarjetas, iconos, flechas, els


def _franja(img: Image.Image, n: int, total: int, rotulo: str):
    d = ImageDraw.Draw(img)
    W, H = img.size
    d.rectangle([0, H - FRANJA, W, H], fill=AZUL_OSCURO)
    d.text((40, H - FRANJA + 14), f"Paso {n} de {total}" if n else "Recorrido completo", font=fuente(TAM["paso"], True),
           fill=(242, 201, 30))
    lineas = partir(rotulo, TAM["franja"], W - 80)
    for i, linea in enumerate(lineas[:2]):
        d.text((40, H - FRANJA + 54 + i * 48), linea, font=fuente(TAM["franja"]), fill="white")


def animar(spec: str) -> None:
    sp = leer(spec)
    lienzo, tarjetas, iconos, flechas, _ = _escena(sp)
    fondo = Image.open(FUENTE / f"{sp['slug']}-fondo.png").convert("RGB")
    k = fondo.width / lienzo["width"]  # px del PNG por unidad de la escena
    def a_px(x, y):
        return ((x - lienzo["x"]) * k, (y - lienzo["y"]) * k)

    sprites = {n: icono_png(e["customData"]["icono"], int(e["width"] * k)) for n, e in iconos.items()}
    pasos = sp["pasos"]
    orden = [p["nodo"] for p in pasos]
    cuadros: list[Image.Image] = []
    f = 0

    def cuadro(activo: int, viaje: tuple | None, final=False):
        nonlocal f
        img = Image.new("RGB", (fondo.width, fondo.height + FRANJA), "white")
        img.paste(fondo, (0, 0))
        capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(capa)
        for i, n in enumerate(orden):
            t = tarjetas[n]
            x0, y0 = a_px(t["x"], t["y"])
            x1, y1 = a_px(t["x"] + t["width"], t["y"] + t["height"])
            if not final and i > activo:  # lo que todavía no pasó: atenuado
                d.rounded_rectangle([x0, y0, x1, y1], 18, fill=(255, 255, 255, 150))
            if final or i == activo:
                pulso = 0.5 + 0.5 * math.sin(2 * math.pi * f / PERIODO)
                for g in range(3):
                    d.rounded_rectangle([x0 - 4 - g * 3, y0 - 4 - g * 3, x1 + 4 + g * 3, y1 + 4 + g * 3], 22,
                                        outline=(*BRILLO, int(200 - g * 60 * (1 - pulso))), width=4)
        img.paste(capa, (0, 0), capa)
        for i, n in enumerate(orden):  # todos los íconos se mueven en bucle; el activo, más fuerte
            e = iconos[n]
            amp = 1.0 if (final or i == activo) else (0.45 if i < activo else 0.3)
            fase = ((f + 5 * i) % PERIODO) / PERIODO
            spr, dx, dy, extras = mover(sprites[n].copy(), e["customData"]["movimiento"], fase, amp)
            x, y = a_px(e["x"], e["y"])
            if not final and i > activo:
                spr.putalpha(spr.getchannel("A").point(lambda v: v // 2))
            img.paste(spr, (int(x + dx), int(y + dy)), spr)
            lado = sprites[n].width
            dd = ImageDraw.Draw(img)
            for tipo, t in extras:
                if tipo == "linea":
                    yy = y + lado * (0.15 + 0.7 * t)
                    dd.line([x + lado * 0.1, yy, x + lado * 0.9, yy], fill=BRILLO, width=4)
                elif tipo == "gotas":
                    for j in range(3):
                        tt = (t + j / 3) % 1
                        dd.ellipse([x + lado * 0.5 - 5, y + lado * (0.55 + 0.4 * tt) - 5,
                                    x + lado * 0.5 + 5, y + lado * (0.55 + 0.4 * tt) + 5], fill=BRILLO)
        if viaje:
            (px, py) = viaje
            dd = ImageDraw.Draw(img)
            dd.ellipse([px - 15, py - 15, px + 15, py + 15], fill=PUNTO, outline="white", width=4)
        if final:
            _franja(img, 0, len(pasos), sp.get("cierre", "Recorrido completo"))
        else:
            _franja(img, activo + 1, len(pasos), pasos[activo]["rotulo"])
        cuadros.append(img)
        f += 1

    for i, p in enumerate(pasos):
        if i:
            fl = flechas.get((orden[i - 1], p["nodo"]))
            if fl:
                (x0, y0), (dx, dy) = (fl["x"], fl["y"]), fl["points"][-1]
                for v in range(VIAJE):
                    s = (v + 1) / VIAJE
                    s = s * s * (3 - 2 * s)
                    cuadro(i - 1, a_px(x0 + dx * s, y0 + dy * s))
        for _ in range(PAUSA):
            cuadro(i, None)
    for _ in range(FINAL):
        cuadro(len(pasos) - 1, None, final=True)

    SALIDA.mkdir(exist_ok=True)
    base = SALIDA / sp["slug"]
    cuadros[-1].save(f"{base}-final.png")
    paleta = cuadros[len(cuadros) // 2].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    gif = [c.quantize(palette=paleta, dither=Image.Dither.NONE) for c in cuadros]
    gif[0].save(f"{base}.gif", save_all=True, append_images=gif[1:], duration=int(1000 / FPS), loop=0,
                optimize=True, disposal=1)
    import imageio.v2 as imageio

    with imageio.get_writer(f"{base}.mp4", fps=FPS, codec="libx264", quality=8, macro_block_size=8,
                            ffmpeg_params=["-pix_fmt", "yuv420p"]) as w:
        for c in cuadros:
            w.append_data(__import__("numpy").asarray(c))
    for ext in ("gif", "mp4"):
        p = Path(f"{base}.{ext}")
        print(f"ok {p.name} {p.stat().st_size / 1e6:.2f} MB")
    print(f"{len(cuadros)} cuadros, {len(cuadros) / FPS:.1f} s, {cuadros[0].size}")


# ---------------------------------------------------------------- verificar
def _sin_tildes(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(c) != "Mn")


def verificar(spec: str) -> int:
    sp = leer(spec)
    lienzo, _, _, _, els = _escena(sp)
    fondo = FUENTE / f"{sp['slug']}-fondo.png"
    k = Image.open(fondo).width / lienzo["width"] if fondo.exists() else 1.0
    fallos = []
    for e in els:
        if e["type"] != "text":
            continue
        minimo = MIN_FRASE if e.get("customData", {}).get("rol") == "frase" else MIN_TEXTO
        if e["fontSize"] * k < minimo:
            fallos.append(f"letra chica ({e['fontSize'] * k:.0f} px < {minimo}): {e['text'][:50]!r}")
    for n, nd in sp["nodos"].items():
        if not (ICONOS / f"{nd['icono']}.svg").exists():
            fallos.append(f"falta el ícono {nd['icono']} ({n})")
    texto = _sin_tildes(" ".join([sp["titulo"]] + [v for nd in sp["nodos"].values() for v in (nd["frase"], nd["termino"])]
                                 + [p["rotulo"] for p in sp["pasos"]]))
    for c in sp.get("conceptos", []):
        if _sin_tildes(c) not in texto:
            fallos.append(f"concepto de la versión técnica ausente: {c}")
    for p in sp["pasos"]:
        if TAM["franja"] < MIN_FRASE or len(partir(p["rotulo"], TAM["franja"], int(lienzo["width"] * k) - 80)) > 2:
            fallos.append(f"el rótulo no entra en dos líneas: {p['rotulo'][:50]!r}")
    tarjetas = {e["customData"]["nodo"]: e for e in els if e["type"] == "rectangle" and e.get("customData", {}).get("nodo")}
    for e in els:
        n = e.get("customData", {}).get("nodo")
        if e["type"] == "text" and n and e["y"] + e["height"] > tarjetas[n]["y"] + tarjetas[n]["height"] - 8:
            fallos.append(f"el texto se sale de la tarjeta {n}: {e['text'][:40]!r}")
    print("\n".join(fallos) or f"ok {sp['slug']}: letra ≥ {MIN_TEXTO}/{MIN_FRASE} px, conceptos completos, textos dentro")
    return 1 if fallos else 0


if __name__ == "__main__":
    cmd, spec = sys.argv[1], sys.argv[2]
    r = {"crear": crear, "exportar": exportar, "animar": animar, "verificar": verificar}[cmd](spec)
    sys.exit(r if isinstance(r, int) else 0)
