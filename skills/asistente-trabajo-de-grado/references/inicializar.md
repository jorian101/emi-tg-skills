# Modo inicializar — del TG del estudiante a un vault listo

Invocación: «inicializá el vault desde mi TG», «arrancá con mi trabajo de grado», o después de `install.sh --docx`.
Sirve para **cualquier** TG de la EMI: con o sin software, con o sin sprints, de cualquier carrera y caso de estudio.
El vault del proyecto de referencia es un ejemplo de resultado, nunca una plantilla de contenido.

## 0. Precondición (determinística, ya la hace el instalador)

```bash
./install.sh --destino <vault> --docx <TG.docx> [--docentes-desde <otro-vault>]
```

Eso extrae el TG (`sources/<slug>.md`), crea `proyecto.yaml` con lo que el TG dice de sí mismo (carátula, objetivos,
antecedentes institucionales, problema, anexos, figuras, tablas) y la carpeta `sources/_propuestas/DEFENSA/` con
`defensa.json`. Si el vault ya existía: `python3 scripts/inicializar_desde_tg.py <vault> <slug>`.

## 1. Completar `proyecto.yaml` (el agente, citando el TG)

Regla dura: **cada valor con su sección del TG** (`seccion: "1.3.1. Identificación del Problema"`); lo que el TG no
dice queda `PENDIENTE` y se pregunta al usuario. Nunca se copia un valor del proyecto de referencia.

| Campo | De dónde sale |
| --- | --- |
| `tg.institucion_caso.nombre/sigla/funcion` | antecedentes institucionales; la función es la de la **unidad** donde se aplica el trabajo |
| `tg.institucion_caso.mision/vision` | si el TG las cita (con su fuente); si no, preguntar al usuario la fuente oficial |
| `tg.problema.causa/efecto` | árbol de problemas (anexo) e identificación del problema. **Causa** = lo que origina el problema; **efecto** = su consecuencia medible. El objetivo general debe atacar la causa (ver criterio de revisores) |
| `tg.revisores` | preguntar al usuario (la carátula no los trae); con eso se completa `config.md` → `evaluadores:` |
| `convenciones.producto` | cómo nombra el TG a su producto («sistema», «asistente», «plataforma»…): el término más usado en el cap. 3 |
| `convenciones.hilo_conductor` | el eje técnico que el objetivo general promete construir |
| `convenciones.terminologia` | solo si hay código (`$CODE_REPO`): pares `termino_codigo: termino_documento` donde difieren |
| `convenciones.terminos_prohibidos` / `terminos_dificiles` | preguntar al usuario / términos del área que un no especialista no entiende |
| `convenciones.paleta_uml` | la paleta institucional del caso de estudio (preguntar; si no hay, la neutra del ejemplo) |
| `entregables.seccion_desarrollo/fases/calendario` | índice del TG: la sección de desarrollo y sus subsecciones (sprints, fases o iteraciones) con fechas de sus tablas de planificación |

## 2. Docentes y evaluadores

- Si el usuario comparte docentes con otro vault (mismo tribunal o carrera), `--docentes-desde` trae sus perfiles a
  `wiki/docentes/` como **segunda opinión** (predicen, no deciden). Agregar cada uno al catálogo `_moc-docentes.md`.
- Los evaluadores propios (`wiki/revisores/Revisor_N.md`, `Tutor.md`) empiezan vacíos: se llenan con sus informes
  (`perfil-revisor-tg`, «ingerir informe»), nunca copiando el perfil de un docente de otro estudiante.

## 3. Modelos de la defensa (en `DEFENSA/`, desde los `assets/defensa/*.example.*`)

Se arman con el **contenido de este TG** y se adaptan al **tipo de proyecto**:

| Entregable | Archivo | Si el TG no tiene software |
| --- | --- | --- |
| Diapositivas | `diapositivas/diapositivas.yaml` → `diapositivas.py crear` | sin demostración ni capturas; resultados con las tablas del TG |
| Tríptico/bíptico | `triptico-biptico/triptico.yaml` | igual (misión, visión, función, problema, objetivos, resultados) |
| Ruta crítica | `ruta-critica/ruta-critica.yaml` (formato `flujo.example.yaml`) | la del **proceso del caso** con el aporte del trabajo |
| Manual de usuario | `MANUAL-A-COPIAR/manual.yaml` + `manual-de-usuario.md` | no existe: se quita de `defensa.json` |
| Diagramas animados | `diagramas/escenas_0N_*.py` (uno por flujo que el TG explica) | el flujo del proceso o del modelo propuesto |
| Segunda pantalla | `TV/tv.yaml` | solo diagramas animados y la ruta crítica |
| Anexos con QR | `ANEXOS-QR/manifiesto-anexos.json` | igual |
| Guion | `GUION/guion-defensa.md` (`guion.plantilla.md`) | igual, sin plan de demostración |

- **Anexos con QR:** mostrar la lista de `tg.anexos` y **preguntar cuáles llevan QR** (marcar `qr: true`); el manifiesto
  sale de esa selección.
- **Diapositivas:** seguir la estructura de [defensa/diapositivas.md](defensa/diapositivas.md) y su tope de 90 palabras;
  título, objetivos y formulación del problema literales; cada figura o tabla con su anexo.
- Dejar en `PENDIENTES-DEFENSA.md` todo lo que falte (fotos, cartas, logos, capturas): no se inventa ni se rellena.

## 4. Cierre

1. `bash scripts/verificar-enlaces.sh` en 0 (el TG extraído cuelga de `index.md`).
2. `python3 $S/notas_vault.py --dir DEFENSA` (hub de defensa en el vault).
3. Resumen al usuario: qué quedó `PENDIENTE` en `proyecto.yaml` y qué preguntas faltan responder.
