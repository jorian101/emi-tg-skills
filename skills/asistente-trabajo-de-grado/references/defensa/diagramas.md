# Modo defensa — diagramas animados para público no técnico

Cada diagrama del documento (pipelines, arquitectura) se presenta en **dos versiones**:

- **Técnica:** la del documento (o la de desarrollo), sin cambios. Es el respaldo para las preguntas del tribunal.
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

## Herramientas

- Motor: Pillow; video con imageio-ffmpeg (trae su ffmpeg, no hace falta instalarlo).
- `diagrama_animado.py` arma `.excalidraw` desde YAML y los exporta con Excalidraw real en Chrome
  headless (necesita red para `esm.sh`). Busca Chrome en `$CHROME`, en el PATH o en el
  `chrome-headless-shell` de `~/.cache/puppeteer`.
- La ruta crítica usa esa misma base (`ruta_critica.py`).
