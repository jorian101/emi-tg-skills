---
title: Índice — contradicciones de revisores vs norma y docentes
type: contradiction
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
tags:
  - contradiction
  - revisores
  - trabajos-grado
---

# Índice — contradicciones entre criterios

> Apartado para los **choques** entre el criterio de un evaluador (o tutor) y la norma, tus docentes,
> u otro evaluador. Se rige por [[wiki/docentes/jerarquia-autoridad|la jerarquía de autoridad]].

**Regla de oro: nada se resuelve en silencio.** Un choque se documenta acá con estado `abierto` y se
le pregunta al estudiante. La jerarquía solo desempata.

## Tipos de choque

| Tipo | Entre quiénes |
|---|---|
| `norma-vs-revisor` | Una regla institucional contradice la exigencia de un evaluador |
| `revisor-vs-revisor` | Dos evaluadores exigen cosas distintas |
| `revisor-vs-tutor` | El evaluador y el tutor chocan |
| `docente-vs-revisor` | Un docente contradice a un evaluador |
| `docente-externo-vs-regla-propia` | Un docente que **no** te evalúa contradice una regla tuya |

## Regla de manejo

1. Detectar el choque al contrastar (skill `perfil-revisor-tg`) o al destilar (`asistente-trabajo-de-grado`).
2. Crear una nota `<slug>.md` acá con `status: abierto`.
3. **Preguntar al estudiante** qué prevalece.
4. Marcar `resuelto` con `resolution` (fuente + fecha + resultado).

## Contradicciones registradas

| Slug | Tipo | Estado |
|---|---|---|
| (ninguna aún) | — | — |

## Plantilla de nota de contradicción

```markdown
---
title: Contradicción — <descripción>
type: contradiction
created: YYYY-MM-DD
status: abierto
tipo: <uno de los tipos de arriba>
sources: []
tags: [contradiction, revisores, trabajos-grado]
---

## El conflicto
<qué exige el evaluador> vs <qué dice la norma, el docente o el otro evaluador>.

## Evidencia
- Evaluador (perfil/feedback): ...
- Norma / docente: ...

## Resolución
- pendiente: preguntar al estudiante qué prevalece.

## Relaciones
- [[wiki/docentes/jerarquia-autoridad]]
```

## Relaciones
- [[wiki/docentes/jerarquia-autoridad]]
- [[wiki/revisores/indice]]
- [[wiki/trabajos-grado/_moc-trabajos-grado]]
- [[index]]
