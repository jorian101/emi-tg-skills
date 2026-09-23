#!/usr/bin/env python3
"""Parse claude-projects/*.json -> nota markdown por proyecto de Claude.

Cada proyecto tiene prompt_template (criterio del vocal) y docs (archivos de
referencia). Este script genera:
  - notas/<proyecto>.md  -> prompt_template verbatim + lista de docs
  - notas/<proyecto>-docs/<doc>.md -> contenido completo de cada doc VOLCADO

Docs a solo listar (sin volcar contenido) se pasan por --listar-only (nombre
de archivo exacto o prefijo). Deduplica docs repetidos entre proyectos por
hash del contenido.

Uso:
  python parse_claude_projects.py --dir <claude-projects/> --out <dir>
    [--listar-only "CPE 2009.pdf" "Manual_de_Tecnica_Legislativa.pdf"]
"""
import argparse
import glob
import hashlib
import json
import re
from pathlib import Path


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")
    return s[:50] or "sin-nombre"


def doc_name(d):
    return d.get("filename") or d.get("name") or "documento"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True, help="dir con los proyectos *.json")
    ap.add_argument("--out", required=True, help="dir de salida")
    ap.add_argument("--listar-only", nargs="*", default=[],
                    help="nombres de docs a listar sin volcar contenido")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    seen_hashes = {}

    for f in sorted(glob.glob(str(Path(args.dir) / "*.json"))):
        d = json.load(open(f, encoding="utf-8"))
        name = d.get("name") or "proyecto-sin-nombre"
        slug = slugify(name)
        template = d.get("prompt_template", "") or ""
        docs = [x for x in d.get("docs", []) if (x.get("content") or "").strip()]
        if not template and not docs:
            print(f"skip: {Path(f).stem} (sin prompt_template ni docs)")
            continue

        lines = ["---",
                 f'title: "Proyecto Claude — {name}"',
                 "type: proyecto-claude",
                 "source: claude-projects/",
                 f"proyecto_id: {Path(f).stem}",
                 "status: extraido",
                 "fiabilidad: prompt_template = instrucciones del vocal; docs = material de referencia",
                 "tags:",
                 "  - claude",
                 "  - proyecto-claude",
                 "---",
                 "",
                 f"# Proyecto Claude — {name}",
                 "",
                 f"> **Descripción:** {(d.get('description') or '')[:200]}",
                 "",
                 "## Prompt del proyecto (criterio del vocal)",
                 "",
                 template or "*(sin prompt_template)*",
                 "",
                 "## Docs de referencia del proyecto",
                 "",
                 f"| Archivo | Chars | Contenido |",
                 f"|---|---|---|",
                 ""]
        for doc in docs:
            dn = doc_name(doc)
            content = doc.get("content", "") or ""
            listar_only = any(
                dn.startswith(p) or dn.endswith(p) for p in args.listar_only
            )
            if listar_only:
                lines.append(f"| `{dn}` | {len(content)} | listado (no volcado) |")
                continue
            h = hashlib.sha256(content.encode()).hexdigest()[:12]
            if h in seen_hashes:
                lines.append(f"| `{dn}` | {len(content)} | **duplicado** de `{seen_hashes[h]}` |")
                continue
            seen_hashes[h] = dn
            # volcar doc a subcarpeta
            doc_slug = slugify(dn)
            ddir = out / f"{slug}-docs"
            ddir.mkdir(parents=True, exist_ok=True)
            (ddir / f"{doc_slug}.md").write_text(
                f"---\ntitle: \"{dn}\"\ntype: doc-proyecto-claude\nsource: {Path(f).stem}\nfiabilidad: material de referencia (puede ser norma o borrador)\n---\n\n# {dn}\n\n> Doc de referencia del proyecto Claude **{name}**.\n\n{content}\n",
                encoding="utf-8")
            lines.append(f"| `{dn}` | {len(content)} | volcado → `{ddir.name}/{doc_slug}.md` |")

        (out / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"ok: {slug}.md ({len(docs)} docs)")


if __name__ == "__main__":
    main()
