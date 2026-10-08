# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

## [limpieza] — 2026-10-08

- Quitada la skill `extraer-conversaciones-ias` (destilaba criterio de un «vocal» desde chats con IAs: flujo del proyecto del autor, no
  de un estudiante) y `docs/migracion-desde-vault.md` (solo servía a quien tenía las skills dentro de su vault). Siguen en el historial de git.

## [instalación 2.0] — 2026-10-08

**El vault es un repositorio nuevo del estudiante y el catálogo de docentes es público sin nombres, con aportes por issue abierto.**

- `install.sh`: `git init` del vault con pre-commit (0 wikilinks rotos, 0 huérfanas, ningún enlace versionado) y primer
  commit; `--remoto` crea el repo **privado** en GitHub sin push; `--code-repo` conecta el repo del proyecto con el agente;
  `--agentes` repetible y sin pisar copias; dependencias opcionales por entregable en `--check`.
- Lo que lleva rutas de una máquina (`scripts/`, `wiki/docentes/<docente>.md`, `config.md`) ya no se versiona: se rehace con
  `asignar_evaluador.py --sync` (clonar el vault en otra máquina).
- Catálogo de docentes **público y sin nombres** (`catalogo-publico/`, opcional con `--catalogo-publico`), `--catalogo` para uno propio, o uno local vacío.
- Colaboración: `registrar_criterio.py`, `nuevo_docente.py` (cualquier docente y rol), `contribuir.py` (contribución saneada,
  iniciales, issue con `gh` previa confirmación o PR), `aplicar_contribucion.py` y `actualizar_catalogo.sh`.
- `scripts/preflight_publicar.py`: puerta antes de publicar (nombres sin distinguir mayúsculas, docentes del catálogo, correos,
  rutas personales y notebooks en las líneas a publicar; `--nombres-de` toma los nombres del catálogo privado).
- **Seudónimos**: cada docente del catálogo público tiene código `d-xxxxxx` y huellas (SHA-256 con sal pública) de pares de
  nombre/apellido; `resolver_docente.py` los reconoce en tu máquina y el nombre queda solo en tu vault. `exportar_publico.py`
  genera el catálogo público desde el privado y aborta sin escribir si se cuela un nombre. Es seudonimización, no anonimato.
- Aportes abiertos: `contribuir.py` abre un issue en el repo público (código/huellas, nunca el nombre; se niega si aparece el nombre de
  tus docentes), con formulario `.github/ISSUE_TEMPLATE/aporte-criterio.yml`; `aplicar_contribucion.py` lo integra en el privado.
- `scripts/test_install.sh`, `test_catalogo.py`, `test_publico_e2e.py`, `test_exportar_publico.py` y `test_pseudonimos.py`: instalación desde cero, otra máquina, sin catálogo y flujo completo de
  contribución. El extractor ya no falla con un TG sin imágenes.

## [perfil-revisor-tg 1.43 · asistente-trabajo-de-grado 3.3] — 2026-10-08

**Catálogo compartido de docentes y solo los evaluadores propios.**

- **Catálogo único** (`<emi-docentes>`, alias `~/.local/share/tg-docentes`): un perfil por docente con lo que
  suele revisar (`revisa:`, `alcance:`), criterios con ocurrencias, historial de roles y estudiantes por iniciales.
  Cada vault enlaza **solo** a su tutor, revisores y docente de TG; los demás no se leen (pueden contradecirse).
- `scripts/asignar_evaluador.py` (`--rol`, `--docente`/`--por-asignar`, `--desde-tg`, `--check`): vincula, desenlaza
  al reasignar y muestra la predicción inicial. `install.sh --catalogo` crea el alias y vincula al tutor de la carátula.
- Reglas pulidas: se reemplaza el «tier de segunda opinión» por «solo los evaluadores identificados»; la predicción se
  acota a lo que cada evaluador revisa; evaluador `por-asignar` (típico del Revisor 2) usa solo las clases `SEM`.
- Modos nuevos en `perfil-revisor-tg`: **asignar** y **registrar corrección** (lo recibido suma al perfil compartido).
- `jerarquia-autoridad.md` reescrita: quiénes cuentan, jerarquía, qué suele revisar cada rol, escalación entre evaluadores.

## [asistente-trabajo-de-grado 3.2 · perfil-revisor-tg 1.42 · generar-entregables-tesis 3.3] — 2026-10-08

**Cualquier TG, cualquier estudiante**: el vault se arma desde el `.docx` y lo propio de cada proyecto vive en
`proyecto.yaml`, no en las skills.

- **`install.sh --docx`**: extrae el TG, arma `proyecto.yaml` con lo que el TG dice de sí mismo (carátula,
  objetivos, antecedentes, problema, anexos, figuras y tablas; `scripts/inicializar_desde_tg.py`), crea la carpeta
  de defensa y `.env.local`. `--docentes-desde` trae perfiles de docentes de otro vault como segunda opinión.
  Probado con tres TG reales de temas distintos.
- **Modo inicializar** (`references/inicializar.md`): el agente completa `proyecto.yaml` citando la sección del TG y
  arma los modelos de la defensa adaptados al tipo de proyecto.
- **Diapositivas desde cero**: `diapositivas.py crear diapositivas.yaml` y tope de **90 palabras** por diapositiva
  en `crear` y `verificar` (calibrado con un mazo real de 30 min: mediana 46).
- **Manual de usuario** como motor genérico (`manual.py`): Markdown con marcas, capturas con marcadores y la
  plantilla Word del autor; tablas y glosario en `manual.yaml`.
- **Ruta crítica vertical** para la solapa del tríptico desde el mismo YAML (`diagrama_flujo.py --vertical`); la
  ruta crítica es el único diagrama en Excalidraw.
- **Tríptico** en hoja carta por defecto, con misión, visión y función de la institución del caso y el bloque EMI.
- **Diagramas animados**: `escenas.py` no exporta si un texto se sale del escenario o se pisa con otro.
- **perfil-revisor-tg**: clases semilla `SEM-01..06` (causa vs efecto, mejora sin número, declarado sin verificar,
  concepto central sin definir, caja negra, validación de un solo sentido) y regla para transcripciones sin hablantes.
- **Sin dominio del proyecto de referencia** en las skills: paleta, producto, hilo conductor, terminología y siglas
  prohibidas se leen del vault (`TERMINOS_PROHIBIDOS`, `proyecto.yaml`); los mapas por sprint quedan como ejemplo.
  `.pii-denylist.local` acepta también términos del dominio para que no vuelvan.

## [asistente-trabajo-de-grado 3.1] — 2026-10-06

**Modo defensa**: cualquier agente puede preparar y mantener los materiales de la defensa a partir del
documento del trabajo de grado, para cualquier tema y estudiante.

- **Motor genérico** en `scripts/defensa/` (sin rutas ni datos): verificación de sincronización
  (hash + fecha) entre el documento, el frontend y cada entregable; correcciones celda por celda que se
  reconocen solas al copiarlas; publicación de finales; anexos con QR (Word → PDF por anexo → Drive → QR).
- **Diagramas en dos versiones**: la técnica y una pública animada por escenas con contenido real
  (`escenas.py`), con los términos verificados contra el documento y letra mínima de 28 px. Ruta crítica
  por carriles desde YAML (`ruta_critica.py`), exportada con Excalidraw real.
- **Capturas declarativas** (`capturas.py`): pantallas, modales y acciones por rol desde YAML, con
  marcadores medidos y bloqueo de los botones que escriben.
- **Vault interconectado** (`notas_vault.py`): hub de defensa, una nota por entregable, nota de estado y
  una nota por captura, con el frontmatter del vault.
- Config del proyecto en `defensa.json` (modelos en `assets/defensa/`); guías en `references/defensa/`.
- `generar-entregables-tesis`: la prohibición de Excalidraw queda acotada a las figuras del documento.

## [perfil-revisor-tg 1.41] — 2026-09-23

Primera versión **portable y distribuible**. Cambios que solo se notan si alguien más la instala:

- **Cero rutas absolutas.** Las 129 menciones en los `.md` y los 4 scripts de Python se resuelven
  desde `config.local.md` / `.env.local`; si falta una variable, el script **falla diciendo cuál**
  en vez de adivinar.
- **Cero datos del autor.** Los docentes se referencian por `ambito` y por rol, nunca por apellido.
- **La allowlist es dato**: el verificador de enlaces la lee del bloque `allowlist` de
  `ORDEN-DEL-VAULT.md`, que es el mismo archivo que lee el humano. Estaba triplicada.
- **Guard de criterios externos** (reglas 39–43): 3 puertas, tope de 1 hallazgo por sección,
  anclaje seccional, control anti-plantilla y tier de segunda opinión.
- **El registro de informes se deriva**, no se escribe a mano: no puede mentir sobre lo que falta.
- **El andamiaje está completo** (`assets/`): perfil de docente, matriz de generalizaciones,
  protocolo del tribunal, registro y las plantillas del catalogo.
- **Portabilidad**: `config.local.md` declara `estudiante` y `evaluadores`; el recorrido del
  tribunal deja de requerir un orquestador de agentes (el transporte es un anexo opcional).

## [0.1.0] — 2026-09-23

Primera publicación del repo. Extracción de las 5 skills desde el vault del autor a un repo
independiente y distribuible.

Qué quedó hecho, en el orden en que se hizo:

- Esqueleto del repo: licencia MIT, guard anti-PII en el pre-commit y CHANGELOG.
- El motor se copió **fiel** (verificado con `diff`) y recién después se editó.
- Los 6 gates que vivían en el vault se mudaron acá: sin ellos la verificación obligatoria era
  letra muerta para quien descargara la skill.
- La allowlist dejó de ser código: se lee del bloque `allowlist` de `ORDEN-DEL-VAULT.md`.
- Las 66 rutas absolutas se reemplazaron por variables; los scripts **fallan diciendo qué falta**
  en vez de adivinar.
- Los nombres reales salieron de la lógica: los docentes se referencian por `ambito` y por rol.
- Se completó el andamiaje: 8 plantillas que no existían.
- `install.sh` + `vault-template/`, y la guía de migración con rollback por paso.
- El vault del autor soltó las skills (42 archivos fuera de su índice) y quedó un symlink.
- El alias se repuntó al repo y se verificó el ciclo completo: un cambio acá llega a los 5 agentes
  sin pasos extra, y existe **una sola copia** del contenido.

### Versiones de las skills al momento de la copia
| Skill | Versión de origen |
|---|---|
| `perfil-revisor-tg` | 1.40 |
| `asistente-trabajo-de-grado` | 3.0 |
| `generar-entregables-tesis` | (sin versión en frontmatter) |
| `extraer-doc-tesis` | 3.0 |
| `extraer-conversaciones-ias` | (sin versión en frontmatter) |
