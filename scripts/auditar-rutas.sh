#!/usr/bin/env bash
# auditar-rutas.sh — falla si queda una ruta personal absoluta en el repo.
#
# El motor debe ser portable: ninguna ruta del usuario puede estar hardcodeada. Las rutas
# se resuelven desde config.local.md / .env.local, o con variables de entorno en los
# scripts ($VAULT, $CORPUS, $CODE_REPO, ...).
#
# Uso: bash scripts/auditar-rutas.sh [directorio]
set -uo pipefail

RAIZ="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
PATRONES='/home/[a-z0-9_.-]+/|/Users/[A-Za-z0-9_.-]+/|/mnt/[a-z]/|~/proyectos/'

# Exclusiones comunes. Tres detalles aprendidos a golpes:
#   1. `grep --exclude` deja de funcionar si se combina con --include (GNU grep 3.11),
#      así que la autoexclusión se hace filtrando la salida por ruta.
#   2. Este auditor y el pre-commit contienen los patrones por definición.
#   3. La config privada (config.md, .env.local) está en .gitignore: nunca se publica,
#      y alarmar por ella sería ruido. El pre-commit sí vigila que no se commitee.
filtrar() {
  grep -vE '/docs/ejemplos/|\.example:|\.template:|\.pii-denylist\.' \
    | grep -vE '/config\.md:|\.env\.local:' \
    | grep -vE '/(auditar-rutas|auditar-pii)\.sh:|\.husky/pre-commit:'
}

HITS="$(grep -rnE "$PATRONES" "$RAIZ" \
  --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ \
  --include='*.md' --include='*.sh' --include='*.py' --include='*.mjs' \
  --include='*.yaml' --include='*.yml' --include='*.json' --include='*.txt' 2>/dev/null \
  | filtrar || true)"

if [ -n "$HITS" ]; then
  echo "FALLA rutas personales hardcodeadas:"
  echo "$HITS" | sed 's/^/  /'
  echo
  echo "Reemplazá por una variable (\$VAULT, \$CORPUS, \$CODE_REPO) o por una ruta relativa."
  echo "Las claves viven en config.local.md / .env.local (ver .env.example)."
  exit 1
fi

echo "OK   0 rutas personales hardcodeadas ($RAIZ)"
