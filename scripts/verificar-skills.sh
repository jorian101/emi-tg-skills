#!/usr/bin/env bash
# Verifica la integridad de los enlaces de skills de todos los agentes.
#
# Un symlink roto deja a un agente sin la skill SIN avisar (ya pasó una vez con
# extraer-doc-tesis en antigravity). Este script lo detecta antes de que muerda.
#
#   bash scripts/verificar-skills.sh                 # rotos + conteo de frágiles
#   bash scripts/verificar-skills.sh --listar-fragiles
#
# Sale 1 si hay algún symlink roto (bloqueante); los frágiles solo se reportan.

set -uo pipefail

SKILL_DIRS=(
  "$HOME/.agents/skills"
  "$HOME/.claude/skills"
  "$HOME/.codex/skills"
  "$HOME/.config/opencode/skills"
  "$HOME/.gemini/antigravity-cli/skills"
)

listar_fragiles=false
[ "${1:-}" = "--listar-fragiles" ] && listar_fragiles=true

rotos=0
fragiles=0
sin_skill_md=0

for dir in "${SKILL_DIRS[@]}"; do
  [ -d "$dir" ] || continue
  for link in "$dir"/*; do
    [ -L "$link" ] || continue
    nombre="$(basename "$link")"

    if [ ! -e "$link" ]; then
      echo "ROTO       $nombre  ->  $(readlink "$link")"
      rotos=$((rotos + 1))
      continue
    fi

    # Un dir de skills global no debería depender de la ruta de un proyecto:
    # si el proyecto se mueve o se borra, la skill desaparece sin aviso.
    case "$(readlink "$link")" in
      "$HOME/proyectos/"*)
        fragiles=$((fragiles + 1))
        if [ "$listar_fragiles" = true ]; then
          echo "FRAGIL     $nombre  ->  $(readlink "$link")"
        fi
        ;;
    esac

    # Existe el enlace pero el destino no es una skill usable.
    if [ -d "$link" ] && [ ! -f "$link/SKILL.md" ]; then
      echo "SIN SKILL  $nombre  (destino sin SKILL.md)"
      sin_skill_md=$((sin_skill_md + 1))
    fi
  done
done

echo
echo "symlinks rotos: $rotos | sin SKILL.md: $sin_skill_md | frágiles (dependen de un proyecto): $fragiles"
if [ "$listar_fragiles" = false ]; then
  echo "  (correr con --listar-fragiles para verlos)"
fi

if [ "$rotos" -gt 0 ]; then
  exit 1
fi
exit 0
