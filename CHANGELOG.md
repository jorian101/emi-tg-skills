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

## [No publicado]

Extracción de las skills desde el vault del autor a un repo independiente y distribuible.

### Por hacer (fases del plan)
- F1 esqueleto del repo, licencia, guard anti-PII.
- F2 copiar el motor (5 skills + gates + plantillas) sin editar.
- F3 gates sin datos incrustados (allowlist leída del manifiesto del vault).
- F4 externalizar las 66 rutas absolutas a `config.local.md` / `.env.local`.
- F5 sacar los nombres reales de la lógica.
- F6 completar `references/` de las 5 skills.
- F7 `vault-template/` + `install.sh` + guía de migración.
- F8 gitignore de la skill en el vault + symlink.
- F9 prueba del ciclo repo → proyecto.
- F10 publicación.

### Versiones de las skills al momento de la copia
| Skill | Versión de origen |
|---|---|
| `perfil-revisor-tg` | 1.40 |
| `asistente-trabajo-de-grado` | 3.0 |
| `generar-entregables-tesis` | (sin versión en frontmatter) |
| `extraer-doc-tesis` | 3.0 |
| `extraer-conversaciones-ias` | (sin versión en frontmatter) |
