# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

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
