---
name: extraer-doc-tesis
description: "Trigger: extraé, convertí o actualizá un documento Word/PDF de la tesis. Genera Markdown navegable, HTML legible, tablas, índices, imágenes, detección de citas y trazabilidad de fuentes en el vault."
license: MIT
metadata:
  author: asistente-legal
  version: "3.0"
---

## Activation Contract

Usá esta skill cuando el usuario pida extraer, convertir o actualizar un `.docx` o `.pdf` del directorio de respaldo de la tesis.

## Hard Rules

- Fuente: `$CORPUS/BACKUP TG`; destino: `$VAULT/sources`.
- Rechazá locks (`~$`) y temporales (`~WRL`). Nunca extraigas un archivo inexistente.
- Para DOCX usá `scripts/extract_document.py`, que genera Markdown, HTML, media, reporte de validación, estado de extracción y detección de citas.
- **Protección contra sobrescritura**: si el Markdown destino tiene cambios manuales sin commitear, el extractor aborta (RuntimeError) salvo `--force`. Antes de usar `--force`, mostrá el `git diff` y pedí confirmación.
- Reemplazá el Markdown y HTML del mismo slug; no borres otros documentos del vault.
- Extraé imágenes a archivos relativos. No dejes `data:image`, Base64 ni rutas absolutas en el Markdown.
- No prometas que Markdown conserva colores o celdas combinadas: para esos casos la salida HTML es la representación visual.
- Si falla la conversión o la validación, conservá el archivo previo y reportá el error.
- **Trazabilidad de fuentes**: después de extraer, regenerá el snapshot de Zotero y el matcher de citas (paso 5 del Execution Steps).

## Decision Gates

| Entrada                                            | Acción                                                 |
| -------------------------------------------------- | ------------------------------------------------------ |
| `.docx`                                            | Pandoc a GFM + HTML5 y extracción de media             |
| `.pdf`                                             | `docling`; fallback a `pymupdf4llm` si está disponible |
| destino con cambios manuales                       | Detener y comparar; no sobrescribir sin aprobación     |
| salida pequeña, sin títulos o sin tablas esperadas | Fallar validación; no reemplazar destino               |

## Execution Steps

1. Confirmá el nombre exacto y calculá el slug ASCII.
2. Ejecutá `python3 scripts/extract_document.py "archivo.docx"` desde la raíz de la skill. Si aborta por cambios manuales, mostrá `git diff` y pedí confirmación antes de `--force`.
3. Revisá el reporte: tablas, imágenes, headings, índice, tamaño, enlaces y cantidad de citas detectadas.
4. Para una actualización posterior, repetí el mismo comando: es idempotente.
5. **Trazabilidad de fuentes**:
   ```bash
   python3 scripts/zotero_snapshot.py
   python3 scripts/match_fuentes.py sources/<slug>.fuentes.json --slug <slug> --source "<archivo.docx>"
   ```
   El snapshot copia `zotero.sqlite` a un temporal y lo lee en modo solo lectura (no requiere Zotero abierto, no lo modifica). El matcher cruza las citas contra el snapshot y escribe `sources/_zotero/fuentes-por-documento/<slug>.fuentes.md`.
6. Si el usuario tiene Zotero abierto con API local, podés consultar en vivo con Zotero MCP para resolver pendientes (búsqueda, metadatos, PDF). Las escrituras en Zotero requieren confirmación explícita.
7. Actualizá `sources/_zotero/revisiones-pendientes.md` con las fuentes no confirmadas.
8. Registrá en Engram la herramienta usada y cualquier incidencia.

## Output Contract

Entregá `<slug>.md`, `<slug>.html`, `media/`, `<slug>.extraction.json`, `<slug>.state.json`, `<slug>.fuentes.json` dentro de `sources/`, y el mapa de fuentes en `sources/_zotero/fuentes-por-documento/<slug>.fuentes.md`. Informá el archivo fuente, conteos validados, citas detectadas y cualquier limitación visual.

## References

- `scripts/extract_document.py` — extractor y validación reproducible.
- `scripts/zotero_snapshot.py` — snapshot read-only de Zotero.
- `scripts/match_fuentes.py` — matcher cita ↔ Zotero.
- `$VAULT/ORDEN-DEL-VAULT.md` — orden canónico del vault.
