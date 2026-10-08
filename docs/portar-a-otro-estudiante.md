# Portar las skills a otro estudiante

Las skills son el **motor**; cada estudiante tiene su **vault** con sus datos. Nada del TG de un estudiante vive en
el repo: si aparece, es un error (el pre-commit y `scripts/auditar-pii.sh` lo frenan con `.pii-denylist.local`, que
también acepta los términos del dominio de tu proyecto).

## Qué es de quién

| Vive en el repo (genérico) | Vive en el vault (de cada estudiante) |
| --- | --- |
| Reglas de forma de la EMI, modos, motores de la defensa | `proyecto.yaml`: datos del TG y convenciones (producto, paleta, terminología, fases) |
| Plantillas (`assets/`) y modelos `*.example.*` | `sources/<slug>.md`: el TG extraído |
| Clases genéricas de corrección (`matriz-generalizaciones`) | Perfiles de sus evaluadores y docentes, informes, reglas propias |
| Ejemplos marcados «proyecto de referencia» | `sources/_propuestas/DEFENSA/`: los YAML y entregables de su defensa |

## Arrancar con otro TG

```bash
./install.sh --destino ~/vault-de-ana --docx "~/Ana/TRABAJO DE GRADO.docx" [--docentes-desde ~/otro-vault]
```

1. El instalador crea el vault, extrae el TG, arma `proyecto.yaml` (carátula, objetivos, anexos, figuras) y la
   carpeta de defensa. Avisa qué quedó `PENDIENTE`.
2. Con el agente: **modo inicializar** (`skills/asistente-trabajo-de-grado/references/inicializar.md`).
3. `skills/perfil-revisor-tg/config.md` es **uno por clon**: si manejás varios vaults desde el mismo clon, cambiá
   `data_dir`, `estudiante` y `evaluadores` al pasar de uno a otro (o usá un clon por estudiante).

## Tipo de proyecto

El contenido se adapta; la estructura de la EMI no. Sin producto de software no hay manual de usuario, capturas ni
demostración, y la ruta crítica es la del proceso del caso de estudio. Con sprints o fases, `generar-entregables-tesis`
lee las fases de `proyecto.yaml`.
