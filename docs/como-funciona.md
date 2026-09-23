# Cómo funciona

## El problema que ataca

Una corrección de trabajo de grado se cae siempre en el mismo lugar:

1. El revisor señala algo **que ya te había señalado** antes.
2. El revisor y el tutor piden cosas que **se contradicen** y descubrís el choque recién en la
   entrega.
3. Corregís a ciegas: no sabés cuál de los dos criterios aplica en ese punto concreto.
4. Terminás aplicando el promedio de todos los criterios, que no es el criterio de ninguno.

Estas skills atacan los cuatro modelando **a cada evaluador por separado**.

## Los tres estados de fiabilidad

Todo punto del sistema —lo que un evaluador valora, lo que no le gusta, un error que señala, una
regla propia— lleva **uno** de estos estados:

| Estado | Significa | Qué podés hacer con él |
|---|---|---|
| `confirmado` | El evaluador lo dijo o lo marcó explícitamente, y hay cita | Aplicarlo directo |
| `inferido` | Es una hipótesis, propia o del agente, sin validar | Se **sugiere**, nunca se exige |
| `abierto` | No hay explicación | Se **pregunta**. No se adivina |

Esto existe por una razón práctica: el error más caro no es equivocarse de criterio, es
**inventarle la intención a un evaluador** y construir sobre esa invención.

## Quién manda cuando dos criterios chocan

```
norma de la institución
        <   tutor
        <   evaluadores + docentes
```

- **Los evaluadores y el docente van juntos arriba**, porque casi nunca chocan: el docente da forma
  y los evaluadores revisan fondo y coherencia. Si chocan, se documenta y se pregunta.
- **El tutor queda último**: sus consejos valen salvo que un evaluador diga lo contrario.
- **Los docentes que no te evalúan no manda nadie.** Sus criterios se guardan en un nivel aparte,
  se consultan solo cuando nadie de arriba resuelve, y **nunca** pueden convertirse en obligación.

Cuando dos fuentes se contradicen, el sistema **no resuelve en silencio**: escribe la contradicción
con estado `abierta` y te la pregunta. Preferís una pregunta incómoda a una corrección inventada.

## Los recorridos

| Recorrido | Cuándo | Qué hace |
|---|---|---|
| **Perfilar** | Querés modelar a un evaluador | Arma o actualiza su perfil a partir de informes, feedback oral, marcas al margen, o de cómo lo describís vos |
| **Ingerir informe** | Tenés informes de revisión | Los lee (con OCR si son escaneos), actualiza el perfil que los firma y deriva la clase de error para predecirla después |
| **Revisar** | Querés corregir una sección | Contrasta la sección contra los perfiles y entrega un plan con la justificación de cada cambio |
| **Tribunal** | Querés saber qué te van a observar | Simula a cada evaluador por separado y después cruza sus hallazgos |

## Por qué no "revisa todo a la vez"

Si mezclás todos los criterios en una sola pasada, obtenés el promedio de todos, que no es el
criterio de ninguno. El recorrido **tribunal** asigna a cada perfil un revisor distinto y después
los hace cruzar: lo que no se sostenga con evidencia se degrada a `inferido`.

## El cuidado con los falsos positivos

Predecir correcciones tiene un riesgo obvio: inventar correcciones que nadie te va a pedir, y
hacerte perder tiempo. Los criterios de docentes que **no** te evalúan pasan por tres puertas:

1. **Evidencia** — cita literal del informe. Sin cita, no entra.
2. **Transferibilidad** — solo se caza lo metodológico; lo que es de forma o de otro dominio, no.
3. **Autoridad** — si contradice algo que tu evaluador confirmó, no se caza: se abre una
   contradicción.

Y además: **un hallazgo externo por sección como máximo**, solo en la sección análoga al caso donde
ese docente aplicó el criterio, y una verificación final de que lo señalado **no exista ya** en tu
documento (puede estar en un anexo).

## Qué NO hace

- No valida formato ni APA 7: eso es otro eje y otra skill.
- No escribe tu trabajo: entrega propuestas.
- No completa datos que no tiene: si hay que medir algo, te lo dice; no lo inventa.
- No te dice que está todo bien. Si no encuentra nada, lo declara explícitamente por perfil.
