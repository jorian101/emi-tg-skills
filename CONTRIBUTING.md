# Cómo contribuir

Gracias por querer mejorar esto. Está pensado para que **cualquier estudiante** pueda adaptarlo a
su institución, así que las contribuciones más valiosas son las que generalizan, no las que agregan
casos particulares.

## Regla número uno: `main` está protegida

**No se pushea a `main` directamente.** Está bloqueado en GitHub: todo cambio entra por *pull
request*. Para proponer algo:

```bash
# 1. Fork en GitHub, y después:
git clone https://github.com/<tu-usuario>/emi-tg-skills
cd emi-tg-skills
git checkout -b fix/lo-que-arreglas

# 2. Hacé el cambio y verificá (ver abajo)
# 3. Commit en Conventional Commits
git commit -m "fix(gates): el verificador ignora los placeholders"

# 4. Push a TU fork y abrí el PR
git push origin fix/lo-que-arreglas
```

¿No sabés programar o no querés abrir un PR? **Abrí un issue igual**: contá qué te pasó, con el
mensaje de error y tu sistema. Un buen reporte vale tanto como un parche.

## Antes de abrir el PR: los gates

```bash
bash scripts/auditar-rutas.sh   # 0 rutas personales hardcodeadas
bash scripts/auditar-pii.sh     # 0 datos privados
bash install.sh --check         # dependencias + gates + verificación
```

Si tocaste `install.sh` o el andamiaje, probá una instalación de verdad, **sin tocar tu entorno**:

```bash
rm -rf /tmp/tg-prueba /tmp/tg-home && mkdir -p /tmp/tg-home
HOME=/tmp/tg-home bash install.sh --destino /tmp/tg-prueba
bash /tmp/tg-prueba/scripts/verificar-enlaces.sh   # debe dar 0 rotos y 0 huérfanas
```

## Qué se acepta y qué no

**Bienvenido**

- Reglas o criterios **generales** que apliquen a cualquier institución o a cualquier carrera.
- Correcciones de portabilidad: rutas, dependencias, supuestos del entorno del autor.
- Bugs en los gates, en el instalador o en el parser de informes.
- Mejoras a la documentación, sobre todo si algo te confundió al instalar.
- Traducciones de la documentación.

**No se acepta** (el pre-commit lo bloquea, pero mejor que lo sepas antes)

- **Nombres reales** de revisores, tutores, docentes o estudiantes. Los perfiles del repo son
  plantillas: los datos son de cada usuario y viven en su vault.
- **Informes de revisión** (PDF, escaneos, transcripciones), aunque estén anonimizados a medias.
- Cualquier dato personal: emails, teléfonos, identificadores de notebooks, rutas de tu máquina.
- Casos particulares presentados como reglas generales ("mi docente pide X" como norma).

## Cómo está organizado el repo

| Carpeta | Qué va ahí |
|---|---|
| `skills/<nombre>/` | La lógica de cada skill. `assets/` son plantillas que se copian; `references/` es documentación que se lee |
| `scripts/` | Los gates. Los comparten todas las skills |
| `vault-template/` | El andamiaje que `install.sh` copia para crear el vault del usuario |
| `docs/` | Cómo funciona, arquitectura, migración |

El **motor** (este repo) no contiene ni un dato del estudiante: eso es lo que lo hace publicable. El
**dato** vive en el vault de cada usuario.

## Estilo

- **Conventional Commits**: `tipo(scope): descripción`. Tipos: feat, fix, docs, style, refactor,
  perf, test, build, ci, chore.
- Un commit por unidad de trabajo.
- Español, sin ceremonia, explicando **por qué** y no solo el qué.
- Si tu cambio toca una regla del sistema, actualizá también su fila en la tabla de gates
  correspondiente: una regla que no se verifica es una intención.
