---
name: generar-entregables-tesis
description: "Trigger: Genera o regenera entregables de tesis de un sprint, una figura, una tabla o los mockups del sprint. Produce Markdown, diagramas, fuentes OpenPencil, PNG y Word con validación reproducible."
license: MIT
metadata:
  author: "jorian"
  version: "3.2.1"
---

# Skill: generar-entregables-tesis

## Activation Contract

When the user asks to generate, regenerate, or update thesis deliverables for a sprint:

- **Modo 1 (Generar)**: "Genera los entregables del Sprint X", "Sprint X terminado, dame los entregables". Asume `sprints/sprint-X/` no existe o esta vacio.
- **Modo 2 (Regenerar total)**: "Regenera TODO el Sprint X", "Rehacer Sprint X desde cero". Elimina `sprints/sprint-X/` completo y vuelve a invocar Modo 1.
- **Modo 3 (Regenerar selectivo)**: "Regenera la Figura N del Sprint X", "Regenera las Tablas 36 y 37 del Sprint X". Regenera solo lo pedido segun `assets/mapa-entregables.md`.
- **Selección explícita**: "Regenera los mockups del Sprint X" regenera solo las figuras de mockup; "Regenera las Figuras N, M y P del Sprint X" regenera solo esas figuras. Nunca convertir un pedido selectivo en regeneración total. Los mockups generados son INMUTABLES: solo se regeneran si el usuario lo pide explicitamente (Hard Rule 30).
- **Modo 4 (Revisión global de redacción)**: "revisa la redaccion en relacion a todos los sprints", "que fluya el relato de S0 a S6". Revisa la continuidad narrativa de TODOS los sprints sin regenerar entregables. No toca mockups ni diagramas salvo pedido explicito (Hard Rule 43).

Flujo completo de los 3 modos en `assets/patrones-regeneracion.md`. Mapeo entregable → archivos en `assets/mapa-entregables.md`.

Output en `$VAULT/sprints/sprint-X/`.

## Hard Rules

1. **Tono OBLIGATORIO en presente del indicativo**: "se diseña", "se crea", "se configura". Nunca pasado ("se diseñó", "se creó"). Nunca primera/segunda persona. **Acentuacion correcta SIEMPRE**: tildes donde corresponde ("se diseña", "código", "gestión", "útil"), prohibido escribir sin tildes ("se disena", "codigo"). Tabla de sustituciones pasado→presente y regla de tildes en `assets/patrones-redaccion.md`. Si una frase no puede reformularse en presente, recurrir a "Actualmente se ..." para rutinas ya implementadas.

2. **Source of truth for subtitles**: `$VAULT/sources/marco-practico.md` seccion 3.4.X. Mapeo 1:1 estricto: Sprint 0 = 3.4.1, Sprint 1 = 3.4.2, ..., Sprint 6 = 3.4.7. Mapeo numerico completo (con doble nivel 3.4.X.Y) en `assets/subtitulos-por-sprint.md`.

3. **Source of truth for code**: inspeccionar `$CODE_REPO/backend/` (migraciones Alembic, Qdrant migrations, entidades de dominio, routers FastAPI, tests) ANTES de escribir. Para mockups, inspeccionar además `$CODE_REPO/frontend/`, `$CODE_REPO/DESIGN.md`, `$CODE_REPO/frontend/src/index.css` y el CSS/componente de la pantalla. Nunca fabricar contenido no respaldado por codigo.

4. **Source of truth for theory**: antes de redactar y elegir herramientas, consultar `$VAULT/wiki/` (`uml-diagramas-teoria.md`, `der-teoria.md`, `arquitectura-easi-rag-teoria.md`) y `$VAULT/sources/marco-practico.md` (secciones 2.x y 3.x). La teoria se usa para DISENAR/ELABORAR el diagrama, pero **NUNCA se menciona en los parrafos introductorios** ni en los parrafos antes de cada Figura/Tabla (sin citas de autores, sin definiciones, sin historia del estandar). El cuerpo del Word describe SOLO el desarrollo concreto del sprint; la teoria queda en el marco teorico de la tesis.

4bis. **Redaccion global (OBLIGATORIA)**: ver reglas completas en `assets/patrones-redaccion.md` seccion "Reglas de redaccion global". Resumen no negociable: - **Sin rutas de archivos**, **sin parentesis** (solo numeracion `3.4.X.Y`), **sin citas a Reglas de seguridad** (Regla 2/4/7 etc.). - **Sin guiones bajos en el cuerpo del Word**: prohibido mencionar nombres de variables, columnas o identificadores con guiones bajos (`expediente_id` -> "identificador del expediente", `created_at` -> "fecha de creacion", `POSTGRES_USER` -> "usuario de la base de datos", `chartdb_diagram.json` -> "el archivo de modelo fisico"). Esta regla aplica SOLO al cuerpo del Word y a los `.md` entregables. Las instrucciones operativas para el usuario (bloques `bash` con comandos) SI pueden llevar nombres tecnicos porque son comandos literales. - **Menos tecnicismo**: describir herramienta y accion, sin nombres de variables largos, siglas internas, flags HTTP ni nombres de indices. - **Sin** "sistema" / "aplicacion" / "app" (u otros equivalentes). Si hay que nombrar al producto, usar **"asistente"**. - **Sin ingles de mas**: preferir castellano (`login` -> `inicio de sesion`, `upload` -> `carga`). - **Tildes y ñ SIEMPRE** en los ENTREGABLES (`.md` y Word): `se diseña`, `código`, `diseño`, `señal`. El asset y el SKILL.md van sin tildes para legibilidad en terminal. - **Solo** `En la Figura N, se...` / `En la Tabla N, se...`. Prohibido `En la captura`, `En la imagen`.

5. **Idempotency**: sobreescribir `.md`, diagramas y `.png` existentes. No crear `_v2` salvo pedido explicito del usuario. Modos 1 y 3 son ejecutables multiples veces sin generar duplicados.

6. **Tooling required** (obligatorio desde Sprint 0): `plantuml` (requiere `java`), `graphviz` (`dot`), `pandoc`, `python-docx`, `silicon` (Aloxaf/silicon), `uv` + `playwright` (backend venv). ChartDB corre en contenedor Docker separado, NO se automatiza export PNG. Si falta algo, PARAR e indicar comandos de instalacion (ver `assets/herramientas-diagramacion.md` seccion instalacion).

7. **RG5 (no secrets)**: PNGs sin `.env`, tokens o datos sensibles. Redactar antes de commit.

8. **Branches de commits**: vault commits van a `main` del vault repo; skill changes se commitean en la rama de trabajo actual de `asistente-legal` (confirmar con el usuario el destino). El `.docx` y `reference.docx` NUNCA se commitean (untracked).

9. **Nota obligatoria**: TODA Figura y TODA Tabla individual debe terminar con un parrafo `Nota.` citando las fuentes exactas (ver `assets/notas-por-entregable.md`). Formato: `Nota. [descripcion]. Elaboracion propia con base en [Autor1 (Ano), Autor2 (Ano), ...], 2026.` Nunca omitir, nunca inventar.

10. **Patron de redaccion obligatorio — UN SOLO parrafo por entregable** (alineado al Word real de BACKUP TG): Toda Figura/Tabla sigue:
    (1) H1 `# 3.4.X.Y. [Titulo de seccion]` (subseccion)
    (2) UN SOLO parrafo introductorio (1-3 oraciones, 3ra persona formal, presente) que INTEGRA la referencia a la Figura/Tabla con la descripcion del contenido: comienza `En la Figura N se [verbo] [descripcion].` o `En la Tabla N se [verbo] [descripcion].` y continua describiendo el desarrollo concreto del sprint. NO existe parrafo intro de seccion separado ni frase "En la Figura N, se..." duplicada.
    (3) la Figura/Tabla: - **Figura**: imagen `![](png){ width=15cm }` y DESPUES de la imagen el titulo `## Figura N: [Titulo]` (el titulo va DEBAJO de la figura, como en el Word real) - **Tabla**: titulo `## Tabla N: [Titulo]` y despues la tabla markdown (el titulo va ARRIBA de la tabla)
    (4) `Nota. [descripcion]. Elaboracion propia con base en [citas], 2026.`
    Si una Figura agrupa multiples imagenes, repetir (2)-(4) por cada imagen individual (una Figura = una sola imagen, Hard Rule 24).
    **El parrafo (2) NUNCA menciona teoria** (sin citas de autores, sin definiciones, sin historia del estandar) **ni ubicacion de archivos/rutas** ni repite la intro del sprint. Ver `assets/patrones-redaccion.md`.

10bis. **Introduccion del sprint (OBLIGATORIA)**: el primer `.md` del sprint (segun el orden logico de `assets/mapa-entregables.md`) debe abrir con un parrafo de introduccion general del sprint ANTES del primer H1 `# 3.4.X.Y`. Este parrafo: - **3-5 oraciones**, 3ra persona formal, presente del indicativo - Describe el sprint en general: que se construye, que modulos cubre, que se entrega - **Sin teoria** (sin citas de autores, sin definiciones, sin historia del estandar) - **Sin rutas** de archivos ni nombres con guiones bajos (ver Hard Rule 4bis) - **Sin dias habiles ni fechas**: la duracion (p. ej. "cinco dias habiles del sprint") y las fechas viven SOLO en el parrafo introductorio de la Tabla de Planificacion. La intro del sprint NO menciona cuantos dias dura ni fechas concretas. - **Sin redundancia** con las intros de seccion (2) de cada Figura/Tabla: la intro del sprint describe el panorama; las intros de seccion describen el entregable puntual. No repetir la misma descripcion dos veces - Ejemplo Sprint 0: "El Sprint 0 se enfoca en la construccion de la infraestructura de datos del asistente. Se diseñan las bases de datos relacional y vectorial, se configuran los parametros del indice de busqueda, y se genera el modelo entidad-relacion que sirve de base para los sprints siguientes. Este sprint cubre la creacion de seis migraciones de esquema, la segmentacion jerarquica de seis leyes del corpus juridico, y la ingesta del corpus en la base de datos vectorial."

11. **Capitalizacion de encabezados**: primera letra mayuscula por palabra significativa; conectoras (`y`, `o`, `de`, `del`, `en`, `para`, `con`, `sin`, `a`, `por`, `el`, `la`, `los`, `las`, `un`, `una`) en minuscula. Sin parentesis en encabezados Word (salvo numeros "3.4.1.1."). Sin abreviaturas: "BD" solo si ya fue introducido; preferir "Base de Datos".

12. **Numeracion de Figuras/Tablas**: estatica, escrita explicitamente en el H2 (ej. `## Figura 46:`, `## Tabla 36:`). Pandoc NO auto-numera (no usar `fig:` captions, usar headers H2 explicitos).

13. **Tablas Scrum**: usar plantillas exactas de `assets/plantillas-tablas.md`. Columnas y citas no negociables. Tablas de planificacion/pruebas/revision/retrospectiva/errores siempre 10pt (`TableCompact`) via post-procesamiento. Las tablas de pruebas usan formato IEEE 829-2008 (Unitarias = Level Test Case; Integracion = Level Test Procedure) y llevan `Fecha de ejecucion: YYYY-MM-DD.` debajo de su titulo H2. Las tablas de "Acciones Correctivas" fueron ELIMINADAS del marco practico: no generarlas en ningun sprint.

14. **Sangria en Word**: CERO sangria, ni en cuerpo ni en celdas de tablas. `first_line_indent = Cm(0)`. Aplicado tanto en `reference.docx` como en post-procesamiento de tablas.

15. **Colores MANTENER en diagramas UML (NO en DER)**: la paleta institucional del Tribunal Supremo Militar aplica SOLO a diagramas UML (PlantUML: componentes, casos de uso, actividades, secuencia).

- **Caso de Uso**: actor `#FDE68A`/`#78350F`, usecase `#FFF7D6`/`#92400E`, rectangle `#FFFBEB`/`#92400E`.
- **Actividades**: acción `#FFF7D6`/`#92400E`, decisión `#FDE68A`/`#78350F`, inicio/fin `#78350F`, flecha `#92400E`, swimlane `#92400E` grosor 2.
- **Secuencia**: lifeline y mensajes con la misma paleta ámbar adaptada.

El DER conceptual (Graphviz `neato`) NO usa paleta: nodos con `fillcolor=white`, rombos opcionalmente `style=filled color=lightgrey`. DER usa `neato` con `overlap=prism`, `K=1`, `splines=true`, `len=1.3` global (ajustable por arista).

16. **Sin `title` en código PlantUML**: el título del diagrama vive solo en el H2 del `.md`. El `.puml` empieza directamente con `@startuml <id>`. Prohibido `title ...` dentro del código fuente. Excepción: si el diagrama va embebido en otro contexto donde se necesita el título, va como comentario UML `%título: ...`, pero nunca como `title`.

17. **Líneas rectas en UML**: todos los diagramas UML (caso de uso, actividades, secuencia) usan `skinparam linetype ortho` o equivalente para líneas rectas. Prohibido el curvado por defecto de PlantUML en diagramas de tesis.

18. **Actores siempre fuera del `package`/`rectangle` del módulo**: los `actor` UML son elementos externos al sistema y deben declararse **fuera** del `package` o `rectangle` que agrupa los `usecase` del módulo. Solo los `usecase` y los elementos internos van dentro del límite del sistema.

19. **Tipografía UML global**: todos los diagramas UML usan `skinparam defaultFontName "Georgia"` y `skinparam defaultFontColor #4A3B1F`. Coherencia visual con la maqueta institucional.

20. **Swimlane "Asistente" nunca "Sistema"**: en diagramas de actividades, el swimlane del backend se nombra `|Asistente|`. Prohibido `|Sistema|`, `|Aplicación|`, `|App|`.

21. **Máximo 10 nodos en diagrama de actividades**: cada diagrama de actividades tiene máximo 10 nodos entre todas las swimlanes. Si excede, dividir en dos diagramas o podar nodos redundantes (fusionar `Selecciona X` + `Envia X` en un solo nodo, eliminar swimlanes de notificación cuando la decisión ya tiene stop).

22. **Código fuente al final del Word (OBLIGATORIO)**: TODO el código fuente NO va en el cuerpo del Word. Va en una seccion aparte "Codigo fuente" al final del `.docx`, SIN numeracion Figura N. Esto incluye sin excepcion:
    - Codigo fuente `.dot` (Graphviz)
    - Codigo fuente `.puml` (PlantUML)
    - El archivo completo `chartdb_diagram.json` (modelo E-R fisico de ChartDB)
    - Cualquier otro bloque de codigo fuente embebido en los `.md` (`.py`, `.sql`, `.ts`, etc.): los snippets de codigo de la Codificacion del Modulo van como Figura PNG (Silicon) en el cuerpo, pero si su codigo fuente se incluye como bloque, va en esta seccion final, nunca en el cuerpo.

Excepcion unica: bloques ` ```bash ` con instrucciones para el usuario (ej. pasos ChartDB, pasos pgAdmin, pasos Qdrant) SI van en cuerpo del Word porque son instrucciones operativas para el lector.

23. **Capturas propias del usuario** (Sprint 0 Figuras 47 ChartDB, 48 esquema BD relacional vía pgAdmin y 50 dashboard Qdrant): la skill NO las genera automáticamente, NO embebe placeholders 1x1 y NO inventa capturas. Si un PNG no existe al momento de ensamblar el Word, preguntar al usuario si se omite esa figura o si espera a subir la captura. Ver `assets/herramientas-diagramacion.md`.

24. **Una Figura = una sola imagen**: cada captura de pantalla, mockup o script de codigo es una **Figura independiente** con su propio numero, su propio titulo y su propia `Nota.`. Cero sufijos `a/b/c`. Prohibido `Figura x.y`, `Captura 53a` o agrupar varias imagenes bajo un mismo numero de Figura. Si un entregable genera N imagenes, cada una recibe su propio `## Figura N:`.

25. **Tamano y alineacion de imagenes en Pandoc**: Markdown usa `![nombre.png](nombre.png){ width=15cm }`. El script de post-procesamiento fuerza alineacion centrada de todas las imagenes.

26. **Orden de generacion logico (Sprint 0)**: PRIMERO el Modelo E-R fisico (JSON leyendo migraciones Alembic), LUEGO el DER conceptual Chen (abstraccion fiel 1:1 del modelo fisico). Prohibido generar el DER conceptual primero.

27. **Silicon dinámico**: extraer fragmentos especificos y relevantes del backend con `sed -n 'START,ENDp' archivo.py > /tmp/snippet.py`, no procesar archivos enteros.

28. **Conventional Commits**: `docs(sprint-X): ...` en vault, `chore(skills): ...` en skill. `git commit --no-verify` (Husky bloquea). No `git add .` — archivos explicitamente. Skills en `.opencode/` son gitignored, requieren `git add -f`.

29. **Denominacion de Figuras**: las Figuras de codigo empiezan con `Figura N: Script de ...`. Las Figuras de mockup empiezan con `Figura N: Mockup de ...`. Las capturas reales del asistente en funcionamiento se titulan `Figura N: Interfaz de [X] en Funcionamiento` (ver Hard Rule 31). Los diagramas DER/UML y tablas mantienen su denominacion habitual. El verbo/objeto tras `Script de` o `Mockup de` describe la pantalla o el componente en castellano sin rutas ni parentesis.

30. **Mockups con OpenPencil (INMUTABLES)**: los mockups generados (`.html`, `.fig`, `.png`) NUNCA se regeneran ni se modifican una vez cerrado el sprint. Son un entregable congelado: no se les cambia diseño, colores, layout ni archivo. Regenerar solo en Modo 3 si el usuario lo pide EXPLICITAMENTE ("regenera los mockups"). La redaccion que los describe en los `.md` si puede ajustarse, pero los artefactos del mockup permanecen. Ver `assets/patrones-mockups.md` y `assets/herramientas-diagramacion.md`.

31. **Capturas reales para la Revision del Sprint**: la Revision del Sprint ya NO lleva tabla. En su lugar, se incluyen capturas de pantalla del asistente en funcionamiento de cada interfaz seleccionada previamente en los mockups. Herramienta: live browser de impeccable, o Playwright si esta instalado. Cada captura es una Figura independiente. La redaccion describe lo cumplido de las Historias de Usuario, sin tecnicismo, sin rutas, sin parentesis, sin Reglas de seguridad. **Denominacion obligatoria**: toda figura de interfaz real en funcionamiento se titula `Figura N: Interfaz de [X] en Funcionamiento` (ej. `Interfaz de Consulta en Funcionamiento`). PROHIBIDO el termino "Pantalla" en titulos de Figuras (`Pantalla de Consulta`, `Pantalla de Historial`). Los nombres de archivo en `revision/` pueden conservar `pantalla-*` aunque el titulo H2 cambie a "Interfaz de...".

32. **Escaneo ortografico final**: al cerrar el Word del sprint, escanear el `.md` o el `.docx` en busca de errores ortograficos y gramaticales: tildes ausentes, ñ confundida con n, palabras sin tilde, concordancia. Corregir antes de entregar. Ver `assets/patrones-regeneracion.md` paso de validacion.

33. **Mockups fieles al asistente**: antes de crear cualquier mockup, leer `assets/patrones-mockups.md`, `$CODE_REPO/DESIGN.md`, `$CODE_REPO/frontend/src/index.css` y el CSS/componente de la pantalla. Usar la paleta azul institucional y la tipografía Open Sans/Nunito Sans del asistente. La paleta ámbar de UML no aplica a mockups.

34. **OpenPencil reproducible**: cada mockup debe conservar fuente `.html`, documento `.fig` validado y PNG capturado desde el HTML. El flujo obligatorio es `import HTML -> .fig -> lint/info/analyze colors -> Playwright PNG`. PNG, JSX, PIL e ImageMagick no son fuentes oficiales.

35. **OpenPencil runtime**: ejecutar el CLI mediante `assets/../scripts/openpencil-cli.mjs` cuando el shim instalado falle con `Bun is not defined`. No improvisar polyfills ni cambiar de herramienta sin registrar el error.

36. **PNG de mockup**: generar el `.png` con `scripts/mockup-html-to-png.py` y Playwright a 1200 por 800 px. `openpencil export` se usa solo si el resultado visual coincide con el HTML; si deforma el layout, conservar el `.fig` validado y usar la captura Playwright.

37. **Completitud del sprint**: antes de ensamblar el Word, recorrer todas las filas del sprint en `assets/mapa-entregables.md` y comprobar cada `.md`, `.png`, `.puml`, `.dot`, `.html` y `.fig` requerido. Un sprint incompleto no se cierra.

38. **Estructura Markdown compartida**: dentro de una misma subsección, el H1 `# 3.4.X.Y.` aparece una sola vez en el primer archivo; los archivos siguientes empiezan en el H2 de su Figura o Tabla. No duplicar intros generales.

39. **Trazabilidad Word**: Pandoc recibe `--resource-path` con todos los subdirectorios del sprint. El postprocesado usa rutas absolutas cuando se ejecuta con `uv --directory`; eliminar los archivos de bloqueo `~$*.docx` después de cerrar el Word.

40. **Humanizar prosa generada (OBLIGATORIO)**: antes de ensamblar el Word, aplicar la skill `humanizer` (`~/.agents/skills/humanizer/SKILL.md`) a los parrafos narrativos generados para que la redaccion sea natural, formal, en tercera persona y sin marcas tipicas de texto generado por IA. **PROTEGER** contra cualquier cambio: citas, notas `Nota.`, fuentes, autores, anios, numeracion de Figuras/Tablas, nombres tecnicos, comandos, bloques de codigo, tablas y datos. Verificacion: despues de humanizar, comparar que ninguna cita ni nota cambio (grep de las `Nota.` y de los autores citados). El humanizer nunca inventa hechos, nombres, fechas ni referencias.

41. **Anti-desincronizacion con tablas finales (OBLIGATORIO)**: las tablas de sprints (planificacion, pruebas, analisis de errores, retrospectivas) alimentan las tablas finales del marco practico (3.4.9 causa-raiz y consolidacion, 3.5 validacion, 3.6.7 resultados globales, 3.7). Si un sprint cambia, esas tablas finales quedan obsoletas. Reglas:
    - Toda tabla de sprint lleva frontmatter `marco_practico_seccion` (ya existe) y, cuando alimenta una tabla final, se registra en `sources/_zotero/revisiones-pendientes.md` como dependencia con tipo `desync`.
    - Antes de regenerar un sprint, verificar que ninguna tabla final lo referencia; si lo hace, crear/actualizar la pendiente P-0XX `desync` indicando la tabla final afectada.
    - Las tablas finales que consolidan datos de sprints deben llevar una nota de verificacion: `Verificado contra sprints S1-S6, <fecha>`.
    - Nunca copiar datos congelados de un sprint a una tabla final sin registrar la dependencia.

42. **Arquitectura RAG visible en los sprints (OBLIGATORIO)**: el hilo conductor del marco practico es el desarrollo de la arquitectura RAG del asistente. Cada sprint debe mostrar su aporte concreto a esa arquitectura segun el codigo real (`$CODE_REPO/backend/`): Sprint 0 = infraestructura de datos (relacional + vectorial) que sostiene el RAG; Sprint 2 = ingesta, segmentacion e indexacion del corpus (la "R" de retrieval); Sprint 3 = recuperacion hibrida con `PipelineRAG` y `HybridSearcher` y reordenamiento por relevancia con el reranker (cross-encoder); Sprint 5 = contexto y trazabilidad con `ExpansorJerarquico` y `EvaluadorVisibilidad`; Sprint 6 = generacion con `ResolvedorPlantillas` y el cliente del modelo de lenguaje. La redaccion de cada sprint conecta su entregable con la pieza del RAG que construye, en lenguaje llano y sin repetir el marco teorico. Si un sprint no aporta a una fase RAG (ej. Sprint 1 auth, Sprint 4 expedientes), se describe como habilitador de las fases siguientes.

42bis. **Sistema descrito en su estado actual (OBLIGATORIO)**: al redactar cualquier entregable, describir el asistente como funciona HOY segun `$CODE_REPO/backend/`. El pipeline RAG se describe con sus fases operativas: clasificacion del tipo de respuesta, busqueda hibrida, **reordenamiento por relevancia (el reranker funciona como tal: reordena los candidatos con un modelo de lenguaje cruzado)** y expansion jerarquica. PROHIBIDO describir el reranker como "desactivado", "deshabilitado", "degradado" o "en fallback": el reranker es una fase operativa del pipeline y se redacta como tal, de forma consistente con el Word real (Sprint 3). Tampoco se mencionan circuit breakers, timeouts ni mecanismos de degradacion internos en el cuerpo del Word.

42ter. **Fecha de ejecucion en tablas de pruebas (OBLIGATORIO)**: cada tabla de Pruebas Unitarias y de Pruebas de Integracion lleva un texto de fecha justo debajo de su titulo H2 y arriba de la tabla, como texto aparte. La fecha es la del **Dia 5** de la planificacion del sprint (ultimo dia habil; el dia de pruebas), formato ISO: `Fecha de ejecucion: 2026-06-19.` Las fechas por sprint salen de `assets/calendario-sprints.md` (S1: 06-19, S2: 06-26, S3: 07-03, S4: 07-10, S5: 07-31, S6: 08-07, todas de 2026).

43. **Fluidez entre sprints (modo aparte, solo a pedido)**: la revision de fluidez transversal NO es parte del flujo normal por sprint. Se activa SOLO cuando el usuario pide "revisa la redaccion en relacion a todos los sprints" o "que fluya el relato de S0 a S6". En ese modo: leer todos los `.md` de los sprints en orden, verificar continuidad narrativa S0→S6, que cada sprint enganche con el siguiente, que no se repita teoria del marco teorico y que no haya descripciones duplicadas entre sprints (ej. describir la segmentacion en S2 y volver a explicarla en S3). Entregar propuestas de ajuste puntual por sprint. No modificar artefactos visuales (mockups, diagramas) salvo pedido explicito.

44. **Terminologia de la unidad indexable (OBLIGATORIO)**: en todo texto de entregable, figura, nota y diagrama la unidad indexable se dice SIEMPRE "segmento" (asi lo usan el Word, las tablas de planificacion y las TU: "segmentar", "segmentos indexables", "consultar segmentos"). "Fragmento" es el nombre de la entidad interna del codigo (Postgres/Qdrant) y queda PROHIBIDO en textos de nodos, mensajes, ramas, titulos y notas de diagramas y .md entregables. Igual la unidad documental procesal: se dice SIEMPRE "obrado" (como el cuerpo del Word); "obra(s)" (entidad del codigo) prohibida en los mismos textos. Gate: `grep -icE "fragment" sprints/sprint-N/diagramas/*.puml` y `grep -iwE "obra|obras" sprints/sprint-N/diagramas/*.puml` deben devolver 0 antes de cerrar el sprint (exencion: diagramas de arquitectura del capitulo 3.3 / sprint 0).

45. **Analisis de conceptos usados por sprint (cierre, con la skill asistente-trabajo-de-grado)**: al terminar una pasada de entregables (o a pedido del usuario), invocar la skill `asistente-trabajo-de-grado` (`$SKILLS/asistente-trabajo-de-grado/SKILL.md`) en su modo auditoria para mapear QUE conceptos del marco teorico se usaron en el desarrollo de cada sprint. Entregar una tabla `concepto del marco teorico → sprint(es) → donde se materializa en el codigo/entregable`. Esto detecta conceptos teoricos sin uso practico (gap) y desarrollo sin fundamento teorico. No se redacta dentro del Word; es un insumo de coherencia que se entrega en el chat y se registra en `sources/_zotero/auditorias/`.

## Checkpoints del usuario

Modos 1 y 3 usan checkpoints. **Modo ligero por defecto**: solo nombre + ruta + 1 linea de intencion. Ver `assets/patrones-regeneracion.md` seccion checkpoints.

### Formato checkpoint ligero (por entregable)

```
[Entregable N] Figura 46: Diagrama Entidad-Relacion
  Ruta: sprints/sprint-0/diagramas/der.md + .dot + .png
  Herramienta: Graphviz notacion Chen, cardinalidad 1/n
  Intencion: 10 entidades + 20 FKs con cardinalidad explicita

¿OK, ajusto algo, o salto este?
```

Si el usuario pide "mostrame el .dot antes", abrir el archivo y mostrar el contenido.

### Checkpoint global (solo Modo 1)

Antes de empezar entregable por entregable, presentar el plan completo:

```
Plan para Sprint X (seccion 3.4.X.Y):
1. Figura N: [titulo] - [herramienta] - [ruta]
2. Figura N+1: [titulo] - [herramienta] - [ruta]
3. Tabla M: [titulo] - Markdown - [ruta]
...
Total: 7 entregables. Orden: logico del sprint.

¿Avanzo o ajustas algo?
```

Modo 2 (regenerar-total) omite checkpoints por entregable: `rm -rf sprints/sprint-X/` luego invoca Modo 1 con checkpoint global unico. En Modo 3 se muestran solo los entregables seleccionados; "mockups del sprint" significa únicamente las Figuras de mockup.

## Herramientas por tipo de entregable

Tabla completa y justificacion en `assets/herramientas-diagramacion.md`.

| Entregable                                  | Herramienta                                                                         |
| ------------------------------------------- | ----------------------------------------------------------------------------------- |
| DER conceptual (Chen)                       | Graphviz (`neato`, aristas `--` no dirigidas)                                       |
| Modelo relacional fisico                    | ChartDB (visor, no export)                                                          |
| Diagrama de Componentes UML                 | PlantUML (component)                                                                |
| Casos de Uso Expandido                      | PlantUML (usecase, verbos permitidos) **o draw.io** (XML, por eleccion del usuario) |
| Diagrama de Actividades                     | PlantUML (activity, swimlanes, recortado)                                           |
| Diagrama de Secuencia                       | PlantUML (sequence, recortado)                                                      |
| Tablas                                      | Markdown                                                                            |
| Mockups UI                                  | HTML/CSS -> OpenPencil `.fig` -> PNG                                                |
| Capturas de Interfaz Real (Revision)        | Live browser de `impeccable` o Playwright                                           |
| Capturas de Scripts de Codigo               | Silicon (fondo blanco obligatorio)                                                  |
| Captura esquema BD (Sprint 0)               | Usuario (pgAdmin 4 ERD Tool)                                                        |
| Captura colecciones BD vectorial (Sprint 0) | Usuario (Qdrant dashboard)                                                          |

**Prohibido**: dbdiagram.io, Excalidraw, Carbon, ray.so, Mermaid (`mmdc`), bocetos a mano.

## Decision Gates

| Need                                       | Action                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| ------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| DER conceptual (Sprint 0)                  | Generar `.dot` con `graph ER` + `layout=neato` + `overlap=prism` + `K=1` + `splines=true` + aristas `--` (no dirigidas). Notacion Chen: `shape=box` entidades, `shape=diamond` relaciones, `shape=ellipse` atributos. **Convencion**: TODO en minuscula `snake_case`; rombos con un solo verbo en minuscula como label (ej. `abre`, `posee`), sin sufijo ni multilinea; identificadores de nodo pueden ser desambiguadores (`adjunta_msg`, `contiene_norma`) pero el `[label="..."]` es un verbo unico. Sin paleta multiple (solo `fillcolor=white` o `color=lightgrey` en rombos). Renderizar: `neato -Tpng archivo.dot -o archivo.png`. Si hay cruces o queda muy abierto, ajustar `K` (global, repulsion) y `len` (por arista o global, longitud) manualmente y re-renderizar. Generar DESPUES del modelo fisico (Hard Rule 20). Ver `wiki/der-teoria.md` para teoria Chen y `assets/herramientas-diagramacion.md` para tabla completa de parametros `neato` afinables. |
| Modelo relacional fisico (Sprint 0)        | Generar `sprints/sprint-0/assets/chartdb_diagram.json` leyendo migraciones Alembic. La skill entrega pasos al usuario para abrir ChartDB en navegador e importar el JSON. NO se automatiza export PNG. Generar PRIMERO (Hard Rule 20).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| UML (component/usecase/activity/sequence)  | Generar `.puml` con sintaxis PlantUML correcta (UML 2.5.1: `actor` para usuarios externos, `interface` con lollipop, `database` para PG/Qdrant, `package` para agrupar). **Obligatorio**: `skinparam linetype ortho` (Hard Rule 17), `skinparam defaultFontName "Georgia"` y `skinparam defaultFontColor #4A3B1F` (Hard Rule 19), paleta ámbar institucional (Hard Rule 15), actores fuera del `package`/`rectangle` (Hard Rule 18), swimlane `                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            | Asistente | `(Hard Rule 20), máx 10 nodos actividades (Hard Rule 21). Renderizar:`plantuml -tpng archivo.puml`. Ver `wiki/uml-diagramas-teoria.md`para teoria UML 2.5.1 y`assets/plantillas-puml.md`para plantillas canonicas. **Excepcion Casos de Uso Expandido**: si el usuario pide "con draw.io", usar`assets/plantilla-drawio-caso-uso.md`(XML draw.io con la MISMA paleta ambar y Georgia; actores como`umlActor`fuera del container;`edgeStyle=orthogonalEdgeStyle`; export PNG con `drawio --export`). El usuario elige la herramienta; por defecto sigue siendo PlantUML. **Post-generacion obligatoria**: guardar el `.drawio`, exportar el PNG con sufijo `-drawio`(nunca pisa el del`.puml`) y abrir el editor (`$LOCAL_BIN/drawio <archivo>.drawio >/dev/null 2>&1 & disown`) para ajuste directo del usuario. GATE DE ADOPCION: el `.md`y el Word solo se actualizan con confirmacion explicita del usuario (ese cambio en el`.md`al PNG`-drawio` marca la fase adoptada); despues, todo cambio detectado (`[ <archivo>.drawio -nt <archivo>-drawio.png ]`) re-exporta el PNG Y reensambla el Word del sprint automaticamente, sin preguntar. |
| Captura de codigo (S1-S6 Codificacion)     | `sed -n 'START,ENDp' archivo.py > /tmp/snippet.py` luego `silicon /tmp/snippet.py -o snippet.png --language python --theme "GitHub" --background "#FFFFFF" --no-window-controls --pad-horiz 20 --pad-vert 20`. Fondo blanco obligatorio, prohibido temas oscuros. Cada snippet = una Figura independiente con titulo `Figura N: Script de ...`. Sin rutas/parentesis/Reglas en el parrafo intro.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| Captura propia pendiente (pgAdmin, Qdrant) | NO generar placeholder. Preguntar al usuario: omitir, placeholder 1x1, o esperar a que suba. Ver Hard Rule 17.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| Tabla Scrum                                | Plantilla exacta de `assets/plantillas-tablas.md`. 10pt via `TableCompact` en post-procesamiento.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `reference.docx`                           | Generar con `python-docx`: Arial 12, interlineado 1.5, margenes APA (top/bottom/right 2.54cm, left 3.0cm), `first_line_indent = Cm(0)` (sin sangria), `Table Grid` base, estilo `TableCompact` 10pt definido.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |

## Execution Steps

### Paso 1: Verify scope y tooling

- Leer `marco-practico.md` seccion 3.4.X (segun sprint pedido)
- Leer teoria: `wiki/der-teoria.md` (DER), `wiki/uml-diagramas-teoria.md` (UML), `wiki/arquitectura-easi-rag-teoria.md` (RAG)
- Inspeccionar backend segun `assets/mapa-entregables.md` para el sprint pedido
- Si hay mockups seleccionados, inspeccionar `assets/patrones-mockups.md`, `$CODE_REPO/DESIGN.md`, `$CODE_REPO/frontend/src/index.css` y el CSS/componente de cada pantalla
- Verificar herramientas instaladas:
  ```bash
  which plantuml dot silicon pandoc openpencil; uv --version; java -version; bun --version
  test -f scripts/openpencil-cli.mjs
  test -f scripts/mockup-html-to-png.py
  uv run --directory $CODE_REPO/backend python -c "import playwright"
  pg_isready -h localhost -p 5433; docker --version
  ```
- Si falta algo, PARAR e indicar comandos (ver `assets/herramientas-diagramacion.md` seccion instalacion)

### Paso 2: Checkpoint global (solo Modo 1)

Presentar plan al usuario: lista de Figuras/Tablas, herramientas, orden. Esperar OK o ajustes.

### Paso 3: Generar entregables

Por cada entregable segun `assets/mapa-entregables.md`:

1. **Checkpoint ligero** (Modo 1 y 3): nombre + ruta + herramienta + 1 linea de intencion. Esperar OK
2. Leer teoria de referencia si corresponde
3. Generar archivo fuente (`.dot`/`.puml`/JSON/Markdown) con contenido en presente, citando teoria
4. Renderizar a PNG (Graphviz/PlantUML/Silicon) segun `assets/herramientas-diagramacion.md`
5. Escribir el `.md` con patron canonico (Hard Rule 10): H1 `# 3.4.X.Y.` + UN SOLO parrafo que integra `En la Figura/Tabla N se ...` + Figura (imagen, luego titulo H2 debajo) o Tabla (titulo H2, luego tabla) + `Nota.`

### Paso 3bis: Humanizar prosa generada (Hard Rule 40)

Antes de ensamblar el Word:

1. Leer `~/.agents/skills/humanizer/SKILL.md`.
2. Aplicar sus reglas a los parrafos narrativos de los `.md` generados (intros de sprint y de seccion, descripciones de Figuras/Tablas).
3. NO aplicar a: notas `Nota.`, citas, fuentes, datos, tablas, comandos, bloques de codigo, numeracion, nombres tecnicos.
4. Verificar con grep que las `Nota.` y los autores citados quedaron identicos antes y despues.
5. Verificar con grep que no entraron anglicismos: prohibido `done`, `Done`, `naming`, `core`, `chat`, `workspace`, `login`, `upload`, `dashboard` en el cuerpo ni en tablas (ver `assets/patrones-redaccion.md`).

### Paso 4: Generate/refresh `reference.docx`

Con `python-docx`:

- Arial 12pt, interlineado 1.5
- Margenes APA (top/bottom/right 2.54cm, left 3.0cm)
- `first_line_indent = Cm(0)` (sin sangria, Hard Rule 14)
- `Table Grid` como base
- Estilo `TableCompact` Arial 10pt definido
- Guardar en la raiz del vault

### Paso 5: Export Word con Pandoc

Listar archivos EXPLICITAMENTE en orden logico (no `*.md` para evitar orden alfabetico). Construir segun `assets/mapa-entregables.md` por sprint. Incluir `--resource-path` con `diagramas`, `mockups`, `capturas`, `revision` y la raiz del vault. Ejemplo Sprint 0:

```bash
pandoc sprints/sprint-0/diagramas/der.md \
  sprints/sprint-0/diagramas/modelo-entidad-relacion.md \
  sprints/sprint-0/capturas/esquema-bd-relacional.md \
  sprints/sprint-0/diagramas/componentes-bd-vectorial.md \
  sprints/sprint-0/tablas/parametros-indice-vectorial.md \
  sprints/sprint-0/tablas/esquema-metadatos-vectorial.md \
  sprints/sprint-0/capturas/README.md \
  -o sprints/sprint-0/sprint-0-entregables.docx \
  --reference-doc=reference.docx \
  --resource-path="sprints/sprint-0/diagramas:sprints/sprint-0/mockups:sprints/sprint-0/capturas:sprints/sprint-0/revision:." \
  --toc --toc-depth=4
```

### Paso 6: Post-procesamiento Word

Script efimero `/tmp/post_process_docx.py`:

1. Centrar todas las imagenes
2. `first_line_indent = Cm(0)` en cuerpo y celdas de tablas
3. Asignar `TableCompact` (10pt) a tablas de pruebas con headers IEEE: `Identificador | Objetivo | Entradas` (Unitarias, LTC) y `Identificador | Entradas y Requisitos` (Integracion, LTPr)
4. Simular `List Table 1 Light` sobre `Table Grid` (bordes sutiles, sin negritas en headers)
5. Mover TODOS los bloques de codigo fuente (``dot`, ``plantuml`, ```json`, ``python`, ``sql`, ```ts`, etc.) a seccion "Codigo fuente" al final, SIN numeracion Figura N (Hard Rule 22). Los bloques ```bash` con instrucciones operativas para el usuario NO se mueven (quedan en el cuerpo).

Ejecutar con rutas absolutas porque `uv --directory` cambia el directorio actual:

```bash
uv run --directory $CODE_REPO/backend python /tmp/post_process_docx.py \
  $VAULT/sprints/sprint-X/sprint-X-entregables.docx
rm -f $VAULT/sprints/sprint-X/'~$'*.docx
```

### Paso 7: Validacion

- `grep -c 'Nota\.' *.md` >= 1 por archivo
- `grep -c 'En la Figura\|En la Tabla' *.md` >= 1 por archivo
- `grep -E '^# 3\.4\.' *.md` lista H1 con numeracion correcta
- `ls -lh sprints/sprint-X/sprint-X-entregables.docx` archivo valido
- `pandoc sprints/sprint-X/sprint-X-entregables.docx -t plain -o /tmp/sprint-X-word.txt` y comprobar que aparecen todas las Figuras y Tablas del mapa
- `unzip -l sprints/sprint-X/sprint-X-entregables.docx | grep word/media` y comprobar que las imágenes esperadas están embebidas
- Comprobar que no quedan archivos de bloqueo `~$*.docx` en el sprint
- Verificar que TODOS los bloques de codigo fuente (``dot`/``plantuml`/```json`/``python`/``sql`/```ts`) NO estan en cuerpo (solo en seccion final "Codigo fuente", ver Hard Rule 22); los ```bash` operativos si pueden estar en el cuerpo.
- Verificar que tono es presente en muestra aleatoria de 3 parrafos
- **Verificar no redundancia (OBLIGATORIO)**: leer la introduccion del sprint (Hard Rule 10bis) y los parrafos de cada Figura/Tabla. La intro del sprint NO debe mencionar dias habiles ni fechas (eso va solo en el parrafo de la Tabla de Planificacion). Cada entregable debe tener UN SOLO parrafo introductorio; el titulo de la Figura va debajo de la imagen y el de la Tabla arriba de la tabla (Hard Rule 10). Si hay overlap entre parrafos o parrafo intro de seccion duplicado, reformular.
- **Verificar fecha en tablas de pruebas (Hard Rule 42ter)**: cada tabla de Pruebas Unitarias e Integracion lleva `Fecha de ejecucion: YYYY-MM-DD.` justo debajo de su titulo H2 (Dia 5 del sprint).
- **Verificar fluidez**: leer 3 parrafos aleatorios del `.docx` y comprobar que el texto fluye sin saltos abruptos entre ideas. Si un parrafo termina con una idea y el siguiente arranca con otra desconectada, añadir una frase de transicion.
- **Verificar sin ingles**: `grep -niE 'done|naming|core|chat|workspace|login|upload|dashboard' *.md` debe devolver solo nombres tecnicos aceptados (herramientas). Ningun estado `Done`: siempre `Hecho`.
- **Verificar puntualidad**: las tablas de pruebas/retrospectivas no deben tener mas de 8 filas; las celdas en una frase. Si una tabla esta inflada, recortarla a lo esencial.
- **Escaneo ortografico final** (ver `assets/patrones-regeneracion.md` seccion "Escaneo ortografico final"): tildes ausentes, ñ confundida con n, palabras sin tilde, reglas de redaccion global (sin rutas/parentesis/Reglas/sistema/aplicacion/app, sin guiones bajos en el cuerpo, sin `en la captura`). Corregir antes de cerrar el sprint.

### Paso 7bis: Guia de revision visual (entregar al usuario)

Despues de generar y validar el Word, la skill entrega al usuario una guia con 3 bloques para que pueda ver y editar los artefactos visuales externos. Esta guia se entrega EN EL CHAT (no en el Word). Cada bloque lleva pasos concretos para abrir, ver y editar.

La guia se entrega SOLO para los entregables que apliquen al sprint generado (ver `assets/mapa-entregables.md`). Ejemplo Sprint 0 (los 3 bloques):

**Bloque 1: Modelo Entidad-Relacion (ChartDB)**

```
Tu modelo entidad-relacion esta en el archivo de modelo fisico. Para abrirlo y editarlo:
1. Levantar ChartDB en Docker:
   docker run -d --name chartdb-temp -p 127.0.0.1:8080:80 --rm ghcr.io/chartdb/chartdb:latest
2. Abrir http://localhost:8080 en el navegador
3. Click en "Import from File"
4. Seleccionar sprints/sprint-0/assets/chartdb_diagram.json
5. ChartDB renderiza el modelo con 19 tablas de dominio y 36 relaciones
6. Para reordenar visualmente: arrastrar las tablas (drag & drop)
7. Para guardar el layout: Export -> Download JSON -> sobrescribe el archivo original
```

**Bloque 2: Esquema de la Base de Datos Relacional (pgAdmin 4)**

```
Tu esquema relacional esta en la base de datos real. Para verlo y capturarlo:
1. Levantar pgAdmin 4 en Docker (misma red que postgres):
   docker run -d --name pgadmin --network asistente-legal_default -p 5050:80 \
     -e PGADMIN_DEFAULT_EMAIL=admin@local.com -e PGADMIN_DEFAULT_PASSWORD=admin \
     dpage/pgadmin4
2. Abrir http://localhost:5050 -> login: admin@local.com / admin
3. Create Server -> Connection:
   - Host: asistente-legal-postgres-1
   - Port: 5432
   - Database: (nombre de la BD, leer de .env)
   - Username: (leer de .env)
   - Password: (leer de .env)
4. Expandir Databases -> Schemas -> public -> Tables
5. Seleccionar todas las tablas -> click derecho -> ERD Tool
6. File -> Export -> Image (PNG) -> guarda como sprints/sprint-0/capturas/esquema-bd-relacional.png
```

**Bloque 3: Colecciones de la Base de Datos Vectorial (Qdrant)**

```
Tus colecciones vectoriales estan en Qdrant. Para verlas:
1. Abrir http://localhost:6333/dashboard (Qdrant debe estar corriendo)
2. Click en la coleccion corpus_juridico
3. Debe mostrar: tamaño del vector (768), distancia (Cosine), configuracion HNSW,
   cuantizacion INT8, indices de payload
4. Screenshot -> guarda como sprints/sprint-0/capturas/colecciones-bd-vectorial.png
```

**Regla de la guia**: los pasos con nombres tecnicos (comandos Docker, nombres de contenedores,Variables de entorno) van en bloques de codigo porque son instrucciones operativas literales. NO se incluyen en el cuerpo del Word (ver Hard Rule 4bis y 16).

### Paso 8: Commit (separado)

- **Vault** (en `$VAULT`):
  ```bash
  git add sprints/sprint-X/ <archivos-explicitos>
  git commit --no-verify -m "docs(sprint-X): entregables regenerados"
  ```
- **Skill** (en `$VAULT`; migró desde el repo de código el 21-sep-2026). Confirmar con el usuario la rama de destino:
  ```bash
  git add .opencode/skills/generar-entregables-tesis/<archivos-cambiados>
  git commit --no-verify -m "refactor(skills): <cambio>"
  ```
- `.docx` y `reference.docx` quedan untracked (nunca commitear)

### Paso 9: Save to Engram

- `mem_save` tras cada commit (RG2): bugfix/decision/architecture segun el cambio
- `mem_session_summary` al cerrar la sesion (RG10)

## Formato Word (reference.docx)

| Elemento                             | Valor                                                                                          |
| ------------------------------------ | ---------------------------------------------------------------------------------------------- |
| Pagina                               | Carta (21.59 x 27.94 cm)                                                                       |
| Margen top/bottom/right              | 2.54 cm                                                                                        |
| Margen left                          | 3.00 cm (binding)                                                                              |
| Fuente Normal                        | Arial 12pt                                                                                     |
| Interlineado                         | 1.5                                                                                            |
| Sangria primera linea                | **0 cm** (sin sangria, Hard Rule 14)                                                           |
| Estilo tablas default                | `Table Grid` (modificado en post-procesamiento para simular `List Table 1 Light`)              |
| Estilo tablas compactas              | `TableCompact` (Arial 10pt, definido en reference.docx)                                        |
| Headers tablas                       | Arial 12pt normal (no bold)                                                                    |
| Body tablas                          | Arial 12pt normal (bold puntual)                                                               |
| Imagenes                             | `![nombre.png](nombre.png){ width=15cm }` en Markdown + centrado forzado en post-procesamiento |
| Codigo fuente (diagramas y snippets) | Seccion aparte al final del Word, sin numeracion Figura N (Hard Rule 22)                       |

## Output Contract

Return:

- Modo ejecutado (1/2/3) y sprint
- Archivos `.md` creados/modificados (ruta completa del vault)
- Archivos `.png` generados (ruta + herramienta usada)
- Comando Pandoc ejecutado y ruta completa del `.docx`
- Capturas propias pendientes (Figuras 47 ChartDB, 48 PostgreSQL y 50 Qdrant si Sprint 0)
- Commits realizados (vault + skill) con hash
- ID de `mem_save` en Engram

## References

- `$VAULT/sources/marco-practico.md` — plan de desarrollo de la tesis, seccion 3.4.X por sprint
- `$VAULT/wiki/uml-diagramas-teoria.md` — teoria UML 2.5.1 componentes
- `$VAULT/wiki/der-teoria.md` — teoria DER notacion Chen
- `$VAULT/wiki/arquitectura-easi-rag-teoria.md` — teoria arquitectura RAG
- `assets/subtitulos-por-sprint.md` — mapeo numerico 1:1 por sprint (7 sprints, doble nivel 3.4.X.Y)
- `assets/plantillas-tablas.md` — 7 plantillas de tablas Scrum con columnas y citas exactas
- `assets/patrones-redaccion.md` — formula del patron intro+Figura/Tabla+Nota, tabla pasado→presente, capitalizacion, verbos permitidos para casos de uso
- `assets/plantillas-puml.md` — plantillas canónicas PlantUML (caso de uso, actividades, secuencia) con paleta institucional, tipografía Georgia y linetype ortho
- `assets/calendario-sprints.md` — fechas Sprint 1-6 (L-V, 5 dias habiles)
- `assets/notas-por-entregable.md` — mapping Figura/Tabla → cita exacta por sprint
- `assets/herramientas-diagramacion.md` — que herramienta usar para cada tipo de diagrama, pasos ChartDB visor, capturas propias psql/Qdrant
- `assets/patrones-regeneracion.md` — 3 modos (generar, regenerar-total, regenerar-selectivo) + checkpoints ligeros
- `assets/mapa-entregables.md` — tabla Figura/Tabla → archivos + herramienta por sprint
- `$CODE_REPO/AGENTS.md` — reglas del proyecto (Conventional Commits, RG1-RG10, branching)

Base directory for this skill: $SKILLS/generar-entregables-tesis
Relative paths in this skill (e.g. `assets/`, scripts) are relative to this base directory.
