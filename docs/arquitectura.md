# Arquitectura

## Motor y datos

```
tg-skills/            ← MOTOR (este repo, público, sin datos)
  skills/             las cinco skills
  scripts/            los gates de verificación
  vault-template/     el andamiaje vacío que se instala

tu-vault/             ← DATOS (repo privado tuyo)
  wiki/               perfiles de evaluadores, docentes, reglas, contradicciones
  sources/            informes crudos, extracciones del Word, bibliografía
```

El motor **no contiene un solo dato del estudiante**. Eso no es una convención de estilo: es lo que
hace que el repo sea publicable y que tus evaluadores y los informes de terceros no se filtren.

## El contrato entre los dos: cinco claves

El único acoplamiento son cinco claves de `config.local.md`:

```
data_dir        dónde viven los perfiles de tus evaluadores
estudiante      quién sos
evaluadores     qué perfiles SÍ mandan (por nombre de archivo)
docentes_en     dónde viven los criterios de docentes
informes_en     dónde se guardan los informes crudos
```

más tres variables de `.env.local` para los scripts (`VAULT`, `CORPUS`, `ZOTERO_SQLITE`).

**Por qué `evaluadores:` y no adivinar:** el sistema no deduce quién te evalúa del nombre de la
carpeta. Si lo hiciera, cualquier docente con un archivo en `docentes_en` pasaría a ser autoridad
sobre tu trabajo. La lista es explícita y se lee de la config.

## El vault y por qué tiene esa forma

El vault sigue el patrón de dos capas:

| Capa | Rol | Se escribe |
|---|---|---|
| `sources/` | Material crudo extraído de fuentes externas (Word, informes, Zotero) | **No** — regenerable, no editable |
| `wiki/` | Capa destilada: perfiles, reglas, contradicciones, teoría | Sí |

Separarlas evita el problema clásico: que una re-extracción pise correcciones manuales, o que
material crudo y conclusiones se mezclen en el mismo archivo.

## Los gates

Tres scripts sostienen las reglas duras. Existen porque **una regla que no se verifica es una
intención**, y porque la revisión mecánica encuentra cosas que el ojo saltea.

| Gate | Qué garantiza |
|---|---|
| `verificar-enlaces.sh` | La red de notas no tiene enlaces rotos ni notas huérfanas |
| `verificar-propuesta.sh` | La propuesta no reintroduce errores ya corregidos (viñetas inline, menciones duplicadas, tablas perdidas) |
| `cobertura-fuentes.sh` | Todo punto `confirmado` o `abierto` de tus evaluadores fue cubierto o declarado |

**La allowlist es dato, no código.** Los paths que el verificador de enlaces debe perdonar (material
crudo, plantillas) se leen del manifiesto del vault, no se hardcodean en el script. Hardcodearlos fue
exactamente el bug que hizo que una ruta nueva apareciera como huérfana y bloqueara un commit.

**El registro se deriva.** El índice de informes no lleva un estado escrito a mano: lo calcula el
script (¿el perfil del docente ya cita su carpeta? → procesado). Así el índice no puede mentir sobre
lo que falta.

## El guard de predicción, en detalle

Los criterios que provienen de docentes que **no** te evalúan entran a una propuesta solo si pasan
tres puertas y respetan dos topes:

**Puertas**
1. **Evidencia**: cita literal + hash + tipo de fuente + ubicación. Una transcripción manual capa el
   criterio en `inferido` como máximo.
2. **Transferibilidad**: `transversal-metodológico` se puede cazar (con cupo); `forma` no (fuera de
   alcance); `dominio` no (es contenido de otro trabajo: un algoritmo de otro tema no dice nada del
   tuyo).
3. **No-colisión de autoridad**: si contradice un punto `confirmado` de un evaluador propio, no se
   caza; se abre una contradicción.

**Topes**
- **1 hallazgo externo por sección**: los vinculantes son tus evaluadores.
- **Anclaje seccional**: solo se caza en la sección análoga al caso donde ese docente aplicó el
  criterio.
- **Control anti-plantilla**: antes de proponer un pendiente hay que verificar que lo señalado no
  exista ya en el documento (puede vivir en un anexo).
- **Aislamiento**: los hallazgos externos van en una subsección **"Segunda opinión (no vinculante)"**,
  fuera de la matriz de cobertura que lee tu evaluador.

## Si no tenés evaluadores propios

El sistema asume que tenés al menos un evaluador y un tutor. Si solo tenés criterios de docentes
externos, no hay desempate posible: todo queda `inferido`, el recorrido de revisión **no puede
cerrar propuestas** y el sistema te avisa que completes tus evaluadores.

## Dependencias externas

| Dependencia | Para qué | ¿Obligatoria? |
|---|---|---|
| `pandoc` | Extraer Word y generar espejos `.docx` | Sí |
| `tesseract` + `poppler` | OCR de informes escaneados | Solo si tenés escaneos |
| `herdr` + `agy` | Transporte del recorrido tribunal a otros agentes | **No** — el tribunal es opcional |
| NotebookLM (MCP o CLI) | Consultar explicaciones de un docente | **No** |
| Zotero (sqlite local) | Verificar que una fuente citada exista de verdad | **No**, pero recomendada |
