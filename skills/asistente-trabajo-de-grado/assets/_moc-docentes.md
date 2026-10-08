---
title: Mapa de contenido — Mis docentes
type: moc
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
tags:
  - moc
  - docentes
  - trabajos-grado
---

# Mis docentes

Solo están los docentes que **te evalúan** (tutor, revisores y docente de TG). Cada uno es un enlace al catálogo
compartido de docentes, que se mantiene con `scripts/asignar_evaluador.py`; no se edita esta tabla a mano. Los
demás docentes del catálogo no aparecen ni se usan (ver [[jerarquia-autoridad]]).

<!-- evaluadores:inicio -->
| Rol | Docente | Desde |
|---|---|---|
| — | sin evaluadores vinculados todavía | — |
<!-- evaluadores:fin -->

## Cómo se suma lo nuevo

- **Te asignaron un evaluador** (el Revisor 2 suele llegar después): `asignar_evaluador.py <vault> --rol revisor_2
  --docente <slug>`; si todavía no está en el catálogo, se crea desde [[_plantilla-docente]].
- **Te corrigieron algo o hay una regla nueva**: pedile al agente «registrar corrección» (`perfil-revisor-tg`): queda
  `confirmado` en tu perfil del evaluador y, si es generalizable, suma al perfil del docente en el catálogo.

## Relaciones
- [[jerarquia-autoridad]] — quién manda entre tus evaluadores y qué suele revisar cada uno
- [[_plantilla-docente]] — docente nuevo en el catálogo
- [[indice]] — criterio de tus evaluadores
