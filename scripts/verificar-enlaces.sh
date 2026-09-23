#!/usr/bin/env bash
# verificar-enlaces.sh — Detecta wikilinks rotos en el vault (red Karpathy)
# Resuelve como Obsidian: por slug de archivo, título (frontmatter) o alias.
# Uso: bash verificar-enlaces.sh [directorio-vault]
set -uo pipefail

VAULT="${1:-$(dirname "$0")/..}"
VAULT="$(cd "$VAULT" && pwd)"

# Recolecta slugs + títulos + aliases de cada nota
declare -A NAMES
while IFS= read -r f; do
    rel="${f#"$VAULT"/}"
    rel="${rel%.md}"
    # 1) slug (ruta sin extensión y basename)
    NAMES["$rel"]=1
    NAMES["$(basename "$rel")"]=1
    # 2) título y aliases del frontmatter
    title="$(awk '/^title:/{sub(/^title: */,""); gsub(/^"|"$/,""); print; exit}' "$f")"
    [[ -n "$title" ]] && NAMES["$title"]=1
    in_aliases=0
    while IFS= read -r line; do
        if [[ "$line" =~ ^aliases:\ *(.*)$ ]]; then
            rest="${BASH_REMATCH[1]}"
            if [[ "$rest" == "["* ]]; then
                # estilo flow: aliases: ["a", "b"] — extraer entrecomillados
                while [[ "$rest" =~ \"([^\"]+)\" ]]; do
                    NAMES["${BASH_REMATCH[1]}"]=1
                    rest="${rest#*\"${BASH_REMATCH[1]}\"}"
                done
                in_aliases=0
            else
                in_aliases=1
            fi
            continue
        fi
        [[ "$line" =~ ^[a-zA-Z_-]+: ]] && in_aliases=0
        if [[ $in_aliases -eq 1 ]]; then
            a="${line}"
            a="${a#"${a%%[![:space:]]*}"}"
            a="${a#-}"
            a="${a#"${a%%[![:space:]]*}"}"
            [[ -n "$a" ]] && NAMES["$a"]=1
        fi
    done < <(sed -n '1,/^---$/p' "$f")
done < <(find "$VAULT" -name "*.md" -not -path "*/.opencode/*" -not -path "*/node_modules/*" -not -path "*/media/*")

ROTOS=0
while IFS= read -r target; do
    t="${target%%|*}"
    t="${t%%#*}"
    t="${t%%^*}"
    t="${t%%\\}"   # escape de pipe en tablas ([[x\|alias]])
    t="$(echo "$t" | sed 's/^ *//;s/ *$//')"
    [[ "$t" == \#* || "$t" == ^* || -z "$t" ]] && continue
    # probar slug exacto y basename
    if [[ -n "${NAMES[$t]:-}" ]]; then continue; fi
    # fallback: sin carpeta (roles/auditor -> auditor)
    base="${t##*/}"
    if [[ -n "${NAMES[$base]:-}" ]]; then continue; fi
    echo "ROTO: [[$t]]"
    ROTOS=$((ROTOS+1))
done < <(rg -o '\[\[[^]]+' "$VAULT"/wiki "$VAULT"/sources "$VAULT"/index.md "$VAULT"/log.md 2>/dev/null | sed 's/^.*\[\[//' | sort -u)

# --- Passada 2: huérfanas (0 links entrantes y salientes) ---
# La allowlist NO vive acá: se lee del bloque ```allowlist de ORDEN-DEL-VAULT.md.
# Un solo lugar para el dato, y el mismo archivo que lee el humano. Si el bloque falta,
# el verificador falla en voz alta en vez de inventar una lista propia.
ERR_HUERFANAS=0
echo "--- Huérfanas (allowlist en ORDEN-DEL-VAULT.md)"
python3 - "$VAULT" <<'PY'
import fnmatch, os, re, sys

vault = sys.argv[1]
MANIFIESTO = os.path.join(vault, 'ORDEN-DEL-VAULT.md')


def leer_allowlist():
    """Lee el bloque ```allowlist del manifiesto: un patrón por línea.

    Devuelve None si el manifiesto no existe o no tiene el bloque, para poder
    distinguir 'lista vacía' de 'lista ausente'.
    """
    if not os.path.isfile(MANIFIESTO):
        return None
    patrones, dentro = [], False
    with open(MANIFIESTO, encoding='utf-8') as fh:
        for linea in fh:
            t = linea.strip()
            if t == '```allowlist':
                dentro = True
                continue
            if dentro and t.startswith('```'):
                break
            if dentro and t and not t.startswith('#'):
                patrones.append(t)
    return patrones if dentro else None


PATRONES = leer_allowlist()
if PATRONES is None:
    print('ERROR: ORDEN-DEL-VAULT.md no tiene un bloque ```allowlist.')
    print('       El verificador no adivina la lista: agregá el bloque o pasá el vault correcto.')
    sys.exit(2)
EXCL = {'node_modules', '.git', '.obsidian', '.opencode', 'media'}
files = {}
for root, dirs, fn in os.walk(vault):
    dirs[:] = [d for d in dirs if d not in EXCL]
    for f in fn:
        if f.endswith('.md'):
            p = os.path.join(root, f)
            files[os.path.relpath(p, vault)] = open(p, encoding='utf-8', errors='ignore').read()

def allowed(rel):
    """Un path es exento si matchea algún patrón del manifiesto.

    Se prueba el path relativo, el basename (para reglas como `AGENTS.md`) y el
    basename como regex (para reglas como `\\d{4}-\\d{2}-\\d{2}\\.md`).
    """
    b = os.path.basename(rel)
    for pat in PATRONES:
        if fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(b, pat):
            return True
        try:
            if re.fullmatch(pat, b):
                return True
        except re.error:
            pass
    return False

names = {}
for rel in files:
    names.setdefault(os.path.basename(rel)[:-3], []).append(rel)
out, inc = set(), set()
for rel, c in files.items():
    for m in re.findall(r'\[\[([^\]]+)\]', c):
        t = m.split('|')[0].split('#')[0].split('^')[0].replace('\\', '').strip()
        if not t:
            continue
        cands = names.get(os.path.basename(t))
        if not cands:
            continue
        hits = [x for x in cands if '/' not in t or t in x[:-3]]
        for x in (hits if hits else ([] if '/' in t else cands)):
            out.add(rel); inc.add(x)
orph = [r for r in sorted(files) if r not in out and r not in inc and not allowed(r)]
for o in orph:
    print(f"HUERFANA: {o}")
print(f"Huérfanas fuera de allowlist: {len(orph)}")
sys.exit(1 if orph else 0)
PY
[[ $? -ne 0 ]] && ERR_HUERFANAS=1

ERR=0
if [[ $ROTOS -gt 0 ]]; then
    echo "ERROR: $ROTOS wikilinks rotos"
    ERR=1
else
    echo "OK: sin wikilinks rotos ($VAULT)"
fi
if [[ $ERR_HUERFANAS -ne 0 ]]; then
    echo "ERROR: huérfanas fuera de allowlist ($VAULT)"
    ERR=1
fi
exit $ERR
