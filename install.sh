#!/usr/bin/env bash
# install.sh — instala las skills y crea tu vault como un repositorio nuevo.
#
# Un usuario = un clon de este repo + un vault + (opcional) el catálogo de docentes. Idempotente: nunca sobrescribe
# un archivo que ya exista; correrlo de nuevo en otra máquina rehace lo que no se versiona (enlaces y config).
#
# Uso:
#   ./install.sh --destino ~/mi-vault                      # crea el vault (repo git con primer commit) e instala
#   ./install.sh --destino ~/mi-vault --docx ~/TG.docx     # además extrae tu TG y arma proyecto.yaml
#   ./install.sh --destino ~/mi-vault --remoto mi-vault    # además crea el repo PRIVADO en GitHub (sin push)
#   ./install.sh --code-repo ~/mi-proyecto                 # conecta el repo de tu proyecto con tus agentes
#   ./install.sh --agentes ~/.claude/skills --agentes ~/.codex/skills   # más agentes (se puede repetir)
#   ./install.sh --catalogo-publico                        # descarga (opcional) el catálogo de docentes SIN nombres
#   ./install.sh --catalogo <url-git|carpeta>              # un catálogo propio (p. ej. el privado del mantenedor)
#   ./install.sh --check                                   # solo verifica, no escribe nada
set -uo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
SKILLS_REPO="$REPO/skills"
ALIAS="$HOME/.local/share/tg-skills"
ALIAS_DOC="$HOME/.local/share/tg-docentes"
AGENTE_DEFAULT="$HOME/.agents/skills"

DESTINO="" DOCX="" CATALOGO="" CATALOGO_PUBLICO="" CODE_REPO="" REMOTO="" CHECK=0
AGENTES=("$AGENTE_DEFAULT")

while [ $# -gt 0 ]; do
  case "$1" in
    --destino)   DESTINO="${2:-}"; shift 2 ;;
    --docx)      DOCX="${2:-}"; shift 2 ;;
    --catalogo)  CATALOGO="${2:-}"; shift 2 ;;
    --catalogo-publico) CATALOGO_PUBLICO=1; shift ;;
    --code-repo) CODE_REPO="${2:-}"; shift 2 ;;
    --remoto)    REMOTO="${2:-}"; shift 2 ;;
    --check)     CHECK=1; shift ;;
    --agentes)   AGENTES+=("${2:-}"); shift 2 ;;
    -h|--help)
      sed -n '2,16p' "$0" | sed 's/^# \{0,1\}//'
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

echo "== emi-tg-skills =="
echo "  repo    $REPO"
echo "  vault   ${DESTINO:-<sin definir>}"
echo

# ---------------------------------------------------------------- dependencias
opcional() { # $1=comando  $2=para qué  $3=cómo instalarlo
  if command -v "$1" >/dev/null 2>&1; then ok "$1 ($2)"; else warn "$1: $2 — instalalo con: $3"; fi
}
echo "== dependencias =="
command -v bash >/dev/null && ok "bash" || err "bash es obligatorio"
command -v python3 >/dev/null && ok "python3" || err "python3 es obligatorio"
command -v git >/dev/null && ok "git" || err "git es obligatorio (el vault es un repositorio)"
python3 -c "import yaml" 2>/dev/null && ok "pyyaml" || err "falta pyyaml: pip install pyyaml (o apt install python3-yaml)"
opcional pandoc "extraer tu Word y armar los .docx" "apt install pandoc"
opcional uv "motores de la defensa (diapositivas, tríptico, manual, diagramas)" "curl -LsSf https://astral.sh/uv/install.sh | sh"
opcional tesseract "OCR de informes escaneados" "apt install tesseract-ocr tesseract-ocr-spa"
opcional rg "verificar-enlaces del vault" "apt install ripgrep"
opcional rclone "subir los anexos a Drive y armar los QR" "apt install rclone"
opcional gh "crear el repo del vault o abrir issues de criterios" "apt install gh && gh auth login"
if command -v google-chrome >/dev/null || command -v chromium >/dev/null || command -v chromium-browser >/dev/null \
   || [ -n "${CHROME:-}" ] || ls "$HOME"/.cache/puppeteer/chrome-headless-shell/*/*/chrome-headless-shell >/dev/null 2>&1; then
  ok "Chrome o Chromium (ruta crítica en Excalidraw)"
else
  warn "Chrome/Chromium: hace falta para exportar la ruta crítica — instalalo o definí CHROME=<ruta>"
fi
if command -v soffice >/dev/null || command -v cscript.exe >/dev/null 2>&1; then ok "LibreOffice u Office (PDF de Word y PowerPoint)"
else warn "LibreOffice/Office: hace falta para exportar a PDF — apt install libreoffice"; fi
[ "$FALLAS" -gt 0 ] && { echo; echo "Faltan dependencias obligatorias."; exit 1; }

# ---------------------------------------------------------------- catálogo de docentes
catalogo_ok() { [ -d "$1/docentes" ]; }
PUBLICO="$REPO/catalogo-publico"
sembrar_publico() { # copia el catálogo público (sin nombres) a un repo git LOCAL: tus cambios van a tu rama local/<usuario>
  mkdir -p "$ALIAS_DOC"
  cp -a "$PUBLICO/." "$ALIAS_DOC/"
  ( cd "$ALIAS_DOC" && git init -q -b main && git add -A && git -c user.name=install -c user.email=install@localhost commit -q -m "chore(docentes): snapshot del catálogo público" )
}
obtener_catalogo() {
  local origen=""
  if [ -n "$CATALOGO" ]; then
    case "$CATALOGO" in
      http*|git@*|ssh://*|file://*)
        origen="$REPO/catalogo"
        if [ ! -e "$origen/.git" ]; then
          if git clone -q "$CATALOGO" "$origen" 2>/dev/null; then
            [ -d "$REPO/.git" ] && { grep -qx 'catalogo/' "$REPO/.git/info/exclude" 2>/dev/null || echo 'catalogo/' >> "$REPO/.git/info/exclude"; }
          else warn "no pude clonar $CATALOGO (¿tenés acceso?)"; origen=""; fi
        fi ;;
      *) if [ -d "$CATALOGO" ]; then origen="$(cd "$CATALOGO" && pwd)"; else warn "no existe la carpeta $CATALOGO"; fi ;;
    esac
  fi
  if [ -n "$origen" ] && ! catalogo_ok "$origen"; then origen=""; fi
  if [ -n "$origen" ]; then
    if [ -d "$ALIAS_DOC" ] && [ ! -L "$ALIAS_DOC" ]; then warn "$ALIAS_DOC es una carpeta real: no la reemplazo por el catálogo"
    else mkdir -p "$(dirname "$ALIAS_DOC")"; ln -sfn "$origen" "$ALIAS_DOC"; ok "catálogo de docentes: $origen"; fi
    return
  fi
  # Opcional: el catálogo público de docentes (sin nombres). En una terminal se pregunta; por defecto, no.
  if [ -z "$CATALOGO_PUBLICO" ] && [ -t 0 ] && [ -z "$CATALOGO" ] && ! catalogo_ok "$ALIAS_DOC" && [ -d "$PUBLICO/docentes" ]; then
    printf '  ¿Descargar el catálogo público de docentes (criterios sin nombres; el nombre de tu docente lo reconocés vos, en tu máquina)? [s/N] '
    read -r r; case "$r" in s|S|si|sí|y|Y) CATALOGO_PUBLICO=1 ;; esac
  fi
  if [ -n "$CATALOGO_PUBLICO" ]; then
    if [ ! -d "$PUBLICO/docentes" ]; then warn "este clon no trae catalogo-publico/ (actualizá con git pull)"
    elif [ -L "$ALIAS_DOC" ]; then warn "$ALIAS_DOC apunta a otro catálogo: no lo reemplazo"
    elif [ -d "$ALIAS_DOC/.git" ]; then bash "$REPO/scripts/actualizar_catalogo.sh" "$ALIAS_DOC" || warn "no pude sincronizar el catálogo público"; ok "catálogo público sincronizado"
    else rm -rf "$ALIAS_DOC"; sembrar_publico; ok "catálogo público (sin nombres) en $ALIAS_DOC"; fi
  fi
  if catalogo_ok "$ALIAS_DOC"; then
    skip "catálogo de docentes ($ALIAS_DOC)"
  else
    # Sin catálogo: uno vacío y local, para que todo funcione con tus propios informes.
    mkdir -p "$ALIAS_DOC/docentes"
    sed "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" "$SKILLS_REPO/asistente-trabajo-de-grado/assets/jerarquia-autoridad.md" > "$ALIAS_DOC/docentes/jerarquia-autoridad.md"
    sed "s/YYYY-MM-DD/$(date +%Y-%m-%d)/g" "$SKILLS_REPO/asistente-trabajo-de-grado/assets/plantilla-docente.md" > "$ALIAS_DOC/docentes/_plantilla-docente.md"
    printf '# Catálogo local de docentes\n\nCreado por install.sh. Los docentes se agregan con scripts/nuevo_docente.py; el catálogo público opcional: ./install.sh --catalogo-publico.\n' > "$ALIAS_DOC/README.md"
    ( cd "$ALIAS_DOC" && git init -q -b main && git add -A && git -c user.name=install -c user.email=install@localhost commit -q -m "chore(docentes): catálogo local vacío" )
    ok "catálogo de docentes local y vacío ($ALIAS_DOC)"
  fi
}

if [ "$CHECK" -eq 1 ]; then
  echo
  echo "== estado =="
  [ -L "$ALIAS" ] && ok "alias skills $ALIAS" || warn "sin alias $ALIAS (corré ./install.sh)"
  catalogo_ok "$ALIAS_DOC" && ok "catálogo de docentes ($ALIAS_DOC)" || warn "sin catálogo de docentes"
  for dir in "${AGENTES[@]}"; do
    n=0; for s in "$SKILLS_REPO"/*/; do [ -L "$dir/$(basename "$s")" ] && n=$((n+1)); done
    [ "$n" -eq "$(ls -d "$SKILLS_REPO"/*/ | wc -l)" ] && ok "agente $dir: $n skills enlazadas" || warn "agente $dir: faltan skills (corré ./install.sh --agentes $dir)"
  done
  if [ -n "$DESTINO" ] && [ -d "$DESTINO" ]; then
    [ -d "$DESTINO/.git" ] && ok "vault es un repo git" || warn "el vault no es un repo git"
    [ "$(git -C "$DESTINO" config core.hooksPath 2>/dev/null)" = ".githooks" ] && ok "hook pre-commit del vault" || warn "hook del vault sin activar"
    if catalogo_ok "$ALIAS_DOC"; then python3 "$REPO/scripts/asignar_evaluador.py" "$DESTINO" --check || FALLAS=$((FALLAS+1)); fi
  fi
  echo
  echo "== verificación del repo =="
  bash "$REPO/scripts/auditar-rutas.sh" || FALLAS=$((FALLAS+1))
  bash "$REPO/scripts/auditar-pii.sh"  || FALLAS=$((FALLAS+1))
  if [ -n "$DESTINO" ] && [ -x "$DESTINO/scripts/verificar-enlaces.sh" ]; then
    bash "$DESTINO/scripts/verificar-enlaces.sh" 2>&1 | tail -2
  fi
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

# Carpeta de la defensa: config y plantillas.
D="sources/_propuestas/DEFENSA"
copiar_asset "$A/defensa/defensa.example.json"           "$D/defensa.json"
copiar_asset "$A/defensa/correcciones-tg.plantilla.md"   "$D/CORRECCIONES-TG/correcciones-tg.md"
copiar_asset "$A/defensa/pendientes-defensa.plantilla.md" "$D/PENDIENTES-DEFENSA.md"

echo
echo "== catálogo de docentes =="
obtener_catalogo

# ---------------------------------------------------------------- tu trabajo de grado
if [ -n "$DOCX" ]; then
  echo
  echo "== tu trabajo de grado =="
  DOCX="$(cd "$(dirname "$DOCX")" && pwd)/$(basename "$DOCX")"
  if [ ! -f "$DOCX" ]; then
    err "no existe $DOCX"
  elif VAULT="$DESTINO" python3 "$SKILLS_REPO/extraer-doc-tesis/scripts/extract_document.py" "$DOCX" >/dev/null; then
    SLUG="$(python3 -c 'import sys,re,unicodedata as u; s=u.normalize("NFKD",sys.argv[1]).encode("ascii","ignore").decode().lower(); print(re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-"))' "$(basename "${DOCX%.*}")")"
    ok "extraído en sources/$SLUG.md"
    if [ -e "$DESTINO/proyecto.yaml" ]; then skip "proyecto.yaml"; else
      python3 "$REPO/scripts/inicializar_desde_tg.py" "$DESTINO" "$SLUG" || err "inicializar_desde_tg.py"
    fi
    # La tabla del documento maestro en ORDEN-DEL-VAULT.md deja de tener placeholders.
    sed -i -e "s|<ruta al .docx vivo de tu trabajo>|$DOCX|" -e "s|sources/<slug>\.|sources/$SLUG.|g" "$DESTINO/ORDEN-DEL-VAULT.md"
    sed -i "s|\$TG_DOCX|$DOCX|" "$DESTINO/$D/defensa.json"
    # El TG extraído cuelga del hub raíz (si no, verificar-enlaces lo da por huérfano).
    grep -q "\[\[sources/$SLUG\]\]" "$DESTINO/index.md" || \
      sed -i "s|^## Datos$|## Datos\n\n- [[sources/$SLUG]] — tu trabajo de grado extraído (no se edita: se re-extrae)|" "$DESTINO/index.md"
  else
    err "no pude extraer $DOCX (¿falta pandoc?)"
  fi
fi

# ---------------------------------------------------------------- evaluadores, enlaces y config
echo
echo "== evaluadores y config =="
python3 "$REPO/scripts/asignar_evaluador.py" "$DESTINO" --desde-tg || err "asignar_evaluador.py --desde-tg"
python3 "$REPO/scripts/asignar_evaluador.py" "$DESTINO" --sync || err "asignar_evaluador.py --sync"
if [ -f "$REPO/.env.local" ]; then
  skip ".env.local"
else
  sed -e "s|^VAULT=.*|VAULT=\"$DESTINO\"|" -e "s|^SKILLS=.*|SKILLS=\"$SKILLS_REPO\"|" "$REPO/.env.example" > "$REPO/.env.local"
  if [ -n "$DOCX" ]; then
    sed -i -e "s|^CORPUS=.*|CORPUS=\"$(dirname "$DOCX")\"|" -e "s|^TG_DOCX=.*|TG_DOCX=\"$DOCX\"|" "$REPO/.env.local"
  fi
  ok ".env.local (VAULT, SKILLS$([ -n "$DOCX" ] && echo ", CORPUS, TG_DOCX")); revisá el resto"
fi
if [ -n "$CODE_REPO" ]; then
  CODE_REPO="$(cd "$CODE_REPO" 2>/dev/null && pwd)" || { err "no existe la carpeta de tu proyecto"; CODE_REPO=""; }
  if [ -n "$CODE_REPO" ]; then
    if grep -q '^CODE_REPO=' "$REPO/.env.local"; then sed -i "s|^CODE_REPO=.*|CODE_REPO=\"$CODE_REPO\"|" "$REPO/.env.local"
    else printf 'CODE_REPO="%s"\n' "$CODE_REPO" >> "$REPO/.env.local"; fi
    ok "CODE_REPO=$CODE_REPO"
  fi
fi

# ---------------------------------------------------------------- vault como repositorio
echo
echo "== repositorio del vault =="
if [ -d "$DESTINO/.git" ]; then skip "el vault ya es un repo git"; else git -C "$DESTINO" init -q -b main && ok "git init en el vault"; fi
git -C "$DESTINO" config core.hooksPath .githooks && ok "pre-commit del vault: 0 wikilinks rotos y ningún enlace versionado"
if [ -z "$(git -C "$DESTINO" rev-parse --verify -q HEAD)" ]; then
  git -C "$DESTINO" add -A
  NOMBRE="$(git -C "$DESTINO" config user.name || true)"; CORREO="$(git -C "$DESTINO" config user.email || true)"
  if git -C "$DESTINO" -c user.name="${NOMBRE:-estudiante}" -c user.email="${CORREO:-estudiante@localhost}" \
       commit -q -m "chore(vault): vault inicial desde mi trabajo de grado"; then
    ok "primer commit del vault"
  else
    err "el primer commit del vault fue rechazado por el pre-commit (corré: bash $DESTINO/scripts/verificar-enlaces.sh)"
  fi
  [ -z "$NOMBRE" ] && warn "git no tiene tu nombre: git config --global user.name \"Tu Nombre\" y user.email"
else
  skip "el vault ya tiene commits"
fi
if [ -n "$REMOTO" ]; then
  if ! command -v gh >/dev/null 2>&1; then warn "--remoto necesita gh (apt install gh && gh auth login)"
  elif git -C "$DESTINO" remote get-url origin >/dev/null 2>&1; then skip "el vault ya tiene remoto origin"
  elif ( cd "$DESTINO" && gh repo create "$REMOTO" --private --source . --remote origin >/dev/null 2>&1 ); then
    ok "repo PRIVADO creado en GitHub como $REMOTO (sin push)"
    warn "cuando quieras publicarlo: git -C $DESTINO push -u origin main"
  else warn "no pude crear el repo remoto (¿gh auth login?)"; fi
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
    destino="$dir/$(basename "$s")"
    if [ -e "$destino" ] && [ ! -L "$destino" ]; then warn "$destino ya existe y no es un enlace: lo dejo (copias viejas no se actualizan)"
    else ln -sfn "${s%/}" "$destino"; fi
  done
  ok "skills en $dir"
done
warn "otros agentes: ./install.sh --agentes ~/.claude/skills (o el que uses)"
if [ -n "$CODE_REPO" ]; then
  cat <<FIN

  Para que el agente de tu proyecto use las skills, agregá esto al AGENTS.md (o CLAUDE.md) de $CODE_REPO:

    ## Trabajo de grado
    - Las skills del TG están en $ALIAS (asistente-trabajo-de-grado, perfil-revisor-tg, generar-entregables-tesis, extraer-doc-tesis).
    - Mi vault: $DESTINO. Antes de redactar o corregir un entregable, leer su proyecto.yaml.
    - Las skills no modifican el Word ni el código: entregan propuestas.
FIN
fi

# ---------------------------------------------------------------- hooks del repo de skills y verificación
if [ -d "$REPO/.git" ]; then
  git -C "$REPO" config core.hooksPath .husky && ok "pre-commit activo en el clon de las skills (core.hooksPath)"
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
  1. Pedile a tu agente: "inicializá el vault desde mi TG" (modo inicializar de asistente-trabajo-de-grado):
     completa proyecto.yaml y los modelos de la defensa citando tu TG, y te pregunta quiénes son tus evaluadores.
  2. Cada revisión que recibas: "ingerir informe" y "registrar corrección" (perfil-revisor-tg). Lo aprendido queda en tu
     catálogo local; para compartirlo con los demás: python3 $REPO/scripts/contribuir.py (te muestra qué se enviaría).
  3. Otra máquina: git clone <tu-vault> y ./install.sh --destino <tu-vault> (rehace enlaces y config).
FIN
else
  echo "Terminó con $FALLAS problema(s): revisá las líneas 'FALLA' de arriba."
fi
exit $(( FALLAS > 0 ))
