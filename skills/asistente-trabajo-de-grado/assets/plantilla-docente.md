---
title: Plantilla de docente
type: plantilla
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: activo
tags:
  - docentes
  - plantilla
---

# Plantilla de docente

Copiar a `wiki/docentes/<slug>.md`, completar y agregar la fila en [[_moc-docentes]].

## Variante A — docente con material propio (clases, audios, PDF)

```yaml
---
title: <Nombre del docente>
type: docente
created: <fecha>
updated: <fecha>
status: activo
nombre: <Nombre Apellido>
rol: <Docente / Tutor / Revisor>
origen: notebooklm      # o el canal del que salió el material
canales: [audio, pdf, apuntes]
ambito: general         # general | especifico — NUNCA un tercer valor
temas: [<qué explica>]
fuente_ids: [<ids de las fuentes>]
tags:
  - docentes
  - trabajos-grado
---
```

## Variante B — docente del que solo tenés informes de revisión

```yaml
---
title: <Nombre del docente>
type: docente
created: <fecha>
updated: <fecha>
status: activo
nombre: <Nombre Apellido>
rol: Docente revisor (informes de trabajo de grado)
origen: informes-revisores
ambito: general         # `general` ya significa "no es norma de tu trabajo específico"
informes: <cantidad>
procedencia: informe    # informe | oral | rayado | autodescrito | analogia-tg
tags: [docentes, trabajos-grado, general, revisor-externo]
---
```

Ver `perfil-revisor-tg/assets/docente.md` para la variante B completa, con la tabla de criterios.

## Cuerpo

# <Nombre del docente>

## Ámbito
- `general` (metodología transversal) o `especifico` (contenido del trabajo).

## Temas que explica
- ...

## Fuentes
- `<fuente_id>`: título (tipo).

## Reglas o criterios destilados
- (Volcar acá lo destilado. Si es de informes, cada fila lleva cita y estado.)

## Relaciones
- [[_moc-docentes]]
