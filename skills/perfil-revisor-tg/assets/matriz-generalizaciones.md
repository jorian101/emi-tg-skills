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

## SEM — clases semilla (observadas en revisores de la EMI, sin dueño)

> Arrancan en todo vault como **`inferido`**: se cazan desde la primera pasada porque varios revisores
> las marcaron en otros TG, pero **no** son obligación hasta que **tu** evaluador las pida (entonces se
> copian a su bloque con su ID y pasan a `confirmado`).

| # | Origen | Clase de error | Dónde más cazar | Regla que cubre | Estado |
|---|---|---|---|---|---|
| SEM-01 | revisores EMI (sesiones e informes) | **Se mide el efecto y no la causa**: la mejora se prueba con tiempo o costo y nada muestra que baje la causa del árbol de problemas (errores, inconsistencias) | OG, validación, conclusiones, diapositiva de resultados | (regla propia por crear) | inferido |
| SEM-02 | revisores EMI | **Mejora sin número**: discusión de resultados sin cifra, unidad, porcentaje ni comparación antes/después con los mismos términos | validación, evaluación técnica, conclusiones | (regla propia por crear) | inferido |
| SEM-03 | revisores EMI | **Declarado y nunca verificado**: un requerimiento (funcional o no funcional) definido al inicio no reaparece en pruebas ni en la evaluación | tablas de requerimientos contra pruebas y cumplimiento | (regla propia por crear) | inferido |
| SEM-04 | revisores EMI | **Concepto central sin definir**: el concepto que nombra el título u objetivo no tiene definición con fuente en el marco teórico | cap. 2 contra título y OG | (regla propia por crear) | inferido |
| SEM-05 | revisores EMI | **Algoritmo como caja negra**: técnica o modelo sin ecuaciones ni gráficas por fase | subsecciones que nombran algoritmos | (regla propia por crear) | inferido |
| SEM-06 | revisores EMI | **Validación de un solo sentido**: los expertos valoran la salida, pero nadie la contrasta con los errores reales ya conocidos del caso | juicio de expertos y su anexo, demostración | (regla propia por crear) | inferido |

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
