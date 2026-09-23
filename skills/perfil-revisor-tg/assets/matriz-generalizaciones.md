---
title: Matriz de generalizaciones predictivas — clases de error derivadas de todo el feedback
type: perfil-revisor
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
sources: []
tags:
  - revisores
  - prediccion
  - generalizacion
---

# Matriz de generalizaciones predictivas

> Cada corrección ya hecha (de un evaluador, un docente o tuya) define una **clase de error**.
> Antes de cada pasada se derivan las clases aplicables a la sección y se **cazan sus instancias
> aunque nadie las haya marcado ahí**. Lo nuevo que se encuentra va a la propuesta como `inferido`
> (se propone, nunca se aplica en silencio).
>
> **Convención de IDs**: un prefijo por evaluador (`R1-NN`, `R2-NN`, `T-NN`, `XX-NN`). Un ID no se
> recicla nunca: si dos bloques usan el mismo número, citar uno marca el otro como cubierto.

## <Prefijo> — <evaluador>

| # | Origen | Clase de error | Dónde más cazar | Regla que cubre | Estado |
|---|---|---|---|---|---|
| R1-01 | <fila o informe> | <la clase, en una frase> | <secciones donde buscar> | <regla propia> | confirmado (1ª ocurrencia) |

## Criterios de docentes que NO te evalúan

> Estos **no** llevan ID numérico ni entran a esta matriz: siguen el precedente "sin clases de
> caza". Sus criterios viven en su perfil de `wiki/docentes/` y se aplican con las tres puertas
> del guard (evidencia, transferibilidad, autoridad) más el tope de 1 hallazgo por sección.

| Criterio externo | Corrobora | Qué agrega |
|---|---|---|
| XX1 (<docente>) | <regla propia o clase existente> | <nada, o qué aporta de nuevo> |

## Modelo de intención por fuente

Para resolver casos no marcados: cómo revisa cada evaluador y qué hacer ante un caso nuevo.

| Fuente | Cómo revisa | Intención operativa |
|---|---|---|
| <evaluador> | <patrón: tiempo, qué tacha, qué pide> | <acción: ante X → hacer Y> |

## Relaciones
- [[indice]]
- [[reglas-propias]]
- [[protocolo-tribunal]]
