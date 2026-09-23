---
title: Perfil — <Docente>
type: docente
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
nombre: <Nombre Apellido>
rol: Docente revisor (informes de trabajo de grado)
origen: informes-revisores
ambito: general
informes: 0
procedencia: informe
tags:
  - docentes
  - trabajos-grado
  - general
  - revisor-externo
---

# <Nombre Apellido>

> [!important] Ámbito y uso
> `ambito: general` — **no es evaluador de este trabajo de grado**: sus criterios provienen de
> informes de revisión a **otros** estudiantes. Se consultan como **segunda opinión**, nunca como
> norma, y **jamás** se emiten `confirmado` sobre tu trabajo (regla del guard). Fuente cruda:
> `sources/informes-revisores/<slug>/` y su `registro.md`.
>
> **Estado de la tabla**: `confirmado` = lo dijo en el informe (hecho verificado, con cita).
> La **aplicabilidad** a tu trabajo es siempre `inferida` o `abierta`.
>
> **Límite de fidelidad**: si el informe llegó transcripto a mano, declaralo acá; la evidencia
> queda capada y no se cita como si fuera el texto del escaneo.

## Criterios de fondo

| # | Criterio | Estado | Tipo | Fuente |
|---|---|---|---|---|
| XX1 | <qué exige, en una frase> | confirmado | transversal-metodológico | "<cita literal>" (informe de <estudiante>, <tipo> <fecha>) |

## Criterios de forma

| # | Criterio | Estado | Tipo | Fuente |
|---|---|---|---|---|
| XXF1 | <observación de forma> | confirmado | forma | <cita> |

## Relaciones
- [[_moc-docentes]] (catálogo)
- [[jerarquia-autoridad]] (tier de segunda opinión)
- `sources/informes-revisores/registro.md`

<!--
Por qué la primera columna NO es numérica: `scripts/cobertura-fuentes.sh` escanea las tablas de
perfil con `^| N |` y convertiría cada criterio en una obligación de tu trabajo de grado. Los
criterios de un docente que no te evalúa nunca son obligaciones.

Por qué col3 = Estado: ese script también lee la tercera columna como estado. Si insertás una
columna antes, el gate deja de fallar y pasa en verde falso.
-->
