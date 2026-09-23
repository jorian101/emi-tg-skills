# Patrones de regeneracion de entregables

Tres modos de operacion segun el pedido del usuario.

## Modo 1: Generar (primera vez)

**Trigger del usuario**: "Genera los entregables del Sprint X", "Sprint X terminado, dame los entregables".

**Asume**: `sprints/sprint-X/` no existe o esta vacio.

**Flujo**:

1. Lectura de contexto (silencioso): `marco-practico.md §3.4.X` + `wiki/<teoria>.md` correspondiente + inspeccion del backend
2. Presentar plan global al usuario (lista de Figuras/Tablas a generar, herramientas, orden)
3. Checkpoint del usuario: "¿Avanzo con este plan o ajustas algo?"
4. Por cada entregable: presentar contenido propuesto (modo ligero: nombre + ruta + 1 linea de intencion), checkpoint, generar
5. Ensamblar Word con Pandoc
6. Post-procesar Word (centrar imagenes, sin sangria, seccion "Codigo fuente de diagramas" al final)
7. Validar estructura (grep Nota., grep "En la Figura", grep H1 3.4.)
8. **Escaneo ortografico final** (ver seccion mas abajo): tildes ausentes, ñ confundida con n, palabras sin tilde, concordancia basica. Corregir antes de entregar.
9. **Validacion anti-redundancia y fecha de pruebas**: cada entregable con UN SOLO parrafo intro (Hard Rule 10 del SKILL.md); intro del sprint sin dias habiles/fechas; tablas de pruebas con `Fecha de ejecucion: YYYY-MM-DD.` debajo de su titulo H2 (Hard Rule 42ter).
10. Commit vault con `git commit --no-verify`
11. `mem_save` + `mem_session_summary`

## Modo 2: Regenerar total

**Trigger del usuario**: "Regenera TODO el Sprint X", "Rehacer Sprint X desde cero".

**Accion**: elimina `sprints/sprint-X/` completo y vuelve a invocar Modo 1.

```bash
rm -rf $VAULT/sprints/sprint-X/
```

**Sin preguntar** sobre capturas propias: el usuario confia en git para recuperar si borra algo por error. `git checkout HEAD~1 -- sprints/sprint-X/` recupera el estado anterior completo.

**Excepcion**: el archivo `sprints/sprint-X/assets/chartdb_diagram.json` (solo Sprint 0) NO se regenera automaticamente, se preserva entre regeneraciones porque es input reproducible. Si el usuario pide "regenera tambien el modelo E-R fisico", entonces se regenera el JSON desde las migraciones Alembic.

**Advertencia**: el archivo `.docx` generado en la corrida anterior queda como untracked en la papelera del vault. Se puede borrar manualmente con `rm sprints/sprint-X/sprint-X-entregables.docx`.

## Modo 3: Regenerar selectivo

**Trigger del usuario**: "Regenera la Figura N del Sprint X", "Regenera las Tablas 36 y 37 del Sprint X", "Regenera los mockups del Sprint X", "Regenera las Figuras N, M y P del Sprint X" o "Regenera el DER conceptual del Sprint 0".

**Accion**: regenera solo los entregables pedidos, sin tocar el resto.

### Mapeo entregable → archivos

Ver `assets/mapa-entregables.md` para la tabla completa. Ejemplos:

| Pedido del usuario                            | Archivos a regenerar                                                                                                                      |
| --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| "Regenera la Figura 46"                       | `diagramas/der.md`, `diagramas/diagrama-entidad-relacion.png`, `diagramas/der.dot`                                                        |
| "Regenera el modelo E-R fisico (Figura 47)"   | `diagramas/modelo-entidad-relacion.md`, `sprints/sprint-0/assets/chartdb_diagram.json`                                                    |
| "Regenera la captura del esquema (Figura 48)" | `capturas/esquema-bd-relacional.md` (la captura `esquema-bd-relacional.png` queda como tarea del usuario, la skill la omite si no existe) |
| "Regenera la Figura 49 (componentes)"         | `diagramas/componentes-bd-vectorial.md`, `diagramas/componentes-bd-vectorial.png`, `diagramas/componentes-bd-vectorial.puml`              |
| "Regenera Tablas 36 y 37"                     | `tablas/parametros-indice-vectorial.md`, `tablas/esquema-metadatos-vectorial.md`                                                          |
| "Regenera los mockups del Sprint X"           | Solo las filas de mockup de `assets/mapa-entregables.md`, incluyendo `.md`, `.html`, `.fig` y `.png`                                      |

### Flujo

1. Identificar archivos del entregable segun la tabla; para mockups incluir siempre `.md`, `.html`, `.fig` y `.png`
2. Borrar solo esos archivos
3. Regenerar solo esos (lectura de contexto puntual: teoria + codigo relevante); en mockups leer también `assets/patrones-mockups.md`, `$CODE_REPO/DESIGN.md`, `$CODE_REPO/frontend/src/index.css` y el CSS/componente de la pantalla
4. Reensamblar Word desde cero (no se puede "parchar" un `.docx` existente)
5. Si el entregable es una captura propia del usuario y el PNG no existe: preguntar si omitir del Word, usar placeholder 1x1, o esperar a que el usuario suba la captura

### Cierre obligatorio de completitud

Antes de ensamblar el Word, comparar el árbol real del sprint con todas las filas
del sprint en `assets/mapa-entregables.md`. Cada fila debe tener sus archivos de
fuente y salida. Para mockups son obligatorios `.md`, `.html`, `.fig` y `.png`;
para UML son obligatorios `.md`, `.puml` y `.png`; para capturas y revisión son
obligatorios `.md` y `.png`; para tablas es obligatorio `.md`. Si falta una fila,
no cerrar el sprint ni generar un Word final.

## Checkpoints del usuario

Los Modos 1 y 3 usan checkpoints. **Modo ligero por defecto**: solo nombre + ruta + 1 linea de intencion del entregable.

### Formato del checkpoint ligero

```
[Entregable N] Figura 46: Diagrama Entidad-Relacion
  Ruta: sprints/sprint-0/diagramas/der.md + .dot + .png
  Herramienta: Graphviz con notacion Chen + cardinalidad 1/n
  Intencion: 10 entidades + 20 FKs con cardinalidad explicita

¿OK, ajusto algo, o salto este?
```

Si el usuario pide "mostrame el .dot antes", la skill abre el archivo y muestra el contenido.

### Checkpoint global (solo Modo 1)

Antes de empezar a generar entregable por entregable, la skill presenta el plan completo:

```
Plan para Sprint X (seccion 3.4.X.Y):

1. Figura N: [titulo] - [herramienta] - [ruta]
2. Figura N+1: [titulo] - [herramienta] - [ruta]
3. Tabla M: [titulo] - Markdown - [ruta]
...

Total: 7 entregables
Orden: logico del sprint

¿Avanzo o ajustas algo?
```

### Verificacion de cumplimiento de Hard Rules (OBLIGATORIO en todo checkpoint global)

Antes de presentar el plan, verificar que cada entregable cumple:

- [ ] Cada entregable con UN SOLO parrafo introductorio (integra "En la Figura/Tabla N se..." + descripcion) (Hard Rule 10)
- [ ] Intro del sprint SIN dias habiles ni fechas (eso va solo en el parrafo de la Tabla de Planificacion) (Hard Rule 10bis)
- [ ] Titulo de Figura DESPUES de la imagen; titulo de Tabla ANTES de la tabla (Hard Rule 10)
- [ ] Tablas de Pruebas con `Fecha de ejecucion: YYYY-MM-DD.` debajo del titulo H2 (Hard Rule 42ter)
- [ ] Sin `title` en codigo PlantUML (Hard Rule 16)
- [ ] `skinparam linetype ortho` en UML (Hard Rule 17)
- [ ] Actores fuera del `package`/`rectangle` del modulo (Hard Rule 18)
- [ ] Paleta institucional ambar + Georgia en UML (Hard Rules 15, 19)
- [ ] Swimlanes con `|Asistente|`, no `|Sistema|` (Hard Rule 20)
- [ ] Actividades con max 10 nodos (Hard Rule 21)
- [ ] Una Figura = una imagen, sin sufijos `a/b/c` (Hard Rule 24)
- [ ] Revision = Figuras, no tabla (Hard Rule 31)
- [ ] Retrospectiva = Kerth 4 columnas (ver `assets/plantillas-tablas.md` §5)
- [ ] Tablas con 5-8 filas y verbos simples (ver `assets/plantillas-tablas.md` §1)
- [ ] Labels de usecase solo de verbos permitidos (ver `assets/patrones-redaccion.md` y `assets/plantillas-puml.md`)
- [ ] Nodos de actividades sin tecnicismos (sin `bcrypt`, `HTTP 4xx`, `ix_*`, etc.)

Si alguna casilla no se cumple, corregir antes de generar.

## Errores comunes a evitar

- **No preguntar** sobre capturas propias en Modo 2 (regenerar-total)
- **Si preguntar** sobre capturas propias en Modo 3 (regenerar-selectivo), porque solo afecta al entregable pedido
- **H1 compartido**: dentro de una subsección, el primer `.md` contiene el H1 y los siguientes archivos comienzan directamente con su H2
- **No usar** `git add .` en ningun modo: agregar archivos explicitamente
- **No commitear** `.docx` ni `reference.docx` en ningun modo (siempre untracked)
- **Idempotencia**: Modo 1 y Modo 3 deben ser ejecutables multiples veces sin generar duplicados

## Escaneo ortografico final (OBLIGATORIO)

Antes de entregar el `.docx` del sprint, escanear todos los `.md` del sprint para detectar y corregir errores ortograficos y gramaticales. Pasos concretos:

1. **Tildes ausentes**: palabras que deberian llevar tilde y no la llevan. Lista minima de control: `se diseña`, `código`, `gestión`, `útil`, `página`, `número`, `construcción`, `análisis`, `también`, `módulo`, `clásico`, `específico`, `práctica`, `técnica`, `informática`, `gestionar`. Ver lista completa en `assets/patrones-redaccion.md`.
2. **ñ confundida con n**: `diseño`, `señal`, `extraña`, `mañana`, `montaña`, `compañía`. Buscar patrones de palabras que terminan en `-no` o `-anio` sospechosas.
3. **Palabras sin tilde frecuentes**: `se disena`, `se creo`, `se configuro`, `codigo`, `gestion`, `util`, `pagina`, `numero`, `modulo`, `aplicacion`, `sistema` (esta ultima prohibida por la regla de redaccion: usar `asistente`), `imagen`, `rapido`.
4. **Concordancia basica**: sujeto-verbo, singular/plural, genero.
5. **Reglas de redaccion global** (ver `assets/patrones-redaccion.md`): sin rutas de archivos, sin parentesis, sin Reglas de seguridad, sin `en la captura`, sin `sistema/aplicacion/app`.

Correcciones se hacen directo sobre los `.md` antes de reensamblar el Word. Si el escaneo encuentra errores estructurales (numeracion de Figuras, parrafo de Nota. faltante), corregirlos antes del escaneo ortografico.

Si el corrector ortografico automatico no esta disponible, hacerlo manual con busquedas puntuales: `grep -rn 'se disena\|se creo\|se configuro\|codigo\|gestion\|pagina\|numero' sprints/sprint-X/`, y revisarlas una por una.
