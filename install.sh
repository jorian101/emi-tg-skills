#!/usr/bin/env bash
# install.sh — instala las skills y crea tu vault.
#
# Idempotente: nunca sobrescribe un archivo que ya exista. Si ya está todo, no hace nada.
#
# Uso:
#   ./install.sh --destino ~/mi-vault     # crea el vault e instala
#   ./install.sh --check                  # solo verifica, no escribe nada
#   ./install.sh                          # usa el vault de config.local.md si existe
set -uo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SKILLS_REPO="$REPO/skills"
ALIAS="$HOME/.local/share/tg-skills"
AGENTE_DEFAULT="$HOME/.agents/skills"

DESTINO=""
CHECK=0
AGENTES=("$AGENTE_DEFAULT")

while [ $# -gt 0 ]; do
  case "$1" in
    --destino) DESTINO="${2:-}"; shift 2 ;;
    --check)   CHECK=1; shift ;;
    --agentes) AGENTES+=("${2:-}"); shift 2 ;;
    -h|--help)
      sed -n '2,10p' "$0" | sed 's/^# \{0,1\}//'
      exit 0 ;;
    *) echo "Opción desconocida: $1 (usá --help)"; exit 2 ;;
  esac
done

ok()   { printf '  ok    %s\n' "$1"; }
skip() { printf '  ya    %s\n' "$1"; }
warn() { printf '  aviso %s\n' "$1"; }
err()  { printf '  FALLA %s\n' "$1"; FALLAS=$((FALLAS+1)); }
FALLAS=0

# ---------------------------------------------------------------- config
CONFIG="$SKILLS_REPO/perfil-revisor-tg/config.md"
if [ -z "$DESTINO" ] && [ -f "$CONFIG" ]; then
  DESTINO="$(awk -F': *' '/^data_dir:/{print $2; exit}' "$CONFIG")"
  DESTINO="$(dirname "$(dirname "$DESTINO")")"
fi

echo "== tg-skills =="
echo "  repo    $REPO"
echo "  vault   ${DESTINO:-<sin definir>}"
echo

# ---------------------------------------------------------------- dependencias
echo "== dependencias =="
command -v bash >/dev/null && ok "bash" || err "bash es obligatorio"
command -v python3 >/dev/null && ok "python3" || err "python3 es obligatorio"
command -v git >/dev/null && ok "git" || warn "git: sin él no hay verificación de cambios"
command -v pandoc >/dev/null && ok "pandoc" || warn "pandoc: hace falta para extraer Word y generar .docx espejo"
command -v tesseract >/dev/null && ok "tesseract (OCR)" || warn "tesseract: solo si tenés informes escaneados"
[ "$FALLAS" -gt 0 ] && { echo; echo "Faltan dependencias obligatorias."; exit 1; }

if [ "$CHECK" -eq 1 ]; then
  echo
  echo "== verificación del repo =="
  bash "$REPO/scripts/auditar-rutas.sh" || FALLAS=$((FALLAS+1))
  bash "$REPO/scripts/auditar-pii.sh"  || FALLAS=$((FALLAS+1))
  [ -n "$DESTINO" ] && [ -d "$DESTINO" ] && bash "$DESTINO/scripts/verificar-enlaces.sh"
  echo
  [ "$FALLAS" -eq 0 ] && echo "TODO OK" || echo "HAY $FALLAS PROBLEMA(S)"
  exit $(( FALLAS > 0 ))
fi

[ -n "$DESTINO" ] || { echo "Necesito --destino <ruta> (o un config.md ya instalado)."; exit 2; }

# ---------------------------------------------------------------- vault
echo
echo "== vault =="
mkdir -p "$DESTINO"
# Copia el andamiaje sin pisar nada existente.
( cd "$REPO/vault-template" && find . -type f -print0 ) | while IFS= read -r -d '' rel; do
  origen="$REPO/vault-template/${rel#./}"
  destino="$DESTINO/${rel#./}"
  if [ -e "$destino" ]; then
    skip "vault/${rel#./}"
  else
    mkdir -p "$(dirname "$destino")"
    cp "$origen" "$destino"
    ok "vault/${rel#./}"
  fi
done

# Carpetas que git no versiona por estar vacías.
mkdir -p "$DESTINO/sources/informes-revisores" "$DESTINO/sources/media" "$DESTINO/wiki/contradictions"

# Los gates viven en el repo: el vault los symlinkea para no tener dos copias.
if [ -e "$DESTINO/scripts" ] && [ ! -L "$DESTINO/scripts" ]; then
  warn "vault/scripts ya existe y no es un symlink: lo dejo como está"
else
  ln -sfn "$REPO/scripts" "$DESTINO/scripts"
  ok "vault/scripts -> $REPO/scripts"
fi

# ---------------------------------------------------------------- plantillas de las skills al vault
copiar_asset() { # $1=origen  $2=destino relativo al vault
  local origen="$1" destino="$DESTINO/$2"
  if [ -e "$destino" ]; then skip "$2"; else
    mkdir -p "$(dirname "$destino")"; cp "$origen" "$destino"; ok "$2"
  fi
}

echo
echo "== plantillas =="
P="$SKILLS_REPO/perfil-revisor-tg/assets"
A="$SKILLS_REPO/asistente-trabajo-de-grado/assets"
copiar_asset "$P/indice.md"                     "wiki/revisores/indice.md"
copiar_asset "$P/reglas-propias.md"             "wiki/revisores/reglas-propias.md"
copiar_asset "$P/reglas-formato-notas-tg.md"    "wiki/revisores/reglas-formato-notas-tg.md"
copiar_asset "$P/matriz-generalizaciones.md"    "wiki/revisores/matriz-generalizaciones.md"
copiar_asset "$P/protocolo-tribunal.md"         "wiki/revisores/protocolo-tribunal.md"
copiar_asset "$P/Tutor.md"                      "wiki/revisores/Tutor.md"
copiar_asset "$P/registro.md"                   "sources/informes-revisores/registro.md"
copiar_asset "$A/_moc-docentes.md"              "wiki/docentes/_moc-docentes.md"
copiar_asset "$A/jerarquia-autoridad.md"        "wiki/docentes/jerarquia-autoridad.md"
copiar_asset "$A/plantilla-docente.md"          "wiki/docentes/_plantilla-docente.md"
copiar_asset "$A/reglas-institucionales.md"     "wiki/trabajos-grado/reglas-institucionales.md"

# Un perfil por evaluador, desde la plantilla común (reemplazando la N).
for n in 1 2; do
  destino="$DESTINO/wiki/revisores/Revisor_$n.md"
  if [ -e "$destino" ]; then skip "wiki/revisores/Revisor_$n.md"; else
    sed -e "s/Revisor N/Revisor $n/g" -e "s/n_revisor: N/n_revisor: $n/" "$P/Revisor_N.md" > "$destino"
    ok "wiki/revisores/Revisor_$n.md"
  fi
done

# ---------------------------------------------------------------- config del motor
echo
echo "== config del motor =="
if [ -f "$CONFIG" ]; then
  skip "skills/perfil-revisor-tg/config.md"
else
  sed -e "s|^data_dir: .*|data_dir: $DESTINO/wiki/revisores|" \
      -e "s|^docentes_en: .*|docentes_en: $DESTINO/wiki/docentes|" \
      -e "s|^informes_en: .*|informes_en: $DESTINO/sources/informes-revisores|" \
      "$SKILLS_REPO/perfil-revisor-tg/config.example.md" > "$CONFIG"
  ok "skills/perfil-revisor-tg/config.md (con tu ruta)"
  warn "completá 'estudiante:' y 'evaluadores:' en ese archivo"
fi
if [ ! -f "$REPO/.env.local" ]; then
  warn "creá $REPO/.env.local desde .env.example (rutas de los scripts)"
fi

# ---------------------------------------------------------------- agentes
echo
echo "== agentes =="
mkdir -p "$(dirname "$ALIAS")"
ln -sfn "$SKILLS_REPO" "$ALIAS"
ok "alias $ALIAS -> $SKILLS_REPO"
for dir in "${AGENTES[@]}"; do
  mkdir -p "$dir"
  for s in "$SKILLS_REPO"/*/; do
    ln -sfn "${s%/}" "$dir/$(basename "$s")"
  done
  ok "skills en $dir"
done
warn "otros agentes: ./install.sh --agentes ~/.claude/skills (o el que uses)"

# ---------------------------------------------------------------- hooks y verificación
if [ -d "$REPO/.git" ]; then
  git -C "$REPO" config core.hooksPath .husky && ok "pre-commit activo (core.hooksPath)"
fi

echo
echo "== verificación =="
bash "$REPO/scripts/auditar-rutas.sh" || FALLAS=$((FALLAS+1))
bash "$REPO/scripts/auditar-pii.sh"  || FALLAS=$((FALLAS+1))
if [ -x "$DESTINO/scripts/verificar-enlaces.sh" ]; then
  bash "$DESTINO/scripts/verificar-enlaces.sh" 2>&1 | tail -3
else
  err "no pude correr $DESTINO/scripts/verificar-enlaces.sh"
fi

echo
if [ "$FALLAS" -eq 0 ]; then
  cat <<FIN

Listo. Próximos pasos:
  1. Completá skills/perfil-revisor-tg/config.md (estudiante + evaluadores).
  2. Completá el perfil de tus evaluadores en $DESTINO/wiki/revisores/.
  3. Si tenés informes: ponelos en una carpeta por docente, exportá INFORMES y corré
       source .env.local && python3 $REPO/scripts/ingerir-informe.py
     y después pedile a tu agente: "ingerir informe".
FIN
else
  echo "Terminó con $FALLAS problema(s): revisá las líneas 'FALLA' de arriba."
fi
exit $(( FALLAS > 0 ))
