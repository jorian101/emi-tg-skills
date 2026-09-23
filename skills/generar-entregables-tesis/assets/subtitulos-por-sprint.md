# Mapeo 1:1 Sprint a seccion marco-practico.md

Mapeo estricto 1:1 (definitivo, sin asimetria). Sprint N = seccion 3.4.N+1 (Sprint 0 = 3.4.1).

| Sprint | Seccion | Tema                                   |
| ------ | ------- | -------------------------------------- |
| 0      | 3.4.1   | Construccion general de bases de datos |
| 1      | 3.4.2   | Gestion de usuarios                    |
| 2      | 3.4.3   | Gestion del corpus juridico            |
| 3      | 3.4.4   | Motor de recuperacion                  |
| 4      | 3.4.5   | Gestion de expedientes                 |
| 5      | 3.4.6   | Motor de contexto                      |
| 6      | 3.4.7   | Generacion de respuestas juridicas     |

## Estructura por sprint (numeracion `3.4.X.Y` con doble nivel)

Nota para el agente:

- SIEMPRE debe haber un H1 para la subseccion y un H2 para cada Figura/Tabla.
- **Una Figura = una sola imagen**: prohibido agrupar varias imagenes bajo el mismo numero. Cada mockup y cada script de codigo es su propia Figura con numero y `Nota.` propios. No hay sufijos `a/b/c`.
- Las Figuras de mockup se titulan `Figura N: Mockup de ...`. Las de codigo, `Figura N: Script de ...`. Las capturas reales de la Revision, `Figura N: [Interfaz en Funcionamiento]`.
- Los numeros de Figura son **secuenciales y consecutivos** dentro de cada sprint. Cuando la cantidad de interfaces o de scripts pueda variar, se ocupa cada uno su propia Figura en orden logico, renumerando hacia abajo las Tablas que vengan despues.
- La Revision del Sprint ya NO lleva Tabla: va bajo la misma seccion `Revision del Sprint` pero solo con Figuras de captura real del asistente, una por cada interfaz seleccionada en los mockups de ese sprint.

La flecha `->` en este archivo es solo guia visual; en el `.md` real del vault se ponen en lineas separadas.

### Sprint 0 - 3.4.1

```
# 3.4.1.1. Construccion de la Base de Datos Relacional
## Figura 46: Diagrama Entidad-Relacion
## Figura 47: Modelo Entidad-Relacion
## Figura 48: Esquema de la Base de Datos Relacional
# 3.4.1.2. Construccion de la Base de Datos Vectorial
## Figura 49: Diagrama de Componentes de la Base de Datos Vectorial
## Tabla 36: Parametros del Indice Vectorial
## Tabla 37: Esquema de Metadatos
## Figura 50: Colecciones de la Base de Datos Vectorial
```

### Sprint 1 - 3.4.2

```
# 3.4.2.1. Planificacion del Sprint 1
## Tabla 38: Planificacion del Sprint 1
# 3.4.2.2. Analisis del Proceso
## Figura 51: Diagrama de Caso de Uso Expandido de la Gestion de Usuarios
# 3.4.2.3. Diseno del Proceso
## Figura 52: Diagrama de Actividades de la Gestion de Usuarios
# 3.4.2.4. Diseno de Interfaz del Modulo
## Figura 53: Mockup de Inicio de Sesion
## Figura 54: Mockup de Gestion de Usuarios
# 3.4.2.5. Codificacion del Modulo
## Figura 55: Script del Servicio de Autenticacion
## Figura 56: Script del Servicio de Creacion de Usuarios
# 3.4.2.6. Pruebas Unitarias
## Tabla 39: Pruebas Unitarias de la Gestion de Usuarios
# 3.4.2.7. Revision del Sprint 1
## Figura 57: Inicio de Sesion en Funcionamiento
## Figura 58: Gestion de Usuarios en Funcionamiento
# 3.4.2.8. Retrospectiva del Sprint 1
## Tabla 40: Retrospectiva del Sprint 1
```

### Sprint 2 - 3.4.3

```
# 3.4.3.1. Planificacion del Sprint 2
## Tabla 41: Planificacion del Sprint 2
# 3.4.3.2. Analisis del Proceso
## Figura 59: Diagrama de Caso de Uso Expandido de la Gestion del Corpus Juridico
# 3.4.3.3. Diseno del Proceso
## Figura 60: Diagrama de Actividades de la Gestion del Corpus Juridico
# 3.4.3.4. Diseno de Interfaz del Modulo
## Figura 61: Mockup de Carga de Documentos del Corpus
## Figura 62: Mockup de Listado de Normas Indexadas
# 3.4.3.5. Codificacion del Modulo
## Figura 63: Script de la Validacion de Carga
## Figura 64: Script de la Indexacion del Corpus
# 3.4.3.6. Pruebas Unitarias
## Tabla 42: Pruebas Unitarias de la Indexacion del Corpus Juridico
# 3.4.3.7. Pruebas de Integracion
## Tabla 43: Pruebas de Integracion de la Indexacion del Corpus Juridico
# 3.4.3.8. Revision del Sprint 2
## Figura 65: Carga de Documentos en Funcionamiento
## Figura 66: Listado de Normas Indexadas en Funcionamiento
# 3.4.3.9. Retrospectiva del Sprint 2
## Tabla 44: Retrospectiva del Sprint 2
# 3.4.3.10. Analisis de Errores en Indexacion
## Tabla 45: Analisis de Errores en Indexacion
```

### Sprint 3 - 3.4.4

```
# 3.4.4.1. Planificacion del Sprint 3
## Tabla 46: Planificacion del Sprint 3
# 3.4.4.2. Analisis del Proceso
## Figura 67: Diagrama de Caso de Uso Expandido del Motor de Recuperacion
# 3.4.4.3. Diseno del Proceso
## Figura 68: Diagrama de Secuencia del Motor de Recuperacion
# 3.4.4.4. Diseno de Interfaz del Modulo
## Figura 69: Mockup de la Consulta
## Figura 70: Mockup del Historial de Consultas
# 3.4.4.5. Codificacion del Modulo
## Figura 71: Script de la Busqueda Hibrida
## Figura 72: Script del Orquestador del Pipeline de Recuperacion
## Figura 73: Script de la Recuperacion de Contexto
# 3.4.4.6. Pruebas Unitarias
## Tabla 47: Pruebas Unitarias del Motor de Recuperacion
# 3.4.4.7. Pruebas de Integracion
## Tabla 48: Pruebas de Integracion del Motor de Recuperacion
# 3.4.4.8. Revision del Sprint 3
## Figura 74: Interfaz de Consulta en Funcionamiento
## Figura 75: Interfaz de Historial de Consultas en Funcionamiento
# 3.4.4.9. Retrospectiva del Sprint 3
## Tabla 49: Retrospectiva del Sprint 3
# 3.4.4.10. Analisis de Errores en Recuperacion
## Tabla 50: Analisis de Errores en Recuperacion
```

### Sprint 4 - 3.4.5

```
# 3.4.5.1. Planificacion del Sprint 4
## Tabla 51: Planificacion del Sprint 4
# 3.4.5.2. Analisis del Proceso
## Figura 76: Diagrama de Caso de Uso Expandido de la Gestion de Expedientes
# 3.4.5.3. Diseno del Proceso
## Figura 77: Diagrama de Actividades de la Gestion de Expedientes
## Figura 78: Diagrama de Secuencia de la Gestion de Expedientes
# 3.4.5.4. Diseno de Interfaz del Modulo
## Figura 79: Mockup de Gestion de Expedientes
## Figura 80: Mockup del Historial de Conversaciones
# 3.4.5.5. Codificacion del Modulo
## Figura 81: Script del Servicio de Expedientes
## Figura 82: Script del Servicio de Obra
# 3.4.5.6. Pruebas Unitarias
## Tabla 52: Pruebas Unitarias de la Gestion de Expedientes
# 3.4.5.7. Pruebas de Integracion
## Tabla 53: Pruebas de Integracion de la Gestion de Expedientes
# 3.4.5.8. Revision del Sprint 4
## Figura 83: Interfaz de Gestion de Expedientes en Funcionamiento
## Figura 84: Interfaz del Historial de Conversaciones en Funcionamiento
# 3.4.5.9. Retrospectiva del Sprint 4
## Tabla 54: Retrospectiva del Sprint 4
```

### Sprint 5 - 3.4.6

```
# 3.4.6.1. Planificacion del Sprint 5
## Tabla 55: Planificacion del Sprint 5
# 3.4.6.2. Analisis del Proceso
## Figura 85: Diagrama de Caso de Uso Expandido del Motor de Contexto
# 3.4.6.3. Diseno del Proceso
## Figura 86: Diagrama de Actividades del Motor de Contexto
## Figura 87: Diagrama de Secuencia del Motor de Contexto
# 3.4.6.4. Diseno de Interfaz del Modulo
## Figura 88: Mockup de la Visualizacion del Contexto Recuperado
# 3.4.6.5. Codificacion del Modulo
## Figura 89: Script de la Expansion Jerarquica del Contexto
## Figura 90: Script del Evaluador de Visibilidad
# 3.4.6.6. Pruebas Unitarias
## Tabla 56: Pruebas Unitarias del Motor de Contexto
# 3.4.6.7. Pruebas de Integracion
## Tabla 57: Pruebas de Integracion del Motor de Contexto
# 3.4.6.8. Revision del Sprint 5
## Figura 91: Interfaz de Visualizacion del Contexto Recuperado en Funcionamiento
# 3.4.6.9. Retrospectiva del Sprint 5
## Tabla 58: Retrospectiva del Sprint 5
# 3.4.6.10. Analisis de Errores en Contexto
## Tabla 59: Analisis de Errores en Contexto
```

### Sprint 6 - 3.4.7

```
# 3.4.7.1. Planificacion del Sprint 6
## Tabla 60: Planificacion del Sprint 6
# 3.4.7.2. Analisis del Proceso
## Figura 92: Diagrama de Caso de Uso Expandido de la Generacion de Respuestas Juridicas
# 3.4.7.3. Diseno del Proceso
## Figura 93: Diagrama de Secuencia de la Generacion de Respuestas Juridicas
# 3.4.7.4. Diseno de Interfaz del Modulo
## Figura 94: Mockup de la Visualizacion de Respuestas en Modo Dictamen
## Figura 95: Mockup de la Visualizacion de Respuestas en Modo Auto de Vista
# 3.4.7.5. Codificacion del Modulo
## Figura 96: Script del Resolvedor de Plantillas
## Figura 97: Script del Cliente del Modelo de Lenguaje
# 3.4.7.6. Pruebas Unitarias
## Tabla 61: Pruebas Unitarias del Modulo Generador de Respuestas Juridicas
# 3.4.7.7. Pruebas de Integracion
## Tabla 62: Pruebas de Integracion del Modulo Generador de Respuestas Juridicas
# 3.4.7.8. Revision del Sprint 6
## Figura 98: Interfaz de Visualizacion de Respuestas en Modo Dictamen en Funcionamiento
## Figura 99: Interfaz de Visualizacion de Respuestas en Modo Auto de Vista en Funcionamiento
# 3.4.7.9. Retrospectiva del Sprint 6
## Tabla 63: Retrospectiva del Sprint 6
# 3.4.7.10. Analisis de Errores en Generacion
## Tabla 64: Analisis de Errores en Generacion
```

## Mapeo de archivos del vault

- `diagramas/`: `.md` con bloques Graphviz (`.dot`) o PlantUML (`.puml`) + `.png` renderizado.
- `tablas/`: `.md` con tablas markdown + `Nota.`
- `capturas/`: `.md` con Figura + `.png` generado por Silicon con fondo blanco.
- `mockups/`: `.md` + `.html` + `.fig` + `.png`; el HTML es la fuente, el `.fig` es el documento editable validado por OpenPencil y el PNG se captura con Playwright.
- `revision/`: `.md` con Figuras de captura real del asistente en funcionamiento + `.png`.
- `sprint-X-entregables.docx`: Archivo Word resultante, untracked, guardado en la raiz de la carpeta del sprint.

## Notas

- En el Word real, "Análisis de Errores" NO lleva subtitulo H4 propio: va directo despues de la Retrospectiva, con su parrafo introductorio y su tabla (solo Sprints 2, 3, 5, 6). La numeracion `3.4.X.10` del H1 en el `.md` es interna (frontmatter/orden), no se muestra como subtitulo en el Word. La tabla de Acciones Correctivas fue eliminada del marco practico; no generarla.
- Sprint 4 NO tiene analisis de errores (es gestion de expedientes, no RAG).
- Los mockups van en carpeta `mockups/` pero se incluyen en el Word como cualquier Figura (no excluir).
- Sprint 0: orden logico de generacion es Modelo E-R primero (ChartDB), DER conceptual despues (Graphviz) — ver Hard Rule 19.
- Las Tablas de Revision (antiguas `Tabla N: Revision del Sprint`) fueron **eliminadas**. Su lugar lo ocupan las Figuras de captura real de la Revision. La numeracion de Tablas se ajusto: a partir de Sprint 2 todas las tablas posteriores bajaron un numero porque ya no hay tabla de Revision.
- Las Tablas de Acciones Correctivas fueron **eliminadas** del marco practico; la numeracion de Tablas se ajusto a la real (S3: 46-50, S4: 51-54, S5: 55-59, S6: 60-64).
- El titulo del sprint en el Word real usa "Planificacion de Sprint 5" (sin "del") solo en Sprint 5; en el resto "Planificacion del Sprint N". Seguir el Word.
