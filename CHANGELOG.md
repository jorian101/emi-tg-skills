# Changelog

Formato: [Keep a Changelog](https://keepachangelog.com/es-ES/1.1.0/).
Versionado: [SemVer](https://semver.org/lang/es/).

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
