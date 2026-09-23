---
title: Jerarquía de autoridad y cadena de escalación (trabajos de grado)
type: politica
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
tags:
  - docentes
  - revisores
  - jerarquia
  - politica
---

# Jerarquía de autoridad y cadena de escalación

> Fuente de verdad **única** que vincula las skills del área. Todas la referencian, ninguna la
> reescribe. Define **quién manda cuando las fuentes chocan** y **a quién escalar una duda**.

## 1. Jerarquía de autoridad (qué prevalece)

En lo **específico** que corrige o decide:

```
norma de la institución
      <   tutor
      <   evaluadores + docentes
```

- **Los evaluadores y los docentes van juntos arriba**: casi nunca chocan, porque el docente da
  **forma** y los evaluadores revisan **fondo y coherencia**. Si chocan, se documenta y se pregunta.
- **El tutor queda último**: sus consejos valen salvo que un evaluador o un docente digan lo
  contrario.
- **La norma de la institución** es el fondo institucional sobre el que se apoya todo.

> [!note] Matiz importante
> No es una línea plana: el **evaluador gana en su punto concreto**, pero el **docente aporta
> contexto** que el evaluador no trata. Un dato del docente que no contradiga al evaluador sigue
> valiendo como complemento.

## 2. Cadena de escalación (a quién consultar ante una duda)

| Situación | Quién responde |
|---|---|
| Duda de contenido del trabajo | Tu **docente** principal → su material es la base |
| Tu docente no resuelve / necesitás 2ª opinión | Un **docente transversal** (`ambito: general`) |
| Un evaluador corrigió algo concreto | El **evaluador** (gana sobre docentes y norma) |
| Cuestionás un punto | Se escala por esta misma cadena |

## 3. Regla anti-contradicción (obligatoria)

Cuando chocan dos fuentes (norma ↔ evaluador, evaluador ↔ evaluador, evaluador ↔ tutor,
docente ↔ evaluador):

1. **NO se aplica nada en silencio.**
2. Se documenta en `wiki/contradictions/` con `status: abierto`.
3. Se **pregunta al usuario** qué prevalece.
4. Solo tras su decisión → `status: resuelto` con `resolution` (fuente, fecha, resultado).

## 4. Docentes externos y casos límite

**Tier de segunda opinión.** Los docentes con `origen: informes-revisores` **no** evalúan tu trabajo:
sus criterios salen de informes a otros estudiantes. Nunca emiten `confirmado` sobre tu trabajo
—techo `inferido`— y **no se pasan** a `scripts/cobertura-fuentes.sh`, que es el gate de obligaciones.

**Convergencia entre externos.** Que dos docentes externos coincidan **no** sube el techo (sigue
`inferido`). Sí cuenta como segunda ocurrencia para promover el criterio a regla propia.

**Sin evaluadores propios.** Si solo tenés criterios de docentes externos, no hay desempate posible:
todo queda `inferido`, el modo revisar **no puede cerrar propuestas** y hay que completar los
evaluadores propios primero. El sistema sabe quiénes son por `config.local.md` → `evaluadores:`,
nunca por el nombre del archivo.

## Relaciones
- [[_moc-docentes]]
- [[indice]]
- [[reglas-propias]]
