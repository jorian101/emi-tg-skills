# Config privada — NUNCA se commitea.
# Copiar a config.local.md y completar con TUS rutas.
#
# Este archivo lo leen las skills para saber dónde vive el dato.

```
data_dir: /ruta/a/tu/vault/wiki/revisores
estudiante: Nombre Apellido
evaluadores:
  - Revisor_1.md
  - Revisor_2.md
  - Tutor.md
docentes_en: /ruta/a/tu/vault/wiki/docentes
informes_en: /ruta/a/tu/vault/sources/informes-revisores
```

## Notas

- **`evaluadores:` es la lista de los que sí mandan.** Los perfiles de `docentes_en` con
  `origen: informes-revisores` son segunda opinión: nunca emiten `confirmado` sobre tu trabajo y no
  se pasan al gate de cobertura. El sistema no adivina quién te evalúa por el nombre del archivo:
  lo lee de acá.
- Si todavía no tenés vault, `install.sh` te crea uno desde `vault-template/`.
- `config.local.md` y `.env.local` están en `.gitignore`.
