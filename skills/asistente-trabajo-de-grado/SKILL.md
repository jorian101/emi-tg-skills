---
name: asistente-trabajo-de-grado
description: "Trigger: revisar, corregir, citar, resumir o auditar el marco teórico o práctico de un trabajo de grado o tesis; consultar NotebookLM (perfil, marco teórico, marco práctico, comparativa por año, apuntes, explicaciones de docentes); proponer correcciones textuales; completar secciones 3.4.8/3.4.9; verificar fuentes y coherencia; generar revisiones pendientes; revisar terminología poco accesible para no especialistas (modo legibilidad); revisar coherencia entre marco teórico y marco práctico (modo coherencia); revisar o redactar el capítulo final de conclusiones y recomendaciones (modo conclusiones); auditar sprint (código ↔ documento). Área general de trabajos de grado con docentes dinámicos. NO modifica directamente el Word ni sobrescribe correcciones manuales sin aprobación."
license: MIT
metadata:
  author: asistente-legal
  version: "3.0"
---

# Skill: asistente-trabajo-de-grado

## Activation Contract

Usá esta skill cuando el usuario pida:

- revisar o corregir el `marco-practico.md` o el marco teórico;
- proponer correcciones textuales (sin tocar el Word todavía);
- citar, verificar fuentes o auditar la bibliografía contra Zotero;
- resumir el marco práctico;
- completar las secciones 3.4.8 (Integración operativa del RAG) o 3.4.9 (Revisión y retroalimentación);
- revisar pendientes de fuentes, citas fantasma o metadatos;
- comparar coherencia entre marco teórico y marco práctico (modo coherencia);
- revisar terminología poco accesible para lectores no especialistas sin perder rigor jurídico (modo legibilidad).
- revisar o redactar el capítulo final de conclusiones y recomendaciones (modo conclusiones).
- consultar NotebookLM con filtro por año, docente y ámbito (modo notebooklm);
- alimentar la red Karpathy del vault (fuentes crudas → destilado en `wiki/`).

## Área de conocimiento y docentes dinámicos

Esta skill trabaja sobre el **área general de trabajos de grado** del vault, no solo sobre este proyecto. La estructura y las fuentes viven en el vault; la skill es un intérprete estable.

- **Documento maestro**: `sources/<slug>.md` (por ejemplo `trabajo-de-grado.md` o `marco-practico.md`), según lo registrado en `ORDEN-DEL-VAULT.md`.
- **Conocimiento destilado**: `wiki/trabajos-grado/` (estructura, perfil, marcos, metodología) — notas con frontmatter `fuente_original` + `seccion_original`.
- **Docentes dinámicos**: `wiki/docentes/_moc-docentes.md` es el **catálogo**. Cada docente es un `.md` con su `ambito` (`general` | `especifico`), su canal (`audio`, `pdf`, `apuntes`) y sus `fuente_id` de NotebookLM. La lista crece sin tocar la skill: crear el `.md` desde `_plantilla-docente.md` + agregar fila al catálogo. **Nunca hardcodear un docente en `SKILL.md`.**

### Catálogo de docentes (se lee en cada corrida)

> Fuente de verdad **única**: `wiki/docentes/_moc-docentes.md`. El catálogo **no se espeja acá**
> (regla de esta skill: "nunca hardcodear un docente en `SKILL.md`"). Leerlo en cada corrida.
>
> El catálogo tiene dos bloques: los **docentes con material propio** (cada uno con su `ambito`
> y su canal: audios, PDF o apuntes) y los **docentes revisores externos**
> (`origen: informes-revisores`), cuyos criterios se destilaron de informes de
> revisión a otros estudiantes y valen como **segunda opinión**, nunca como norma.

**Uso real de cada docente**: el docente `especifico` es el principal (fuente de criterio de contenido). El `general` es **segunda opinión de emergencia**: se consulta solo cuando no se sabe qué hacer o se buscan puntos de vista distintos, no como norma del trabajo específico.

> [!important] Desambiguación de docentes
> La skill NUNCA asume "explicación general = norma del trabajo". Cada consulta debe resolver el `docente` y su `ambito`. Si no se puede determinar el docente de una fuente, marcarla `pendiente` y no usarla como norma. Jerarquía y cadena de escalación: `wiki/docentes/jerarquia-autoridad.md` (fuente única, compartida con `perfil-revisor-tg`).

## Reglas de oro

1. **No modificar directamente el Word.** Entregar primero propuestas textuales, diffs y recomendaciones. Esperar aprobación explícita.
2. **No sobrescribir correcciones manuales.** Antes de reemplazar el Markdown, verificar `git diff` en el vault y presentar el conflicto.
3. **Redacción en tercera persona, normal y académica.** Aplicar `humanizer` solo a la prosa generada, NUNCA a citas, datos, tablas, código, numeración ni notas `Nota.`.
4. **No inventar.** Nunca fabricar autores, fechas, hechos, DOI o fuentes. Lo no confirmado se marca pendiente.
5. **Citas solo en notas.** En el marco práctico los párrafos son autorales; las fuentes van en las notas de figuras y tablas con el patrón establecido.
6. **Coherencia con las otras skills.** El orden de secciones lo define `ORDEN-DEL-VAULT.md`; la evidencia técnica la aporta `generar-entregables-tesis`; la extracción la hace `extraer-doc-tesis`. Ninguna de ellas debe contradecir a esta skill.

7. **Anti-desincronización (OBLIGATORIA).** Las tablas finales (3.4.9, 3.5, 3.6.7, 3.7) consolidan datos de las tablas de sprints. Reglas:
   - Toda tabla final lleva frontmatter `fuentes` listando los archivos de sprint exactos de los que deriva (ruta + sección `marco_practico_seccion`).
   - Al regenerar un sprint (via `generar-entregables-tesis`), verificar en `ORDEN-DEL-VAULT.md` qué tablas finales dependen de él; si una tabla de sprint cambió, crear/actualizar una pendiente `P-0XX` tipo `desync` en `sources/_zotero/revisiones-pendientes.md` para re-sincronizar la tabla final.
   - Las tablas finales que consolidan sprints llevan la nota `Verificado contra sprints S1-S6, <fecha>`.
   - Nunca congelar datos de un sprint en una tabla final sin registrar la dependencia.

8. **Humanizador obligatorio en propuestas.** Toda prosa nueva o reescrita propuesta por los modos legibilidad y coherencia pasa por `humanizer` (modo embebido) antes de entregarse, con las mismas exclusiones de la regla 3 (nunca sobre citas, datos, tablas, código, numeración ni notas). Objetivo: que el documento no parezca redactado por IA.

9. **Consultas NotebookLM filtradas y tipadas.** Nunca consultes el notebook completo sin filtrar. Toda consulta usa `tipo_consulta` + `año` + `docente`/`ambito` (ver "Consulta NotebookLM" abajo). No se cruzan años ni docentes salvo que el `tipo_consulta` sea explícitamente `comparativa`.

## Consulta NotebookLM (MCP/CLI)

El notebook fuente se declara en `.env.local` (`NLM_NOTEBOOK_ID`). Las consultas se hacen con `nlm` (CLI) o el MCP `gemini-notebook-mcp`. **Siempre autenticá primero** con `nlm login` si el estado no es `configured`.

> [!warning] Auth inestable entre llamadas
> El auth de `nlm` expira entre invocaciones de bash separadas. **Corré el login y TODAS las queries en un solo bloque bash contiguo** para no perder la sesión. Reauth: `$LOCAL_BIN/nlm-auth-brave` (abre Brave con CDP) y luego `nlm login --provider openclaw --cdp-url http://127.0.0.1:9223`.

> [!important] Consulta y actualización del vault
> Si un dato buscado **no está** destilado en el vault (`wiki/trabajos-grado/`, `wiki/docentes/`), consultalo en el notebook y **actualizá el vault** con el hallazgo. Flujo: consulta tipada → guardar crudo en `sources/notebooklm/trabajos-grado/` → destilar la nota → verificar enlaces.

### Tipos de consulta tipados

| `tipo_consulta` | Qué responde                                         | Filtro mínimo         |
| --------------- | ---------------------------------------------------- | --------------------- |
| `perfil`        | Estructura del perfil del trabajo de grado           | `año` + `docente`     |
| `teorico`       | Marco teórico (Hernández Sampieri, metodología)      | `año` + `docente`     |
| `practico`      | Marco práctico (sprints, matriz, árbol de problemas) | `año` + `docente`     |
| `temario`       | Temarios y contenidos específicos                    | `año`                 |
| `introduccion`  | Introducciones                                       | `año`                 |
| `comparativa`   | Comparar entre años (ej. temario 2024 vs 2025)       | `año_a` + `año_b`     |
| `apuntes`       | Apuntes de clase / notas sueltas                     | — (solo `referencia`) |
| `docente`       | Explicaciones de un docente                          | `docente` + `ambito`  |

### Parámetros obligatorios

- **`año`**: default `2025` (canónico del trabajo actual). Si `año != 2025`, la respuesta se envuelve en callout de **comparación** y no se propone como corrección.
- **`docente`**: `salgueiro` | `narvaez` | `desconocido`. Si `desconocido`, marcar `pendiente`, no usar como norma.
- **`estado`** (opcional): `oficial` | `borrador` | `incompleto` | `antiguo_con_errores` | `apuntes`. Solo `año=2025 + estado=oficial` es **canónico**; el resto son ideas o comparativa.

### Output contract de cada consulta

Cada hallazgo devuelve, como mínimo:

```
fuente: <título de la fuente / source_id>
año: <2025 | 2024 | otros>
estado: <oficial | borrador | incompleto | antiguo_con_errores | apuntes>
docente: <salgueiro | narvaez | desconocido>
ambito: <general | especifico | - >
flag: <canonico_2025 | comparativa | ideas | referencia | general>
cita: <texto o cita textual>
```

### Reglas anti-confusión

1. **No mezclar años** sin `tipo_consulta=comparativa`. Si una query mezcla años, abortar y pedir aclarar.
2. **No mezclar docentes.** Un docente `general` ≠ un docente `especifico` ≠ la norma del trabajo de grado. El `ambito` resuelve el conflicto de fuente.
3. **Fuentes incompletas o antiguas con errores** aportan ideas, no definiciones. Siempre callout de advertencia.
4. **Apuntes de clase** son `referencia`, nunca norma.
5. Solo `año=2025 + oficial` alimenta el destilado canónico en `wiki/trabajos-grado/`.
6. **Contradicciones entre fuentes:** si dos fuentes se contradicen (numeración de capítulos, norma ISO, estructura), NO se resuelve en silencio. Documentar en `wiki/contradictions/tg-*.md` y añadir al índice `wiki/trabajos-grado/contradicciones.md`. Estado `abierta` o `resuelto`.

## Patrones de notas (obligatorios)

- Con fuente bibliográfica:
  `Nota. [Descripción]. Elaboración propia con base en Autor (año), Autor (año), & Autor (año), 2026.`
- Técnico sin fuente bibliográfica:
  `Nota. [Descripción]. Elaboración propia mediante [herramienta], 2026.`
- Captura propia:
  `Nota. [Descripción]. Elaboración propia, 2026.`

## Fuentes de verdad (en orden de jerarquía)

Para **este proyecto** (asistente legal) rige este orden:

1. Código actual del proyecto (`$CODE_REPO/backend/`, `$CODE_REPO/frontend/`, migraciones, tests). Esta skill vive en el vault: toda ruta al repo de código va **absoluta**, nunca relativa al cwd.
2. Entregables de `generar-entregables-tesis` (evidencia técnica).
3. `sources/marco-practico.md` (documento académico).
4. `wiki/` (teoría).
5. Zotero — MCP en vivo o `sources/_zotero/library-snapshot.json`.
6. NotebookLM y material auxiliar (fase posterior).

### Área general de trabajos de grado (eje propio, no reemplaza al anterior)

Para el área de TG como conocimiento transversal, el orden es:

1. **Norma / documento oficial del área** (documento maestro aprobado de la EMI). Prevalece sobre explicaciones de docentes.
2. **Documento académico maestro** del área (`sources/<slug>.md`).
3. **Docentes con `ambito=especifico`** — explican el contenido del TG.
4. **Docentes con `ambito=general`** — metodología transversal; respalda pero no es norma del trabajo específico, y es **segunda opinión de emergencia**.
5. **Apuntes de clase** — solo `referencia`, nunca norma.
6. **Trabajos de otros años / incompletos / antiguos** — solo ideas y comparativa.
7. **Zotero** y **NotebookLM** — fuentes, en ese orden.

> [!important] Revisores: plano aparte (criterio, no norma)
> Los evaluadores (**revisores/tutor**) y sus perfiles (`wiki/revisores/`, skill `perfil-revisor-tg`) son **criterio de un evaluador**, no norma. **El revisor gana sobre la norma y sobre los docentes** en lo que corrige explícitamente. La jerarquía completa y la cadena de escalación viven en una sola nota compartida: `wiki/docentes/jerarquia-autoridad.md`. Todo punto de un perfil es `confirmado` / `inferido` / `abierto` (nunca adivinar la intención del evaluador).

## Relación con `perfil-revisor-tg` (complementarias)

- **Esta skill** aporta la **norma** (reglas EMI/2025, estructura, metodología), las **fuentes** (modo fuentes) y la **coherencia** (modo coherencia).
- **`perfil-revisor-tg`** aporta el **criterio** (cómo revisa un evaluador concreto) y es el **driver exclusivo de las pasadas de corrección** (regla 31 de esa skill): ningún otro modo corre pasadas de corrección de fondo.
- **División:** esta skill NO perfila evaluadores ni adivina su intención; la otra NO redefine la norma EMI.
- **Choque norma↔revisor / revisor↔revisor / revisor↔tutor:** no se resuelve en silencio. Se documenta en `wiki/contradictions/tg-revisor-*.md` con estado `abierta` y se pregunta al usuario. Ver `wiki/docentes/jerarquia-autoridad.md`.

## Modos de trabajo

### Modo notebooklm (consultar y destilar de NotebookLM)

Invocación: pedido explícito ("consultá en notebook", "extraé de notebooklm", "qué dijo <docente>", "compará 2024 vs 2025"). Pasos:

1. **Autenticar** si hace falta: `nlm login --check`; si no está `configured`, correr el flujo de auth (`$LOCAL_BIN/nlm-auth-brave` o `nlm login`). Todo en un solo bloque bash (ver el warning de auth arriba).
2. **Confirmar el notebook**: `nlm notebook list`. El tuyo es el que declara `NLM_NOTEBOOK_ID` en `.env.local`. Usar el alias `admin` solo si apunta a ese notebook (verificar con `nlm alias list`).
3. **Listar fuentes**: `nlm source list <nb-id>` y etiquetar cada una por `año` + `estado` + `docente` + `ambito`. La taxonomía vive en `wiki/docentes/` y en los hallazgos de `sources/notebooklm/`.
4. **Construir la query** con `tipo_consulta` + `año` + `docente` y filtrar por `source_ids` cuando el CLI lo permita. Nunca query global sin filtrar.
   ```
   nlm notebook query <nb-id> "<pregunta>" --source-ids <id1,id2>
   ```
5. **Recolectar hallazgos** en `sources/notebooklm/` con el formato del Output contract de consulta (fuente/año/estado/docente/ambito/flag/cita). Separar: canónico 2025, comparativa/incompletos/antiguos, apuntes, docentes.
6. **Destilar** al vault (`wiki/trabajos-grado/`, `wiki/docentes/`) solo lo que sea `canonico_2025` o aporte real como idea/referencia, con frontmatter `fuente_original` + `seccion_original` + ejemplo real cuando exista.
7. **No sobrescribir**: si una nota destino ya tiene cambios manuales, `git diff` y pedir aprobación antes de `--force`.

### Modo revision (revisar y proponer)

> Delegado. Las pasadas de corrección de fondo de una sección del TG las gobierna `perfil-revisor-tg` de punta a punta (extracción → plan → propuesta → verificación con matriz de cobertura evaluador+tutor+reglas). Esta skill aporta a esas pasadas la norma, las fuentes (modo fuentes), la coherencia (modo coherencia) y la legibilidad (modo legibilidad) cuando se le piden explícitamente. **No correr pasadas de corrección desde este modo**: el ruteo ambiguo es la causa documentada de propuestas sin cobertura.
>
> Los gates del Revisor 2 y las reglas CyR no se pierden con la delegación: viven como datos en `wiki/revisores/reglas-propias.md` (MP-34–MP-40, CyR-01–05), que `perfil-revisor-tg` lee en cada corrida.

Invocación: pedido explícito de corrección de fondo ("corregí esta sección según el revisor", "revisá el 3.2").

1. Activar `perfil-revisor-tg` (modo revisar) como driver; esta skill queda como proveedora de norma/fuentes/coherencia.
2. Lo demás lo gobierna `perfil-revisor-tg` (incluye su Output Contract: matriz de cobertura, verificación mecánica, sellos de vigencia).

### Modo legibilidad (terminología)

Invocación: SOLO bajo pedido explícito ("revisá la terminología", "chequeo de legibilidad").

1. Escanear la prosa de `sources/marco-practico.md` completo. Quedan FUERA del escaneo: tablas, notas `Nota.`, citas bibliográficas, código, numeración y epígrafes de figuras/tablas (regla 3).
2. Detectar términos jurídicos/técnicos que una persona no especialista no puede entender en su primera aparición. Ejemplos semilla: segunda instancia, radicatoria, auto de vista, ejecutoriado, cosa juzgada. La lista crece con lo encontrado en cada corrida.
3. Clasificar cada término con UNO de estos tres tratamientos:
   - `definida`: ya está definido o explicado en una mención previa → registrar como OK.
   - `glosa`: proponer una glosa breve (paréntesis o aposición) en la primera mención.
   - `teorico`: es doctrinario y recurrente pero no tiene base en el cap. 2 → derivarlo al modo coherencia como gap de fundamento teórico.
4. Aplicar `humanizer` (modo embebido) a toda prosa propuesta antes de entregarla (regla 8).
5. Escribir el resultado en `sources/_zotero/auditorias/legibilidad-terminologia.md` con la tabla `término | ubicación | estado | propuesta textual`.
6. Registrar pendientes tipo `terminologia` en `revisiones-pendientes.md`. Términos ya registrados ahí (abiertos o resueltos) NO se vuelven a marcar.

Restricción dura: este modo NUNCA reemplaza términos jurídicos por lenguaje coloquial ni reduce precisión. El término siempre queda; lo que se corrige es su presentación.

### Modo fuentes (citas y Zotero)

1. Verificar el snapshot (`sources/_zotero/library-snapshot.json`) o consultar Zotero MCP.
2. Cruzar citas detectadas (`fuentes-por-documento/<slug>.fuentes.md`).
3. Marcar `confirmada`, `coincidencia probable` o `pendiente`.
4. Para pendientes: buscar variantes, revisar el documento fuente y pedir la descarga antes de agregar a Zotero.
5. Alta y corrección de metadatos en Zotero: siempre con confirmación explícita y verificación posterior.

### Modo auditoria

Revisar:

- citas en el texto sin entrada bibliográfica;
- entradas bibliográficas nunca citadas;
- citas sin item en Zotero (fantasma);
- fuentes en Zotero sin PDF;
- autor/año/DOI inconsistentes;
- duplicados;
- errores de APA 7 modificado;
- conceptos del marco teórico no usados en el práctico (análisis profundo: modo coherencia);
- conceptos técnicos del práctico sin fundamento teórico (análisis profundo: modo coherencia);
- recomendaciones de actualización (sin ejecutarlas en silencio).

Escribir el resultado en `sources/_zotero/auditorias/` y actualizar `revisiones-pendientes.md`.

### Modo coherencia (marco teórico ↔ práctico)

Invocación: SOLO bajo pedido explícito ("revisá la coherencia teórico-práctico"). Es el análisis profundo de los dos chequeos de coherencia listados en modo auditoria.

Método bidireccional sobre `sources/marco-practico.md` (cap. 2 = marco teórico; el resto del documento = generalidades y marco práctico):

1. **Teoría muerta**: extraer los conceptos definidos en el cap. 2 (por subsección) y verificar cuáles nunca reaparecen después. Un concepto teórico que el desarrollo práctico jamás usa es un gap del lado práctico (o candidata a recorte, solo como recomendación, nunca ejecutada en silencio).
2. **Uso sin sustento**: detectar conceptos técnicos/jurídicos usados fuera del cap. 2 sin fundamento previo en él. Es un gap del lado teórico. Los derivados del paso `teorico` del modo legibilidad entran acá.
3. Construir la matriz `concepto | subsección teórica | secciones donde se usa` y marcar los gaps por lado.
4. Recomendaciones de cierre: qué agregar a cada lado. Si incluyen prosa propuesta, pasarla por `humanizer` (regla 8). `wiki/teoria/` sirve como material de apoyo para fundamentar, pero no sustituye al cap. 2.
5. Escribir el resultado en `sources/_zotero/auditorias/coherencia-teorico-practico.md`.
6. Registrar pendientes tipo `coherencia` en `revisiones-pendientes.md`.

Ambos sentidos se reportan por separado: un gap del lado práctico no se "arregla" escribiendo teoría nueva sin aprobación, y viceversa.

### Modo completar (3.4.8 / 3.4.9)

- **3.4.8 Integración operativa del RAG**: métricas de recuperación y generación, relevancia y umbrales, comparación de configuraciones, configuración final, despliegue y operación, evaluación de rendimiento.
- **3.4.9 Revisión y retroalimentación**: cumplimiento de la pila del producto, resultados globales, análisis de errores, acciones correctivas, retrospectiva consolidada, pendientes y mejoras.

Ambos modos entregan propuesta textual; no se escribe en el Word directamente.

### Modo resumen

Resumir el marco práctico (o una sección) conservando trazabilidad técnica y las notas de fuentes. Entregar el resumen como propuesta.

### Modo conclusiones (capítulo final, audio del docente)

Invocación: el usuario pide revisar o redactar conclusiones y recomendaciones.

1. **Una conclusión por OE + síntesis del OG al final**, cada una nombrando el _para qué_ de su objetivo. Prohibido "se cumplió el objetivo".
2. **Estructura por viñeta:** estado inicial → lo construido y CÓMO → comparación antes/después con cifras. Las cifras son SOLO las que demuestran el "para" del objetivo (comparaciones, porcentajes justificados en la evaluación técnica); nada de tamaño de construcción (SLOC, conteos de módulos) salvo que demuestren el para.
3. **Recomendación = dato → acción con destinatario.** Actor obligatorio en cada una; clasificación metodológicas/académicas/prácticas (estas últimas dirigidas a la institución del caso o a la EMI).
4. **Prohibido autoelogio** ("funciona", "satisfactorio" sin dato) y datos nuevos.
5. **Formato:** párrafo puente obligatorio, viñetas de guion, pasado impersonal, 2 páginas (1+1), sin citas bibliográficas **ni remisiones a tablas/secciones/anexos** (regla de forma del docente externo, ver MP-32 en reglas-propias: las cifras se conservan como resultados, la trazabilidad vive en la propuesta, no en el capítulo).
6. Toda conclusión debe poder rastrearse a la evaluación técnica o económica del cuerpo; si un número no tiene fuente en el cuerpo, se marca pendiente, nunca se inventa.
7. **Para cuantitativo sin medición (MP-33):** si el OG promete reducción sin punta medida, formular como **proyección diferenciada por fase** en el **cuartil inferior del rango literario** (piso RCT ~21% Schwarcz et al., 2025; techo 68% Reid et al., 2025) con método declarado en nota y **R-X de verificación post-implementación**; nunca "medición real" ni "estimado" desnudo (Hernández et al., 2014, p.204).
8. **Reglas del Revisor 2 (MP-34–MP-39):** lo prometido en el OG entra a conclusiones como compromiso de prueba; alcance por instancia interna; informe de subsanación punto por punto; OG/OEs/título/temario no se modifican.
9. **Reglas CyR (MP-40, CyR-01–05):** notas de tabla breves; conclusiones con apertura verbo-OE directo sin carencia (forma de la tutora; fondo del docente intacto); cada cifra en la conclusión de su objetivo (P/R y métricas solo en OE4); C-OG con _para_ literal y evidencia acotada a la fase demostrada + puente doctrinal en §1; recomendaciones ≤6 claras con actor, positivas y negativas desde §1.7 (sin EMI salvo pedido); C-OG fórmula piloto+proyección, nunca "proyección" sola.
10. **Checklist anti-errores Revisor 2 (toda propuesta que toque el OG):** un solo efecto; objeto del _para_ sin repetir términos del sujeto; alcance a la instancia (nunca "todo el proceso"); cada cifra con % y fuente del cuerpo; comparativa antes/después con mismos términos; matriz OE→nuevo _para_ que pruebe que ningún OE se rompe; ripple listado punto por punto (OG, C-OG, Matriz B); nota de trámite (sin OK del tribunal no se pega, MP-39).

### Modo auditoria-sprint (código ↔ documento por sprint)

Invocación: el usuario pide `audita sprint N`. SOLO lectura hasta que el usuario diga `procede`.

1. **Checklist exhaustivo por sprint, en orden, sin saltear piezas:**
   a. **Épicas** — Tabla 13: UNA fila de matriz por cada fila de épica del sprint, con su Nota y su remisión de fuente. Verificar que la épica como historia grande sin refinar cubra todo lo que el revisor podría exigir. El conteo se deriva de leer la tabla y se explicita en la propuesta ("1 épica: E-06").
   b. **Historias de usuario** — UNA fila de matriz por cada HU del sprint con su nombre, criterios de aceptación, prioridad y estimación (Anexo P; cuando el texto de la HU vive en Notion, usar el mapeo HU↔RF de `wiki/profiles/` del vault). Leer cada criterio: es lo que el revisor contrastará. El mapeo sprint↔HU canónico se deriva de `wiki/profiles/` + columna Sprint de la Tabla 59; PROHIBIDO confiar en el mapeo del `AGENTS.md` del repo de código sin verificarlo (está desactualizado en al menos un sprint). Conteo explicito ("3 HU: HU-13..15").
   c. **Pila** — Tabla 14: UNA fila de matriz por cada fila de RF del sprint; trazabilidad épica → HU → RF y coherencia prioridad/estimación contra el desglose de la planificación. Conteo explicito.
   d. **RNF** — Tabla 15: UNA fila de matriz por cada RNF aplicable al sprint + una fila por cada Regla de seguridad 1-7 que corresponda. Conteo explicito ("2 RNF + Regla 4").
   e. **Documentación del sprint** — diez piezas, cada una con su sección en la matriz y su Nota verificada: (e1) planificación (tareas, horas, días, objetivo, fechas); (e2) figura de caso de uso expandido; (e3) figura de actividades; (e4) figura de secuencia si el sprint la tiene; (e5) Anexo V mockups; (e6) codificación 3.4.x.4 (+ Anexo W scripts); (e7) pruebas unitarias (TU); (e8) pruebas de integración (TI); (e9) análisis de errores (E01..En con estado); (e10) figura(s) de revisión/captura y tabla de retrospectiva. Una pieza que no existe en el documento se marca `N/A` con motivo, nunca se omite en silencio.
   f. **Párrafos oración por oración:** intro del sprint, objetivo y fechas de la planificación, cada tarea desdoblada por `y` copulativo, análisis y diseño (texto de cada figura), codificación, intro de pruebas, revisión y retrospectiva. Cada oración se contrasta contra el inventario; si una tarea no tiene correlato en la codificación, se marca `abierto`.
   g. **Trazabilidad final** — Tablas 59/66 y toda tabla final que cite al sprint (regla anti-desincronización 7).
   h. **Alcance fuera de sprint (auditar una vez, no por sprint):** §3.3 Tablas 16-27 + Figuras 38-40 (arquitectura RAG, segmentación, comparativas LLM/embedding/reranker, prompts, HNSW, payload); Sprint 0, Figuras 41-43 + Tablas 26-27 (MER, BD vectorial); bloque 3.4.8-3.7, Tablas 55-78 (integración RAG, validación, evaluación técnica y económica) + Anexos Q, R, S, T, U, X, Y, Z.
   1bis. **Puerta de cobertura (bloqueante).** Antes de presentar cualquier decisión, la propuesta debe arrancar con la tabla `Cobertura del checklist`: una fila por cada ítem del paso 1 (a, b, c, d, e1..e10, f, g) con `verificado: dónde` (fila de matriz, tabla o figura concreta) o `N/A: motivo`. Un ítem sin fila en esa tabla = no auditado = PROHIBIDO presentar la auditoría al usuario o generar aplicados. La misma tabla encabeza el mensaje al usuario y el `.md` de la propuesta.
2. **Inventario por sprint/módulo:** registrar o actualizar todos los códigos relevantes — backend (`application/` UC, `domain/entities`, `adapters`, `routers`, migraciones), frontend (`pages/`, `api/`, componentes), tests — **con sección explícita de interfaces** (endpoints y contratos HTTP, props y contratos de componentes, firmas de UC/puertos; cada interfaz o parámetro lleva etiqueta `expuesto: UI | API | .env/config | código-only | infra`). El inventario marca por ítem si cumple con el documento (`confirmado`, `cubierto-por-chat`, `doctrina/proceso`, `abierto`, `sobrante/duplicado`).
3. **Revisión al máximo, corrección al mínimo.** Por cada celda, párrafo y Nota del checklist, desdoblar la frase al máximo en 6 dimensiones — `actores (quién/Tabla 12) | verbo (qué hace) | objeto (qué) | alcance/cardinalidad (cuántos/cuáles) | tiempo (cuándo/cuánto tarda/frecuencia) | lugar/capa (frontend/backend/Qdrant/infra)` — y abrir todas las **interpretaciones alternativas** que el revisor podría hacer en cada dimensión, aunque parezcan triviales; lo no listado se asume no revisado. Gatillos obligatorios (si la celda contiene uno, abrir interpretación sí o sí): `revocar, cerrar/invalidar, automático, rápido/inmediato/tiempo real, calibrar/ajustar/parametrizar, aislar, monitorear/supervisar, gestionar/procesar, validar/verificar, sincronizar, generar`. Adjetivo sin cifra (`rápido`, `automático`, `eficiente`) → mapear a RNF Tabla 15 o marcar `abierto por falta de SLA`. Contrastar cada interpretación contra el inventario. Lo ambiguo se marca `abierto` con la interpretación riesgosa explicitada, nunca se asume a favor. Regla de promesas: toda promesa de retrospectiva ("lo que se hará distinto") se verifica contra el siguiente sprint o contra propuesta; si no hay evidencia, se marca `abierto`.
4. **Diagramas: revisión maximalista, corrección minimalista.** **Base canónica:** la base de todo diagrama es el original ámbar de su sprint (el primer commit de `sprints/sprint-N/diagramas/`, respaldado en `respaldo-historico/`), NUNCA el contenido de una rama no canónica; está prohibido "portar contenido vigente" sobre la paleta. **Reglas de estilo y técnica obligatorias (espejo de las Hard Rules de `generar-entregables-tesis`):** paleta ámbar HR 15 (CU: actor `#FDE68A`/`#78350F`, usecase `#FFF7D6`/`#92400E`, rectangle `#FFFBEB`/`#92400E`; actividades: acción `#FFF7D6`/`#92400E`, decisión `#FDE68A`/`#78350F`, inicio/fin `#78350F`, flecha `#92400E`, swimlane `#92400E` grosor 2; secuencia: misma paleta adaptada); `skinparam linetype ortho` HR 17; Georgia + `#4A3B1F` HR 19; **prohibido `title` dentro del `.puml`** HR 16 (el título vive en el H2 del `.md` y en el epígrafe del Word); **swimlanes `|Asistente|`/`|Base de Datos|`, prohibido `|Sistema|`** HR 20; **máximo 10 nodos en actividades** HR 21; abstracción según HR 4bis: sin rutas de archivos, sin códigos ni flags HTTP, sin nombres de clases, valores de configuración ni identificadores con guiones bajos, sin paréntesis en los usecases, sin anglicismos ("upload" → "carga") — el diagrama muestra la intención y el detalle técnico queda en la prosa del Word. Casos de uso: modelo el del sprint 1 (`4676aec`) — 7-8 casos máximo, patrón verbo en infinitivo + objeto directo y nada más (prohibidos complementos, paréntesis y etiquetas tipo "(baja lógica)", "de RAG", "[Sprint 5]"); no cada endpoint es un caso: si un estado o dato ya se muestra en otro caso se fusiona (p. ej. el estado de indexación vive en el listado), y los detalles de implementación (baja lógica, retención, regex, endpoints) pertenecen a la prosa del Word, no al diagrama; actores fuera del `rectangle`; la autenticación NO se modela como caso "Iniciar Sesión" dentro de cada módulo. Única fuente `.puml` (los `.drawio` son respaldo histórico y no se regeneran). **Corrección:** solo si el original contradice el código (routers/UC/ports) o la prosa aprobada del Word, y al MISMO nivel de abstracción del original — renombrar, agregar o quitar nodos/casos; prohibido "corregir" inyectando detalle de implementación. **No se edita para "mejorar la precisión":** un nodo o mensaje del original que no afirma nada falso contra el código en su estado actual NO se toca, aunque pueda escribirse "mejor"; editar de más es empeorar el diagrama. **Lenguaje comprensible (mandatorio):** los textos de nodos, mensajes, ramas y carriles deben entenderlos un relator sin leer el código — prohibida la jerga interna (hidratar, fusión de rankings, puntajes, embed, fallback, cooldown, singleton); si la prosa del propio Word usa la palabra técnica, el diagrama usa la llana equivalente; si la interfaz no muestra algo, el diagrama tampoco lo afirma. **Terminología obligatoria:** en todo texto de diagrama la unidad indexable se dice SIEMPRE "segmento" (termino del documento: "Segmentar normas", "Consultar segmentos", "segmentos indexables"); prohibido "fragmento" en nodos, mensajes, ramas y notas, que es el nombre de la entidad interna del codigo. Asimismo la unidad documental procesal se dice SIEMPRE "obrado" (asi lo usa el cuerpo del Word: "cargar obrado", "publicar el obrado"); prohibido "obra(s)" en nodos, mensajes, participantes y notas — es el nombre de la entidad interna del codigo. **Gate verificable:** tras tocar los diagramas de un sprint, `grep -icE 'fragment' sprints/sprint-N/diagramas/*.puml` y `grep -iwE 'obra|obras' sprints/sprint-N/diagramas/*.puml` deben devolver 0 en todos los archivos (exencion: diagramas de arquitectura general del capitulo 3.3 / sprint 0); sin eso el barrido no esta cerrado. **Verificación mensaje por mensaje:** en actividades y secuencia se contrasta CADA mensaje contra lo que el código hace hoy (no solo la estructura ni los nombres de componentes), con vigilancia especial en estos dos tipos; el caso de uso se rige además por el canon de 7-8 casos verbo+objeto. Revisión al máximo, corrección al mínimo: se toca una palabra solo para eliminar una afirmación falsa o ambigua, jamás para completar o detallar. Cada actor, caso, relación `<<include>>/<<extend>>`, carril, diamante, rama de error y nota se contrasta contra código y Word. Tras tocar cualquier `.puml`: regenerar el PNG y verificar frescura (`plantuml -pipe` vs `md5sum` del `.png`); `@startuml` coincide con el nombre de archivo (sin tildes). Cada discrepancia genera UNA decisión tipificada (paso 5bis), sin agrupar. Figuras de mockups y de revisión sin correlato en el Word se marcan con "numeración provisional Anexo V / pendiente de ubicación" y no se renumeran a ciegas.
5. **Protocolo de decisiones:** primero se audita (solo lectura) y se presenta al usuario la tabla de `Cobertura del checklist` (paso 1bis) + la matriz `requerimiento | evidencia | estado | acción` + inventario con interfaces + chequeo de diagramas + lista numerada de decisiones tipificadas (paso 5bis). Se espera el `procede` explícito del usuario. Sin ese `procede`, no se ejecuta nada. Recién con `procede` se ejecutan los fixes, un commit por tarea, en la rama de revisión del ciclo.
   5bis. **Decisiones tipificadas:** cada `abierto` se traduce en UNA decisión con tipo explícito — `quitar` (código o fragmento documental sobrante/duplicado), `agregar` (código, test, tabla, figura o Nota faltante) o `actualizar` (corregir texto, cifra o actor existente) — que aplica tanto a código como a documento. Prohibido presentar decisiones con "o" / "ó" / alternativa / elección: cada `abierto` genera exactamente UNA decisión tipificada. Toda decisión lista: tipo, objetivo (código/documento), archivo(s) afectado(s), interpretación del revisor que la motiva y estado (`abierto`). Regla del `y` copulativo: toda celda con "A y B" / "A, B y C" se desdobla en N requerimientos atómicos antes de clasificar.
6. Para cada `abierto`: proponer la corrección mínima pero completa — debe cerrar la ambigüedad sin dejar flancos a futura malinterpretación del revisor — sea fix de código o corrección del documento; no tocar el Word sin aprobación explícita.
   6bis. **Docx de partes aplicadas (después del `procede`).** Solo después de que el usuario acepta las decisiones, generar UN `auditoria-sprint-N-aplicado.docx` por sprint. NUNCA es una copia del Word completo (prohibido duplicar el documento de decenas de MB): contiene SOLO las partes modificadas, cada una etiquetada con su ID de decisión y su ubicación en el Word vigente. Formato por ítem: para texto (párrafos, celdas de tabla, Notas), un par `Buscar:` (cadena exacta actual) / `Reemplazar con:` (cadena final); para figuras, la imagen final incrustada (~15 cm) con la leyenda `Figura NN — reemplazar/insertar` (el título del Word no se copia: es numeración automática). Verificar las cadenas `Buscar:` contra el Word vigente con `python-docx` (que cada una exista exactamente una vez, o indicar la ventana de anclaje si hay repetidas). Destino: `sources/_propuestas/auditoria-sprint-N-*/auditoria-sprint-N-aplicado.docx`. Sirve para copiar cada parte al `TRABAJO-DE-GRADO.docx`; no reemplaza al Word vigente. Generación: script `python-docx` que construye el documento desde cero. Verificación obligatoria con `python-docx` (NO `pandoc -t plain | grep`): todo ítem presente, cada imagen con `blip`, tamaño final pequeño. Notas técnicas: usar `python3.13` (tiene `docx`, el 3.12 no); en el Word vigente los placeholders de figuras vacías traen `wp:docPr` con `descr=None`; entre un epígrafe y su Nota puede haber una fila de párrafos vacíos (ventana ±30); los epígrafes son numeración automática (buscar por título real, sin el número).

## Orden de trabajo al pedir una actualización

1. Verificar archivo fuente y cambios manuales.
2. Comparar antes de sobrescribir.
3. Extraer (via `extraer-doc-tesis`) si corresponde.
4. Validar extracción.
5. Aplicar orden canónico (`ORDEN-DEL-VAULT.md`).
6. Detectar citas/bibliografía.
7. Consultar Zotero (MCP o snapshot).
8. Actualizar fuentes vinculadas.
9. Auditar citas y metadatos.
10. Generar revisiones pendientes.
11. Comparar marco teórico ↔ práctico (si se pidió: modo coherencia).
12. Revisar código y entregables.
13. Proponer correcciones textuales.
14. Humanizar prosa.
15. Entregar diff y esperar aprobación.
16. Actualizar Markdown solo tras aprobación.
17. Regenerar Word solo mediante el flujo autorizado.

Los modos legibilidad, coherencia y notebooklm son de invocación explícita: no corren automáticamente dentro de este flujo; se ejecutan como pasos adicionales solo cuando el usuario los pide.

## Herramientas y rutas

- `$VAULT/ORDEN-DEL-VAULT.md` — orden canónico.
- `$VAULT/sources/marco-practico.md` — documento maestro (asistente legal).
- `$VAULT/sources/<slug>.md` — documento maestro del área (ej. `trabajo-de-grado.md`).
- `$VAULT/sources/notebooklm/trabajos-grado/` — hallazgos crudos de NotebookLM (allowlist del vault).
- `$VAULT/wiki/trabajos-grado/` — conocimiento destilado del área (incluye `reglas-narvaez-2025.md`).
- `$VAULT/wiki/trabajos-grado/contradicciones.md` — índice de contradicciones del área.
- `$VAULT/wiki/contradictions/tg-*.md` — notas de contradicción (numeración, ISO, etc.).
- `$VAULT/wiki/docentes/` — catálogo dinámico de docentes (`_moc-docentes.md`, `_plantilla-docente.md`, un `.md` por docente).
- `$VAULT/wiki/docentes/jerarquia-autoridad.md` — jerarquía + cadena de escalación (compartida con `perfil-revisor-tg`).
- `$VAULT/wiki/revisores/` — criterio de evaluadores y tutor (skill `perfil-revisor-tg`), plano aparte de la norma.
- `$VAULT/wiki/contradictions/tg-revisor-indice.md` — choques revisor ↔ norma ↔ docente.
- `$VAULT/sources/_zotero/` — fuentes y pendientes.
- `$SKILLS/extraer-doc-tesis/scripts/zotero_snapshot.py` — snapshot read-only (antes vivía en el repo de código; migró al vault el 21-sep-2026).
- `$SKILLS/extraer-doc-tesis/scripts/match_fuentes.py` — matcher de citas.
- `~/.agents/skills/humanizer/SKILL.md` — revisión de estilo y patrones de redacción IA.
- Zotero MCP (`zotero-mcp`) — consulta en vivo si Zotero está abierto.
- NotebookLM: CLI `nlm` (`$LOCAL_BIN/nlm`) y/o MCP `gemini-notebook-mcp`. Notebook: el que declara `NLM_NOTEBOOK_ID` en `.env.local`. Auth: `nlm login` o `$LOCAL_BIN/nlm-auth-brave`.
- Pandoc, git diff, pdftotext — soporte.

## Output Contract

Entregar siempre:

- listado de correcciones propuestas (texto original → propuesta);
- fuentes revisadas (confirmada/probable/pendiente);
- pendientes nuevos en `revisiones-pendientes.md`;
- aviso claro de que el Word no fue modificado;
- próximos pasos sugeridos.

Cuando se pidió modo notebooklm: hallazgos con el formato del Output contract de consulta (`fuente/año/estado/docente/ambito/flag/cita`), el crudo guardado en `sources/notebooklm/trabajos-grado/` y las notas destiladas en `wiki/` con frontmatter `fuente_original` + `seccion_original`.

Cuando se pidió modo legibilidad: tabla `término | ubicación | estado | propuesta textual` y pendientes `terminologia`.

Cuando se pidió modo coherencia: matriz concepto ↔ secciones con gaps por lado y pendientes `coherencia`.

Cuando se pidió modo auditoria-sprint: matriz `requerimiento | evidencia | estado | acción`, pendientes de implementación o corrección documental, y —solo después del `procede`— UN `auditoria-sprint-N-aplicado.docx` por sprint con SOLO las partes modificadas (pares buscar/reemplazar e imágenes finales, nunca una copia del Word completo).
