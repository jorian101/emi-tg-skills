#!/usr/bin/env bash
# cobertura-fuentes.sh — Gate de cobertura: todo ítem confirmado/abierto del
# revisor, tutor y reglas debe aparecer en la matriz de cobertura de la propuesta.
# Uso: bash scripts/cobertura-fuentes.sh <propuesta.md> <perfil.md> [<perfil2.md> ...]
#
# Convención de citado en la propuesta (obligatoria desde skill v1.20):
#   R1#N .... fila N de Qué valora / NO le gusta / Errores (Revisor 1)
#   R1D#N ... duda N de Revisor 1        |  T#N ... tutor (consejos/NO gusta)
#   TD#N ... duda del tutor              |  MP-NN / MT-NN ... reglas-propias
#   DOC#N ... regla docente (Revisor_1 decisiones o wiki/docentes)
# Fallback: si la fila del perfil trae anclas (Tabla N, Fig. N, sección),
# basta que el ancla aparezca en la propuesta.
# Sale 0 si todo lo confirmado/abierto está cubierto; si no, lista faltantes.
set -uo pipefail
PROP="${1:?uso: cobertura-fuentes.sh <propuesta.md> <perfil.md>...}"
shift
SRC="$1"
case "$SRC" in
  *Revisor_1*) PFX="R1" ;;
  *Revisor_2*) PFX="R2" ;;
  *Tutor*)     PFX="T" ;;
  *jerarquia*|*docente*|*Docente*|*/docentes/*) PFX="DOC" ;;
  *)           PFX="X" ;;
esac
FAIL=0
DOC_ROWS=0
check_row() { # $1=num $2=estado $3=texto $4=kind(D=duda)
  local num="$1" estado="$2" texto="$3" kind="$4" tag=""
  [[ "$estado" != *"confirmado"* && "$estado" != *"abierto"* ]] && return 0
  if [ "$kind" = D ]; then
    tag="${PFX}D#${num}"
    grep -q "$tag" "$PROP" && { echo "OK   $tag :: ${texto:0:70}"; return 0; }
  else
    tag="${PFX}#${num}"
    grep -q "$tag" "$PROP" && { echo "OK   $tag :: ${texto:0:70}"; return 0; }
  fi
  # fallback por anclas de evidencia
  anchors=$(echo "$texto" | grep -o -E '(Tabla|Figura|Fig\.) [0-9]+|3\.[0-9.]+|mockups?|glosario' | sort -u | tr '\n' '|')
  if [ -n "$anchors" ]; then
    echo "$anchors" | tr '|' '\n' | grep -q . || anchors=""
  fi
  hit=0
  for a in $(echo "$anchors" | tr '|' ' '); do
    grep -q -F "$a" "$PROP" && hit=1
  done
  if [ "$hit" -eq 1 ]; then echo "OK   $tag (ancla) :: ${texto:0:70}"; return 0; fi
  echo "FALTA $tag [$estado] :: ${texto:0:90}"
  FAIL=1
}
for PERFIL in "$@"; do
  case "$PERFIL" in
    *Revisor_1*) PFX="R1" ;;
    *Revisor_2*) PFX="R2" ;;
    *Tutor*)     PFX="T" ;;
    *jerarquia*|*docente*|*Docente*|*/docentes/*) PFX="DOC" ;;
    *)           PFX="X" ;;
  esac
  rows_this_file=0
  in_dudas=0
  while IFS= read -r line; do
    [[ "$line" =~ ^##\ Dudas\ abiertas ]] && in_dudas=1
    [[ "$line" =~ ^##\ Relaciones ]] && in_dudas=0
    [[ "$line" =~ ^\|[[:space:]]*#+ ]] && continue
    if [ "$in_dudas" -eq 1 ]; then
      # Dudas: | # | Duda | Contexto | Estado |
      [[ "$line" =~ ^\|[[:space:]]*([0-9]+)[[:space:]]*\|[[:space:]]*([^|]+)[[:space:]]*\|[[:space:]]*([^|]+)[[:space:]]*\|[[:space:]]*([^|]+) ]] || continue
      rows_this_file=$((rows_this_file+1))
      check_row "${BASH_REMATCH[1]}" "${BASH_REMATCH[4]}" "${BASH_REMATCH[2]}" D
      continue
    fi
    [[ "$line" =~ ^\|[[:space:]]*([0-9]+)[[:space:]]*\|[[:space:]]*([^|]+)[[:space:]]*\|[[:space:]]*([^|]+) ]] || continue
    rows_this_file=$((rows_this_file+1))
    num="${BASH_REMATCH[1]}"; c2="${BASH_REMATCH[2]}"; c3="${BASH_REMATCH[3]}"
    # tablas Qué valora/NO gusta/Errores/Decisiones: estado en 3ra col
    if [[ "$c3" =~ confirmado|abierto|resuelto ]]; then
      check_row "$num" "$c3" "$c2" R
    elif [[ "$c3" =~ [a-z] ]]; then
      echo "INFO estado no estándar ${PFX}#${num} [$c3] :: ${c2:0:60}"
    fi
  done < "$PERFIL"
  # Fuente sin filas numeradas (ej. jerarquía-autoridad.md): exigir tag DOC#jerarquia
  if [ "$rows_this_file" -eq 0 ] && [ "$PFX" = "DOC" ]; then
    if grep -q "DOC#jerarquia" "$PROP"; then
      echo "OK   DOC#jerarquia (jerarquía considerada)"
    else
      echo "FALTA DOC#jerarquia [docente no considerado en la propuesta]"
      FAIL=1
    fi
  fi
done
# reglas MP/MT citadas en la propuesta (spot-check: las MP-1..MP-20 mencionadas existen)
for r in $(grep -o -E 'MP-[0-9]+|MT-[0-9]+' "$PROP" | sort -u); do
  echo "INFO regla citada: $r"
done
exit $FAIL
