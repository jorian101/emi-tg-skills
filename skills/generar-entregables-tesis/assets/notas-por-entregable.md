# Notas obligatorias por entregable (citas exactas)

## Sprint 0 - Citas exactas (confirmadas)

| Entregable                                   | Cita exacta                                                                                                                                                                                                                                                                                                       |
| -------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Figura 46 (DER)                              | `Nota. La figura presenta el modelo de base de datos relacional detallando tablas con sus respectivas claves. Elaboracion propia con base en Pressman (2010), Dominguez Chavez (2019), DORUD (2020), Centeno, Zambrano y Rodriguez (2020), Roma y Olivera (2020) y Voron (2023), 2026.`                           |
| Figura 47 (Modelo E-R)                       | Misma cita que Figura 46: `Nota. La figura presenta el modelo de base de datos relacional detallando tablas con sus respectivas claves. Elaboracion propia con base en Pressman (2010), Dominguez Chavez (2019), DORUD (2020), Centeno, Zambrano y Rodriguez (2020), Roma y Olivera (2020) y Voron (2023), 2026.` |
| Figura 48 (Esquema BD captura)               | `Nota. La figura muestra la estructura fisica de las tablas. Elaboracion propia mediante el cliente PostgreSQL 16, 2026.`                                                                                                                                                                                         |
| Figura 49 (Componentes BD Vectorial)         | `Nota. La figura muestra la arquitectura y persistencia vectorial. Elaboracion propia con base en T. Xiao y Zhu (2025), Burkov (2025), Alammar y Grootendorst (2024), Ozturk y Mesut (2024) y Jha, Anto y KK (2026), 2026.`                                                                                       |
| Tabla 36 (Parametros HNSW)                   | `Nota. La tabla detalla la configuracion del indice HNSW. Elaboracion propia con base en Ma et al. (2025), Oracle (2023), Ren, Doekemeijer, Apparao y Trivedi (2025) y Jha, Anto y KK (2026), 2026.`                                                                                                              |
| Tabla 37 (Esquema Metadatos)                 | `Nota. La tabla describe la estructura de metadatos asociados a los vectores. Elaboracion propia con base en Weaviate (2025) y Kimothi (2025), 2026.`                                                                                                                                                             |
| Figura 50 (Colecciones BD Vectorial captura) | Misma cita que Figura 49: `Nota. La figura muestra la arquitectura y persistencia vectorial. Elaboracion propia con base en T. Xiao y Zhu (2025), Burkov (2025), Alammar y Grootendorst (2024), Ozturk y Mesut (2024) y Jha, Anto y KK (2026), 2026.`                                                             |

## Sprints 1-6 - Citas por tipo de tabla Scrum

Ver `assets/plantillas-tablas.md` para las 6 plantillas con citas exactas:

- **Planificacion**: Menzinsky et al. (2016) y Satpathy (2013).
- **Pruebas Unitarias (IEEE 829-2008)**: IEEE (2008), Pressman (2010) y Myers (2011).
- **Pruebas de Integracion (IEEE 829-2008)**: IEEE (2008), Sommerville (2011), Myers (2011) y Pressman (2010).
- **Revision**: Schwaber y Sutherland (2020) y Satpathy (2013).
- **Retrospectiva**: Kerth (2001) solamente. NO citar Nelson en la nota de retrospectiva.
- **Analisis de Errores**: Mathieu et al. (2024).

## Sprints 1-6 - Citas para diagramas UML, Mockups y Capturas

| Diagrama                                         | Cita                                                                                                                                                                 |
| ------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Caso de Uso Expandido                            | `Nota. La figura ilustra el diagrama de caso de uso expandido del modulo. Elaboracion propia con base en OMG (2017), Sundaramoorthy (2022) y Unhelkar (2020), 2026.` |
| Actividades                                      | `Nota. La figura ilustra el flujo de actividades del proceso. Elaboracion propia con base en OMG (2017), Pressman (2010) y Sundaramoorthy (2022), 2026.`             |
| Secuencia                                        | `Nota. La figura ilustra la secuencia de interacciones entre componentes. Elaboracion propia con base en OMG (2017), Pressman (2010) y Sundaramoorthy (2022), 2026.` |
| Mockups (HTML/CSS + OpenPencil)                  | `Nota. La figura muestra el mockup de [nombre de la interfaz]. Elaboración propia con HTML/CSS y OpenPencil, 2026.`                                                  |
| Capturas de Codificacion (Silicon, fondo blanco) | `Nota. La figura muestra el script de [nombre del servicio o componente]. Elaboracion propia con Silicon, 2026.`                                                     |
| Capturas Reales de la Revision (impeccable)      | `Nota. La figura muestra el asistente en funcionamiento del modulo de [nombre]. Elaboracion propia, 2026.`                                                           |

## Sprints 1-6 - Citas para tablas Scrum (renumeradas)

Las tablas de Revision del Sprint fueron **eliminadas**. La numeracion de las tablas siguientes fue ajustada; ver `assets/subtitulos-por-sprint.md` y `assets/plantillas-tablas.md` para los numeros finales y las plantillas.

- **Planificacion**: Menzinsky et al. (2016) y Satpathy (2013).
- **Pruebas Unitarias (IEEE 829-2008)**: IEEE (2008), Pressman (2010) y Myers (2011).
- **Pruebas de Integracion (IEEE 829-2008)**: IEEE (2008), Sommerville (2011), Myers (2011) y Pressman (2010).
- **Retrospectiva (Kerth - The Original 4)**: Kerth (2001). Formato de la cita: `Nota. La tabla analiza la forma de trabajo del sprint a partir de las cuatro preguntas de Kerth. Elaboracion propia con base en Kerth (2001), 2026.` NO citar Nelson en la nota de retrospectiva.
- **Analisis de Errores**: Mathieu et al. (2024).

## Reglas

- No omitir el `Nota.`: bloqueante. Toda Figura y toda Tabla debe cerrar con su `Nota.`
- No inventar autores: si falta uno, PEDIR confirmacion al usuario antes de escribir.
- Ano `2026` siempre (ano de elaboracion de la tesis).
- `Nota.` en negrita en el Word final (post-procesamiento con `python-docx`: run con `bold=True`).
- Formato: `Nota. [descripcion]. Elaboracion propia con base en [citas], 2026.`
