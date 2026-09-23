# Mapa de entregables: Figura/Tabla -> archivos + herramienta

Usado por el modo regenerar-selectivo para saber que archivos tocar cuando el usuario pide regenerar un entregable puntual.

## Reglas generales del mapa

- **Una Figura = una sola imagen**. Cero sufijos `a/b/c`. Si hay varias pantallas, varias Figuras.
- Cada mockup se titula `Figura N: Mockup de ...`.
- Cada script de codigo se titula `Figura N: Script de ...`.
- Las capturas de la Revision del Sprint se titulan `Figura N: [Interfaz] en Funcionamiento`.
- Mockups con **HTML/CSS + OpenPencil** (`.html` -> `.fig` validado -> `.png` capturado con Playwright). Capturas de codigo con **Silicon** fondo blanco. Capturas de Revision con **live browser de impeccable** (o Playwright).
- La Revision del Sprint ya NO lleva Tabla: son Figuras de captura real, una por cada interfaz seleccionada en los mockups de ese sprint.
- Las Tablas que llevaban numeracion de Revision desaparecen; las tablas siguientes se renumeran (ver `assets/subtitulos-por-sprint.md` que tiene los numeros finales).

## Sprint 0 - 3.4.1

| Entregable                     | Archivos                                                                                                                     | Herramienta                          | Notas                                                                                  |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------- |
| Figura 46 (DER Chen)           | `diagramas/der.md`, `diagramas/diagrama-entidad-relacion.png`, `diagramas/der.dot`                                           | Graphviz (Chen con cardinalidad 1/n) | El `.dot` es la fuente, se renderiza a PNG con `neato -Tpng`                           |
| Figura 47 (Modelo E-R fisico)  | `diagramas/modelo-entidad-relacion.md`, `sprints/sprint-0/assets/chartdb_diagram.json`                                       | ChartDB (visor, no export)           | El `.md` lleva pasos ChartDB; el JSON es el input reproducible. No hay PNG automatico. |
| Figura 48 (Esquema BD captura) | `capturas/esquema-bd-relacional.md`, `capturas/esquema-bd-relacional.png`                                                    | Captura propia del usuario (psql)    | La skill NO genera el PNG. Si no existe, omitir o placeholder.                         |
| Figura 49 (Componentes UML)    | `diagramas/componentes-bd-vectorial.md`, `diagramas/componentes-bd-vectorial.png`, `diagramas/componentes-bd-vectorial.puml` | PlantUML (component UML 2)           | `.puml` es la fuente                                                                   |
| Tabla 36 (Parametros HNSW)     | `tablas/parametros-indice-vectorial.md`                                                                                      | Markdown                             | Sin imagen                                                                             |
| Tabla 37 (Esquema Metadatos)   | `tablas/esquema-metadatos-vectorial.md`                                                                                      | Markdown                             | Sin imagen                                                                             |
| Figura 50 (Qdrant dashboard)   | `capturas/README.md`, `capturas/colecciones-bd-vectorial.png`                                                                | Captura propia del usuario           | Igual que Figura 48                                                                    |

## Sprint 1 - 3.4.2

| Entregable                                                    | Archivos                                                                                                                                             | Herramienta                                        |
| ------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------- |
| Tabla 38 (Planificacion Sprint 1)                             | `tablas/planificacion-sprint-1.md`                                                                                                                   | Markdown                                           |
| Figura 51 (Caso de Uso Expandido)                             | `diagramas/caso-uso-gestion-usuarios.md`, `diagramas/caso-uso-gestion-usuarios.png`, `diagramas/caso-uso-gestion-usuarios.puml` (opcional `.drawio`) | PlantUML (usecase verbos permitidos) **o draw.io** |
| Figura 52 (Actividades)                                       | `diagramas/actividades-gestion-usuarios.md`, `diagramas/actividades-gestion-usuarios.png`, `diagramas/actividades-gestion-usuarios.puml`             | PlantUML (activity recortado)                      |
| Figura 53 (Mockup de Inicio de Sesion)                        | `mockups/mockup-inicio-sesion.md`, `.html`, `.fig`, `.png`                                                                                           | HTML/CSS + OpenPencil CLI                          |
| Figura 54 (Mockup de Gestion de Usuarios)                     | `mockups/mockup-gestion-usuarios.md`, `.html`, `.fig`, `.png`                                                                                        | HTML/CSS + OpenPencil CLI                          |
| Figura 55 (Script de Autenticacion)                           | `capturas/snippet-autenticacion.md`, `capturas/snippet-autenticacion.png`                                                                            | Silicon fondo blanco                               |
| Figura 56 (Script de Creacion de Usuarios)                    | `capturas/snippet-creacion-usuarios.md`, `capturas/snippet-creacion-usuarios.png`                                                                    | Silicon fondo blanco                               |
| Tabla 39 (Pruebas Unitarias)                                  | `tablas/pruebas-unitarias-sprint-1.md`                                                                                                               | Markdown                                           |
| Figura 57 (Interfaz de Inicio de Sesion en Funcionamiento)    | `revision/inicio-sesion-funcionamiento.md`, `revision/inicio-sesion-funcionamiento.png`                                                              | Live browser impeccable                            |
| Figura 58 (Interfaz de Gestion de Usuarios en Funcionamiento) | `revision/gestion-usuarios-funcionamiento.md`, `revision/gestion-usuarios-funcionamiento.png`                                                        | Live browser impeccable                            |
| Tabla 40 (Retrospectiva Kerth)                                | `tablas/retrospectiva-sprint-1.md`                                                                                                                   | Markdown (4 columnas)                              |

## Sprint 2 - 3.4.3

| Entregable                                                    | Archivos                                                                              | Herramienta                             |
| ------------------------------------------------------------- | ------------------------------------------------------------------------------------- | --------------------------------------- |
| Tabla 41 (Planificacion)                                      | `tablas/planificacion-sprint-2.md`                                                    | Markdown                                |
| Figura 59 (Caso de Uso)                                       | `diagramas/caso-uso-gestion-corpus-juridico.md`, `.png`, `.puml` (opcional `.drawio`) | PlantUML (usecase verbos) **o draw.io** |
| Figura 60 (Actividades)                                       | `diagramas/actividades-gestion-corpus-juridico.md`, `.png`, `.puml`                   | PlantUML (activity recortado)           |
| Figura 61 (Mockup de Carga de Documentos)                     | `mockups/mockup-carga-documentos.md`, `.html`, `.fig`, `.png`                         | HTML/CSS + OpenPencil CLI               |
| Figura 62 (Mockup de Listado de Normas)                       | `mockups/mockup-listado-normas.md`, `.html`, `.fig`, `.png`                           | HTML/CSS + OpenPencil CLI               |
| Figura 63 (Script de Validacion de Carga)                     | `capturas/snippet-validacion-carga.md`, `.png`                                        | Silicon fondo blanco                    |
| Figura 64 (Script de Indexacion del Corpus)                   | `capturas/snippet-indexacion-corpus.md`, `.png`                                       | Silicon fondo blanco                    |
| Tabla 42 (Pruebas Unitarias)                                  | `tablas/pruebas-unitarias-sprint-2.md`                                                | Markdown                                |
| Tabla 43 (Pruebas Integracion)                                | `tablas/pruebas-integracion-sprint-2.md`                                              | Markdown                                |
| Figura 65 (Interfaz de Carga de Documentos en Funcionamiento) | `revision/carga-documentos-funcionamiento.md`, `.png`                                 | Live browser impeccable                 |
| Figura 66 (Interfaz de Listado de Normas en Funcionamiento)   | `revision/listado-normas-funcionamiento.md`, `.png`                                   | Live browser impeccable                 |
| Tabla 44 (Retrospectiva Kerth)                                | `tablas/retrospectiva-sprint-2.md`                                                    | Markdown (4 columnas)                   |
| Tabla 45 (Analisis de Errores en Indexacion)                  | `tablas/analisis-errores-indexacion.md`                                               | Markdown (sin Sprint/Tipo/Frecuencia)   |

## Sprint 3 - 3.4.4

| Entregable                                                       | Archivos                                                                         | Herramienta                             |
| ---------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------- |
| Tabla 46 (Planificacion)                                         | `tablas/planificacion-sprint-3.md`                                               | Markdown                                |
| Figura 67 (Caso de Uso)                                          | `diagramas/caso-uso-motor-recuperacion.md`, `.png`, `.puml` (opcional `.drawio`) | PlantUML (usecase verbos) **o draw.io** |
| Figura 68 (Secuencia)                                            | `diagramas/secuencia-motor-recuperacion.md`, `.png`, `.puml`                     | PlantUML (sequence recortado)           |
| Figura 69 (Mockup de la Consulta)                                | `mockups/mockup-pantalla-consulta.md`, `.html`, `.fig`, `.png`                   | HTML/CSS + OpenPencil CLI               |
| Figura 70 (Mockup del Historial de Consultas)                    | `mockups/mockup-pantalla-historial.md`, `.html`, `.fig`, `.png`                  | HTML/CSS + OpenPencil CLI               |
| Figura 71 (Script de Busqueda Hibrida)                           | `capturas/snippet-busqueda-hibrida.md`, `.png`                                   | Silicon fondo blanco                    |
| Figura 72 (Script del Orquestador del Pipeline)                  | `capturas/snippet-orquestador-pipeline.md`, `.png`                               | Silicon fondo blanco                    |
| Figura 73 (Script de Recuperacion de Contexto)                   | `capturas/snippet-recuperacion-contexto.md`, `.png`                              | Silicon fondo blanco                    |
| Tabla 47 (Pruebas Unitarias)                                     | `tablas/pruebas-unitarias-sprint-3.md`                                           | Markdown                                |
| Tabla 48 (Pruebas Integracion)                                   | `tablas/pruebas-integracion-sprint-3.md`                                         | Markdown                                |
| Figura 74 (Interfaz de Consulta en Funcionamiento)               | `revision/pantalla-consulta-funcionamiento.md`, `.png`                           | Live browser impeccable                 |
| Figura 75 (Interfaz de Historial de Consultas en Funcionamiento) | `revision/pantalla-historial-funcionamiento.md`, `.png`                          | Live browser impeccable                 |
| Tabla 49 (Retrospectiva Kerth)                                   | `tablas/retrospectiva-sprint-3.md`                                               | Markdown (4 columnas)                   |
| Tabla 50 (Analisis de Errores en Recuperacion)                   | `tablas/analisis-errores-recuperacion.md`                                        | Markdown (sin Sprint/Tipo/Frecuencia)   |

## Sprint 4 - 3.4.5

| Entregable                                                             | Archivos                                                                  | Herramienta                             |
| ---------------------------------------------------------------------- | ------------------------------------------------------------------------- | --------------------------------------- |
| Tabla 51 (Planificacion)                                               | `tablas/planificacion-sprint-4.md`                                        | Markdown                                |
| Figura 76 (Caso de Uso)                                                | `diagramas/caso-uso-expedientes.md`, `.png`, `.puml` (opcional `.drawio`) | PlantUML (usecase verbos) **o draw.io** |
| Figura 77 (Actividades)                                                | `diagramas/actividades-expedientes.md`, `.png`, `.puml`                   | PlantUML (activity recortado)           |
| Figura 78 (Secuencia)                                                  | `diagramas/secuencia-expedientes.md`, `.png`, `.puml`                     | PlantUML (sequence recortado)           |
| Figura 79 (Mockup de Gestion de Expedientes)                           | `mockups/mockup-gestion-expedientes.md`, `.html`, `.fig`, `.png`          | HTML/CSS + OpenPencil CLI               |
| Figura 80 (Mockup del Historial de Conversaciones)                     | `mockups/mockup-historial-conversaciones.md`, `.html`, `.fig`, `.png`     | HTML/CSS + OpenPencil CLI               |
| Figura 81 (Script del Servicio de Expedientes)                         | `capturas/snippet-servicio-expedientes.md`, `.png`                        | Silicon fondo blanco                    |
| Figura 82 (Script del Servicio de Obra)                                | `capturas/snippet-servicio-obra.md`, `.png`                               | Silicon fondo blanco                    |
| Tabla 52 (Pruebas Unitarias)                                           | `tablas/pruebas-unitarias-sprint-4.md`                                    | Markdown                                |
| Tabla 53 (Pruebas Integracion)                                         | `tablas/pruebas-integracion-sprint-4.md`                                  | Markdown                                |
| Figura 83 (Interfaz de Gestion de Expedientes en Funcionamiento)       | `revision/gestion-expedientes-funcionamiento.md`, `.png`                  | Live browser impeccable                 |
| Figura 84 (Interfaz del Historial de Conversaciones en Funcionamiento) | `revision/historial-conversaciones-funcionamiento.md`, `.png`             | Live browser impeccable                 |
| Tabla 54 (Retrospectiva Kerth)                                         | `tablas/retrospectiva-sprint-4.md`                                        | Markdown (4 columnas)                   |

## Sprint 5 - 3.4.6

| Entregable                                                           | Archivos                                                                     | Herramienta                             |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------- |
| Tabla 55 (Planificacion)                                             | `tablas/planificacion-sprint-5.md`                                           | Markdown                                |
| Figura 85 (Caso de Uso)                                              | `diagramas/caso-uso-motor-contexto.md`, `.png`, `.puml` (opcional `.drawio`) | PlantUML (usecase verbos) **o draw.io** |
| Figura 86 (Actividades)                                              | `diagramas/actividades-motor-contexto.md`, `.png`, `.puml`                   | PlantUML (activity recortado)           |
| Figura 87 (Secuencia)                                                | `diagramas/secuencia-motor-contexto.md`, `.png`, `.puml`                     | PlantUML (sequence recortado)           |
| Figura 88 (Mockup de Visualizacion del Contexto)                     | `mockups/mockup-visualizacion-contexto.md`, `.html`, `.fig`, `.png`          | HTML/CSS + OpenPencil CLI               |
| Figura 89 (Script de Expansion Jerarquica del Contexto)              | `capturas/snippet-expansion-jerarquica.md`, `.png`                           | Silicon fondo blanco                    |
| Figura 90 (Script del Evaluador de Visibilidad)                      | `capturas/snippet-evaluador-visibilidad.md`, `.png`                          | Silicon fondo blanco                    |
| Tabla 56 (Pruebas Unitarias)                                         | `tablas/pruebas-unitarias-sprint-5.md`                                       | Markdown                                |
| Tabla 57 (Pruebas Integracion)                                       | `tablas/pruebas-integracion-sprint-5.md`                                     | Markdown                                |
| Figura 91 (Interfaz de Visualizacion del Contexto en Funcionamiento) | `revision/visualizacion-contexto-funcionamiento.md`, `.png`                  | Live browser impeccable                 |
| Tabla 58 (Retrospectiva Kerth)                                       | `tablas/retrospectiva-sprint-5.md`                                           | Markdown (4 columnas)                   |
| Tabla 59 (Analisis de Errores en Contexto)                           | `tablas/analisis-errores-contexto.md`                                        | Markdown (sin Sprint/Tipo/Frecuencia)   |

## Sprint 6 - 3.4.7

| Entregable                                                                    | Archivos                                                                            | Herramienta                             |
| ----------------------------------------------------------------------------- | ----------------------------------------------------------------------------------- | --------------------------------------- |
| Tabla 60 (Planificacion)                                                      | `tablas/planificacion-sprint-6.md`                                                  | Markdown                                |
| Figura 92 (Caso de Uso)                                                       | `diagramas/caso-uso-generacion-respuestas.md`, `.png`, `.puml` (opcional `.drawio`) | PlantUML (usecase verbos) **o draw.io** |
| Figura 93 (Secuencia)                                                         | `diagramas/secuencia-generacion-respuestas.md`, `.png`, `.puml`                     | PlantUML (sequence recortado)           |
| Figura 94 (Mockup de Visualizacion en Modo Dictamen)                          | `mockups/mockup-visualizacion-dictamen.md`, `.html`, `.fig`, `.png`                 | HTML/CSS + OpenPencil CLI               |
| Figura 95 (Mockup de Visualizacion en Modo Auto de Vista)                     | `mockups/mockup-visualizacion-auto-vista.md`, `.html`, `.fig`, `.png`               | HTML/CSS + OpenPencil CLI               |
| Figura 96 (Script del Resolvedor de Plantillas)                               | `capturas/snippet-resolvedor-plantillas.md`, `.png`                                 | Silicon fondo blanco                    |
| Figura 97 (Script del Cliente del Modelo de Lenguaje)                         | `capturas/snippet-cliente-llm.md`, `.png`                                           | Silicon fondo blanco                    |
| Tabla 61 (Pruebas Unitarias)                                                  | `tablas/pruebas-unitarias-sprint-6.md`                                              | Markdown                                |
| Tabla 62 (Pruebas Integracion)                                                | `tablas/pruebas-integracion-sprint-6.md`                                            | Markdown                                |
| Figura 98 (Interfaz de Visualizacion en Modo Dictamen en Funcionamiento)      | `revision/visualizacion-dictamen-funcionamiento.md`, `.png`                         | Live browser impeccable                 |
| Figura 99 (Interfaz de Visualizacion en Modo Auto de Vista en Funcionamiento) | `revision/visualizacion-auto-vista-funcionamiento.md`, `.png`                       | Live browser impeccable                 |
| Tabla 63 (Retrospectiva Kerth)                                                | `tablas/retrospectiva-sprint-6.md`                                                  | Markdown (4 columnas)                   |
| Tabla 64 (Analisis de Errores en Generacion)                                  | `tablas/analisis-errores-generacion.md`                                             | Markdown (sin Sprint/Tipo/Frecuencia)   |

## Notas generales

- Todos los `.md` siguen el patron canonico de `patrones-redaccion.md` (presente, 3ra persona formal, patron UN SOLO parrafo + Figura/Tabla + Nota., sin rutas/parentesis/Reglas, tildes y ñ). El titulo de la Figura va debajo de la imagen; el de la Tabla arriba de la tabla.
- Las tablas de Pruebas Unitarias e Integracion usan formato IEEE 829-2008 (LTC/LTPr) con `Fecha de ejecucion: YYYY-MM-DD.` debajo de su titulo H2 (ver `assets/plantillas-tablas.md` §2 y §3, y Hard Rule 42ter).
- Los `.dot`/`.puml` son la fuente del diagrama; el `.png` se regenera siempre que la fuente cambie.
- Los **Casos de Uso Expandido** pueden generarse con PlantUML (default) o con draw.io si el usuario lo pide ("con draw.io"). En draw.io la fuente es el `.drawio` (XML) y el `.png` se exporta con `drawio --export`. El `.puml` previo se preserva. Ver `assets/plantilla-drawio-caso-uso.md`.
- Los `.html` son la fuente estática del mockup, los `.fig` son los documentos editables validados por OpenPencil y los `.png` se capturan con Playwright desde el HTML. Los mockups usan `DESIGN.md` y los tokens CSS reales del frontend; nunca la paleta UML. Los PNG de capturas de codigo los genera Silicon con fondo blanco; los de Revision los genera el live browser de impeccable (o Playwright si esta instalado).
- Sprint 0: Figura 48 y Figura 50 son capturas propias del usuario (psql, Qdrant dashboard); la skill NO las genera.
- Las tablas de Revision del Sprint fueron **eliminadas**. Su lugar lo ocupan las Figuras de captura real bajo la seccion `revision/`.
- Las tablas de **Acciones Correctivas** fueron **eliminadas** del marco practico: no generarlas. La numeracion de Tablas esta alineada con el marco practico real (S2 termina en T45; S3: 46-50; S4: 51-54; S5: 55-59; S6: 60-64).
- Las Figuras de captura real de la Revision se titulan `Interfaz de [X] en Funcionamiento` (nunca "Pantalla"). Los archivos `revision/pantalla-*.md` conservan su nombre interno.
- La numeracion de Tablas cambio porque ya no hay tablas de Revision ni de Acciones Correctivas. Ver `assets/subtitulos-por-sprint.md` para los numeros finales definitivos.
- Los mockups son INMUTABLES: sus `.html/.fig/.png` no se regeneran ni modifican una vez cerrado el sprint (Hard Rule 30).
- El `.docx` se reensambla desde cero en cada regeneracion, no se parcha.
