---
title: Protocolo del tribunal — predicción por perfil con delegados cruzados
type: protocolo
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
sources: []
tags:
  - revisores
  - tribunal
  - prediccion
  - delegacion
aliases:
  - Protocolo del tribunal
  - Modo tribunal
---

# Protocolo del tribunal

> [!important] Qué es esto
> Cómo se predice **qué corregiría cada evaluador** sobre una sección. No reemplaza al modo
> revisar: lo complementa. El modo revisar responde "¿qué está mal?"; el tribunal responde
> "¿qué me van a corregir, y quién?".

## 1. Por qué existe

Los perfiles ya saben cómo revisa cada evaluador y la [[matriz-generalizaciones]] ya deriva clases
de error. Lo que faltaba era **aplicarlos por separado**, uno a la vez: una sola pasada mezcla los
criterios y termina prediciendo el promedio de todos, que no es el criterio de ninguno.

## 2. Cuándo se usa

- El pedido es "modo tribunal", "predecí las correcciones", "qué diría cada revisor".
- Antes de una entrega, para saber qué van a observar **antes** de que lo observen.
- Cuando dos perfiles parecen empujar en direcciones opuestas y hay que verlo explícito.

No se usa para producir el corregido (eso es modo revisar) ni como sustituto de leer el perfil.

## 3. Asignación de perfiles a delegados

Un **brief por evaluador**, nunca el mismo texto neutro a todos. Dos o más delegados, cada uno con
un perfil distinto. Si solo hay un canal disponible, el tribunal **no aplica**: se delega normal.

**Los docentes que no te evalúan quedan `N/A` por default**: son segunda opinión, no norma. Solo
entran si el usuario lo pide, y en ese caso van como brief aparte, con el tope de 1 hallazgo por
sección y las tres puertas del guard.

## 4. Armado del brief (uno por evaluador)

1. Leer su perfil (`Revisor_N.md`, `Tutor.md` o `wiki/docentes/<slug>.md`).
2. Leer `reglas-propias.md` y `matriz-generalizaciones.md`.
3. **Extraer solo las filas aplicables a la sección** (no el perfil entero, no el vault entero).
4. El brief declara: perfil, ámbito, capítulos que revisa, sus filas aplicables, sus clases de
   error derivadas y sus dudas `abiertas`.

Cada fila entra con su **estado de fiabilidad** y se propaga al hallazgo: un punto `abierto` no se
puede usar como exigencia.

## 5. Las dos rondas

**Ronda 1 — revisión por perfil.** Cada delegado revisa la sección *como ese evaluador* y devuelve,
por hallazgo:

```
ubicación | hallazgo | perfil que lo motiva | evidencia | estado (confirmado|inferido|abierto)
```

Sin evidencia, el hallazgo no entra.

**Ronda 2 — cruce.** A cada delegado se le pasa la salida **verbatim** del otro y debe **confirmar o
refutar cada hallazgo con evidencia**. Lo que no se sostiene se degrada a `inferido` o `abierto`;
nunca se borra en silencio.

**Tope: 2 rondas.** Si los dos sostienen su punto, se corta y decide el usuario.

## 6. Síntesis y puerta de cobertura

Matriz final: `perfil | ubicación | hallazgo | estado | acción | justificación`.

**Puerta de cobertura de perfiles (bloqueante)**: una fila por cada perfil, con `verificado: dónde`
(brief enviado + hallazgos) o `N/A: motivo`. **Un perfil sin fila = no auditado = prohibido
presentar la salida al usuario.**

## 7. Contradicciones entre perfiles

No se resuelven por mayoría ni por jerarquía automática. Se documentan en
`wiki/contradictions/` con estado `abierto` y se pregunta al usuario. La jerarquía solo desempata.

## 8. Transporte (opcional)

Si tenés un orquestador de agentes (por ejemplo `herdr` con paneles), el transporte concreto —cómo
se envía el brief, cómo se maneja un delegado que pide permiso, el fallback a archivo si la salida
se corta— va en un anexo de tu propia instalación. **No es una dependencia dura**: el protocolo
funciona igual con dos sesiones de agente separadas, o con dos revisiones hechas a mano y cruzadas
por vos.

## 9. Reglas duras

1. **Vigencia primero**: sin el sha del Word verificado, no se arma ningún brief (un tribunal sobre
   una extracción vieja predice correcciones ya aplicadas).
2. **Un brief por perfil**, nunca uno neutro compartido.
3. **Sin evidencia no hay hallazgo.**
4. **Tope de 2 rondas.**
5. **Puerta de cobertura** obligatoria antes de presentar.
6. **Nunca auto-aplicar**: la salida es propuesta; el Word y el vault no se tocan.

## Relaciones
- [[indice]]
- [[reglas-propias]]
- [[matriz-generalizaciones]]
- [[jerarquia-autoridad]]
