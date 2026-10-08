---
title: Registro de informes de revisores
type: indice
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: []
tags:
  - revisores
  - informes
  - registro
---

# Registro de informes de revisores

> Material crudo en `sources/informes-revisores/<docente>/`. Esta tabla la mantiene
> `scripts/ingerir-informe.py` (idempotente por sha256). El `estado` es **derivado, no escrito a
> mano**: `procesado` = el perfil del docente ya cita su carpeta; `sin-texto` = el OCR no dejó
> texto utilizable; `pendiente` = falta destilar. `rol`/`tipo`/`estudiante` son best-effort desde
> el nombre del archivo.

| informe | docente | estudiante | rol | tipo | fecha | sha256 | fuente_texto | estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |

<!-- Esta tabla la llena `scripts/ingerir-informe.py`: NO agregar filas de ejemplo acá.
     Una fila con celdas completas (<Docente>/<archivo>.pdf …) es leída como informe real
     por `read_registro()` y contamina el registro y el gate `--check` de cualquier vault nuevo. -->
