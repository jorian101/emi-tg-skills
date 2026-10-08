# Modo defensa — tríptico y bíptico

Motor: `scripts/defensa/triptico.py` (`generar` y `verificar`). El **contenido** vive en `triptico.yaml` del vault (modelo:
`assets/defensa/triptico.example.yaml`); el script no tiene datos.

- **Tríptico:** hoja **carta** horizontal a doble cara (`hoja: a4` si la institución lo pide). Exterior: **solapa** (datos del proyecto
  y de la EMI: carrera, área y línea de investigación, más la **ruta crítica vertical**), **contratapa** (caso de estudio: foto del anexo,
  **misión y visión** de la institución citadas, y la **función de la unidad** donde se aplica el trabajo) y **portada** (fondo oscuro).
  Interior: problema (causa → efecto) y objetivo general con el árbol de problemas, objetivos específicos y el producto, y resultados con
  su ámbito y la recomendación.
- **Una sola tipografía** (`fuente:`, Calibri por defecto) en todo el tríptico, la misma que la ruta crítica. Viñetas `li` con sangría
  francesa. **Sin espacios vacíos**: si un panel queda corto, se agrega contenido literal del TG (misión, visión, función, recomendación),
  no relleno; si se desborda, se achica la imagen o se acorta el párrafo.
- **Ruta crítica en la solapa:** la versión horizontal no se lee en un panel de ~8,8 cm. Se exporta la vertical desde el **mismo** YAML
  (`diagrama_flujo.py exportar ruta-critica.yaml --vertical`, con `vertical: [fila, col]` por nodo para una sola columna) y se inserta
  con `[img, ruta, 7.3]`. Nunca se redibuja a mano: dos fuentes se desincronizan.
- **Sin texto interpretativo:** nada de «esto demuestra», «revoluciona»; solo lo que el TG afirma.
- **Bíptico oficial (marco práctico al 100 %):** es otro entregable, no un respaldo del tríptico. Su formato lo da el docente que lo exige
  (`formatos/<código>/formato.yaml`, clave `biptico`, con su plantilla `.docx`): hoja carta apaisada, 2 páginas y 4 paneles. Orden:
  **título → formulación del problema → objetivos (general y específicos) → límites → desarrollo del OE1 (análisis, aspectos más relevantes) →
  desarrollo del OE2 (diseño) → desarrollo del OE3 (desarrollo)**, y la portada (comando general, escuela, unidad académica, «Marco práctico»,
  logo, título, estudiante, año). Se edita la plantilla oficial, sin cambiar sus encabezados ni su orden; `verificar_formato.py --tipo biptico`
  lo comprueba.
- **Ejemplo de tríptico del docente:** hoja carta apaisada, exterior e interior de tres columnas (tablas de 1 × 3), márgenes ≈ 1,0 / 0,8 / 0,6 / 0,6 cm, títulos de panel
  13 pt, cuerpo 8,5 pt, pies de figura 7,5 pt y viñeta «▪»; interior en el orden **el problema → la solución → resultados y aporte**, y
  exterior con cifras, datos del proyecto, tecnologías y la portada. Es un ejemplo (no norma): `verificar_formato.py --tipo triptico` informa
  los desvíos como avisos.
- **Contenido literal del documento**: problema, objetivos, perfiles, configuración, cifras. Cada número debe existir en el documento:
  `triptico.py verificar triptico.yaml --tg <extracción>.md` sale 1 si falta alguno.
- **Imágenes:** del propio documento (`word/media`, o extraídas de las diapositivas) y a resolución suficiente (más de 150 ppp en el tamaño
  impreso). Una imagen grande hace pesar el .docx: reducirla a unos 2200 px de ancho.
- **Cuando llega evidencia nueva** (por ejemplo, el conteo de errores antes y después): agregar la cifra a la lista de resultados del yaml y
  al documento primero. Nada sale en el tríptico que el documento no tenga.
- **PDF:** exportar desde una copia con `word_a_pdf.py` (un archivo por vez; si Word falla con varios, repetir uno a uno) y revisar cada
  panel: nada debe cortarse al pie de la página. Si un panel se desborda, achicar la imagen o acortar el párrafo.
