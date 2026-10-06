# Modo defensa — cómo se trabaja cada entregable

## Correcciones al documento (`correcciones-tg.md`)

- **Un solo archivo vivo**, con una sección `### C-NN` por corrección (plantilla:
  `assets/defensa/correcciones-tg.plantilla.md`). Se regenera su `.docx` con
  `pandoc correcciones-tg.md -o correcciones-tg.docx` para que el autor lo lea en Word.
- **Celda por celda:** el autor aplica a mano en Word, y en una tabla de Word cada celda es independiente.
  Por eso nunca se propone una fila entera como texto a buscar.
- `**Buscar** en «ancla»:` hace que el verificador busque solo en los 400 caracteres que siguen al ancla
  (el rótulo de la fila, por ejemplo), para no confundir celdas cortas iguales.
- **Insertar:** el bloque Buscar va vacío. **Borrar:** el bloque Reemplazar va vacío.
- Las ecuaciones de Word (OMML) no se encuentran con Ctrl+H: se indica corregirlas a mano.
- Cuando el autor reescribe algo a su manera, su versión manda. La corrección se ajusta a lo que él
  escribió, o se retira si quedó superada, y se le avisan los problemas que queden (gramática, ambigüedad).
- **Conclusiones y recomendaciones:** cada conclusión repite el verbo y el complemento de su objetivo y
  **termina con la misma cláusula «para…» del objetivo** (objetivos específicos y general). Cada
  recomendación: «Se recomienda a [quién] [verbo]…, para [finalidad]».
- **Revisión de datos:** cada cifra se cruza con su tabla o anexo; se explica qué es medido y qué es
  proyección, el tamaño de las muestras y el intervalo de confianza, para que no se malinterprete.

## Manual de usuario

- Se genera completo en `manual_a_copiar` (texto fuente + capturas + plantilla con el formato del autor);
  el autor lo copia al oficial. `verificar_correcciones.py --manual` lista las secciones que difieren.
- Si cambió el frontend: recapturar (ver [capturas.md](capturas.md)) y ajustar el texto a los nombres
  nuevos de pantallas y menús. El manual no promete funciones que el documento no declara.

## Tríptico y bíptico

- **Contenido literal del documento:** problema, objetivos, perfiles, configuración, resultados y cifras
  económicas, copiados tal cual. Verificar con un script que cada cifra exista en el documento.
- Diseño institucional (paleta, logo de la institución tomado del propio documento, una foto del caso de
  estudio tomada de un anexo). Exportar a PDF y revisar cada página.

## Artículo

- Si hay un «oficial» formateado por el autor (por ejemplo a dos columnas), se cambia **solo el texto de
  los runs** de los párrafos afectados; nunca estilos, columnas ni figuras.
- Exportar a PDF antes y después: mismo número de páginas y mismas secciones. Si un párrafo se corre de
  página, avisarlo.

## Diapositivas

- `python-pptx`: cambiar el texto del run (un párrafo suele tener un solo run); no crear formas nuevas
  salvo que se pida.
- Textos más cortos que el documento si no caben, pero con todos sus datos y la forma «verbo… para…».
- **Reemplazar una imagen:** agregar la nueva con el mismo ancho y posición (alto según su proporción,
  centrada en la caja vieja), insertarla en el mismo orden de capas y borrar la anterior.
- **Diagramas animados:** van en una diapositiva propia a pantalla completa (si no, la letra se proyecta
  demasiado chica). Al insertar diapositivas, renumerar el número escrito en cada una.
- Verificar: comparar el texto de todas las diapositivas antes y después (solo cambian las tocadas y los
  números), exportar a PDF y mirar las tocadas.

## Anexos con QR

- `anexos-qr.docx` lo edita el autor; el manifiesto (`manifiesto-anexos.json`) declara letra, título y
  nombre del archivo en Drive. `anexos_pipeline.py --dir DEFENSA` exporta el PDF, lo divide por portada
  («ANEXO X»), sube a Drive con el mismo nombre (mismo link, mismo QR) y arma `QR-ANEXOS.docx`.
- **Si el documento renumera los anexos**, hay que cambiar letra y título en el manifiesto y renombrar
  los archivos en Drive con `rclone moveto` (conserva el ID, así el QR impreso sigue sirviendo). El
  divisor falla con error si una portada del PDF no está en el manifiesto o al revés.

## Ruta crítica

- `ruta-critica.yaml` (modelo: `assets/defensa/ruta-critica.example.yaml`): carriles por rol y una
  columna por tarea en orden, con su tiempo observado. Debajo de cada tarea, **cómo asiste el sistema**,
  con los requerimientos del documento (RF-xx).
- Solo se nombra lo que el documento declara: si el sistema no genera un documento, se dice «sin
  plantilla propia» y se describe el apoyo real.
- `ruta_critica.py crear|verificar|exportar <spec>`: `.excalidraw` editable, PNG a escala de cartulina y
  PDF. `verificar` falla si un texto se sale de su caja o queda chico.

## Publicación

`publicar_finales.py --dir DEFENSA` copia a `finales` los entregables con `"final": true`. Se niega si
alguno está desactualizado. `--forzar` solo cuando lo pendiente sea conocido y ajeno al contenido (por
ejemplo, capturas que esperan credenciales).
