#!/usr/bin/env python3
"""Parse ChatGPT export .md (un archivo por chat) -> notas markdown.

Formato de cada archivo: frontmatter (title, source URL) + bloques
"#### You:" (prompts) y "#### ChatGPT:" (respuestas).

Modo 1 (listar):  python parse_chatgpt_md.py --dir <dir> --listar
Modo 2 (volcar):  python parse_chatgpt_md.py --dir <dir> --out <dir> --clasificacion <json>
                  JSON: {"juridica": {"<basename sin prefijo>": "<categoria>"}, "excluida": {...}}
                  El basename es el nombre del archivo sin "ChatGPT-" ni ".md"
                  (p. ej. "Figuras_procesales_similares").
"""
import argparse
import glob
import hashlib
import json
import re
from pathlib import Path

PREFIX = "ChatGPT-"
SOURCE_LABEL = "chatgpt-chats"


def basename_of(f):
    name = Path(f).stem
    if name.startswith(PREFIX):
        name = name[len(PREFIX):]
    return name


def parse_chat(f):
    c = open(f, encoding="utf-8", errors="replace").read()
    title = re.search(r"^title:\s*(.+)$", c, re.M)
    source = re.search(r"^source:\s*(.+)$", c, re.M)
    title = title.group(1).strip() if title else basename_of(f)
    source = source.group(1).strip() if source else ""
    blocks = re.split(r"\n#### (You|ChatGPT):\s*\n", c)
    msgs = []
    for i in range(1, len(blocks), 2):
        role = "human" if blocks[i] == "You" else "assistant"
        body = blocks[i + 1].strip()
        if body:
            msgs.append((role, body))
    return {"title": title, "source": source, "msgs": msgs, "basename": basename_of(f)}


def is_api_error(content):
    return bool(re.search(r"(?i)oops|high traffic|check back|error al procesar", content))


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "sin-titulo"


def summarize(content, n=220):
    return content[:n].replace("\n", " ") + ("…" if len(content) > n else "")


def listar(d):
    files = sorted(glob.glob(str(Path(d) / "*.md")))
    print(f"Total archivos: {len(files)}\n")
    for f in files:
        p = parse_chat(f)
        total = sum(len(b) for _, b in p["msgs"])
        n_h = sum(1 for r, _ in p["msgs"] if r == "human")
        first = next((b for r, b in p["msgs"] if r == "human"), "")
        print(f"{p['basename'][:48]:48s} | {total:7d} | {n_h:2d} prompts | {first[:70].replace(chr(10),' ')}")


def volcar(d, out, clasificacion_path):
    with open(clasificacion_path, encoding="utf-8") as f:
        cla = json.load(f)
    juridicas = cla.get("juridica", {})
    excluidas = cla.get("excluida", {})

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    creadas = []
    hashes = {}
    for f in sorted(glob.glob(str(Path(d) / "*.md"))):
        bname = basename_of(f)
        if bname not in juridicas:
            continue
        cat = juridicas[bname]
        p = parse_chat(f)
        reqs = [b for r, b in p["msgs"] if r == "human"]
        resps = [b for r, b in p["msgs"] if r == "assistant"]
        first_resp = resps[0] if resps else ""
        last_resp = resps[-1] if resps else ""
        mid_resps = resps[1:-1] if len(resps) > 2 else []

        # hash del archivo fuente
        hashes[bname] = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]

        lines = ["---",
                 f'title: "ChatGPT — {p["title"]}"',
                 "type: conversacion-ia",
                 f"source: {SOURCE_LABEL}",
                 f"categoria: {cat}",
                 "status: extraido",
                 "fiabilidad: respuesta-IA no validada",
                 "tags:",
                 "  - conversacion-ia",
                 "  - chatgpt",
                 f"  - {cat}",
                 "---",
                 "",
                 f'# {p["title"]}',
                 "",
                 "> [!info] Metadatos",
                 f"> - **Fuente:** {p['source'] or 'chatgpt-chats-parte-1'}",
                 f"> - **Tema:** `{cat}`",
                 f"> - **Mensajes:** {len(reqs)} prompts del vocal, {len(resps)} respuestas de la IA",
                 "",
                 "> [!warning] Fiabilidad",
                 "> Los **prompts del vocal** son criterio confiable. Las **respuestas**",
                 "> de la IA son borradores NO validados: pueden ser erróneos o alucinados",
                 "> y el vocal no siempre los corrige. Verificar todo contra fuente primaria.",
                 "",
                 "## Prompts del vocal (criterio)",
                 ""]
        for n, r in enumerate(reqs, 1):
            lines += [f"### Turno {n} — prompt del vocal", "", r, ""]

        lines += ["## Respuesta de la IA — primer borrador", "", first_resp, ""]

        if mid_resps:
            lines += ["## Correcciones intermedias (resumen)", ""]
            for n, r in enumerate(mid_resps, 2):
                lines += [f"- **Respuesta {n}** ({len(r)} chars): {summarize(r)}", ""]
            lines += [""]

        if last_resp and last_resp != first_resp:
            if is_api_error(last_resp):
                lines += ["## Última respuesta de la IA (no validada por el vocal)",
                          "",
                          "> [!warning] Error de servicio",
                          '> Esta "respuesta" fue un error del servicio (sin contenido). No usar como criterio.',
                          ""]
            else:
                lines += ["## Última respuesta de la IA (no validada por el vocal)", "", last_resp, ""]

        fname = f"{slugify(p['title'])[:50]}.md"
        (out / fname).write_text("\n".join(lines), encoding="utf-8")
        creadas.append(fname)

    with open(Path(out) / "_hashes.json", "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)

    print(f"Notas creadas: {len(creadas)} (jurídicas: {len(juridicas)}, excluidas: {len(excluidas)})")
    for f in creadas:
        print(f"  ok {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True, help="dir con los .md de ChatGPT")
    ap.add_argument("--out", default=None)
    ap.add_argument("--clasificacion", default=None)
    ap.add_argument("--source", default="chatgpt-chats",
                    help="etiqueta de la parte (p. ej. chatgpt-chats-parte-2)")
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    global SOURCE_LABEL
    SOURCE_LABEL = args.source

    if args.listar:
        listar(args.dir)
    elif args.out and args.clasificacion:
        volcar(args.dir, args.out, args.clasificacion)
    else:
        ap.error("Usar --listar o --out con --clasificacion")


if __name__ == "__main__":
    main()
