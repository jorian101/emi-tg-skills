"""Ejemplo de animación por escenas (versión pública de un diagrama), para copiar y adaptar.

Copiar a <carpeta de defensa>/diagramas/escenas_01_flujo.py y correr:
  uv run --with pillow --with imageio --with imageio-ffmpeg --with numpy \\
    python $SKILLS/asistente-trabajo-de-grado/scripts/defensa/escenas.py escenas_01_flujo \\
    --modulos diagramas --tg $VAULT/sources/<extracción del documento>.md

Reglas que se aprendieron haciendo esto (ver references/defensa/diagramas.md):
  - cada paso es una ESCENA con contenido REAL del proyecto (un documento real que se procesa), no un ícono;
  - los nombres técnicos van tal cual el documento y se listan en TERMINOS_TG (render() los verifica);
  - nada de metáforas que suenen a otra cosa; lo que no es medido se rotula «ilustrativo» o «de ejemplo»;
  - letra de 28 px como mínimo (el motor lo exige) y rótulos de hasta dos líneas.
"""

from escenas import AZUL, AZUL_OSC, ESCENA, GRIS, NARANJA, VERDE, tramo

SLUG = "01-flujo-publico"
TITULO = "Cómo procesa el sistema un documento"
CIERRE = "Así queda el documento: dividido en partes, cada una con su lugar, listo para buscar"
X0, Y0, X1, Y1 = ESCENA
PARTES = ["Primera parte del documento de ejemplo.", "Segunda parte del documento de ejemplo.",
          "Tercera parte del documento de ejemplo."]


def s1_llega(c, t):
    a = tramo(t, 0.05, 0.5)
    x = X0 + 60 + (1 - a) * -400
    c.caja(x, Y0 + 80, x + 700, Y0 + 520, (255, 255, 255), AZUL, 3, 12, alfa=int(255 * a))
    c.texto((x + 30, Y0 + 100), "Documento de ejemplo", 32, AZUL_OSC, True, alfa=int(255 * a))
    for k, p in enumerate(PARTES):
        c.texto((x + 30, Y0 + 170 + k * 70), p, 28, GRIS, alfa=int(255 * a))


def s2_divide(c, t):
    ancho = (X1 - X0 - 120) / 3
    for k, p in enumerate(PARTES):
        a = tramo(t, 0.1 + 0.2 * k, 0.4 + 0.2 * k)
        x = X0 + 30 + k * (ancho + 30)
        y = Y0 + 80 + 100 * a
        c.caja(x, y, x + ancho, y + 260, (255, 255, 255), NARANJA, 3, 12, alfa=int(255 * a))
        c.etiqueta(x + 14, y + 14, f"parte {k + 1}", NARANJA, 28, alfa=int(255 * a))
        c.texto((x + 20, y + 70), p, 28, AZUL_OSC, ancho=ancho - 40, alfa=int(255 * a))


def s3_guarda(c, t):
    c.texto((X0 + 30, Y0 + 30), "Base de datos", 32, VERDE, True)
    for k, p in enumerate(PARTES):
        a = tramo(t, 0.1 + 0.25 * k, 0.4 + 0.25 * k)
        y = Y0 + 100 + k * 120
        c.caja(X0 + 30, y, X1 - 30, y + 100, (240, 250, 242), VERDE, 2, 10, alfa=int(255 * a))
        c.texto((X0 + 50, y + 30), p, 30, AZUL_OSC, alfa=int(255 * a))


PASOS = [
    ("Llegada", "Llega el documento al sistema", s1_llega),
    ("División", "El documento se divide en partes que se pueden buscar", s2_divide),
    ("Guardado", "Cada parte se guarda en la base de datos con su lugar en el documento", s3_guarda),
]

TERMINOS_TG: list[str] = []  # completar con los términos técnicos que se muestran (tal cual el documento)
