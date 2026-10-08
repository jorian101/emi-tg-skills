#!/usr/bin/env python3
"""Motor de animaciones por escenas para público no técnico (versión pública de los diagramas).

En vez de íconos sueltos, cada paso del flujo es una ESCENA dibujada con contenido real (un artículo
del corpus que se lee, se arma en árbol, se corta, se guarda y se vectoriza). Arriba va la barra del
recorrido con los nombres del TG; abajo, la franja que explica el paso en lenguaje llano.

Una animación = un módulo con TITULO, PASOS [(nombre_tg, rotulo, funcion_escena)], CIERRE y
TERMINOS_TG (términos técnicos que se muestran y que tienen que existir en el TG).
Uso: uv run --with pillow --with imageio --with imageio-ffmpeg --with numpy python escenas.py <modulo> \
       [--modulos CARPETA] [--tg TG.md]
     El módulo (<modulo>.py) vive en la carpeta del proyecto (--modulos, por defecto la actual); la
     salida va a <CARPETA>/salida/. Ejemplo comentado: assets/defensa/escenas_ejemplo.py.
"""

from __future__ import annotations

import importlib
import math
import sys
import unicodedata
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI / "salida"
W, H = 1920, 1080
BARRA = (0, 96, W, 206)  # recorrido
ESCENA = (40, 226, W - 40, 920)  # escenario
FRANJA_Y = 940
FPS, CUADROS_PASO, CUADROS_FINAL = 14, 56, 28
AZUL, AZUL_OSC, GRIS, GRIS_CLARO = (10, 58, 130), (3, 33, 84), (73, 80, 87), (233, 236, 239)
NARANJA, ROJO, VERDE, VIOLETA, AMARILLO = (245, 159, 0), (215, 25, 32), (47, 158, 68), (103, 65, 217), (242, 201, 30)
CELESTE = (231, 240, 251)
_F = "/usr/share/fonts/truetype/dejavu/DejaVuSans{}.ttf"
MIN_PX = 28


def fuente(tam: int, negrita=False, mono=False) -> ImageFont.FreeTypeFont:
    if mono:
        return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", tam)
    return ImageFont.truetype(_F.format("-Bold" if negrita else ""), tam)


def partir(texto: str, f: ImageFont.FreeTypeFont, ancho: float) -> list[str]:
    lineas, actual = [], ""
    for p in texto.split():
        prueba = f"{actual} {p}".strip()
        if f.getlength(prueba) <= ancho or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = p
    return lineas + [actual]


# ---------------------------------------------------------------- primitivas
class Lienzo:
    """Envuelve ImageDraw con texto que valida la letra mínima (nada por debajo de 28 px)."""

    usados: set[int] = set()

    def __init__(self, img: Image.Image):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.cajas_texto: list[tuple] | None = None  # se llena solo mientras se dibuja la escena (chequeo geométrico)

    def texto(self, xy, txt, tam=32, color=AZUL_OSC, negrita=False, ancho=None, centro=False, mono=False,
              interlinea=1.25, alfa=255) -> float:
        if tam < MIN_PX:
            raise ValueError(f"letra de {tam} px < {MIN_PX}: {txt[:40]!r}")
        Lienzo.usados.add(tam)
        f = fuente(tam, negrita, mono)
        lineas = partir(txt, f, ancho) if ancho else txt.split("\n")
        x, y = xy
        for i, linea in enumerate(lineas):
            lx = x + (ancho - f.getlength(linea)) / 2 if (centro and ancho) else x
            self.d.text((lx, y + i * tam * interlinea), linea, font=f, fill=(*color[:3], alfa))
            if self.cajas_texto is not None and alfa > 0 and linea.strip():
                self.cajas_texto.append((*self.d.textbbox((lx, y + i * tam * interlinea), linea, font=f), linea))
        return y + len(lineas) * tam * interlinea

    def caja(self, x0, y0, x1, y1, relleno=CELESTE, borde=AZUL, ancho=3, radio=16, alfa=255):
        self.d.rounded_rectangle([x0, y0, x1, y1], radio, fill=(*relleno[:3], alfa), outline=(*borde[:3], alfa),
                                 width=ancho)

    def flecha(self, a, b, color=AZUL, ancho=5, t=1.0):
        bx, by = a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t
        self.d.line([a, (bx, by)], fill=color, width=ancho)
        if t > 0.95:
            ang = math.atan2(by - a[1], bx - a[0])
            p = [(bx, by), (bx - 18 * math.cos(ang - 0.45), by - 18 * math.sin(ang - 0.45)),
                 (bx - 18 * math.cos(ang + 0.45), by - 18 * math.sin(ang + 0.45))]
            self.d.polygon(p, fill=color)

    def etiqueta(self, x, y, txt, color, tam=28, alfa=255) -> float:
        f = fuente(tam, True)
        w = f.getlength(txt) + 24
        self.d.rounded_rectangle([x, y, x + w, y + tam + 16], 10, fill=(*color[:3], alfa))
        self.d.text((x + 12, y + 7), txt, font=f, fill=(255, 255, 255, alfa))
        return x + w


def ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def tramo(t: float, a: float, b: float) -> float:
    """Avance 0→1 de una sub-animación que ocurre entre las fracciones a y b del paso."""
    return ease((t - a) / (b - a)) if b > a else float(t >= a)


# ---------------------------------------------------------------- cuadro completo
def cuadro(mod, i: int, t: float, final=False) -> Image.Image:
    img = Image.new("RGB", (W, H), "white")
    c = Lienzo(img)
    c.texto((0, 24), mod.TITULO, 44, AZUL_OSC, True, ancho=W, centro=True)
    n = len(mod.PASOS)
    ancho = (BARRA[2] - 80 - (n - 1) * 14) / n
    for j, (nombre, _, _) in enumerate(mod.PASOS):  # barra del recorrido con los nombres del TG
        x0 = 40 + j * (ancho + 14)
        hecho, activo = final or j < i, (not final and j == i)
        relleno = AZUL if activo else (CELESTE if hecho else GRIS_CLARO)
        c.caja(x0, BARRA[1] + 10, x0 + ancho, BARRA[3] - 10, relleno, AZUL if (activo or hecho) else (173, 181, 189), 3, 14)
        c.texto((x0 + 8, BARRA[1] + 22), f"{j + 1}. {nombre}", 28, (255, 255, 255) if activo else AZUL_OSC, activo,
                ancho=ancho - 16, centro=True, interlinea=1.15)
    if not final:  # punto rojo que avanza dentro del paso activo
        x0 = 40 + i * (ancho + 14)
        px = x0 + 14 + (ancho - 28) * ease(min(1, t * 1.6))
        c.d.ellipse([px - 11, BARRA[3] - 21, px + 11, BARRA[3] + 1], fill=ROJO, outline="white", width=3)
    c.caja(*ESCENA, (251, 252, 253), (206, 212, 218), 2, 20)
    c.cajas_texto = []
    if final:
        mod.PASOS[-1][2](c, 1.0)
        rotulo, num = mod.CIERRE, "Recorrido completo"
    else:
        mod.PASOS[i][2](c, t)
        rotulo, num = mod.PASOS[i][1], f"Paso {i + 1} de {n}"
    img.info["textos"], c.cajas_texto = c.cajas_texto, None
    c.d.rectangle([0, FRANJA_Y, W, H], fill=AZUL_OSC)
    c.texto((40, FRANJA_Y + 12), num, 30, AMARILLO, True)
    c.texto((40, FRANJA_Y + 54), rotulo, 38, (255, 255, 255), ancho=W - 80, interlinea=1.2)
    return img


def problemas_geometricos(img: Image.Image) -> list[str]:
    """Textos de la escena que se salen del escenario o se pisan entre sí (en el cuadro final de cada paso)."""
    x0, y0, x1, y1 = ESCENA
    cajas, out = img.info.get("textos", []), []
    for a in cajas:
        if a[0] < x0 or a[1] < y0 or a[2] > x1 or a[3] > y1:
            out.append(f"fuera del escenario: {a[4][:40]!r}")
    for k, a in enumerate(cajas):
        for b in cajas[k + 1:]:
            if min(a[2], b[2]) - max(a[0], b[0]) > 2 and min(a[3], b[3]) - max(a[1], b[1]) > 2:
                out.append(f"se pisan: {a[4][:30]!r} y {b[4][:30]!r}")
    return out


def _sin_tildes(s: str) -> str:
    return "".join(ch for ch in unicodedata.normalize("NFD", s.lower()) if unicodedata.category(ch) != "Mn")


def verificar_terminos(mod, tg: Path) -> list[str]:
    texto = _sin_tildes(tg.read_text(encoding="utf-8"))
    return [t for t in mod.TERMINOS_TG if _sin_tildes(t) not in texto]


def render(nombre: str, tg: Path | None, modulos: Path | None = None) -> None:
    global SALIDA
    modulos = (modulos or Path.cwd()).resolve()
    SALIDA = modulos / "salida"
    sys.path.insert(0, str(AQUI))  # para que el módulo importe este motor con `from escenas import ...`
    sys.path.insert(0, str(modulos))
    mod = importlib.import_module(nombre)
    if tg:
        faltan = verificar_terminos(mod, tg)
        if faltan:
            sys.exit(f"Términos que el TG no tiene (no se pueden mostrar): {faltan}")
        print(f"ok términos: los {len(mod.TERMINOS_TG)} aparecen en el TG")
    largos = [r for _, r, _ in mod.PASOS + [("", mod.CIERRE, None)] if len(partir(r, fuente(38), W - 80)) > 2]
    if largos:
        sys.exit(f"Rótulos que no entran en dos líneas: {largos}")
    cuadros = []
    for i in range(len(mod.PASOS)):
        for k in range(CUADROS_PASO):
            cuadros.append(cuadro(mod, i, k / (CUADROS_PASO - 1)))
    for _ in range(CUADROS_FINAL):
        cuadros.append(cuadro(mod, 0, 1.0, final=True))
    geom = [f"paso {j + 1}: {m}" for j in range(len(mod.PASOS))
            for m in problemas_geometricos(cuadros[j * CUADROS_PASO + CUADROS_PASO - 1])]
    if geom:
        sys.exit("Chequeo geométrico (corregir posiciones antes de exportar):\n" + "\n".join(geom))
    print("ok geometría: ningún texto fuera del escenario ni pisado")
    SALIDA.mkdir(exist_ok=True)
    base = SALIDA / mod.SLUG
    cuadros[-1].save(f"{base}-final.png")
    for j in range(len(mod.PASOS)):  # una imagen fija por paso, para el Word o la diapositiva sin animación
        cuadros[j * CUADROS_PASO + CUADROS_PASO - 1].save(f"{base}-paso-{j + 1}.png")
    import imageio.v2 as imageio
    import numpy as np

    with imageio.get_writer(f"{base}.mp4", fps=FPS, codec="libx264", quality=8, macro_block_size=8,
                            ffmpeg_log_level="error") as w:
        for c in cuadros:
            w.append_data(np.asarray(c))
    paleta = cuadros[len(cuadros) // 3].quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    gif = [c.quantize(palette=paleta, dither=Image.Dither.NONE) for c in cuadros]
    gif[0].save(f"{base}.gif", save_all=True, append_images=gif[1:], duration=int(1000 / FPS), loop=0, optimize=True)
    for ext in ("mp4", "gif"):
        p = Path(f"{base}.{ext}")
        print(f"ok {p.name} {p.stat().st_size / 1e6:.1f} MB")
    print(f"{len(cuadros)} cuadros, {len(cuadros) / FPS:.0f} s; letra mínima usada {min(Lienzo.usados)} px")


if __name__ == "__main__":
    args = sys.argv[1:]
    tg = Path(args[args.index("--tg") + 1]) if "--tg" in args else None
    modulos = Path(args[args.index("--modulos") + 1]) if "--modulos" in args else None
    render(args[0], tg, modulos)
