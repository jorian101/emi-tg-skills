#!/usr/bin/env bash
# actualizar_catalogo.sh — trae las novedades del repo principal del catálogo sin perder tus cambios locales.
#
# Uso:
#   bash scripts/actualizar_catalogo.sh [catalogo]              # rebase de tu rama local/<usuario> sobre origin/main
#   bash scripts/actualizar_catalogo.sh [catalogo] --reiniciar  # tu aporte ya se integró: vuelve a origin/main (guarda un respaldo)
# El catálogo es $DOCENTES_EMI o ~/.local/share/tg-docentes. Sale 1 si no hay remoto, no hay acceso o hay un choque.
set -uo pipefail
REINICIAR=0
CAT=""
for a in "$@"; do
  case "$a" in --reiniciar) REINICIAR=1 ;; *) CAT="$a" ;; esac
done
CAT="${CAT:-${DOCENTES_EMI:-$HOME/.local/share/tg-docentes}}"
CAT="$(cd "$CAT" 2>/dev/null && pwd -P)" || { echo "No encuentro el catálogo."; exit 1; }
g() { git -C "$CAT" "$@"; }
[ -e "$CAT/.git" ] || { echo "El catálogo no es un repo git: no hay de dónde actualizar."; exit 1; }
g remote get-url origin >/dev/null 2>&1 || { echo "El catálogo no tiene remoto 'origin' (es local): nada que actualizar."; exit 1; }
g fetch -q origin || { echo "Sin acceso al repo principal del catálogo (¿te invitaron? ¿hay red?). Seguís con tu copia local."; exit 1; }
PRINCIPAL="$(g symbolic-ref -q --short refs/remotes/origin/HEAD 2>/dev/null || true)"
[ -n "$PRINCIPAL" ] || { g rev-parse --verify -q origin/main >/dev/null && PRINCIPAL=origin/main || PRINCIPAL=origin/master; }
RAMA="$(g rev-parse --abbrev-ref HEAD)"
LOCAL="local/$(id -un | tr 'A-Z' 'a-z' | tr -c 'a-z0-9\n' '-')"

if [ "$REINICIAR" -eq 1 ]; then
  RESP="respaldo/local-$(date +%Y%m%d-%H%M%S)"
  g branch "$RESP" "$RAMA" 2>/dev/null && echo "  ok    respaldo de tu rama en $RESP"
  g checkout -q -B "$LOCAL" "$PRINCIPAL" && echo "  ok    $LOCAL vuelve a $PRINCIPAL"
  exit 0
fi

case "$RAMA" in
  local/*)
    if g rebase -q "$PRINCIPAL"; then echo "  ok    $RAMA al día con $PRINCIPAL"
    else
      g rebase --abort
      echo "Choque entre tus cambios y los del repo principal (¿ya integraron tu aporte?)."
      echo "  Si ya está integrado: bash scripts/actualizar_catalogo.sh --reiniciar (guarda un respaldo)."
      exit 1
    fi ;;
  *) g merge -q --ff-only "$PRINCIPAL" && echo "  ok    $RAMA al día con $PRINCIPAL" ;;
esac
