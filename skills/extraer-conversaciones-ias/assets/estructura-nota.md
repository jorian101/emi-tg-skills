# Estructura de notas — conversaciones con IAs previas

Plantillas de nota para `sources/conversaciones-ias/`. Las crean los scripts de
`assets/scripts/`; este archivo documenta el contrato por si hay que editarlas
a mano o adaptar un formato nuevo.

## Convención común del frontmatter

```yaml
---
title: "..."
type: conversacion-ia | gem-gemini
source: <nombre del archivo fuente>
conv_index: <N> # solo deepseek
gem_index: <N> # solo gems
categoria: <tema>
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: extraido
fiabilidad: <origen> # ver convención de fiabilidad abajo
tags:
  - conversacion-ia
  - deepseek | gemini | ...
  - <categoria>
---
```

## Nota de conversación DeepSeek

Secciones en este orden:

1. `> [!info] Metadatos` — fuente, conv_index, tema, fechas, nº de prompts/respuestas, nota de adjuntos vacíos.
2. `> [!warning] Fiabilidad` — obligatorio: prompts = criterio confiable; respuestas = borradores NO validados.
3. `## Prompts del vocal (criterio)` — uno por turno, **verbatim**:
   `### Turno N — prompt del vocal`.
4. `## Respuesta de la IA — primer borrador` — primera respuesta completa.
5. `## Correcciones intermedias (resumen)` — solo si hay >2 respuestas: una línea por respuesta intermedia (`- **Respuesta N** (chars): resumen`).
6. `## Última respuesta de la IA (no validada por el vocal)` — última respuesta completa.
   - Si la última es un error de servicio (Oops/high traffic), usar el callout
     `> [!warning] Error de servicio` y NO incluir el texto de error como contenido.

## Nota de Gem de Gemini

1. `## Instrucciones del Gem` — verbatim.
2. `## Archivos adjuntos del Gem` — solo si hay archivos listados.

## Nota de resumen .docx

1. `> [!note] Origen` — ruta del docx + aviso de posible variante de material ya volcado.
2. `## Contenido extraído (verbatim del .docx)`.

## Convención de fiabilidad (obligatoria en `fiabilidad:`)

| Valor                                   | Significado                                                              |
| --------------------------------------- | ------------------------------------------------------------------------ |
| `prompt del vocal`                      | Criterio explícito del vocal — confiable                                 |
| `respuesta-IA no validada`              | Borrador de la IA — puede ser erróneo/alucinado, no la corrigió el vocal |
| `instrucciones redactadas por el vocal` | Gem escrito por el vocal — criterio, no hecho normativo                  |
| `texto del propio chat del vocal`       | Resumen .docx del chat — fuente confiable                                |

## Sin wikilinks salientes (por diseño)

Las notas volcadas NO llevan wikilinks salientes: son material crudo y su
fiabilidad no está validada. La conexión al grafo vive en los hubs:

- Categoría → fila en la tabla "Conexiones al wiki" de
  `sources/conversaciones-ias/categorias.md` (≥1 wikilink representativo).
- Criterio destilado → `wiki/criterio-vocal/indice.md`.

NO "arregles" las notas agregándoles enlaces: rompe la distinción
fuente-crudo/wiki-validado y dispara el chequeo de huérfanas innecesariamente
(están exentas por allowlist — ver `ORDEN-DEL-VAULT.md`
§Convención de conexiones).
