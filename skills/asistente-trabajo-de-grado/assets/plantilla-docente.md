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

# Plantilla de docente (catálogo compartido)

Un docente nuevo se crea **en el catálogo** (`$DOCENTES_EMI/docentes/<slug>.md`, por defecto
`~/.local/share/tg-docentes`), no en el vault: así lo que un estudiante registra le sirve a cualquier otro que
tenga al mismo docente. Después se vincula desde el vault con
`python3 scripts/asignar_evaluador.py <vault> --rol <rol> --docente <slug>`.

```yaml
---
title: <Grado y nombre del docente>
type: docente
created: <fecha>
updated: <fecha>
status: activo
revisa: <capítulos o temas que suele revisar>
alcance: fondo          # fondo | forma | ambos
nombre: <Nombre Apellido>
rol: <Docente de TG / Docente revisor / Tutor>
canales: [informe]      # informe | audio | pdf | apuntes | oral
tags:
  - docentes
  - trabajos-grado
---
```

## Cuerpo

1. Callout «Cómo se usa este perfil» (copiar del de cualquier docente del catálogo).
2. `## Criterios de fondo` — tabla `| ID | Criterio | Estado | Ocurrencias | Fuente |`. El ID lleva un prefijo propio
   del docente (`MAG1`, `YAN3`): **nunca** numérico, para que el gate de cobertura de un vault no lo tome como
   obligación. `Ocurrencias` cuenta informes o sesiones distintas: desde 2 es patrón. La fuente cita al estudiante
   **por iniciales** («informe a D.P., MP 15/05») y nunca enlaza notas de un vault.
3. `## Criterios de forma` — fuera del alcance de las skills de fondo; se anotan igual.
4. `## Cómo trabaja` — plantilla de sus informes, qué pide primero, cómo concede.
5. `## Historial de roles` — `| Rol | Estudiante | Desde |` (lo completa `asignar_evaluador.py`).
6. `## Relaciones` — solo `[[_moc-docentes]] · [[jerarquia-autoridad]]`.
