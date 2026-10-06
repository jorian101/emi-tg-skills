# Modo defensa — flujo general

Guía para que **cualquier agente** prepare y mantenga los materiales de la defensa de un trabajo de
grado (diapositivas, tríptico/bíptico, artículo, manual de usuario, anexos con QR, ruta crítica,
diagramas animados), para cualquier tema y cualquier estudiante. El motor (scripts de esta skill) no
tiene datos: todo sale de la config del proyecto en el vault.

## Principios (no negociables)

1. **El documento del trabajo de grado (Word) es la única fuente de verdad del contenido.** Lo edita el
   autor, a mano. Todo lo demás se deriva de él (y del código, para las capturas de pantalla).
2. **El autor copia a mano solo dos cosas:** las correcciones al documento y el manual de usuario. Para
   eso hay **un único archivo vivo** de correcciones (celda por celda) y **una única versión a copiar** del
   manual. Nunca se crean propuestas sueltas nuevas.
3. **No mostrar nada que el documento no declare** (nombres, cifras, colecciones, herramientas). Lo que no
   es medido se rotula «de ejemplo» o «ilustrativo».
4. **El formato de los entregables no se rompe:** en Word y PowerPoint se cambia solo el texto de los runs
   existentes; las imágenes se reemplazan conservando posición y tamaño; se verifica exportando a PDF y
   mirando cada página o diapositiva tocada.
5. **Todo queda en el vault y enlazado:** hub `wiki/defensa/_moc-defensa.md`, una nota por entregable, la
   nota de estado y una nota por captura (ver `notas_vault.py`).
6. **No se hace push** sin autorización explícita del autor; commits con Conventional Commits.

## Puesta en marcha (una vez por proyecto)

1. Carpeta de defensa en el vault, p. ej. `$VAULT/sources/_propuestas/DEFENSA/`.
2. Copiar `assets/defensa/defensa.example.json` → `DEFENSA/defensa.json` y completar: `fuentes.tg`,
   `fuentes.frontend`, `manual_oficial`, `manual_a_copiar`, `correcciones`, `finales`, `anexos`, `vault`
   y la lista de `entregables` (archivos, de qué dependen, cómo se regeneran, si son finales).
3. Copiar `assets/defensa/correcciones-tg.plantilla.md` → `DEFENSA/CORRECCIONES-TG/correcciones-tg.md`.
4. Generar el hub y las notas: `python3 $S/notas_vault.py --dir DEFENSA` (con `S=$SKILLS/asistente-trabajo-de-grado/scripts/defensa`).
5. Agregar `DEFENSA/.sync-estado.json` al `.gitignore` del vault (es estado local de la máquina).

## Ciclo de trabajo (cada vez que el autor cambia el documento)

```bash
S=$SKILLS/asistente-trabajo-de-grado/scripts/defensa
python3 $S/verificar_sincronizacion.py --dir DEFENSA --nota   # qué quedó viejo y qué falta copiar; escribe estado-defensa.md
python3 $S/verificar_correcciones.py --dir DEFENSA --mover     # pasa a «Aplicadas» lo que el autor ya copió
python3 $S/verificar_correcciones.py --dir DEFENSA --manual    # secciones del manual por copiar al oficial
# … regenerar o editar cada entregable marcado (ver entregables.md) …
python3 $S/verificar_sincronizacion.py --dir DEFENSA --marcar-al-dia <nombre>   # solo si se revisó y no lo afectaba
python3 $S/publicar_finales.py --dir DEFENSA                    # copia los finales; se niega si alguno quedó viejo
```

1. **Re-extraer el documento** con la skill `extraer-doc-tesis` para tener su texto en el vault.
2. **Cruzar cifras:** cada número de cada entregable tiene que aparecer en el documento; lo que falle se
   corrige en el entregable (o, si el error es del documento, se agrega a `correcciones-tg.md`).
3. Corregir los entregables marcados, verificar el formato (PDF a PNG, revisión visual) y publicar.
4. Commit por bloque y nota de estado actualizada.

## Guías por tema

| Tema | Guía |
|---|---|
| Correcciones, manual, tríptico, artículo, diapositivas, anexos QR, ruta crítica, publicación | [entregables.md](entregables.md) |
| Diagramas animados para público no técnico (dos versiones) | [diagramas.md](diagramas.md) |
| Capturas de la interfaz: pantallas, modales y acciones, por rol | [capturas.md](capturas.md) |
| Trampas conocidas y cómo evitarlas | [trampas.md](trampas.md) |

## Scripts (`scripts/defensa/`)

| Script | Qué hace |
|---|---|
| `config.py` | Lee `defensa.json` desde `--dir`, `$DEFENSA_DIR` o el directorio actual |
| `verificar_sincronizacion.py` | Hash + fecha de las fuentes contra cada entregable; `--nota` escribe el estado en el vault |
| `verificar_correcciones.py` | Marca cada corrección APLICADA / PENDIENTE / REVISAR leyendo el Word; `--manual` compara el manual |
| `publicar_finales.py` | Copia los finales a `finales`, solo lo que cambió |
| `notas_vault.py` | Hub, notas por entregable y nota de estado en el vault |
| `escenas.py` | Motor de animaciones por escenas (versión pública de los diagramas) |
| `diagrama_animado.py`, `ruta_critica.py` | `.excalidraw` desde YAML y export con Excalidraw real; ruta crítica por carriles |
| `diagrama_flujo.py` | Diagrama de flujo desde YAML (pasos numerados, decisiones, colores por fase): la ruta crítica dentro del sistema |
| `capturas.py` | Capturas declarativas por rol con marcadores medidos y bloqueo de botones que escriben |
| `anexos_pipeline.py` (+ `anexos_dividir.py`, `drive_subir.py`, `anexos_qr.py`, `watch_anexos.py`) | Anexos con QR: Word → PDF por anexo → Drive → QR |
| `word_a_pdf.py`, `watch_a_pdf.py` | PDF desde Word/PowerPoint (Windows desde WSL, o LibreOffice) y vigilante |

Tests: `python3 $S/tests/test_verificar_sincronizacion.py`, `python3 $S/tests/test_verificar_correcciones.py`,
`uv run --with playwright --with pyyaml python $S/tests/test_capturas.py`.
