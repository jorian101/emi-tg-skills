# Modo defensa — diagramas animados para público no técnico

Cada diagrama del documento (pipelines, arquitectura) se presenta en **dos versiones**:

- **Técnica:** la figura del documento, sin cambios. Es el respaldo para las preguntas del tribunal.
- **Pública:** una animación **por escenas** que explica el mismo flujo a alguien que no es técnico, **sin
  perder conceptos**.

## Qué aprendimos (y por qué así)

- **Íconos sueltos que rebotan no explican nada.** Cada paso es una **escena** con contenido real del
  proyecto. Por ejemplo, un artículo real del corpus que se lee, se arma en árbol, se corta en segmentos,
  se guarda y se vectoriza; o una consulta real que se clasifica, se busca, se reordena y se responde.
- **Los términos técnicos se mantienen**, tal cual los usa el documento, y el dibujo los explica. Quitar
  conceptos para «simplificar» es contraproducente.
- **Nada de metáforas que suenen a otra cosa** (p. ej. «huella», que se confunde con «firma»).
- **Nada que el documento no declare.** `TERMINOS_TG` lista cada término técnico que se muestra, y
  `escenas.py --tg <extracción>` no genera si alguno no está en el documento. Los nombres que solo están
  dentro de una figura del documento van aparte, en `TERMINOS_FIGURA`, citando la figura.
- **Letra legible:** 28 px como mínimo en 1920 px (el motor lo exige) y rótulos de hasta dos líneas.
- **Valores no medidos** (los números de un vector, el orden de unos candidatos, una respuesta) se
  rotulan «ilustrativos» o «de ejemplo».
- **Registro formal** en los ejemplos que aparecen en pantalla (consultas, mensajes): tercera persona o
  «usted», nunca voseo ni tuteo.
- **El producto propone y la persona decide:** una escena que muestra una validación o una decisión dice
  qué hace el producto (responde, cita, señala) y quién decide; no le atribuye la decisión al producto.
- **Ningún texto fuera del escenario ni pisado:** `escenas.py` lo comprueba en el cuadro final de cada paso
  y no exporta si falla (además de la revisión por visión del paso 4).
- **Un ejemplo por cada variante que el TG declara** (p. ej. cada tipo de consulta o de documento): mostrar
  una sola deja afuera lo que el tribunal va a preguntar.

## Cómo se arma

1. Leer en el documento la sección del flujo (fases y tablas) y sacar de los datos reales del proyecto el
   ejemplo que se va a mostrar (un artículo, una consulta, fragmentos reales). Ver en el código los
   valores exactos (tipos de segmento, padres) si el documento los nombra.
2. Copiar `assets/defensa/escenas_ejemplo.py` a `DEFENSA/diagramas/escenas_0N_<flujo>.py`. Definir
   `TITULO`, `PASOS = [(nombre del documento, rótulo llano, función de escena)]`, `CIERRE` y `TERMINOS_TG`.
   Las primitivas son `c.texto`, `c.caja`, `c.flecha`, `c.etiqueta` y `tramo(t, a, b)` para animar por tramos.
3. Correr: `escenas.py escenas_0N_<flujo> --modulos DEFENSA/diagramas --tg <extracción>.md`. Salen MP4
   (para PowerPoint), GIF, una imagen fija por paso y la final.
4. Revisar por visión las imágenes de cada paso (textos que se pisan, que se salen, que quedan chicos).
5. Mostrar el primer diagrama al autor **antes** de hacer los demás con el mismo estilo.
6. Ponerlos en las diapositivas: una propia a pantalla completa por diagrama, antes de su versión
   técnica (ver [entregables.md](entregables.md)).

## Herramientas (qué se hace con qué)

| Diagrama | Herramienta | Salida |
| --- | --- | --- |
| Diagramas animados para público no técnico | `escenas.py` (Pillow + imageio-ffmpeg, trae su ffmpeg) | MP4, GIF, PNG por paso |
| **Ruta crítica (el único en Excalidraw)** | `diagrama_flujo.py crear\|verificar\|exportar` desde YAML; `--vertical` para la solapa del tríptico | `.excalidraw`, PNG, PDF |
| Figuras del documento (UML, DER, etc.) | las de `generar-entregables-tesis` (Excalidraw prohibido ahí) | — |

- La exportación de Excalidraw usa Excalidraw real en Chrome headless (`diagrama_animado.py`; necesita red
  para `esm.sh`). Busca Chrome en `$CHROME`, en el PATH o en el `chrome-headless-shell` de `~/.cache/puppeteer`.
- `ruta_critica.py` (carriles por rol) es el motor anterior; se conserva para quien ya lo usa, pero la ruta
  crítica nueva va con `diagrama_flujo.py` (ver [flujo.md](flujo.md)).
