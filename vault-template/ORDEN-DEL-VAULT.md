# Manifiesto de orden del vault (fuente de verdad)

Este archivo define el orden canónico que debe respetar cualquier agente (humano o IA) al extraer,
actualizar o reconciliar documentos. **No se depende del orden alfabético del filesystem ni del
orden de lectura de herramientas.**

## Propósito

Evitar que una reextracción sobrescriba correcciones manuales, desordene la numeración o mezcle
contenido desactualizado. Extraer nunca significa "fusionar automáticamente": si hay cambios
manuales pendientes, se compara y se decide antes de reemplazar.

## Fuente del documento maestro

| Campo | Valor |
| --- | --- |
| Archivo fuente | `<ruta al .docx vivo de tu trabajo>` |
| Markdown en el vault | `sources/<slug>.md` |
| Reporte de extracción | `sources/<slug>.extraction.json` |
| Media | `sources/media/` |

> **El documento vivo, no la copia.** Verificá siempre por **sha256**, no por fecha: en unidades de
> red o sincronizadas (OneDrive, montajes de Windows) la fecha de modificación miente. Si el sha no
> coincide con el que registra tu extracción, re-extraé antes de opinar.

## Convención de conexiones (anti-huérfanas)

Toda nota nueva debe ser alcanzable desde la red.

1. **Regla MOC**: toda nota creada FUERA de la allowlist debe conectar a ≥1 hub
   (`wiki/_moc.md`, `index.md`, o el hub de su carpeta).
2. **Allowlist oficial** (exentas por diseño, NO enlazarlas masivamente):

```allowlist
# Un patrón por línea. ESTE BLOQUE ES LA FUENTE DE VERDAD: lo lee `scripts/verificar-enlaces.sh`
# y no hay ninguna copia hardcodeada en el código. Acepta globs (`sprints/**`) y expresiones
# regulares sobre el nombre del archivo (`\d{4}-\d{2}-\d{2}\.md`).
sprints/**
sources/informes-revisores/**
sources/_propuestas/**
sources/media/**
AGENTS.md
GEMINI.md
\log{2}\.md
\d{4}-\d{2}-\d{2}\.md
```

3. **Verificación pre-commit obligatoria**:
   `bash scripts/verificar-enlaces.sh` → 0 wikilinks rotos Y 0 huérfanas fuera de allowlist
   (exit 1 bloquea).

## Dependencias entre artefactos (anti-desincronización)

Si cambia un artefacto fuente, hay que re-sincronizar el que lo consume. Anotá acá tus
dependencias reales, por ejemplo:

| Artefacto final | Depende de |
| --- | --- |
| <tabla o sección del documento> | <tablas o notas fuente> |
| Conclusiones | <evaluaciones técnicas y económicas> |

Al regenerar una fuente, recorrer esta tabla; si algo cambió, crear la pendiente correspondiente en
`sources/_zotero/revisiones-pendientes.md`.

## Jerarquía de fuentes de verdad

1. El **código o sistema real** que documentás (si aplica).
2. Tus **entregables** verificables (figuras, capturas, mediciones).
3. El **documento académico** (`sources/`).
4. `wiki/` (criterio destilado).
5. Tu gestor bibliográfico (Zotero u otro).
6. Material auxiliar.

## Reglas obligatorias al extraer o actualizar

1. Verificar el archivo fuente exacto y su hash.
2. Comprobar si el Markdown destino tiene cambios manuales sin mergear.
3. Si existen, generar una comparación (`git diff`) y **detenerse** antes de sobrescribir.
4. Extraer Markdown, HTML, tablas, imágenes e índices.
5. Validar la extracción (reporte `extraction.json`).
6. No mezclar automáticamente contenido nuevo con correcciones manuales.
7. No modificar el Word fuente: entregar propuestas primero.
