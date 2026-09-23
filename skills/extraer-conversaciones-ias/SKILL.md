---
name: extraer-conversaciones-ias
description: "Trigger: extraé conversaciones de IAs, nuevas prompts y respuestas del vocal, volcá chats de DeepSeek/Gemini/ChatGPT al vault. Extrae prompts y respuestas de IAs previas a sources/conversaciones-ias/, destila wiki/criterio-vocal/ y audita la fiabilidad de cada respuesta."
license: MIT
metadata:
  author: "jorian"
  version: "1.1.0"
---

# Skill: extraer-conversaciones-ias

## Activation Contract

Se activa cuando el usuario entrega archivos o texto de conversaciones con IAs
(DeepSeek JSON, Gems de Gemini HTML, resúmenes .docx, ChatGPT u otras) para
extraer al vault de conocimiento. Objetivo: que el asistente legal gane
criterio del vocal (prompts) sin contaminarse con respuestas erróneas de la IA.

## Hard Rules

1. Fuente = solo lectura. Nunca modificar el original (ruta "IAs usadas antes
   del proyecto").
2. **Auditoría de fiabilidad obligatoria**: distinguir SIEMPRE `prompt`
   (criterio del vocal, confiable) de `respuesta-IA` (NO validada, puede
   alucinar). Etiquetar "Última respuesta de la IA (no validada)" y marcar
   errores de servicio con callout `[!warning]`.
3. No atribuir al vocal lo que proviene de una respuesta de la IA. En
   `wiki/criterio-vocal/` marcar el origen de cada afirmación (prompt/gem/
   respuesta-IA/corpus).
4. Todo número, norma, resolución, reglamento o partida de una _respuesta_
   debe validarse contra fuente primaria antes de adoptarse.
5. Respetar `ORDEN-DEL-VAULT.md` y la estructura
   `sources/conversaciones-ias/` + `wiki/criterio-vocal/`.
6. Adjuntos FILE pueden venir vacíos en el JSON — no inventar contenido.
7. Verificar enlaces con `scripts/verificar-enlaces.sh` (0 rotos y 0 huérfanas
   fuera de allowlist).
8. Commit solo de archivos propios; el vault puede tener deuda de commits
   ajenos (todo `wiki/` sin trackear). No arrastrar contenido ajeno.
9. **Alcanzabilidad vía hubs**: las notas volcadas NO llevan wikilinks
   salientes (material crudo). Cada categoría usada debe tener fila con ≥1
   wikilink representativo en la tabla "Conexiones al wiki" de
   `sources/conversaciones-ias/categorias.md`. Convención completa:
   `ORDEN-DEL-VAULT.md` §Convención de conexiones.

## Decisiones por defecto (NO preguntar al usuario)

La skill resuelve estas decisiones automáticamente; solo preguntar si hay duda
genuina de clasificación jurídica o de estructura del vault.

1. **Formato nuevo** (JSON/HTML de otra IA): crear parser nuevo siguiendo el
   patrón de `parse_claude.py`. Solo preguntar si es binario/propietario sin
   estructura clara.
2. **Archivo de memoria/perfil** (sin `chat_messages`): nota de perfil del
   vocal en `wiki/criterio-vocal/perfil-vocal.md`; no es conversación.
3. **Docs de proyectos**: normas públicas masivas (>100K chars, CPE/manuales/
   leyes) = solo listar; docs de casos concretos = volcar completos; duplicados
   por hash = deduplicar listando la referencia.
4. **Borrador vinculado a caso existente**: volcar como material vinculado con
   wikilink al caso; nunca duplicar el caso.
5. **Material de otra jurisdicción** (no flujo SAC: consulta/apelación TSJM):
   contexto con evidencia mixta (primaria para instancia inferior, secundaria
   para producción del vocal); NO indexar en RAG ni en `seed_casos_tsjm.py`.
6. **Clasificación jurídica**: decisión del agente sin preguntar; el JSON de
   clasificación lo construye el agente, nunca lo inventa el script.
7. **Nunca descartar por nombre**: el título del chat no define la
   clasificación. Abrir el contenido (primer prompt + respuesta) antes de
   excluir. Un chat tipo "Tesis_..." puede ser jurídico si desarrolla derecho
   (tipificación, reforma normativa, delitos, garantías); solo es metodológico
   NO jurídico si el contenido es puramente metodología (Sampieri/APA) sin
   desarrollo jurídico sustantivo.

## Decision Gates

| Situación                             | Acción                                                                    |
| ------------------------------------- | ------------------------------------------------------------------------- |
| Archivo `deepseek-conversations.json` | `parse_deepseek.py --listar`, clasificar, `--volcar`                      |
| HTML de Gems de Gemini                | `parse_gemini_gems.py --listar`, `--out`                                  |
| Resumen .docx                         | `parse_gemini_docx.py --src ... --out ... --titulo "..."`                 |
| `claude-conversations.json`           | `parse_claude.py --listar`, clasificar, `--volcar`                        |
| `claude-projects/*.json`              | `parse_claude_projects.py --dir ... --out ... [--listar-only ...]`        |
| `claude-memories.json`                | nota de perfil en `wiki/criterio-vocal/perfil-vocal.md` (no conversación) |
| `grok-conversations.json`             | `parse_grok.py --listar`, clasificar, `--volcar`                          |
| `grok-conversations.json --project`   | `parse_grok.py --project --out ...` (custom_personality)                  |
| `chatgpt-chats-parte-1/*.md`          | `parse_chatgpt_md.py --dir ... --listar`, clasificar, `--volcar`          |
| `gemini-chat-parte-1/*.pdf`           | `parse_gemini_pdf.py --dir ... --listar`, clasificar, `--volcar`          |
| Otro formato (ChatGPT...)             | volcar manual siguiendo `assets/estructura-nota.md`                       |
| ¿La respuesta contradice el corpus?   | descartarla como criterio; marcarla `respuesta-IA`                        |
| Categoría nueva de documento          | crear/actualizar nota en `wiki/criterio-vocal/`                           |

## Execution Steps

1. Listar archivos fuente; calcular hashes SHA-256 para el manifiesto.
2. Parsear con el script de `assets/scripts/` (modo `--listar` primero).
3. Clasificar cada conversación/Gem: jurídica (extraer) vs no (listar con
   motivo). Construir el JSON de clasificación.
4. Volcar notas a `sources/conversaciones-ias/` (ver `assets/estructura-nota.md`).
5. Actualizar `sources/conversaciones-ias/manifiesto.md` (hashes + clasificación
   - sección de fiabilidad).
6. Destilar/actualizar `wiki/criterio-vocal/` con origen por afirmación.
7. Integrar vía hubs (nunca editar las notas volcadas para enlazarlas):
   actualizar la tabla "Conexiones al wiki" de `categorias.md` con ≥1
   wikilink representativo por categoría tocada; `criterio-vocal/indice.md`
   si hay criterio nuevo; `_moc.md`/`index.md` solo si se creó una nota fuera
   de `sources/conversaciones-ias/`; `matriz-autoridad-confianza.md` ante
   casos nuevos de alucinación.
8. `bash .../vault/scripts/verificar-enlaces.sh` → 0 rotos y 0 huérfanas
   fuera de allowlist (bloquea el commit).
9. Commit convencional en el vault (`docs(vault): extraer conversaciones de <IA>`),
   solo archivos propios.

## Output Contract

- Notas volcadas en `sources/conversaciones-ias/` (deepseek/, gemini-gems/,
  claude/, claude-projects/, grok/, grok-projects/, chatgpt/, gemini-parte-N/,
  resumen).
- `manifiesto.md` actualizado como índice resumen (hashes + clasificación +
  fiabilidad).
- Catálogos dinámicos al día: `categorias.md` y `casos-conocidos.md`
  (agregar categoría/caso antes de clasificar/volcar).
- `wiki/criterio-vocal/` con veredictos por origen (incl. `perfil-vocal.md`),
  solo criterio NUEVO (destilación incremental).
- Enlaces verificados (0 rotos y 0 huérfanas fuera de allowlist) y tabla
  "Conexiones al wiki" de `categorias.md` al día.
- Commit convencional con solo archivos propios.
- `mem_save` (`topic_key: vault/conversaciones-ias`).

## References

- `references/flujo-detallado.md` — pasos completos, criterio de clasificación, auditoría.
- `assets/estructura-nota.md` — plantillas de nota y convención de fiabilidad.
- `assets/categorias.yaml` — catálogo canónico de categorías (dinámico).
- `assets/scripts/` — parsers (deepseek, gemini gems, gemini docx, claude, claude-projects, grok, chatgpt, gemini pdf).
