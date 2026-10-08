#!/usr/bin/env bash
# test_install.sh — instalación desde cero en un HOME falso: vault = repo nuevo, catálogo, enlaces y otra máquina.
# Uso: bash scripts/test_install.sh        (no toca tu HOME, tu config.md ni tu .env.local)
set -uo pipefail
AQUI="$(cd "$(dirname "$0")/.." && pwd)"
T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
FALLO=0
chk() { if eval "$2"; then printf '  ok    %s\n' "$1"; else printf '  FALLA %s\n' "$1"; FALLO=1; fi; }

copiar_repo() { # $1=destino: el árbol de trabajo (sin .git ni datos locales), para no tocar el config.md real
  mkdir -p "$1"
  ( cd "$AQUI" && git ls-files -co --exclude-standard -z ) | while IFS= read -r -d '' f; do
    [ -f "$AQUI/$f" ] && ( cd "$AQUI" && cp --parents "$f" "$1/" )
  done
}

# --- fixtures: catálogo central con un docente, un TG sintético y un gh falso
mkdir -p "$T/central/docentes" "$T/bin" "$T/home1" "$T/home2" "$T/proyecto"
PERFIL='---
title: Ing. Ana Prueba
type: docente
status: activo
revisa: "marco práctico"
alcance: fondo
nombre: Ing. Ana Prueba
rol: Tutor
---

# Ing. Ana Prueba

## Criterios de fondo

| ID | Criterio | Estado | Ocurrencias | Fuente |
|---|---|---|---|---|
| ANA1 | Cifras con porcentaje | confirmado | 2 | informe a X.Y. |

## Historial de roles

| Rol | Estudiante | Desde |
|---|---|---|

## Relaciones
- [[_moc-docentes]]
'
printf '%s\n' "$PERFIL" > "$T/central/docentes/ana.md"
( cd "$T/central" && git init -q -b main && git add -A && git -c user.name=t -c user.email=t@x commit -q -m base )
printf '%s\n\n' '**ESCUELA MILITAR DE INGENIERÍA**' '**TRABAJO DE GRADO**' '**SISTEMA DE PRUEBA**' '**CASO: INSTITUCIÓN DE PRUEBA**' \
  '**LUIS PEREZ**' '**TUTOR: ING. ANA PRUEBA**' '**LA PAZ, 2026**' '**DEDICATORIA**' 'Texto.' > "$T/TG.md"
printf '# 1. INTRODUCCIÓN\n\nTexto de la introducción.\n' >> "$T/TG.md"
pandoc "$T/TG.md" -o "$T/TG.docx" 2>/dev/null || { echo "  FALLA falta pandoc para armar el TG de prueba"; exit 1; }
printf '#!/usr/bin/env bash\necho "$@" >> "%s/gh.log"\nexit 0\n' "$T" > "$T/bin/gh"; chmod +x "$T/bin/gh"

echo "== máquina 1: instalación desde cero =="
copiar_repo "$T/r1"
V="$T/mi-vault"
HOME="$T/home1" PATH="$T/bin:$PATH" bash "$T/r1/install.sh" --destino "$V" --docx "$T/TG.docx" --catalogo "file://$T/central" \
  --agentes "$T/home1/agente/skills" --code-repo "$T/proyecto" --remoto mi-vault > "$T/salida1.txt" 2>&1
RC=$?
chk "install.sh termina sin fallas (rc=$RC)" '[ "$RC" -eq 0 ]'
chk "el vault es un repo git con 1 commit" '[ "$(git -C "$V" rev-list --count HEAD 2>/dev/null)" = 1 ]'
chk "hook del vault activo" '[ "$(git -C "$V" config core.hooksPath)" = .githooks ]'
chk "0 enlaces simbólicos en el índice" '[ "$(git -C "$V" ls-files -s | grep -c "^120000")" = 0 ]'
chk "scripts/ del vault es un enlace local (ignorado)" '[ -L "$V/scripts" ] && git -C "$V" check-ignore -q scripts'
chk "el tutor de la carátula quedó vinculado al catálogo" '[ -L "$V/wiki/docentes/ana.md" ] && grep -q "docente: \"\[\[ana\]\]\"" "$V/wiki/revisores/Tutor.md"'
chk "config.md con tu vault y tu nombre" 'grep -q "data_dir: $V/wiki/revisores" "$T/r1/skills/perfil-revisor-tg/config.md" && grep -q "estudiante: LUIS PEREZ" "$T/r1/skills/perfil-revisor-tg/config.md"'
chk "skills enlazadas al agente" '[ -L "$T/home1/agente/skills/perfil-revisor-tg" ]'
chk "CODE_REPO en .env.local" 'grep -q "^CODE_REPO=" "$T/r1/.env.local"'
chk "--remoto crea el repo PRIVADO (sin push)" 'grep -q -- "--private" "$T/gh.log"'
chk "el pre-commit rechaza un wikilink roto" '( cd "$V" && printf "[[no-existe-xyz]]\n" > wiki/roto.md && git add wiki/roto.md && ! git -c user.name=t -c user.email=t@x commit -q -m x >/dev/null 2>&1 )'
git -C "$V" reset -q; rm -f "$V/wiki/roto.md"
chk "el pre-commit rechaza un enlace simbólico versionado" '( cd "$V" && ln -s /tmp enlace-malo && git add -f enlace-malo && ! git -c user.name=t -c user.email=t@x commit -q -m x >/dev/null 2>&1 )'
git -C "$V" rm -q --cached -f enlace-malo 2>/dev/null; rm -f "$V/enlace-malo"
chk "install.sh --check en verde" 'HOME="$T/home1" bash "$T/r1/install.sh" --destino "$V" --agentes "$T/home1/agente/skills" --check >/dev/null 2>&1'

echo "== máquina 2: clonar el vault y reinstalar =="
git clone -q "$V" "$T/vault2"
chk "el clon no trae enlaces ni config" '[ ! -e "$T/vault2/scripts" ] && [ ! -e "$T/vault2/wiki/docentes/ana.md" ]'
copiar_repo "$T/r2"
HOME="$T/home2" bash "$T/r2/install.sh" --destino "$T/vault2" --catalogo "file://$T/central" --agentes "$T/home2/agente/skills" > "$T/salida2.txt" 2>&1
chk "se rehacen scripts/ y el enlace del docente" '[ -L "$T/vault2/scripts" ] && [ -L "$T/vault2/wiki/docentes/ana.md" ]'
chk "config.md de la máquina 2 apunta al vault clonado" 'grep -q "data_dir: $T/vault2/wiki/revisores" "$T/r2/skills/perfil-revisor-tg/config.md"'
chk "verificar-enlaces del clon en verde" 'bash "$T/vault2/scripts/verificar-enlaces.sh" >/dev/null 2>&1'

echo "== sin acceso al catálogo: uno local y vacío =="
copiar_repo "$T/r3"; mkdir -p "$T/home3"
HOME="$T/home3" bash "$T/r3/install.sh" --destino "$T/vault3" --catalogo "file://$T/no-existe" > "$T/salida3.txt" 2>&1
chk "catálogo local vacío creado y vault funcional" '[ -d "$T/home3/.local/share/tg-docentes/docentes" ] && [ "$(git -C "$T/vault3" rev-list --count HEAD)" = 1 ]'

echo "== catálogo público (opcional, sin nombres) =="
copiar_repo "$T/r4"; mkdir -p "$T/home4" "$T/home5"
chk "el repo trae catalogo-publico/ con perfiles sin nombre" 'ls "$T/r4/catalogo-publico/docentes"/d-*.md >/dev/null 2>&1 && ! grep -lE "^nombre:" "$T"/r4/catalogo-publico/docentes/d-*.md | grep -q .'
HOME="$T/home5" bash "$T/r4/install.sh" --destino "$T/vault5" > "$T/salida5.txt" 2>&1
chk "sin pedirlo (no hay terminal) NO se descarga: catálogo local vacío" '[ ! -f "$(ls "$T"/home5/.local/share/tg-docentes/docentes/d-*.md 2>/dev/null | head -1)" ] && ! ls "$T"/home5/.local/share/tg-docentes/docentes/d-*.md >/dev/null 2>&1'
HOME="$T/home4" bash "$T/r4/install.sh" --destino "$T/vault4" --catalogo-publico > "$T/salida4.txt" 2>&1
chk "--catalogo-publico siembra un catálogo local con perfiles y huellas" 'ls "$T"/home4/.local/share/tg-docentes/docentes/d-*.md >/dev/null 2>&1 && grep -q "^claves:" "$(ls "$T"/home4/.local/share/tg-docentes/docentes/d-*.md | head -1)" && [ -d "$T/home4/.local/share/tg-docentes/.git" ]'
chk "el vault queda como repo con 1 commit y sin nombres de docentes" '[ "$(git -C "$T/vault4" rev-list --count HEAD)" = 1 ] && [ ! -e "$T/vault4/wiki/docentes/_nombres.local.yaml" ]'
HOME="$T/home4" bash "$T/r4/scripts/actualizar_catalogo.sh" > "$T/salida4b.txt" 2>&1
chk "actualizar_catalogo.sh sincroniza el snapshot sin romper nada" '[ $? -eq 0 ] && ! grep -qi "choque" "$T/salida4b.txt"'

if [ "$FALLO" -eq 0 ]; then echo "ok test_install"; else echo "FALLÓ test_install"; tail -30 "$T/salida1.txt"; exit 1; fi
