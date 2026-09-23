# Patron canonico de redaccion de entregables (Sin choque de titulos)

## Verbos permitidos para casos de uso (OBLIGATORIO — leer primero)

Los labels de los `usecase` en los diagramas de caso de uso expandido deben usar **solo** estos verbos de accion, en castellano, sin parentesis ni tecnicismos. En la base de datos nunca se elimina un registro; cuando un caso podria "eliminar" o "inhabilitar", se usa **"Cambiar Estado de Cuenta"** (el registro se marca inactivo, no se borra). Esta tabla tambien aplica a labels de nodos de actividades y mensajes de secuencia.

### Permitidos

| Verbo                       | Uso tipico                                             |
| --------------------------- | ------------------------------------------------------ |
| `Iniciar Sesion`            | Autenticacion.                                         |
| `Cerrar Sesion`             | Logout.                                                |
| `Crear Usuario`             | Alta de usuario.                                       |
| `Crear Norma`               | Carga e indexación de una norma del corpus.            |
| `Listar Usuarios`           | Listado.                                               |
| `Listar Normas`             | Listado de normas registradas.                         |
| `Modificar Rol`             | Cambio de rol/perfil.                                  |
| `Cambiar Estado de Cuenta`  | Activar/inactivar (nunca "inhabilitar" ni "eliminar"). |
| `Restablecer Contrasena`    | Reset password forzado por admin.                      |
| `Consultar`                 | Consultar Historial, Consultar Obra.                   |
| `Consultar Fragmentos`      | Inspección de fragmentos del corpus.                   |
| `Ver`                       | Ver Estado de Indexacion, Ver Expediente.              |
| `Ver Integridad del Corpus` | Comprobación de consistencia del corpus.               |

### Prohibidos (sinonimos o fuera)

Gestionar, Administrar, Evaluar, Recuperar, Validar, Forzar, Cerrar (sesion si), Realizar, Clasificar, Generar, Ajustar, Resolver, Seleccionar, Editar, Publicar, Sugerir, Extraer, Monitorear, Reconciliar, Indexar, Inhabilitar, Eliminar, Borrar, Tramitar, Manejar, Valorar, Conducir, Refrescar, Resetear, y cualquier sinonimo de los anteriores.

### Reglas para los labels

- Verbo en castellano, capitalizado la primera letra. Sin `\n(login)`, `\n(logout)`, `(Regla N)`, `[Diseno]`, sin parentesis de ningun tipo.
- Mantener tildes y ñ en los labels de `.puml` y `.dot`, además de la prosa del documento.
- Sin tecnicismos: `Refrescar Access Token` -> `Iniciar Sesion` (el refresco es detalle interno). `Reranking HTTP (bge-reranker)` -> no se modela como caso de uso.
- Un caso de uso = una funcionalidad de negocio discreta, no un paso tecnico interno.

> **Referencia cruzada**: ver `assets/plantillas-puml.md` para plantillas canonicas PlantUML completas con paleta institucional, tipografia Georgia y `linetype ortho`.

---

## Tono obligatorio: presente

Toda la redaccion de los entregables va en **presente** del indicativo, sin excepcion. Esto incluye verbos principales, auxiliares y participios.

## Uso de tildes (acentuacion ortografica) — OBLIGATORIO

La redaccion de los entregables usa **acentuacion ortografica correcta del espanol**. Todas las tildes van donde corresponde: agudas terminadas en vocal/n/s, llanas que NO terminan en vocal/n/s, esdrujulas y sobresdrujulas siempre, diacriticas en monosilabos (él, tú, mí, sí, dé, sé, más, aún, qué, cuál, cuándo, dónde, cómo, cuánto, quién).

**Prohibido escribir sin tildes** ("se disena", "se creo", "codigo", "util"). Ejemplos obligatorios:

| Sin tilde (PROHIBIDO) | Con tilde (OBLIGATORIO)          |
| --------------------- | -------------------------------- |
| se disena             | se diseña                        |
| se creo               | se creó / se crea (segun tiempo) |
| se configuro          | se configuró / se configura      |
| gestion               | gestión                          |
| codigo                | código                           |
| util                  | útil                             |
| pagina                | página                           |
| numero                | número                           |
| construccion          | construcción                     |
| analisis              | análisis                         |
| el / tu (pronombre)   | él / tú                          |

Verificar en la revision final (Paso 7 de Execution Steps) que no queden palabras sin tilde que lo requieran. Nota: este asset de la skill se mantiene sin tildes para ser legible en terminal; los ENTREGABLES (`.md` y Word) SI llevan tildes.

### Tabla de sustituciones (pasado → presente)

| NO usar (pasado / futuro)       | SI usar (presente)      |
| ------------------------------- | ----------------------- |
| se diseño                       | se diseña               |
| se creó                         | se crea                 |
| se configuró                    | se configura            |
| se implementó                   | se implementa           |
| se desplegó                     | se despliega            |
| se ejecutó                      | se ejecuta              |
| se definió                      | se define               |
| se realizó                      | se realiza              |
| se obtuvo                       | se obtiene              |
| se almacenó                     | se almacena             |
| se persistió                    | se persiste             |
| se procesó                      | se procesa              |
| se registró                     | se registra             |
| se generó                       | se genera               |
| se devolvió                     | se devuelve             |
| se recibió                      | se recibe               |
| se envió                        | se envía                |
| fue implementado                | se implementa           |
| fueron creados                  | se crean                |
| participó / participaron        | participa / participan  |
| fue usado / fueron usados       | se usa / se usan        |
| sirvió para / sirvieron para    | sirve para              |
| permitió obtener                | permite obtener         |
| permitió generar                | permite generar         |
| fue necesario                   | es necesario            |
| resultó útil                    | resulta útil            |
| será implementado / será creado | se implementa / se crea |

### Excepcion valida

Pasado solo cuando narras un **evento puntual ya cerrado y no recurrente**. En este proyecto NO aplica porque toda la documentacion describe el sistema vigente (Sprint 0 ya deployado, codigo en uso).

Ejemplos invalidos: "se diseno el Sprint 0", "se crearon las tablas en marzo", "el sprint finalizo el 15 de julio".
Ejemplos validos (presente): "se disena el modelo relacional", "se crean las tablas usuario y expediente", "el sprint se ejecuta durante 5 dias habiles".

## Estructura canonica de cada entregable

Patron de UN SOLO parrafo por entregable (alineado al Word real de BACKUP TG). No existe parrafo intro de seccion separado ni frase "En la Figura N, se..." duplicada.

```markdown
---
sprint: X
entregable: [titulo]
fuente: codigo | tesis
categoria_tesis: diagramas | tablas | capturas | mockups
marco_practico_seccion: "3.4.X.Y"
---

# 3.4.X.Y. [Titulo de la subseccion H1]

[PARRAFO UNICO - OBLIGATORIO. Comienza con la referencia a la Figura/Tabla e integra la descripcion del contenido:
"En la Figura N se [verbo] [descripcion breve del contenido]." o "En la Tabla N se [verbo] [descripcion breve del contenido]."
Luego 1-3 oraciones mas que describen el desarrollo concreto del sprint: que se disena, que se crea, que se configura.
NO definiciones de teoria, NO citas de autores, NO rutas de archivos, NO repeticion de la intro del sprint.]

[FIGURA:] ![nombre.png](nombre.png){ width=15cm }

## Figura N: [Titulo de la Figura] <- DESPUES de la imagen (debajo)

[TABLA:] ## Tabla N: [Titulo de la Tabla] <- antes de la tabla (arriba)
[tabla markdown]

[Solo tablas de pruebas: "Fecha de ejecucion: YYYY-MM-DD." justo debajo del titulo H2, antes de la tabla.]

Nota. [descripcion]. Elaboracion propia con base en [Autor1 (Ano), Autor2 (Ano), ...], 2026.
```

## Regla para el contexto bajo subtitulos

El parrafo unico ubicado inmediatamente debajo de cada subtitulo (H1) debe hablar del **desarrollo concreto del entregable**. NO incluye:

- Definiciones de conceptos (eso va en marco teorico)
- Explicaciones de "que es una BD relacional" / "que es HNSW" / "que es UML"
- Historia del estandar o de la herramienta
- Citas de autores o referencias teoricas (Chen, OMG, Pressman, etc.)
- Comparaciones entre alternativas
- Repeticion de la intro del sprint (dias habiles, fechas, panorama general)

SI incluye:

- Descripcion de lo que se hace y la herramienta usada
- Decisiones tomadas (por que X y no Y), en lenguaje natural
- Referencia a la Figura/Tabla y su contenido concreto

## Reglas de redaccion global (OBLIGATORIAS)

Aplican a TODA redaccion textual de entregables: parrafo intro H1/H2, frase `En la Figura/Tabla N, se...` y `Nota.`. Tambien a nodos de diagramas (`.puml`), labels y mensajes.

- **Sin rutas de archivos**: prohibido `backend/src/...`, `/asistente/...`, `application/auth/`, `Asistente.tsx`, etc. Describir en lenguaje natural.
- **Sin parentesis** (solo numeracion `3.4.X.Y`). La explicacion debe ser fluida sin recurrir a parentesis. Prohibido `Iniciar Sesion (login)`, `[Regla 4]`, `(skeleton)`, `HTTP 409`, `(m=16)`.
- **Sin citas a Reglas de seguridad**: prohibido "Regla 2", "Regla 4", "Regla 7", "filtro de privacidad", etc. La seguridad se asume; no se menciona en los entregables.
- **Menos tecnicismo**: describir la herramienta usada y lo que se hace, evitando nombres de variables largos (`TrazabilidadPipeline`, `usuario_id`, `ix_usuario_carnet`), siglas internas, flags HTTP y nombres de indices. Mencionar la herramienta o la accion esta bien; no meter identificadores de codigo.
- **Sin ingles de mas**: preferir el castellano. `login` -> `inicio de sesion`, `logout` -> `cierre de sesion`, `upload` -> `carga`, `dashboard` -> `panel`, `done`/`Done` -> `Hecho`, `Estado: Done` -> `Estado: Hecho`, `naming` -> `denominacion`, `core` -> `nucleo`, `chat` -> `conversacion`, `workspace` -> `espacio de trabajo`. **PROHIBIDA cualquier palabra en ingles en el cuerpo del Word y en las celdas de tablas** (incluidos los estados de planificacion). Solo se conservan terminos tecnicos sin traduccion acceptada (Qdrant, PostgreSQL, JWT, HNSW) y los nombres de herramientas (Docker, FastAPI, Playwright). El estado de una tarea en la tabla de planificacion SIEMPRE es `Hecho` en castellano, nunca `Done`.
- **Sin** las palabras "sistema", "aplicacion", "app" (u otros equivalentes). Si hay que nombrar al producto, usar **"asistente"**. Mejor aun si no se nombra y se redacta en voz pasiva refleja ("se disena", "se crea").
- **Escritura correcta**: tildes siempre (`se diseña`, `código`, `gestión`, `útil`, `página`, `número`, `construcción`, `análisis`) y **ñ** donde corresponda (`diseño`, `señal`, `extraña`). Prohibido `se disena`, `codigo`, `util`. El asset de la skill se mantiene sin tildes para legibilidad en terminal; los ENTREGABLES (`.md` y Word) SI llevan tildes y ñ.
- **Solo** `En la Figura N, se...` / `En la Tabla N, se...`. Prohibido `En la captura`, `En la imagen`. Toda foto, mockup o script es una Figura.
- **Anti-redundancia (OBLIGATORIO)**: cada entregable tiene UN SOLO parrafo introductorio que integra la referencia a la Figura/Tabla con la descripcion del contenido (Hard Rule 10 del SKILL.md). NO se repite la intro del sprint en cada entregable: la intro del sprint describe el panorama y NO menciona dias habiles ni fechas (eso va solo en el parrafo de la Tabla de Planificacion). Si dos parrafos del mismo sprint repiten la misma idea (misma frase reescrita), reformular uno. Regla: un concepto se describe UNA sola vez por sprint; el resto del texto avanza. Verificar con una lectura corrida del `.md` antes de ensamblar el Word.
- **Puntualidad y extension**: los parrafos introductorios son cortos (1-3 oraciones) y van al grano. Sin relleno, sin frases generales vacias ("este componente es fundamental para el sistema"). Si una descripcion ocupa mas de 5 lineas, simplificarla.
- **Lector no tecnico (OBLIGATORIO)**: el lector es un jurado academico, no un desarrollador. Se describe QUE se construyo y QUE hace cada pieza en lenguaje llano apoyandose en el marco teorico (el cap. 2 explica los conceptos; el marco practico NO repite esas definiciones). Nombres de herramientas y tecnologias se mencionan como tales (se usa PostgreSQL, Qdrant, FastAPI, Ollama) sin explicar que son ni como funcionan. Los detalles de implementacion (variables, flags, indices, queries) se omiten del cuerpo. Excepcion: la tabla de Analisis de Errores puede usar la columna `Componente Afectado` con ruta tecnica (unica columna permitida).

### Ejemplos validados por el usuario

Patron de UN SOLO parrafo: el parrafo unico comienza con la referencia a la Figura/Tabla e integra la descripcion del contenido concreto. El titulo de la Figura va DESPUES de la imagen; el de la Tabla antes de la tabla.

**Ejemplo 1 - der.md (Figura 46)**:

> "En la Figura 46 se presenta el modelo conceptual de la base de datos relacional del asistente legal. El diagrama se construye a partir de las migraciones Alembic que definen las entidades usuario, expediente, obra, norma, fragmento, borrador, espacio_trabajo, chat_privado, mensaje_chat y documento_chat, así como las veinte relaciones de clave foránea que conectan dichas entidades."
> (imagen) -> `## Figura 46: Diagrama Entidad-Relación` -> Nota.

**Ejemplo 2 - componentes-bd-vectorial.md (Figura 49)**:

> "En la Figura 49 se ilustra la arquitectura y persistencia vectorial que soporta el ciclo de recuperación del asistente legal. El diagrama de componentes expone los módulos de ingesta, embedding y recuperación que interactúan con la colección corpus_juridico de Qdrant, junto con las interfaces REST y de línea de comandos que exponen estas funcionalidades a los usuarios finales y a las tareas automatizadas. El operador jurídico se representa como actor externo al asistente, mientras que las bases de datos PostgreSQL y Qdrant se modelan como nodos de persistencia diferenciados de los módulos aplicativos."
> (imagen) -> `## Figura 49: Diagrama de Componentes de la Base de Datos Vectorial` -> Nota.

**Ejemplo 3 - parametros-indice-vectorial.md (Tabla 36)**:

> "En la Tabla 36 se detalla la configuración aplicada al índice HNSW de la colección corpus_juridico de Qdrant. Los parámetros de índice describen la estructura de navegación aproximada que el motor utiliza para resolver las búsquedas por vecinos más cercanos de manera eficiente en espacios de alta dimensionalidad, equilibrando la velocidad de recuperación con la calidad del resultado."
> `## Tabla 36: Parámetros del Índice Vectorial` -> (tabla) -> Nota.

## Regla para multiples imagenes en una misma Figura

Una Figura = una sola imagen (Hard Rule 24 del SKILL.md). Si un entregable produce N imagenes, cada una recibe su propio numero, su propio titulo y su propia `Nota.`. Nunca se agrupan varias imagenes bajo el mismo numero con el patron `a/b/c`.

## Formula del parrafo introductorio de Figura/Tabla

El parrafo unico del entregable comienza con:

`En la [Figura|Tabla] N, se [verbo] [descripcion breve].`

- Mayuscula inicial en `En`
- Punto final (no dos puntos)
- Verbo en **3ra persona singular, presente**
- Descripcion concisa (1 linea), seguida de 1-3 oraciones que describen el contenido concreto
- Verbos validos: presenta, muestra, resume, ilustra, detalla, visualiza, observan, recoge, detallan, consolida, documenta, analiza, expone, lista, contiene

### Selector heuristico

| Verbo                  | Cuando usar                                         |
| ---------------------- | --------------------------------------------------- |
| `presenta`             | default; introduce cualquier Figura/Tabla           |
| `muestra`              | capturas de pantalla, esquemas fisicos, mockups     |
| `ilustra`              | diagramas conceptuales (DER, componentes)           |
| `detalla`              | tablas con parametros/estructuras tecnicas          |
| `resume`               | tablas resumen (revision, KPIs)                     |
| `visualiza`/`observan` | diagramas de procesos o vistas                      |
| `consolida`            | tablas retrospectivas, consolidaciones              |
| `recoge`               | tablas de analisis de errores                       |
| `expone`               | diagramas arquitectonicos (componentes, despliegue) |
| `lista`                | tablas de analisis de errores                       |
| `contiene`             | tablas de parametros de configuracion               |

## Reglas de capitalizacion (encabezados Word)

- **Palabra significativa**: primera letra mayuscula
- **Conectoras en minuscula**: `y`, `o`, `de`, `del`, `en`, `para`, `con`, `sin`, `a`, `por`, `el`, `la`, `los`, `las`, `un`, `una`
- **Sin parentesis** en encabezados (salvo numeros como "3.4.1.1.")
- **Sin abreviaturas**: "BD" solo si ya fue introducido; preferir "Base de Datos"

| Correcto                                      | Incorrecto                                    |
| --------------------------------------------- | --------------------------------------------- |
| `Diseno del Proceso`                          | `Diseno Del Proceso`                          |
| `Analisis del Proceso`                        | `Analisis Del Proceso (caso uso expandido)`   |
| `Pruebas Unitarias de la Gestion de Usuarios` | `Pruebas Unitarias de la gestion de usuarios` |

## Estilo de parrafo (3ra persona formal)

- **Voz pasiva refleja** en presente: "Se define", "Se procede", "Se evaluan", "Se recuperan"
- **Impersonal**: "El asistente implementa", "El asistente genera" (preferible a "el sistema" / "la aplicacion"). Mejor aun: voz pasiva sin sujeto.
- **Evitar 1ra/2da persona**: nunca "yo", "nosotros", "usted", "tu"
- **Oraciones**: 3-6 por parrafo introductorio; una idea por oracion
- **Verbos en presente** para todo estado actual

## Formato de Nota obligatoria

`Nota. [descripcion de que se muestra]. Elaboracion propia con base en [Autor1 (Ano), Autor2 (Ano), ...], 2026.`

- `Nota.` en linea nueva, separada del bloque anterior
- `Nota.` en **negrita** (Word: run con `bold=True` en el post-procesamiento)
- Punto final (no dos puntos)
- Lista de autores separada con `y` para el ultimo; si 3+, comas entre los primeros y `y` antes del ultimo
- Ano `2026` siempre (ano de elaboracion de la tesis)
- Variante con cita externa: `Tomado de Titulo (p. X), por Autor(es), Ano, Editorial.`
- Variante captura propia: `Elaboracion propia mediante [herramienta], 2026.`

> **Nota**: la tabla de verbos permitidos para casos de uso se movio al inicio de este archivo (seccion "Verbos permitidos para casos de uso (OBLIGATORIO — leer primero)"). Ver tambien `assets/plantillas-puml.md` para plantillas canonicas PlantUML.

## Manejo del codigo fuente de diagramas en el Word

**Regla clave**: los bloques ` ```dot ` y ` ```plantuml ` que viven en el `.md` del vault **se embeben en el Word pero en una seccion aparte al final**, no en el cuerpo de cada Figura.

- En el cuerpo de cada Figura, el `.md` lleva el bloque fuente (porque permite regenerar el PNG)
- Al armar el Word con Pandoc, el codigo fuente se mueve a una seccion final titulada **"Codigo fuente de diagramas"** (sin numeracion Figura N)
- Esta seccion aparece DESPUES de la ultima Figura/Tabla del sprint
- Cada bloque fuente se asocia a su Figura mediante un H2 con el mismo titulo que la Figura (sin el prefijo "Figura N:")

Excepcion: los bloques ` ```bash ` con instrucciones para el usuario (ej. pasos de ChartDB en `modelo-entidad-relacion.md`) **SI se embeben en el cuerpo del Word** porque son instrucciones utiles, no fuente de diagramas.

```

```
