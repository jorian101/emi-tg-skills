#!/usr/bin/env bash
# auditar-pii.sh — falla si el repo contiene datos privados.
#
# Cubre lo mismo que .husky/pre-commit pero sobre TODO el repo (útil antes de publicar y
# como gate de CI). El pre-commit mira solo lo que está por commitear; este mira todo.
#
# Uso: bash scripts/auditar-pii.sh [directorio]
set -uo pipefail

RAIZ="${1:-$(cd "$(dirname "$0")/.." && pwd)}"
DENY="$RAIZ/.pii-denylist.local"

# Ver el comentario de auditar-rutas.sh: `--exclude` + `--include` no se llevan bien.
# Además, los dominios reservados para documentación no son PII.
filtrar() {
  grep -vE '/docs/ejemplos/|\.example:|\.template:|\.pii-denylist\.' \
    | grep -vE '/config\.md:|\.env\.local:' \
    | grep -vE '/(auditar-rutas|auditar-pii)\.sh:|\.husky/pre-commit:' \
    | grep -vE '@(example|local|test|invalid)\.(com|org|net)|@localhost'
}

buscar() { # $1=etiqueta  $2=regex
  local etiqueta="$1" extra="$2" hits
  hits="$(grep -rnEi "$extra" "$RAIZ" \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ \
    --include='*.md' --include='*.sh' --include='*.py' --include='*.mjs' \
    --include='*.yaml' --include='*.yml' --include='*.json' --include='*.txt' 2>/dev/null \
    | filtrar || true)"
  if [ -n "$hits" ]; then
    echo "FALLA $etiqueta:"
    echo "$hits" | sed 's/^/  /'
    return 1
  fi
  return 0
}

FAIL=0
buscar "emails" '[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}' || FAIL=1
buscar "credenciales" 'nvapi-|sk-[A-Za-z0-9]{20,}|ghp_[A-Za-z0-9]{20,}' || FAIL=1
buscar "UUID / links de notebook" \
  'notebooklm\.google\.com|/notebook/[0-9a-f-]{36}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}' || FAIL=1

# --- Apellidos en NOMBRES DE ARCHIVO ---
# El chequeo de contenido es sensible a mayúsculas (para no confundir "terceros" con el
# apellido "Terceros"), pero en un slug el apellido va en minúscula: `reglas-<apellido>-2025.md`
# se escapaba. Se buscan entonces los tokens que PARECEN archivo y se comparan en minúscula.
# Prosa común ("de terceros") no es un token de archivo, así que no dispara.
buscar_slugs() {
  local tokens deny_low hits
  tokens="$(grep -rhoE '[A-Za-z0-9._/-]+\.(md|py|sh|yaml|yml|json|txt)' "$RAIZ" \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ 2>/dev/null \
    | tr 'A-Z' 'a-z' | sort -u || true)"
  deny_low="$(grep -vE '^[[:space:]]*(#|$)' "$DENY" | tr 'A-Z' 'a-z' || true)"
  hits="$(printf '%s\n' "$tokens" | grep -Ef <(printf '%s\n' "$deny_low") || true)"
  if [ -n "$hits" ]; then
    echo "FALLA apellido en un nombre de archivo:"
    echo "$hits" | sed 's/^/  /'
    return 1
  fi
  return 0
}

# Denylist local (apellidos y nombres reales). Sin -i a propósito: los nombres van
# capitalizados, así "terceros" (palabra común) no matchea el apellido "Terceros".
if [ -f "$DENY" ]; then
  HITS="$(grep -rnEf <(grep -vE '^[[:space:]]*(#|$)' "$DENY") "$RAIZ" \
    --exclude-dir=.git --exclude-dir=node_modules --exclude-dir=__pycache__ \
    --include='*.md' --include='*.sh' --include='*.py' --include='*.mjs' \
    --include='*.yaml' --include='*.yml' --include='*.json' --include='*.txt' 2>/dev/null \
    | filtrar || true)"
  if [ -n "$HITS" ]; then
    echo "FALLA términos del denylist local:"
    echo "$HITS" | sed 's/^/  /'
    FAIL=1
  fi
else
  echo "AVISO no hay .pii-denylist.local: el guard no puede buscar tus apellidos reales."
  echo "      Copiá .pii-denylist.example y completalo (está en .gitignore)."
fi

buscar_slugs || FAIL=1

[ "$FAIL" -eq 0 ] && echo "OK   0 datos privados detectados ($RAIZ)"
exit $FAIL
