# Modo defensa — diapositivas de la defensa pública

Para que **cualquier modelo** actualice el mazo sin contexto previo. Motor: `scripts/defensa/diapositivas.py`
(`uv run --with python-pptx --with pillow --with pyyaml python diapositivas.py <comando> MAZO.pptx …`).

## Estructura que espera el docente de trabajo de grado

1. Portada → abstract (resumen ejecutivo) → **documentación administrativa** (la primera imagen es la carta de solicitud al caso de estudio)
   → introducción → objetivo general (completo) → objetivos específicos (una sola diapositiva) → metodología → marco práctico → trabajo de campo
   → costos → demostración → conclusiones → recomendaciones → gracias.
2. **No se lee**: texto solo en título, objetivos y formulación del problema; todo lo demás son imágenes, esquemas y diagramas.
3. En las diapositivas de conclusiones va el **rango de páginas exacto** de la evidencia de cada objetivo («OE3: págs. 127 a 172»). Salen del
   índice del documento; si el autor lo actualiza, se revisan.
4. El detalle que no cabe en el tiempo **no se borra**: se **oculta** (`ocultar`) y queda como respaldo para las preguntas.
5. Las animaciones y los videos van a la segunda pantalla (ver `tv-videos.md`), no al mazo.

## Tiempo: 30 minutos

20 de exposición + 8 de demostración + 2 de preguntas. Se calcula un minuto por diapositiva visible como máximo y se reparte en el guion
(`guion.md`). Si el mazo tiene más de 22 diapositivas visibles, se ocultan las de detalle técnico antes de recortar texto.

## Pasos para actualizar el mazo (checklist)

1. Re-extraer el documento (`extraer-doc-tesis`) y correr `verificar_sincronizacion.py --nota`.
2. `diapositivas.py texto MAZO --md /tmp/mazo.md` y leerlo entero: qué dice cada diapositiva hoy.
3. `diapositivas.py cifras MAZO --tg <extracción>.md`: cada número debe estar en el documento. Corregir en el mazo lo que falle; si el
   error es del documento, va a `correcciones-tg.md`.
4. Cambiar texto **solo en los runs** (python-pptx `run.text`), sin tocar estilos; las tarjetas de cifras se clonan de una existente
   (`tarjetas`). Imágenes: `imagen` conserva posición y proporción; las del documento salen de `word/media` del .docx a su resolución original.
5. Diapositiva nueva: `tarjetas --despues N --spec s.yaml` o clonar una existente; después renumerar los números escritos en cada una
   (el mazo del proyecto lo hace en su script).
6. Guion en las notas del orador: `notas MAZO guion.yaml`.
7. `diapositivas.py verificar MAZO`: imágenes con menos de 150 ppp o sin descripción, cajas vacías.
8. Exportar a PDF **desde una copia** (`word_a_pdf.py`): si PowerPoint tiene el archivo abierto, la conversión exporta lo que está abierto y
   no lo guardado en disco. Mirar cada diapositiva tocada (PDF a PNG) y confirmar que el número de páginas es el esperado (las ocultas no salen).
9. Pedir al autor que **cierre PowerPoint sin guardar** antes de abrir el archivo nuevo: si guarda desde una copia vieja, pisa los cambios.

## Reglas de contenido

- Solo lo que el documento declara. Lo que no se midió se rotula «siguiente medición» o «de ejemplo»; nunca una cifra inventada.
- Misma terminología que el documento y orden obligatorio del corpus jurídico (ver memoria del proyecto) cuando se nombran las fuentes.
- Causa y efecto: si un revisor pide ver la causa, la diapositiva muestra lo medido (efecto, calidad de lo citado, juicio de expertos) y dice
  cuál es la medición pendiente; no la presenta como hecha.
