# tg-skills

Skills para **revisar y corregir un trabajo de grado con los criterios de tus propios
evaluadores** (revisor 1, revisor 2, tutor y docentes), en vez de con consejos genéricos.

> **Estado:** el motor y el instalador están listos. Falta el paso de migración del entorno del
> autor (`docs/migracion-desde-vault.md`), que es opcional para quien instala desde cero.

## Qué problema resuelve

Una corrección de trabajo de grado se cae siempre en el mismo lugar: el revisor señala algo que **ya
te había señalado**, o te pide algo que **contradice** lo que te pidió el tutor. Estas skills
modelan a cada evaluador por separado, guardan de dónde sale cada criterio y se niegan a inventar la
intención de nadie.

## Las cinco skills

| Skill | Qué hace |
|---|---|
| `perfil-revisor-tg` | Perfila evaluadores, ingiere sus informes, predice qué van a corregir y corre las pasadas de revisión del **fondo** |
| `asistente-trabajo-de-grado` | Norma, estructura y coherencia del trabajo; catálogo de docentes y consulta de sus explicaciones |
| `generar-entregables-tesis` | Entregables por sprint: figuras, tablas, mockups y Word |
| `extraer-doc-tesis` | Extrae el Word/PDF al vault con reporte de validación y trazabilidad de citas |
| `extraer-conversaciones-ias` | Destila criterio de docentes desde conversaciones previas con IAs, **auditando** su fiabilidad |

## Cómo está armado: motor y datos

- **Este repo es el motor.** Contiene la lógica, las plantillas y los gates de verificación. No
  contiene ni un dato tuyo.
- **Tu vault es el dato.** Los perfiles de tus evaluadores, tus reglas y los informes viven en tu
  propio repositorio privado (patrón `sources/` de solo lectura + `wiki/` editable).
- El único acoplamiento entre los dos son unas pocas claves en `config.local.md` y `.env.local`,
  ambas fuera de git.

## Instalación

```bash
git clone <url> "$HOME/tg-skills"
cd "$HOME/tg-skills"
./install.sh            # symlinks a tus agentes + crea el vault desde vault-template/
```

El instalador es idempotente: nunca sobrescribe un archivo que ya exista. Para ver qué haría sin
escribir nada: `./install.sh --check`.

### Documentación

- `docs/como-funciona.md` — el modelo mental: estados de fiabilidad, jerarquía, recorridos y qué
  **no** hace.
- `docs/arquitectura.md` — motor y datos, el contrato de config, los gates y el guard de predicción.
- `docs/migracion-desde-vault.md` — solo si venís de tener las skills dentro de un vault.
- `docs/portar-a-otro-estudiante.md` — pendiente.

## Límites honestos

- **Solo fondo.** Coherencia, contenido, evidencia, redundancia y redacción. No valida formato ni
  APA 7.
- **No escribe tu trabajo.** Entrega propuestas; el Word lo tocás vos.
- **No adivina.** Todo criterio lleva su estado: `confirmado` (el evaluador lo dijo), `inferido`
  (hipótesis) o `abierto` (hay que preguntar). Si no puede citar de dónde sale, no entra.
- **Un docente que no te evalúa no manda.** Sus criterios son segunda opinión, nunca norma, y no
  pueden convertirse en obligación.

## Relación con `emi-professor-skill`

Son repos hermanos y distintos: `emi-professor-skill` modela **cómo enseña y pregunta un docente**;
este modela **cómo evalúa un revisor un trabajo de grado**. Comparten convenciones deliberadamente
(config privada fuera de git, datos en un workspace propio, guard anti-PII en el pre-commit,
provenance explícito) para que un usuario pueda aprender una sola vez.

## Licencia

MIT. Ver `LICENSE`.
