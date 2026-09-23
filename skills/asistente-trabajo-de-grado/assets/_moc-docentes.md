---
title: Mapa de contenido — Docentes (área trabajos de grado)
type: moc
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
tags:
  - moc
  - docentes
  - trabajos-grado
---

# Mapa de contenido — Docentes

Catálogo **dinámico** de docentes. Es la fuente de verdad que leen las skills. Para agregar un
docente: crear su `.md` desde [[plantilla-docente]] y agregar su fila acá. **Nunca hardcodear un
docente en un `SKILL.md`.**

## Docentes con material propio

Docentes con clases, audios, apuntes o PDF. Cada uno tiene su `ambito`.

| Docente | Ámbito | Canal | Fuentes | Nota |
|---|---|---|---|---|
| [[<slug>]] | `general` o `especifico` | <audio / pdf / apuntes> | <ids o títulos de las fuentes> | <qué explica> |

## Docentes revisores externos

Docentes que **no** evalúan tu trabajo, pero cuyos criterios se destilaron de informes de revisión a
otros estudiantes (`sources/informes-revisores/`). `origen: informes-revisores`. Se consultan como
**segunda opinión** y nunca emiten `confirmado` sobre tu trabajo.

| Docente | Informes | Peso de sus criterios | Nota |
|---|---|---|---|
| [[<slug>]] | 0 | <qué exige> | <nombre completo> |

> [!note] Tu tutora va en otro lado
> Si tenés informes suscritos por tu propia tutora, sus criterios viven en `wiki/revisores/Tutor.md`,
> no acá, para no duplicar el dato.

## Ámbito y desambiguación

- **`general`** — explicación transversal, sirve a cualquier trabajo, NO es norma del tuyo.
- **`especifico`** — explica el contenido de tu trabajo concreto; prevalece sobre lo general.

> [!important] Regla anti-confusión
> Un docente `general` ≠ un docente `especifico` ≠ la norma institucional. Cada consulta debe
> resolver `docente` + `ambito`. Si no se determina el docente de una fuente, marcarla `pendiente`
> y no usarla como norma.

## Relaciones
- [[jerarquia-autoridad]] — quién manda cuando hay choque y a quién escalar dudas
- [[plantilla-docente]] — scaffold para un docente nuevo
- [[indice]] — criterio de tus evaluadores
