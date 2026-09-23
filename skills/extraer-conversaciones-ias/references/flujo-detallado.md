# Flujo detallado — extraer conversaciones de IAs al vault

Complemento del `SKILL.md`. Documenta pasos, criterios y reglas de auditoría
que el agente debe aplicar. Las rutas fuente de esta sesión (referencia):

```
$CORPUS/Problematica docs/IAs usadas antes del proyecto/
```

## 1. Identificar y registrar la fuente

- Listar los archivos que entregue el usuario.
- Calcular hash SHA-256 (primeros 16 chars) y registrarlos en el manifiesto.
- Confirmar la ruta base de "IAs usadas antes del proyecto" si cambió.

## 2. Parsear

Según el formato, invocar el script correspondiente de `assets/scripts/`:

| Formato                              | Script                     | Modo previo | Modo de volcado                                          |
| ------------------------------------ | -------------------------- | ----------- | -------------------------------------------------------- |
| `deepseek-conversations.json`        | `parse_deepseek.py`        | `--listar`  | `--out <dir> --clasificacion <json>`                     |
| `gemini_gems_data.html`              | `parse_gemini_gems.py`     | `--listar`  | `--out <dir> [--clasificacion <json>]`                   |
| `resumenes de chats de gemini.docx`  | `parse_gemini_docx.py`     | —           | `--src <docx> --out <dir> --titulo "..."`                |
| `claude-conversations.json`          | `parse_claude.py`          | `--listar`  | `--out <dir> --clasificacion <json>`                     |
| `claude-projects/*.json`             | `parse_claude_projects.py` | —           | `--dir <dir> --out <dir> [--listar-only ...]`            |
| `claude-memories.json`               | manual                     | —           | nota de perfil en `wiki/criterio-vocal/perfil-vocal.md`  |
| `grok-conversations.json`            | `parse_grok.py`            | `--listar`  | `--out <dir> --clasificacion <json>`                     |
| `grok-conversations.json` (proyecto) | `parse_grok.py --project`  | —           | `--out <dir>` (custom_personality)                       |
| `chatgpt-chats-parte-1/*.md`         | `parse_chatgpt_md.py`      | `--listar`  | `--out <dir> --clasificacion <json>`                     |
| `gemini-chat-parte-1/*.pdf`          | `parse_gemini_pdf.py`      | `--listar`  | `--out <dir> --clasificacion <json> --source <etiqueta>` |
| Otro (ChatGPT, Claude... otros)      | manual                     | —           | volcar siguiendo `assets/estructura-nota.md`             |

- `--listar` emite la tabla para clasificar; el agente decide y construye el
  JSON de clasificación, NUNCA lo inventa el script.
- Ruta de volcado por defecto:
  `$VAULT/sources/conversaciones-ias/`

### Notas específicas de Claude

- `claude-conversations.json`: lista de conversaciones con `chat_messages[]`.
  Solo se extrae texto de bloques `type=text`; `thinking`/`tool_use`/
  `tool_result` son razonamiento interno y se ignoran. Prompts del vocal =
  `sender: human`; respuestas = `sender: assistant`.
- `claude-projects/*.json`: `prompt_template` (criterio del vocal) + `docs`
  (archivos de referencia). El `prompt_template` puede venir vacío y el prompt
  real estar en `description`. Usar `--listar-only` para normas públicas
  masivas (CPE, manuales) que solo se listan sin volcar. Salta proyectos sin
  prompt ni docs.
- `claude-memories.json`: NO es conversación — es la memoria de contexto que
  Claude construyó sobre el usuario. Vuelca como perfil del vocal (contexto de
  trabajo, principios que exige, casos vistos), no como prompts.

### Notas específicas de Grok

- `grok-conversations.json`: objeto con `conversations[]`, `projects[]`,
  `tasks[]`, `media_posts[]` (los dos últimos suelen estar vacíos). Cada
  conversación: `conversation` (metadatos, `title`) + `responses[]` con
  `response.sender` (`human`/`assistant`), `response.message` (texto),
  `response.model` (p. ej. `grok-3`) y `file_attachments` (solo IDs, sin
  contenido — no inventar).
- `projects[]`: `custom_personality` = criterio del vocal (como el
  `prompt_template` de Claude). Volcar con `--project` como nota de proyecto en
  `sources/conversaciones-ias/grok-projects/`.
- Adjuntos siempre vacíos en el export: registrar en el frontmatter
  ("file_attachments: solo IDs, sin contenido").

### Notas específicas de ChatGPT

- `chatgpt-chats-parte-1/*.md`: un archivo por chat. Frontmatter `title` +
  `source` (URL `chatgpt.com/c/...`) + bloques `#### You:` (prompts) y
  `#### ChatGPT:` (respuestas).
- La clave de clasificación es el **basename del archivo sin el prefijo
  `ChatGPT-`** (p. ej. `Figuras_procesales_similares`).
- Los chats que empiezan con `![image](data:image/jpeg;base64,...` contienen
  capturas; suelen ser técnicos (se excluyen).
- Los hashes de los archivos volcados se escriben en `_hashes.json` — moverlo
  fuera del vault (a `/tmp`) después de volcar, no versionarlo.

### Notas específicas de Gemini (PDF)

- `gemini-chat-parte-1/*.pdf`: un PDF por chat exportado de Gemini. Contiene
  título (nombre de archivo), URL `gemini.google.com/app/<id>` y bloques
  `User prompt:` / `Response:`. Requiere `pdftotext` (poppler-utils).
- **ADVERTENCIA CRÍTICA**: el export de Gemini **NO incluye los archivos
  adjuntos** (ni los subidos ni los generados). Cada prompt se clasifica:
  - `inline`: el documento está pegado en el prompt (texto visible → usable).
  - `ausente`: el prompt menciona adjunto sin contenido → callout, se conserva
    el criterio del vocal pero NO los datos del adjunto.
  - `fallido`: la respuesta indica que no pudo leer el archivo → callout.
- Aun sin adjuntos, **extraer patrones de criterio** de los prompts (cómo pide
  desvirtuar argumentos, cómo estructura GEMs, qué exige de motivación/
  fundamentación/congruencia) y **patrones de redacción** de las respuestas
  (estructura de considerandos/informes), sin adoptar números/fojas no
  visibles.
- El parser escribe `_hashes.json` en el out → moverlo fuera del vault después
  de volcar.

### Decisiones por defecto (evitar preguntar al usuario)

Estas reglas se resolvieron como fricción en la primera extracción de Claude.
Aplicarlas automáticamente; solo preguntar si hay duda genuina de clasificación
jurídica o de estructura del vault.

1. **Formato nuevo de otra IA** (JSON/HTML con `chat_messages` o similar):
   crear parser nuevo en `assets/scripts/` siguiendo el patrón de
   `parse_claude.py` (modo `--listar` + volcar, frontmatter `fiabilidad:`,
   marcar errores de servicio). Solo preguntar si es binario/propietario sin
   estructura clara.
2. **Archivo de memoria/perfil/contexto** (sin `chat_messages`): NO es
   conversación. Volcar como nota de perfil del vocal en
   `wiki/criterio-vocal/perfil-vocal.md` (contexto de trabajo, principios,
   casos vistos). No tratarlo como prompts.
3. **Docs de proyectos** (`--listar-only` del parser de proyectos):
   - **Norma pública masiva** (>100K chars; CPE, manuales, leyes, decretos):
     solo listar, no volcar contenido.
   - **Doc de caso concreto** (resoluciones, informes de caso): volcar
     completo verbatim.
   - **Duplicado por hash** de contenido: deduplicar listando la referencia al
     primer volcado.
4. **Borrador vinculado a caso ya documentado**: si el doc es un borrador/v2 de
   un caso existente en `sources/casos-tsjm/casos/`, volcar como material
   vinculado con wikilink al caso; nunca duplicar el caso.
5. **Material de otra jurisdicción** (no flujo SAC — no es consulta/apelación
   TSJM): crear caso como **contexto** con `nivel_evidencia: mixta` (primaria
   para piezas de instancia inferior oficiales, secundaria para producción del
   vocal). NO agregarlo a `seed_casos_tsjm.py` ni indexarlo en RAG.
6. **Clasificación jurídica**: decisión del agente, sin preguntar. El agente
   construye el JSON de clasificación revisando cada conversación/Gem; el
   script nunca la inventa.

## 3. Clasificar (jurídica vs no)

Criterio **jurídica**: derecho militar, constitucional, penal, procesal, civil,
administrativo, laboral; documentos procesales (auto de vista, memorial,
sumario, amparo, informe de descargo, PIE, solicitud de archivo/ascenso);
criterio del vocal como abogado/Vocal Relator.

**Excluir** (con motivo en el manifiesto): técnico (impresora, apps), personal
(pan, bicarbonato, vehículo), marketing (naming de chatbot), quejas de
rendimiento, diapositivas/presentaciones, finanzas personales.

**NO descartar por nombre**: el título del chat no define la clasificación.
Siempre abrir el contenido (primer prompt + respuesta) antes de excluir. Caso
real: 4 chats llamados "Tesis_..." resultaron tener contenido jurídico
(tipificación de extorsión sexual en el Código Penal, delitos informáticos en
el CPM) y debieron incluirse. Regla: si un chat parece "tesis metodológica"
pero su contenido desarrolla derecho (tipificación, reforma normativa, delitos,
garantías), es **jurídica**. Solo es tesis metodológica NO jurídica si su
contenido es puramente de metodología de la investigación (Sampieri, APA,
estructura de capítulos) sin desarrollo jurídico sustantivo.

## 3b. Catálogos dinámicos (Plan 0 — el vault va a crecer)

El vault es **dinámico**: llegan más chats de IAs (Gemini parte N, ChatGPT parte
N, nuevas IAs). Antes de clasificar CADA lote nuevo:

1. **Usar categorías del catálogo** (`assets/categorias.yaml` en la skill =
   `sources/conversaciones-ias/categorias.md` en el vault). Solo esas.
2. **Categoría nueva** → agregarla en AMBOS (yaml + vault) ANTES de clasificar.
   Nunca inventar una categoría al vuelo.
3. **Caso recurrente** (Uscamayta, Mendoza, Sapiencia, Colque, anteproyectos)
   → consultar `sources/conversaciones-ias/casos-conocidos.md` ANTES de volcar.
   Si el caso ya está → vincular con callout `[!note] Caso vinculado`; no
   duplicar. Si es caso nuevo en ≥2 fuentes → agregar fila a la tabla.
4. **Manifiesto = índice resumen**: actualizar solo la fila de la fuente (nº
   jurídicas/excluidas/duplicados). Los hashes detallados viven en el
   `_hashes.json` de cada fuente (fuera del vault). No listar cientos de
   hashes inline.
5. **Destilación incremental**: antes de agregar criterio a
   `wiki/criterio-vocal/`, verificar si ya existe (secciones 1-10 de
   criterio-argumentacion). Solo agregar si es NUEVO (origen prompt/gem
   confiable); si es confirmación, agregar solo la fuente al frontmatter de la
   nota existente.

## 4. Volcar a `sources/conversaciones-ias/`

Estructura (no crear carpetas nuevas salvo que haga falta):

```
conversaciones-ias/
├── manifiesto.md          ← actualizar SIEMPRE
├── deepseek/              → una nota por conversación jurídica
├── gemini-gems/           → una nota por Gem
└── resumen-chats-gemini.md o similar
```

- Si la categoría ya existe, la nota nueva se agrega sin romper la numeración.
- No sobrescribir correcciones manuales previas (comparar antes de reemplazar).

## 5. Auditoría de fiabilidad (NO opcional)

Cada nota debe distinguir el origen de cada afirmación:

- `prompt` → criterio del vocal (confiable).
- `gem` → instrucciones que el vocal redactó (confiable).
- `respuesta-IA` → borrador NO validado (puede alucinar; no atribuir al vocal).
- `corpus` → verificable contra casos reales del vault.

Reglas duras:

1. Las respuestas se etiquetan "Última respuesta de la IA (no validada)".
2. Errores de servicio → callout `> [!warning] Error de servicio`, sin contenido.
3. Cualquier norma/número/resolución/partida de una _respuesta_ debe validarse
   contra fuente primaria antes de adoptarse (ver `wiki/matriz-autoridad-confianza`).
4. En la destilación wiki, cada afirmación marca su origen; lo derivado solo de
   una respuesta se reetiqueta como "hipótesis de la IA" o se retira.

## 6. Destilar en `wiki/criterio-vocal/`

Notas (crear o actualizar según lo que aporte el material nuevo):

- `indice.md` — lista de notas + tipos de documento que produce el vocal.
- `patrones-de-consulta.md` — role-prompting, fases, corrección por criterio.
- `criterio-argumentacion.md` — estándares con origen por afirmación y veredicto.
- `estilo-documentos-vocal.md` — estructuras de documentos, marcando si la
  estructura la propuso la IA.

Regla: **solo** lo que provenga de prompts/Gems es criterio confirmado del
vocal. Lo de respuestas va marcado como hipótesis.

## 7. Actualizar integraciones (vía hubs, nunca las notas volcadas)

Las notas en `sources/conversaciones-ias/` NO llevan wikilinks salientes:
son material crudo y la conexión vive en los hubs (ver `ORDEN-DEL-VAULT.md`
§Convención de conexiones).

- `sources/conversaciones-ias/categorias.md` — OBLIGATORIO: la tabla
  "Conexiones al wiki" debe tener fila con ≥1 wikilink representativo por
  cada categoría tocada en esta extracción (alias con `\|` dentro de tablas).
- `wiki/criterio-vocal/indice.md` — si la destilación agregó criterio nuevo,
  convertir a wikilinks las menciones de conversaciones relevantes.
- `wiki/_moc.md` e `index.md` — solo si se creó una nota FUERA de
  `sources/conversaciones-ias/` (ej. perfil del vocal).
- `wiki/matriz-autoridad-confianza.md` — si aparece un caso nuevo de alucinación.

## 8. Verificar y commitear

1. `bash $VAULT/scripts/verificar-enlaces.sh`
   → 0 rotos Y 0 huérfanas fuera de allowlist. Si falla, corregir antes de
   commitear (exit 1 = commit bloqueado).
2. Commit convencional en el vault (el vault es repo git propio):
   `docs(vault): extraer conversaciones de <IA> al vault`.
3. **Solo archivos propios**: el vault puede tener deuda de commits de sesiones
   previas (todo `wiki/` sin trackear). Commitear únicamente lo que esta
   ejecución creó/modificó; no arrastrar contenido ajeno.
4. `mem_save` con `topic_key: vault/conversaciones-ias`.

## 9. Conocimiento previo (fuente de esta sesión)

- 54 conversaciones DeepSeek jurídicas de 99; 45 excluidas.
- 25 Gems de Gemini (21 jurídicos, 4 no).
- Skill AUTO DE VISTA del .docx era variante de `raw/promt/promt-operativo.md`.
- Alucinaciones documentadas: conv 42 (resoluciones ministeriales inventadas),
  conv 91 (R-AB-DB-001), conv 67 (Convocatoria 02/2025).
