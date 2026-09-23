#!/usr/bin/env python3
"""Parse gemini_gems_data.html -> nota markdown por Gem de Gemini.

Modo 1 (listar):  python parse_gemini_gems.py --src <html> --listar
                  Emite los nombres de los Gems para que el agente los clasifique.
Modo 2 (volcar):  python parse_gemini_gems.py --src <html> --out <dir>
                  Genera una nota por Gem. Cada nota se etiqueta como
                  juridico o no-juridico; la distinción la hace el agente y se
                  pasa por --clasificacion ({"<nombre gem>": "<tema>"|null}).
"""
import argparse
import html as htmllib
import json
import re
from pathlib import Path


def extract_gems(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    gems = []
    i = 0
    while i < len(lines):
        if lines[i] == "Nombre:" and i + 1 < len(lines):
            name = lines[i + 1]
            j = i + 2
            instr = []
            arch = []
            while j < len(lines) and lines[j] != "Nombre:":
                if lines[j] == "Instrucciones:":
                    j += 1
                    while j < len(lines) and lines[j] != "Archivos:" and lines[j] != "Nombre:":
                        instr.append(lines[j]); j += 1
                    if j < len(lines) and lines[j] == "Archivos:":
                        j += 1
                        while j < len(lines) and lines[j] != "Nombre:" and lines[j] != "Instrucciones:":
                            arch.append(lines[j]); j += 1
                    break
                else:
                    j += 1
            if instr:
                gems.append({"name": name, "instrucciones": "\n".join(instr), "archivos": arch})
            i = j
        else:
            i += 1
    return gems


def listar(src):
    with open(src, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    text = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = htmllib.unescape(text)
    gems = extract_gems(text)
    print(f"Total Gems: {len(gems)}\n")
    for n, g in enumerate(gems):
        print(f"{n} | {g['name']}")


def volcar(src, out, clasificacion_path=None):
    with open(src, encoding="utf-8", errors="replace") as f:
        raw = f.read()
    text = re.sub(r"<script.*?</script>", " ", raw, flags=re.S)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.S)
    text = re.sub(r"<[^>]+>", "\n", text)
    text = htmllib.unescape(text)
    gems = extract_gems(text)

    temas = {}
    if clasificacion_path:
        with open(clasificacion_path, encoding="utf-8") as f:
            temas = json.load(f)

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for n, g in enumerate(gems):
        tema = temas.get(g["name"]) if temas else None
        tags = ["gemini-gem", tema or "no-juridico"]
        lines = ["---",
                 f'title: "Gem Gemini — {g["name"]}"',
                 "type: gem-gemini",
                 "source: gemini_gems_data.html",
                 f"gem_index: {n}",
                 f"categoria: {tema or 'no-juridico'}",
                 "status: extraido",
                 "fiabilidad: instrucciones redactadas por el vocal (criterio, no hecho normativo)",
                 "tags:",
                 *[f"  - {t}" for t in tags],
                 "---",
                 "",
                 f'# {g["name"]}',
                 "",
                 "## Instrucciones del Gem",
                 "",
                 g["instrucciones"],
                 ""]
        if g["archivos"]:
            lines += ["## Archivos adjuntos del Gem", ""]
            lines += [f"- {a}" for a in g["archivos"]]
            lines += [""]
        slug = re.sub(r"[^a-z0-9]+", "-", g["name"].lower()).strip("-")[:40]
        fname = f"{n:02d}-{tema or 'no-juridico'}-{slug}.md"
        (out / fname).write_text("\n".join(lines), encoding="utf-8")
        print(f"  ok {fname}")
    print(f"Gems volcados: {len(gems)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="ruta a gemini_gems_data.html")
    ap.add_argument("--out", default=None, help="dir de salida de notas")
    ap.add_argument("--clasificacion", default=None, help="json {\"<nombre>\": \"<tema>\"|null}")
    ap.add_argument("--listar", action="store_true", help="emitir nombres de Gems")
    args = ap.parse_args()

    if args.listar:
        listar(args.src)
    elif args.out:
        volcar(args.src, args.out, args.clasificacion)
    else:
        ap.error("Usar --listar o --out")


if __name__ == "__main__":
    main()
