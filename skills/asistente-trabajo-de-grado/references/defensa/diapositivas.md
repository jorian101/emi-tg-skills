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
8. **Abrir y guardar con PowerPoint** (COM `Presentations.Open` + `SaveAs` formato 24) y comprobar que abre: python-pptx puede dejar
   ids de forma repetidos que PowerPoint no repara. Las ocultas van al final (`mover`) para que la numeración visible sea seguida.
9. Exportar a PDF **desde una copia** (`word_a_pdf.py`): si PowerPoint tiene el archivo abierto, la conversión exporta lo que está abierto y
   no lo guardado en disco. Mirar cada diapositiva tocada (PDF a PNG) y confirmar que el número de páginas es el esperado (las ocultas no salen).
10. Pedir al autor que **cierre PowerPoint sin guardar** antes de abrir el archivo nuevo: si guarda desde una copia vieja, pisa los cambios.

## Figuras densas (diagramas)

- Una figura con letra chica (BPMN, arquitectura, flujo) va **a pantalla completa**: `diapositivas.py diagrama MAZO N NOMBRE --leyenda "Figura N · … (Anexo X)"`
  quita los demás objetos, recorta el margen blanco, escala al máximo y tapa la línea del encabezado. El texto que desplaza va a las notas.
- No se amplía una imagen más de lo que aguanta: **≥ 110 ppp** en el tamaño proyectado. Si la figura de origen es chica (organigrama, árbol), se
  recorta el margen y se reubica sin sumar diapositivas, y se avisa que su letra seguirá siendo pequeña.
- Los diagramas animados para público no técnico van a la segunda pantalla; no sustituyen a las figuras del documento en el proyector.

## Reglas de contenido

- **Título, objetivo general, objetivos específicos y formulación del problema se copian literales** y se verifican contra el documento.
- **Cada tabla, figura o cifra cita su anexo**, tal como lo dice la «Nota.» de esa tabla o figura en el documento («Elaboración propia
  con base en el Anexo …»); las fotos, entrevistas y registros llevan la letra del anexo en su leyenda. Las leyendas nuevas clonan el estilo de una
  existente y van a 11 pt como mínimo.
- **Guion y notas en tercera persona**, con frases tomadas del documento.

- Solo lo que el documento declara. Lo que no se midió se rotula «siguiente medición» o «de ejemplo»; nunca una cifra inventada.
- Misma terminología que el documento y orden obligatorio del corpus jurídico (ver memoria del proyecto) cuando se nombran las fuentes.
- Causa y efecto: si un revisor pide ver la causa, la diapositiva muestra lo medido (efecto, calidad de lo citado, juicio de expertos) y dice
  cuál es la medición pendiente; no la presenta como hecha.
