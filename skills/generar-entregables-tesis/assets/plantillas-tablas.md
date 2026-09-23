# 6 plantillas de tablas Scrum con columnas y citas EXACTAS

No negociables. Usar estas plantillas literales para las tablas Scrum de cada sprint. Las columnas no se modifican, no se agregan ni quitan, salvo confirmacion explicita del usuario.

## 1. Pila del Sprint (Planificacion)

- **Filas superiores**: Objetivo del Sprint (1-2 oraciones, sin tecnicismo) en la **fila 1** y **Fechas** (Inicio Lunes, Fin Viernes) en la **fila 2**. Inyectar fechas de `assets/calendario-sprints.md`.
- **Headers**: `ID HU | Tarea | Estimacion Inicial Horas | Estado | Dia 1 (YYYY-MM-DD) | Dia 2 | Dia 3 | Dia 4 | Dia 5`
- **5 columnas de dias fijas** (L-V), no dinamicas. Formato ISO: Dia 1 (2026-06-15), Dia 2 (2026-06-16), etc.
- **Tareas**: cada tarea empieza con un **verbo permitido** de `assets/patrones-redaccion.md` seguido de lo que trata, en castellano. Pocas tareas por sprint (5-8), no confundir con subtareas. Cortas, sin rutas de archivos, sin parentesis, sin ingles de mas, sin tecnicismo (`POST`, `JWT`, flags HTTP prohibidos). Ejemplo valido: `Crear Usuario y Asignar Rol`. Ejemplo invalido: `Crear endpoint POST /auth/login con bcrypt + rate limit`.
- **Nota**: `Nota. La tabla detalla el desglose de historias de usuario en tareas y el control del esfuerzo pendiente diario. Elaboracion propia con base en Menzinsky et al. (2016) y Satpathy (2013), 2026.`

## 2. Pruebas Unitarias (formato IEEE 829-2008, 10pt)

- **Estilo Word**: `TableCompact` (Arial 10pt) aplicado via post-procesamiento con `python-docx`. Solo esta tabla usa 10pt; el resto del documento usa Arial 12pt.
- **Formato de columnas segun IEEE Std 829-2008, Level Test Case (LTC, seccion 11)**: `Identificador | Objetivo | Entradas | Resultado Esperado`. El LTC define la informacion de entradas y salidas de la prueba: identificador del caso, objetivo, inputs y outcome(s).
- **Fecha de ejecucion (OBLIGATORIO)**: justo debajo del titulo H2 y antes de la tabla, como texto aparte: `Fecha de ejecucion: YYYY-MM-DD.` Es la fecha del Dia 5 (ultimo dia habil) de la planificacion del sprint.
- **Nota**: `Nota. La tabla consolida la validacion estructural y funcional de los componentes aislados conforme al estandar IEEE 829-2008. Elaboracion propia con base en IEEE (2008), Pressman (2010) y Myers (2011), 2026.`
- **Recomendacion**: formato grupal para sprints de desarrollo tradicional; formato individual (ficha detallada) solo para modulos criticos de investigacion. El post-procesamiento detecta tablas con header "ID | Componente Evaluado" y les asigna `TableCompact` automaticamente.
- **Extension**: POCAS filas (5-8), solo los casos mas representativos. `Objetivo` en una frase, `Entradas` en una frase y `Resultado Esperado` en una frase, sin detalle de implementacion. Nada que el lector no pueda comprender con el marco teorico.

## 3. Pruebas de Integracion (formato IEEE 829-2008, 10pt)

- **Formato de columnas segun IEEE Std 829-2008, Level Test Procedure (LTPr, seccion 12)**: `Identificador | Entradas y Requisitos | Pasos Ejecutados | Salida Esperada`. El LTPr describe los pasos ordenados para ejecutar los casos de prueba e integra las entradas, salidas y requisitos.
- **Fecha de ejecucion (OBLIGATORIO)**: justo debajo del titulo H2 y antes de la tabla, como texto aparte: `Fecha de ejecucion: YYYY-MM-DD.` Es la fecha del Dia 5 (ultimo dia habil) de la planificacion del sprint.
- **Nota**: `Nota. La tabla documenta la evaluacion de la interaccion y el flujo de datos entre los modulos acoplados conforme al estandar IEEE 829-2008. Elaboracion propia con base en IEEE (2008), Sommerville (2011), Myers (2011) y Pressman (2010), 2026.`
- **Extension**: POCAS filas (3-6), solo los flujos mas relevantes del sprint. Cada celda en una frase breve. Si una columna queda casi vacia para casi todas las filas, fusionarla o eliminarla (salvo confirmacion del usuario).

## 4. Revision del Sprint (sin tabla — capturas reales)

- **Ya NO lleva tabla**. En su lugar, se incluyen **capturas de pantalla del asistente en funcionamiento** de cada interfaz seleccionada previamente en los mockups del sprint.
- Cada captura es una **Figura independiente** titulada segun la interfaz (regla de denominacion en `SKILL.md`).
- Herramienta: live browser de `impeccable` o Playwright. Ver `assets/herramientas-diagramacion.md`.
- **Redaccion**: cada Figura describe lo cumplido de las Historias de Usuario del sprint, sin tecnicismo, sin rutas, sin parentesis, sin Reglas de seguridad.
- **Nota** por captura: `Nota. La figura muestra el asistente en funcionamiento del modulo de [nombre]. Elaboracion propia, 2026.`
- Esta seccion reemplaza a la antigua Tabla de Revision (parecia inutil frente a las Pruebas Unitarias y de Integracion, ya cubrian la verificacion funcional).

## 5. Retrospectiva del Sprint (Kerth - The Original 4)

- Cuatro columnas, basadas en las cuatro preguntas de Norman Kerth (Project Retrospectives, 2001). Ver teoria en `$VAULT/sources/retrospectiva-kerth.md`.
- **Headers**: `Lo que se hizo bien | Lo que se aprendio | Lo que se hara distinto la proxima vez | Lo que todavia se desconoce`
- **Enfoque**: mas general que la tabla de Analisis de Errores. Pocas filas (3-6); se generaliza. No tecnico: especifico y directo, en castellano natural, sin rutas, sin parentesis, sin Reglas de seguridad. Cada celda en una frase breve; no repetir aciertos entre filas. Evitar el relleno: solo lo que aporta al analisis.
- **Traduccion de las 4 preguntas de Kerth**:
  - `Lo que se hizo bien` - What did we do well, that if we don't discuss we might forget?
  - `Lo que se aprendio` - What did we learn?
  - `Lo que se hara distinto la proxima vez` - What should we do differently next time?
  - `Lo que todavia se desconoce` - What still puzzles us?
- **Nota**: `Nota. La tabla analiza la forma de trabajo del sprint a partir de las cuatro preguntas de Kerth. Elaboracion propia con base en Kerth (2001), 2026.`

## 6. Analisis de Errores

- **Headers**: `ID Error | Descripcion | Componente Afectado | Impacto | Estado`
- Columnas removidas: `Sprint`, `Tipo de Error`, `Frecuencia`.
- `Componente Afectado` puede llevar ruta de archivo (es la unica columna donde esta permitido).
- **Descripcion**: breve, sin rutas (van en Componente), sin parentesis, sin Reglas de seguridad. Dejar los errores mas relevantes. Tecnica pero breve: una linea por error, sin ambiguedad, sin largas explicaciones. `Impacto` en una frase llana (que le pasa al lector si ocurre el error).
- **Nota**: `Nota. La tabla documenta las fallas detectadas en el asistente durante el sprint. Elaboracion propia con base en Mathieu et al. (2024), 2026.`

## Reglas generales

- `Nota.` SIEMPRE al final de cada tabla, en linea nueva separada del bloque anterior. Formato exacto: `Nota. [descripcion]. Elaboracion propia con base en [citas], 2026.`
- Columnas no negociables salvo confirmacion explicita del usuario.
- Nombres de HU (HU-NN) provienen de la planificacion Notion del proyecto.
- Formato individual de Pruebas Unitarias (ficha detallada) solo para modulos criticos; default es formato grupal.
- El año `2026` es siempre el ano de elaboracion de la tesis. No cambiar.
- Listado de autores: separados con `y` para el ultimo; si 3+, comas entre los primeros y `y` antes del ultimo.
