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

- **`evaluadores:` es la lista de los que sí mandan.** Cada uno se vincula a su perfil compartido con
  `scripts/asignar_evaluador.py`; los docentes que no te evalúan no se leen. El sistema no adivina quién te evalúa por el
  nombre del archivo: lo lee de acá y del `docente:` de cada perfil.
- Si todavía no tenés vault, `install.sh` te crea uno desde `vault-template/`.
- `config.local.md` y `.env.local` están en `.gitignore`.
