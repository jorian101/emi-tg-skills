# Modo defensa — segunda pantalla (TV) con videos en bucle

Motor: `scripts/defensa/tv.py TV.yaml` genera `index.html` (abrir en el navegador, `F` = pantalla completa). Modelo: `assets/defensa/tv.example.yaml`.

- El proyector muestra el mazo; la TV muestra videos **sin sonido y en bucle** que el orador cambia con el teclado (una tecla por video,
  flechas para el siguiente y el anterior, `M` para ver el menú).
- Qué lleva: el producto funcionando en cada caso de uso principal del TG (uno por video, en el orden de la demostración), los diagramas
  animados y la ruta crítica como imagen. Es también el **video de respaldo** que pide el docente ante una caída del servidor.
- Videos con usuarios reales de cada rol, nunca con cuentas de prueba. Grabación: un script de Playwright propio del proyecto (p. ej. `videos-modulos/grabar.py`) y exportación a MP4
  1080p. Los archivos pesados viven fuera de git; copiar la carpeta a un disco y probarla en la computadora de la defensa.
- Si un video no existe, la página lo marca «por grabar» y `tv.py` lo avisa al generar: no deja una pantalla negra.
- Antes de la defensa: probar con la TV conectada, volumen en cero, y dejar la página en pantalla completa con un bucle.
