# Modo defensa — tríptico y bíptico

Motor: `scripts/defensa/triptico.py` (`generar` y `verificar`). El **contenido** vive en `triptico.yaml` del vault (modelo:
`assets/defensa/triptico.example.yaml`); el script no tiene datos.

- **Tríptico:** A4 horizontal a doble cara. Exterior: solapa (datos del proyecto, configuración), contratapa (caso de estudio con una foto del
  anexo) y portada (fondo oscuro). Interior: problema y objetivo general con el árbol de problemas, objetivos específicos y el asistente
  con su flujo, y resultados con causa y efecto y economía.
- **Bíptico:** respaldo de dos paneles con lo mismo, más corto.
- **Contenido literal del documento**: problema, objetivos, perfiles, configuración, cifras. Cada número debe existir en el documento:
  `triptico.py verificar triptico.yaml --tg <extracción>.md` sale 1 si falta alguno.
- **Imágenes:** del propio documento (`word/media`, o extraídas de las diapositivas) y a resolución suficiente (más de 150 ppp en el tamaño
  impreso). Una imagen grande hace pesar el .docx: reducirla a unos 2200 px de ancho.
- **Cuando llega evidencia nueva** (por ejemplo, el conteo de errores antes y después): agregar la cifra a la lista de resultados del yaml y
  al documento primero. Nada sale en el tríptico que el documento no tenga.
- **PDF:** exportar desde una copia con `word_a_pdf.py` (un archivo por vez; si Word falla con varios, repetir uno a uno) y revisar cada
  panel: nada debe cortarse al pie de la página. Si un panel se desborda, achicar la imagen o acortar el párrafo.
