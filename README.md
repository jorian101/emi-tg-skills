# emi-tg-skills

Skills para **revisar y corregir un trabajo de grado con los criterios de tus propios
evaluadores** (revisor 1, revisor 2, tutor y docentes), en vez de con consejos genéricos.

> **Estado:** el motor y el instalador están listos para instalar desde cero (ver más abajo).

## Qué problema resuelve

Una corrección de trabajo de grado se cae siempre en el mismo lugar: el revisor señala algo que **ya
te había señalado**, o te pide algo que **contradice** lo que te pidió el tutor. Estas skills
modelan a cada evaluador por separado, guardan de dónde sale cada criterio y se niegan a inventar la
intención de nadie.

## Las cuatro skills

| Skill | Qué hace |
|---|---|
| `perfil-revisor-tg` | Perfila evaluadores, ingiere sus informes, predice qué van a corregir y corre las pasadas de revisión del **fondo** |
| `asistente-trabajo-de-grado` | Norma, estructura y coherencia del trabajo; catálogo de docentes y consulta de sus explicaciones; **modo defensa**: diapositivas, tríptico, artículo, manual, anexos con QR, ruta crítica, diagramas animados y capturas, todo derivado del documento y enlazado en el vault |
| `generar-entregables-tesis` | Entregables por sprint: figuras, tablas, mockups y Word |
| `extraer-doc-tesis` | Extrae el Word/PDF al vault con reporte de validación y trazabilidad de citas |

## Cómo está armado: motor y datos

- **Este repo es el motor.** Contiene la lógica, las plantillas y los gates de verificación. No
  contiene ni un dato tuyo.
- **Tu vault es el dato.** Los perfiles de tus evaluadores, tus reglas y los informes viven en tu
  propio repositorio privado (patrón `sources/` de solo lectura + `wiki/` editable).
- El único acoplamiento entre los dos son unas pocas claves en `config.local.md` y `.env.local`,
  ambas fuera de git.

## Instalación

```bash
git clone <url> "$HOME/emi-tg-skills"
cd "$HOME/emi-tg-skills"
./install.sh --destino ~/mi-vault --docx ~/TRABAJO-DE-GRADO.docx --code-repo ~/mi-proyecto
```

Eso deja tu **vault como un repositorio nuevo** (con su pre-commit y primer commit; `--remoto <nombre>` crea el repo
privado en GitHub, sin push), tu TG extraído, las skills enlazadas a tu agente y el repo de tu proyecto conectado.
Detalle, otra máquina y problemas frecuentes: [`docs/instalacion.md`](docs/instalacion.md).

Después, tres pasos con tu agente:

1. **«inicializá el vault desde mi TG»** — completa `proyecto.yaml` y los modelos de la defensa citando tu TG
   (pregunta lo que el TG no dice: revisores, qué anexos llevan QR).
2. **«ingerir informe»** y **«registrar corrección»** con cada revisión — arma el perfil de cada evaluador.
3. **modo defensa** — diapositivas, tríptico, ruta crítica, manual, anexos con QR, diagramas animados y guion.

**Catálogo de docentes (colaborativo, sin nombres).** `catalogo-publico/` trae los perfiles de tutores, revisores y docentes de TG
**sin nombres** (código y huellas); descargarlo es opcional (`--catalogo-publico`) y el nombre de tu docente lo reconocés vos, en tu
máquina. Lo que te corrigen se comparte por **issue abierto a todos** (`scripts/contribuir.py`), sin invitaciones. Los nombres viven solo en el
catálogo privado del mantenedor. Detalle y límites: [`docs/instalacion.md`](docs/instalacion.md).

El instalador es idempotente: nunca sobrescribe un archivo que ya exista. Para ver qué haría sin
escribir nada: `./install.sh --check`.

> **Sobre el nombre del alias.** El repo se llama `emi-tg-skills`, pero el alias con el que tus
> agentes ven las skills se llama `~/.local/share/tg-skills`. Es a propósito: un alias estable
> sobrevive a los movimientos del repo, así que su nombre no se toca aunque el repo se renombre.

### Documentación

- `docs/como-funciona.md` — el modelo mental: estados de fiabilidad, jerarquía, recorridos y qué
  **no** hace.
- `docs/arquitectura.md` — motor y datos, el contrato de config, los gates y el guard de predicción.
- `docs/portar-a-otro-estudiante.md` — qué es del motor, qué es de cada vault y cómo arrancar con otro TG.

## Límites honestos

- **Solo fondo.** Coherencia, contenido, evidencia, redundancia y redacción. No valida formato ni
  APA 7.
- **No escribe tu trabajo.** Entrega propuestas; el Word lo tocás vos.
- **No adivina.** Todo criterio lleva su estado: `confirmado` (el evaluador lo dijo), `inferido`
  (hipótesis) o `abierto` (hay que preguntar). Si no puede citar de dónde sale, no entra.
- **Solo cuentan tus evaluadores.** Tutor, revisores y docente de TG; los demás docentes se ignoran, porque pueden
  contradecirse y no te evalúan.

## Relación con `emi-professor-skill`

Son repos hermanos y distintos: `emi-professor-skill` modela **cómo enseña y pregunta un docente**;
este modela **cómo evalúa un revisor un trabajo de grado**. Comparten convenciones deliberadamente
(config privada fuera de git, datos en un workspace propio, guard anti-PII en el pre-commit,
provenance explícito) para que un usuario pueda aprender una sola vez.

## Contribuir

`main` está protegida: **todo cambio entra por pull request**, no por push directo. Podés abrir
issues aunque no programes — un buen reporte vale tanto como un parche.

Lo más valioso son las generalizaciones: reglas que sirvan a cualquier institución o carrera, y
arreglos de portabilidad. Lo que **no** se acepta son datos reales de nadie (ni nombres, ni
informes, ni rutas de tu máquina). Ver [`CONTRIBUTING.md`](CONTRIBUTING.md).

## Licencia

MIT. Ver `LICENSE`.
