# Portar las skills a otro estudiante

Las skills son el **motor**; cada estudiante tiene su **vault** con sus datos. Nada del TG de un estudiante vive en
el repo: si aparece, es un error (el pre-commit y `scripts/auditar-pii.sh` lo frenan con `.pii-denylist.local`, que
también acepta los términos del dominio de tu proyecto).

## Qué es de quién

| Vive en el repo (genérico) | Vive en el vault (de cada estudiante) |
| --- | --- |
| Reglas de forma de la EMI, modos, motores de la defensa | `proyecto.yaml`: datos del TG y convenciones (producto, paleta, terminología, fases) |
| Plantillas (`assets/`) y modelos `*.example.*` | `sources/<slug>.md`: el TG extraído |
| Clases genéricas de corrección (`matriz-generalizaciones`) | Lo `confirmado` de sus evaluadores, informes, reglas propias |
| — | Perfil de cada docente en el **catálogo público sin nombres** (`catalogo-publico/`), enlazado solo para sus evaluadores; el nombre, solo en su vault |
| Ejemplos marcados «proyecto de referencia» | `sources/_propuestas/DEFENSA/`: los YAML y entregables de su defensa |

## Arrancar con otro TG (resumen; el detalle está en `docs/instalacion.md`)

```bash
./install.sh --destino ~/vault-de-ana --docx "~/Ana/TRABAJO DE GRADO.docx" [--catalogo-publico]
```

1. El instalador crea el vault, extrae el TG, arma `proyecto.yaml` (carátula, objetivos, anexos, figuras) y la
   carpeta de defensa. Avisa qué quedó `PENDIENTE`.
2. Con el agente: **modo inicializar** (`skills/asistente-trabajo-de-grado/references/inicializar.md`).
3. `skills/perfil-revisor-tg/config.md` es **uno por clon** y lo escribe `install.sh` (y `asignar_evaluador.py --sync`): un clon por
   estudiante.

## Tipo de proyecto

El contenido se adapta; la estructura de la EMI no. Sin producto de software no hay manual de usuario, capturas ni
demostración, y la ruta crítica es la del proceso del caso de estudio. Con sprints o fases, `generar-entregables-tesis`
lee las fases de `proyecto.yaml`.

## Evaluadores y correcciones

- `asignar_evaluador.py <vault> --rol tutor|revisor_1|revisor_2|docente_tg --docente <slug>` vincula a cada uno (o
  `--por-asignar`, típico del Revisor 2) y muestra su predicción inicial. `--check` verifica que solo estén los propios.
- Si te reasignan un revisor, se vuelve a correr: el anterior deja de leerse en tu vault.
- «Registrar corrección» (skill `perfil-revisor-tg`) deja lo recibido como `confirmado` en tu vault y, si es
  generalizable, suma al perfil del docente en el catálogo (estudiantes por iniciales).
