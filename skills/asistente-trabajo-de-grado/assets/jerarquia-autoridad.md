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

## 0. Quiénes cuentan: solo tus evaluadores identificados

Para tu TG cuentan **solo** quienes te evalúan: tu **tutor**, tus **revisores** (el Revisor 2 suele asignarse
después) y tu **docente de TG** (el que dicta la materia; puede variar de un paralelo a otro). Cada uno se vincula
desde su perfil en `wiki/revisores/` (campo `docente:` con el slug del docente) al catálogo compartido de docentes con
`scripts/asignar_evaluador.py`. **Los demás docentes del catálogo se ignoran**, aunque tengan criterios parecidos:
pueden contradecirse y no te evalúan. Mientras un evaluador está `por-asignar`, solo valen las clases genéricas
`SEM-NN` de la matriz de generalizaciones.

## 1. Jerarquía de autoridad (qué prevalece)

En lo **específico** que corrige o decide:

```
norma de la institución
      <   tutor
      <   revisores + docente de TG
```

- **Los revisores y el docente de TG van juntos arriba**: casi nunca chocan, porque el docente da
  **forma** (norma EMI, estructura) y los revisores revisan **fondo y coherencia**. Si chocan, se documenta y
  se pregunta.
- **El tutor queda último**: sus consejos valen salvo que un revisor o el docente digan lo contrario.
- **La norma de la institución** es el fondo institucional sobre el que se apoya todo.
- Entre lo propio, **lo `confirmado`** (lo que ese evaluador te corrigió a vos) **manda sobre lo predicho** de su
  perfil del catálogo (`inferido (predicción)`).

> [!note] Matiz importante
> No es una línea plana: el **revisor gana en su punto concreto**, pero el **docente aporta
> contexto** que el revisor no trata. Un dato del docente que no contradiga al revisor sigue
> valiendo como complemento.

## 2. Qué suele revisar cada rol (dirige la predicción)

| Rol | Suele revisar | Alcance |
|---|---|---|
| Docente de TG | todo el documento contra la norma EMI: formato, estructura del perfil y de los capítulos, matriz de consistencia, defensa | forma (y estructura) |
| Revisor 1 / Revisor 2 | marco práctico, coherencia con los objetivos, números y validación, evaluación técnica y económica, conclusiones | fondo |
| Tutor | alcance, estructura, marco teórico, avance; aconseja | fondo, como consejo |

El campo `revisa:` del perfil de cada docente en el catálogo precisa esto para esa persona. Una predicción se aplica
**solo en los capítulos que ese evaluador suele revisar**; fuera de ellos no se caza.

## 3. Cadena de escalación (a quién consultar ante una duda)

| Situación | Quién responde |
|---|---|
| Duda de forma o de estructura | Tu **docente de TG** → su material es la base |
| Un revisor corrigió algo concreto | El **revisor** (gana sobre docente y norma en ese punto) |
| Duda de alcance o de avance | Tu **tutor** |
| Cuestionás un punto | Se escala por esta misma cadena, siempre entre tus evaluadores |

Una segunda opinión de un docente que **no** te evalúa solo se consulta si el usuario la pide explícitamente, y
nunca entra a las propuestas como criterio.

## 4. Regla anti-contradicción (obligatoria)

Cuando chocan dos fuentes (norma ↔ revisor, revisor ↔ revisor, revisor ↔ tutor, docente ↔ revisor):

1. **NO se aplica nada en silencio.**
2. Se documenta en `wiki/contradictions/` con `status: abierto`.
3. Se **pregunta al usuario** qué prevalece.
4. Solo tras su decisión → `status: resuelto` con `resolution` (fuente, fecha, resultado).

## 5. Casos límite

**Sin evaluadores identificados.** Todo queda `inferido` desde las clases `SEM-NN`; el modo revisar **no puede
cerrar propuestas** y se avisa al estudiante que identifique a sus evaluadores. El sistema sabe quiénes son por
`config.md` → `evaluadores:` y por el `docente:` de cada perfil, nunca por el nombre del archivo.

**Cambio de evaluador.** Si te reasignan un revisor, `asignar_evaluador.py` desvincula al anterior: su perfil deja
de leerse en tu vault (lo que te corrigió queda como historial en tu perfil de revisor).

## Relaciones
- [[_moc-docentes]]
- [[indice]]
- [[reglas-propias]]
