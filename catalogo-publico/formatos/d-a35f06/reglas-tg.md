# Reglas del docente de TG para el trabajo de grado (carrera de Ingeniería de Sistemas, EMI)

Reglas accionables de formato, redacción, estructura y defensa que el docente de Trabajo de Grado exige y que **causan rechazo** si no se
cumplen. Fuente: clases y apuntes del docente de TG (gestión 2025-2026). El orden de las diapositivas y las medidas del Word están en
`formato.yaml`; el formato de las notas de figura y tabla, en `reglas-formato-notas-tg.md` de `perfil-revisor-tg`.

## 1. Formato del Word (reglas rígidas)

| Regla | Detalle |
|---|---|
| Hoja y márgenes | Carta; márgenes superior 2,54, inferior 2,54, izquierdo 3,0 y derecho 2,54 cm |
| Letra | Arial 12, texto justificado |
| Interlineado | **1,5** en todo el documento; sin espacio «después del párrafo» (0 pt) |
| Sangría | **Sin sangría** al inicio de párrafos; texto alineado a la izquierda del margen |
| Entre secciones | De párrafo a subtítulo de 2.º nivel, **2 Enters**; de subtítulo a párrafo, **1 Enter** |
| Títulos de 3.º y 4.º nivel | Alineados con los márgenes del texto |
| Títulos de capítulo | Sin signos de puntuación al final |
| Ecuaciones | Numeradas en orden, al costado derecho, y citadas por su número |
| Tablas y matriz | Letra tamaño 10 |
| Viñetas | Solo guion simple (`-`); sin círculos gruesos ni números salvo necesidad |
| Notas de figuras y tablas | `Nota.` + descripción + fuente; a la izquierda, al ancho de la imagen, tamaño 10 |
| Índice | Interlineado **simple** (distinto del cuerpo) |
| Bibliografía y anexos | No se enumeran; bibliografía en APA, sangría francesa e interlineado simple |

## 2. Redacción académica

- **Introducción «sin decir el asesino»**: en forma de embudo, de lo general a lo específico; no adelanta la problemática ni la solución tecnológica.
- **Marco teórico sin relleno**: nada de conceptos genéricos de IA que no aporten al sistema; cada párrafo tiene su uso práctico en el diseño y el marco teórico «dialoga» con el resto del proyecto.
- **Autoplagio**: todo trabajo previo del propio autor se cita en APA.
- **Formulación del problema** declarativa (no interrogativa) y sin juicios de valor (evitar «deficiente»).
- **Objetivos específicos** como procesos continuos (analizar, diagnosticar), con un solo verbo principal y **sin paréntesis**.

## 3. Estructura del perfil → Capítulo 1

- Antecedentes académicos: máximo 6 trabajos (3 de la EMI, luego locales, luego internacionales); título en mayúsculas sin negrilla; autor como «Ingeniero»; cada uno con comparación (diferencia y similitud).
- Planteamiento del problema: mínimo 3 páginas, de lo general a lo particular; identificación con árbol de problemas (anexo).
- Justificación: al menos técnica, económica y social.
- Límites y alcances: dónde empieza y dónde acaba el software; es la mejor defensa ante el tribunal.
- Metodología: enfoque, tipo, método, técnicas y cuadro metodológico.
- Cronograma con herramienta de gestión y **hitos** (cada defensa es un hito), no un cuadro simple.
- Temario tentativo a doble nivel (capítulo y subtítulo).

## 4. Marco práctico (Capítulo 3)

- No hay Capítulo 4: la evaluación técnica y económica van **dentro** del Capítulo 3.
- Cada sección del Capítulo 3 corresponde a **un objetivo específico**; el desarrollo va en sprints (Scrum) y, si hay IA o PLN, Scrum con CRISP-DM anidado.
- Cada sprint se describe de forma narrativa, no como una colección de código.

## 5. Matriz de consistencia

- Es el instrumento de trazabilidad: **el contenido del Capítulo 2 queda delimitado por la matriz**; toda teoría listada tiene su sección homóloga.
- Sin celdas ni filas vacías o con guiones (si una fila no se usa, se borra); columnas de la ficha = acciones del objetivo; sin paréntesis en objetivos.
- «Revistas» solo científicas indexadas; letra 10 y sin sangría.

## 6. Evaluación técnica y económica

- Técnica: calidad ISO y puntos de función. Costo: COCOMO II, puntos de función o tiempo × desarrolladores × sueldo.
- Viabilidad: relación costo-beneficio (IR = BN/CT, viable si IR > 1); VAN y TIR para el largo plazo.

## 7. Conclusiones y recomendaciones

- Una conclusión (al menos un párrafo) **por cada objetivo específico**; cero información nueva, sin citas y sin repetir el marco teórico.
- Recomendaciones: metodológicas, académicas y prácticas (dirigidas al caso de estudio).

## 8. Defensa

- No se lee (resta puntos): imágenes, esquemas y diagramas.
- Diapositiva de cumplimiento de objetivos con el **rango de páginas exacto** de la evidencia de cada uno (por ejemplo, «OE3: págs. 62-80»).
- Llevar un **video grabado** del sistema funcionando: una caída del servidor en vivo puede costar la reprobación.
