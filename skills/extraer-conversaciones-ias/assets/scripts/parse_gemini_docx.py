#!/usr/bin/env python3
"""Extrae resumenes de chats de gemini.docx -> nota markdown.

Uso: python parse_gemini_docx.py --src <file.docx> --out <dir> --titulo "<titulo>"
"""
import argparse
import re
import zipfile
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="ruta al .docx de resumen de chats")
    ap.add_argument("--out", required=True, help="dir de salida de la nota")
    ap.add_argument("--titulo", default="Resumen de chats de IA", help="título de la nota")
    ap.add_argument("--tag", default="gemini", help="tag de origen (gemini, deepseek, chatgpt...)")
    args = ap.parse_args()

    z = zipfile.ZipFile(args.src)
    xml = z.read("word/document.xml").decode("utf-8", errors="replace")
    text = re.sub(r"<w:p [^>]*>", "\n", xml)
    text = re.sub(r"<w:p>", "\n", text)
    text = re.sub(r"<[^>]+>", "", text)
    paras = [l.strip() for l in text.split("\n") if l.strip()]
    body = "\n\n".join(paras)

    note = f"""---
title: "{args.titulo}"
type: conversacion-ia
source: {Path(args.src).name}
categoria: skill
created: 2026-08-15
updated: 2026-08-15
status: extraido
fiabilidad: texto del propio chat del vocal (fuente confiable)
tags:
  - conversacion-ia
  - {args.tag}
  - skill
---

# {args.titulo}

> [!note] Origen
> Extraído de `{Path(args.src).name}`. Revisar si es variante de material ya
> volcado en el vault antes de duplicar (ej. skill AUTO DE VISTA ya existía en
> `sources/casos-tsjm/raw/promt/promt-operativo.md`).

## Contenido extraído (verbatim del .docx)

{body}
"""
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    fname = f"{re.sub(r'[^a-z0-9]+', '-', args.titulo.lower()).strip('-')[:40]}.md"
    (out / fname).write_text(note, encoding="utf-8")
    print(f"ok: {out / fname}")


if __name__ == "__main__":
    main()
