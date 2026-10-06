# Modo defensa — trampas conocidas

Cada una costó una corrida mala. Revisarlas antes de dar algo por terminado.

| Trampa | Síntoma | Cómo evitarla |
|---|---|---|
| Extracción vieja del documento | Se corrigen entregables contra un texto que el autor ya cambió | Re-extraer con `extraer-doc-tesis` al empezar y comparar la fecha del Word con la de la extracción |
| Anexos renumerados | El pipeline de QR sube contenido cruzado | El manifiesto manda; si el documento cambia letras, cambiar manifiesto y nombres en Drive (`rclone moveto`) |
| Bloques «Buscar» de filas enteras | Ctrl+H no encuentra nada en Word | Celda por celda, con `**Buscar** en «ancla»:` |
| Fragmentos cortos | El verificador marca APLICADA o PENDIENTE por un texto igual en otro lado | Usar ancla o un fragmento con contexto; las ecuaciones se revisan a mano |
| Reloj de Windows desfasado (WSL) | Las fechas de los archivos no sirven para comparar | El check usa hash + margen de 10 min; no confiar solo en la fecha |
| Textos que no caben | Se salen de la caja en diapositivas, tarjetas o rótulos | Renderizar a PNG y mirar; los verificadores fallan si un texto se sale |
| GIF dentro de una diapositiva | La letra se proyecta a ~17 px | Diapositiva propia a pantalla completa |
| Nombres que el documento no declara | El tribunal pregunta por algo que no está en el trabajo | `TERMINOS_TG` y cruce de cifras contra el documento |
| Metáforas | «Huella» se lee como «firma» | Términos del documento, explicados con el dibujo |
| Cuentas de prueba en material para la institución | Las capturas muestran usuarios de prueba | Cuentas reales; si falta la clave, preguntar |
| Word abierto con el archivo | Un vigilante dispara a mitad de un guardado | Esperar unos segundos tras el cambio (los vigilantes ya lo hacen) |
| `--forzar` al publicar | Llega a finales algo viejo | Solo si lo pendiente es conocido y ajeno al contenido |
