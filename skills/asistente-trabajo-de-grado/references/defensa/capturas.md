# Modo defensa — capturas de la interfaz (pantallas, modales y acciones)

`capturas.py` saca las capturas del manual, las diapositivas y el artículo por rol, a partir de un YAML
declarativo (modelo comentado: `assets/defensa/capturas.example.yaml`). Queda todo en el vault: las PNG,
`marcadores.json` y una nota por captura enlazada al hub.

```bash
DEMO_USUARIO_OPERADOR=… DEMO_CLAVE=… \
  uv run --with playwright --with pyyaml python $S/capturas.py DEFENSA/capturas.yaml --dir DEFENSA [--solo 60-op-editar] [--ensayo]
```

## Qué se declara

- **Por rol:** la cuenta (`usuario_env` / `clave_env`: los valores se leen del entorno y **nunca** se
  escriben en el archivo).
- **`pantallas`:** id, ruta, título y sección del manual (van a la nota del vault) y un recorte opcional.
- **`operaciones`:** pasos que dejan un **modal abierto** o la **pantalla tras una acción**: `clic`,
  `llenar`, `elegir`, `tecla` y `esperar` (ms, `dialogo`, `{respuesta: /api/…}` o un localizador).
- **`marcadores`:** localizadores, en el orden de los números que se dibujan sobre la figura. El punto se
  mide solo (a la izquierda del elemento, a media altura) y queda en `marcadores.json`, que el generador
  del manual tiene que leer directo (nunca copiar coordenadas a mano).
- **Localizadores:** `{rol, nombre[, exacto]}`, `{css}`, `{texto}`, `{titulo_empieza}`, más
  `{dentro: dialogo}` (el último diálogo), `{n: 2}` o `{ultimo: true}`. Preferir rol + nombre accesible,
  que sobrevive a cambios de estilos.

## Seguridad

- `seguridad.prohibidos`: botones que escriben (Crear, Guardar, Aprobar, Publicar, Eliminar…). Un clic
  sobre ellos **aborta la operación**. Para una escritura indispensable, el paso lleva `escribe: true` y
  tiene que quedar cupo en `escrituras_permitidas`. Los datos creados van con prefijo DEMO y se limpian.
- Toda operación con modal se cierra al terminar (Cancelar / Cerrar o Escape).
- **Material para la institución:** cuentas reales del sistema, nunca cuentas de prueba (sus nombres
  delatan un entorno de pruebas). Si no se conoce la clave, **se pregunta al autor**; no se cambia.
- Nada con datos reales de la institución o sensibles se envía a servicios externos durante las capturas.

## Navegador

Chrome de `$CHROME`, el `chrome-headless-shell` de `~/.cache/puppeteer`, o el que instala Playwright
(`uv run --with playwright playwright install chromium-headless-shell`).
