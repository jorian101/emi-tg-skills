---
title: Propuesta <sección> v<k>
type: propuesta-tg
created: YYYY-MM-DD
word_mtime: <mtime del .docx al generar>
word_sha: <sha del document.xml>
hojas_word: <nro de hojas del Word reportado por el estudiante; curva hacia 300>
extraction_sha: <sha de .extraction.json>
skill_version: <vX.Y>
rules_commit: <sha de feat con reglas-propias>
---

# Propuesta <sección> v<k>: <título corto>

## 0. Sellos de vigencia (regla 34)

- Word: `<ruta>` mtime `<mtime>` sha `<sha>` — si el Word cambia, re-extraer antes de opinar.
- Skill `perfil-revisor-tg` vX.Y + reglas-propias @ `<sha>` (ramas `feat/...`).

## 1. Fuentes consultadas (MP-14, todas, sin omitir)

| Fuente                 | Versión/estado      | Qué aporta a esta pasada         |
| ---------------------- | ------------------- | -------------------------------- |
| Revisor_N.md           | <fecha>             | <puntos usados>                  |
| Tutor.md               | <fecha>             | <puntos usados>                  |
| reglas-propias.md      | MP-x..MP-y          | <reglas aplicadas>               |
| Docente (jerarquía)    | <regla>             | <lo que desempata o complementa> |
| Zotero (obra, sección) | <verificado en PDF> | <fundamento usado>               |

## 2. Matriz de cobertura (obligatoria, regla 37)

Cada ítem `confirmado`/`abierto` del revisor y tutor lleva UNA fila, citada con
tag para `cobertura-fuentes.sh`:

- `R1#N` fila N de Qué valora / NO le gusta / Errores · `R1D#N` duda N
- `T#N` tutor · `TD#N` duda del tutor · `MP-NN` / `MT-NN`
- `DOC#N` regla docente numerada · `DOC#jerarquia` (obligatorio siempre:
  jerarquía considerada, docente y tutor como complemento jerarquizado)

| Tag  | Ítem    | Estado en perfil | Resolución en esta pasada         |
| ---- | ------- | ---------------- | --------------------------------- |
| R1#2 | <texto> | confirmado       | <aplicado § / pendiente + porqué> |

Sin tag no hay cobertura: `cobertura-fuentes.sh` falla en voz alta.

## 3. Decisiones (cada una con fuente + estado de fiabilidad)

- <decisión> — fuente: <perfil/regla> (`confirmado`/`inferido`/`abierto`).
- Divergencias deliberadas del estudiante (regla 35): `respetar`/`consultar` con motivo.

## 4. Cambios aplicados al corregido

<lista quirúrgica: qué cambió, dónde; nada adyacente>

## 5. Verificación (salidas pegadas, regla 37)

```
$ bash scripts/verificar-propuesta.sh <corregido.md> <corregido.docx>
<pegar salida>
$ bash scripts/cobertura-fuentes.sh <propuesta.md> <perfiles...>
<pegar salida>
```

## 6. Pendientes (del revisor, del estudiante, de Word)

- <pendiente> — dueño — `abierto`/`en corrección`
