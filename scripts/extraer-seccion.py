#!/usr/bin/env python3
"""extraer-seccion.py — Extracción de una sección por rango dinámico H2 desde un .docx.

Uso:
  python3 scripts/extraer-seccion.py <docx> "<H2-INICIO>" "<H2-FIN>" <out.md> <out.json>

- Localiza el párrafo H2 que empieza con H2-INICIO y corta antes del siguiente
  H2/H1 (o ante H2-FIN si se indica).
- Emite .md con párrafos normalizados (una línea en blanco entre bloques) y
  tablas con fila separadora `| --- |` (cuentan como w:tbl en pandoc).
- Emite .json con metadatos: rango, mtime, tamaño, sha (sello de vigencia).
- Orden de documento preservado: paseo secuencial, nunca prosa-primero.

Reglas: MT-30, perfil-revisor-tg 30/34.
"""
import hashlib
import json
import os
import sys
from xml.etree import ElementTree as ET
import zipfile

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def ptext(p):
    return "".join(x.text or "" for x in p.iter(W + "t")).strip()


def pstyle(p):
    for pPr in p.findall(W + "pPr"):
        s = pPr.find(W + "pStyle")
        if s is not None:
            return s.get(W + "val") or ""
    return ""


def main():
    if len(sys.argv) != 6:
        print(__doc__)
        sys.exit(2)
    src, h2_ini, h2_fin, out_md, out_json = sys.argv[1:6]
    with zipfile.ZipFile(src) as z:
        xml = z.read("word/document.xml")
    root = ET.fromstring(xml)
    body = root.find(W + "body")
    plist = list(root.iter(W + "p"))
    pidx = {id(p): i for i, p in enumerate(plist)}

    start = end = None
    for i, p in enumerate(plist):
        t, st = ptext(p), (pstyle(p) or "").lower()
        if start is None and t.startswith(h2_ini) and st.startswith("t"):
            start = i
            continue
        if start is not None and i > start and t:
            if t.startswith(h2_fin) or (st.startswith("t") and not t.startswith(h2_ini)):
                end = i
                break
    if start is None:
        sys.exit(f"ERROR: H2 inicial no hallado: {h2_ini}")
    if end is None:
        end = len(plist)

    md = []
    ntables = 0
    for ch in list(body):
        if ch.tag == W + "p":
            i = pidx.get(id(ch))
            if i is not None and start <= i < end:
                t = ptext(ch)
                if t:
                    md.append(t)
                    md.append("")
        elif ch.tag == W + "tbl":
            ci = [pidx.get(id(p)) for p in ch.iter(W + "p")]
            ci = [c for c in ci if c is not None]
            if not ci or not (start <= min(ci) < end):
                continue
            ntables += 1
            rows = [
                [" ".join(x.text or "" for x in tc.iter(W + "t")).strip()
                 for tc in tr.findall(W + "tc")]
                for tr in ch.findall(W + "tr")
            ]
            ncol = max(len(r) for r in rows)
            rows = [(r + [""] * ncol)[:ncol] for r in rows]
            md.append("| " + " | ".join(rows[0]) + " |")
            md.append("|" + "|".join(" --- " for _ in range(ncol)) + "|")
            for r in rows[1:]:
                md.append("| " + " | ".join(r) + " |")
            md.append("")
    text = "\n".join(md).rstrip() + "\n"
    with open(out_md, "w", encoding="utf-8") as f:
        f.write(text)
    st = os.stat(src)
    meta = {
        "source": src,
        "h2_inicio": h2_ini,
        "para_range": [start, end],
        "paras": end - start,
        "tables_in_range": ntables,
        "words": len(text.split()),
        "mtime": st.st_mtime,
        "size": st.st_size,
        "sha256": hashlib.sha256(xml).hexdigest()[:16],
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=1, ensure_ascii=False)
    print(f"rango {start}-{end} | {meta['words']} palabras | {ntables} tablas")


if __name__ == "__main__":
    main()
