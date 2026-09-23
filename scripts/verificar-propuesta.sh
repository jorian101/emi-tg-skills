#!/usr/bin/env bash
# verificar-propuesta.sh — Suite de verificación mecánica de un corregido/propuesta.
# Uso: bash scripts/verificar-propuesta.sh <corregido.md> [<docx1> <docx2> ...]
# Sale 0 si todo pasa; lista cada fallo. Regla 37 de perfil-revisor-tg.
set -uo pipefail
MD="${1:?uso: verificar-propuesta.sh <corregido.md> [docx...]}"
shift || true
FAIL=0
ok()   { echo "OK   $1"; }
bad()  { echo "FALLA $1"; FAIL=1; }

# 1. viñetas inline en render plain (MT-30)
N=$(pandoc -t plain "$MD" | grep -c ': - ' || true)
[ "$N" -eq 0 ] && ok "0 viñetas inline" || bad "$N viñetas inline (pandoc -t plain ': - ')"

# 2. siglas prohibidas (MP-5)
N=$(grep -c -E '\b(TSJM|TPJM|SAC)\b' "$MD" || true)
[ "$N" -eq 0 ] && ok "0 siglas TSJM/TPJM/SAC" || bad "$N siglas prohibidas"

# 3. sin H5 (MP-7/MP-14)
N=$(grep -c '^##### ' "$MD" || true)
[ "$N" -eq 0 ] && ok "0 H5" || bad "$N encabezados H5"

# 4. menciones Tabla/Figura únicas (MP-11)
DUP=$(grep -o -E '(Tabla|Figura) [0-9]+' "$MD" | sort | uniq -d | tr '\n' ' ')
[ -z "$DUP" ] && ok "menciones únicas" || bad "menciones duplicadas: $DUP"

# 4b. menciones con tabla real (cada "Tabla N" debe tener su tabla `| --- |`; detecta tablas perdidas en rebuilds)
NMEN=$(grep -o -E 'Tabla [0-9]+' "$MD" | sort -u | wc -l)
NTAB=$(awk '/^\| [-:| ]+\|$/{n++} END{print n+0}' "$MD")
[ "$NMEN" -eq "$NTAB" ] && ok "menciones ($NMEN) = tablas ($NTAB)" || bad "menciones ($NMEN) != tablas ($NTAB): hay mención sin tabla o tabla sin mención"

# 5. concordancias conocidas (subcadenas, no match exacto)
PAT='se resume los|se expone los|se describe estas|se define los|historias de usuarios|se detalla los|Alo largo|Apartir|con base a|debe de'
HIT=$(grep -n -E "$PAT" "$MD" || true)
[ -z "$HIT" ] && ok "0 errores de concordancia/typos" || { bad "concordancias/typos:"; echo "$HIT"; }

# 6. IDs y celdas normalizadas (MT-30)
HIT=$(grep -n -E 'E -0|RF -[0-9]|Estimació n|ID  RF|E-00[0-9]' "$MD" || true)
[ -z "$HIT" ] && ok "IDs normalizados" || { bad "IDs con espacios:"; echo "$HIT"; }

# 7. H4 huérfano (H4 seguido de otro encabezado sin contenido)
HIT=$(grep -n -A2 '^#### ' "$MD" | grep -B1 '^.*-\s*#### ' || true)
if [ -z "$HIT" ]; then ok "0 H4 huérfanos"; else bad "posible H4 huérfano:"; echo "$HIT"; fi

# 7b. corridas de párrafos de una línea (MP-22, solo INFO: la señal la juzga el humano, S9)
# Detecta ≥3 bloques consecutivos de prosa corta (una sola línea, ≤140 car.).
# Excluye encabezados, tablas, citas, listas, Notas, títulos en negrita,
# comentarios, frontmatter y líneas de datos (etiqueta + valor numérico).
# Falsos positivos esperados: listas de cifras, títulos de figura sueltos.
python3 - "$MD" <<'PY' || true
import re, sys
lines = open(sys.argv[1], encoding='utf-8').read().split('\n')
blocks, cur, start = [], [], 1
for idx, ln in enumerate(lines, 1):
    if ln.strip() == '':
        if cur:
            blocks.append((start, cur))
            cur = []
        start = idx + 1
    else:
        cur.append((idx, ln))
if cur:
    blocks.append((start, cur))
def short_prose(b):
    _, bl = b
    if len(bl) != 1:
        return False
    t = bl[0][1].strip()
    if len(t) > 140 or len(t) < 10:
        return False
    if not re.search(r'[A-Za-zÁÉÍÓÚáéíóúñÑ]', t):
        return False
    if re.match(r'^(#{1,6}\s|\||>|- |\* |\d+\.\s|```|<!--|Nota\.|Nota:|\*\*|!\[)', t):
        return False
    if re.match(r'^.{1,50}:\s*[≈\d]', t):
        return False
    return True
run = []
for b in blocks:
    if short_prose(b):
        run.append(b)
    else:
        if len(run) >= 3:
            print('INFO posible fragmentación (MP-22, revisar): líneas ' + ','.join(str(s) for s, _ in run))
        run = []
if len(run) >= 3:
    print('INFO posible fragmentación (MP-22, revisar): líneas ' + ','.join(str(s) for s, _ in run))
PY

# 8. tablas reales en docx (MT-30)
W='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
for D in "$@"; do
  [ -f "$D" ] || { bad "docx inexistente: $D"; continue; }
  N=$(python3 -c "
import sys, zipfile
from xml.etree import ElementTree as ET
W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
root = ET.fromstring(zipfile.ZipFile(sys.argv[1]).read('word/document.xml'))
print(len(root.find(W + 'body').findall(W + 'tbl')))
" "$D")
  echo "INFO $D -> $N w:tbl"
done

# 9. palabras
echo "INFO palabras: $(pandoc -t plain "$MD" | wc -w)"

# 10. frescura del espejo docx (regla 28: el .docx debe regenerarse en el mismo commit que el .md)
for D in "$@"; do
  [ -f "$D" ] || continue
  if [ "$D" -ot "$MD" ]; then bad "espejo desactualizado: $D es más viejo que $MD (regenerar con pandoc)"; else ok "espejo al día: $(basename "$D")"; fi
done
exit $FAIL
