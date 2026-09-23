#!/usr/bin/env python3
"""Parse chats de Gemini exportados como PDF -> notas markdown.

Formato de cada PDF: título (nombre de archivo), URL gemini.google.com/app/<id>,
bloques "User prompt:" y "Response:". Requiere pdftotext (poppler-utils).

Advertencia de adjuntos: el export de Gemini NO incluye los archivos adjuntos.
Cada prompt se clasifica como:
  - inline:  el documento está pegado en el prompt (texto visible -> usable).
  - ausente: el prompt menciona adjunto pero no trae contenido -> callout.
  - fallido: la respuesta indica que no pudo leer el archivo -> callout.
Se extrae SIEMPRE el criterio del vocal (prompts); los datos del adjunto no
visible NO se adoptan como hecho (patrones de redacción sí, como referencia).

Modo 1 (listar):  python parse_gemini_pdf.py --dir <dir> --listar
Modo 2 (volcar):  python parse_gemini_pdf.py --dir <dir> --out <dir>
                  --clasificacion <json> --source <etiqueta>
                  JSON: {"juridica": {"<basename>": "<categoria>"}, "excluida": {...}}
"""
import argparse
import glob
import hashlib
import json
import re
import subprocess
from pathlib import Path

SOURCE_LABEL = "gemini-parte-1"

RE_PROMPT = re.compile(r"User prompt: (.*?)(?=Response:|$)", re.S)
RE_RESP = re.compile(r"Response: (.*?)(?=User prompt:|$)", re.S)
RE_URL = re.compile(r"https://gemini\.google\.com/app/\S+")
RE_FALLIDO = re.compile(
    r"(?i)(no puedo (leer|ver|acceder)|no puedo leer el archivo|no se pudo|"
    r"no puedo analizar el archivo|archivo.*no.*leer|no tengo acceso al documento|"
    r"no tengo acceso a información personal|vuelve a subir|reenvía|no legible|"
    r"desafortunadamente, no puedo (generar|imagin))"
)
RE_MENCIONA_ADJ = re.compile(
    r"(?i)(adjunt|archivo|documento|foto|imagen|pdf|word|escane|anexo|manual|informe|resolución|sentencia)"
)


def pdf_text(path):
    r = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                       capture_output=True, text=True)
    return r.stdout


def classify_prompt(text):
    """Clasifica un prompt por disponibilidad de adjunto: inline/ausente/fallido."""
    if RE_FALLIDO.search(text):
        return "fallido"
    if RE_MENCIONA_ADJ.search(text):
        # si el texto tiene mucha densidad (el doc pegado), asumimos inline
        if len(text) > 800:
            return "inline"
        return "ausente"
    return "ninguno"


def basename_of(f):
    return Path(f).stem


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "sin-titulo"


def summarize(content, n=220):
    return content[:n].replace("\n", " ") + ("…" if len(content) > n else "")


def listar(d):
    files = sorted(glob.glob(str(Path(d) / "*.pdf")))
    print(f"Total PDFs: {len(files)}\n")
    for f in files:
        t = pdf_text(f)
        prompts = RE_PROMPT.findall(t)
        n_adj = sum(1 for p in prompts if RE_MENCIONA_ADJ.search(p))
        first = prompts[0].strip()[:70].replace("\n", " ") if prompts else ""
        print(f"{basename_of(f)[:48]:48s} | {len(t):6d} | {len(prompts):2d} turnos | {n_adj:2d} con adj | {first}")


def volcar(d, out, clasificacion_path, source):
    with open(clasificacion_path, encoding="utf-8") as f:
        cla = json.load(f)
    juridicas = cla.get("juridica", {})
    excluidas = cla.get("excluida", {})

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    creadas = []
    hashes = {}
    for f in sorted(glob.glob(str(Path(d) / "*.pdf"))):
        bname = basename_of(f)
        if bname not in juridicas:
            continue
        cat = juridicas[bname]
        t = pdf_text(f)
        prompts = [p.strip() for p in RE_PROMPT.findall(t) if p.strip()]
        resps = [r.strip() for r in RE_RESP.findall(t) if r.strip()]
        url_m = RE_URL.search(t)
        url = url_m.group(0) if url_m else ""

        first_resp = resps[0] if resps else ""
        last_resp = resps[-1] if resps else ""
        mid_resps = resps[1:-1] if len(resps) > 2 else []

        hashes[bname] = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]

        # clasificar adjuntos por turno
        adj_status = [classify_prompt(p) for p in prompts]
        n_ausente = adj_status.count("ausente")
        n_fallido = adj_status.count("fallido") + sum(
            1 for r in resps if RE_FALLIDO.search(r)
        )

        lines = ["---",
                 f'title: "Gemini — {bname}"',
                 "type: conversacion-ia",
                 f"source: {source}",
                 f"categoria: {cat}",
                 "status: extraido",
                 "fiabilidad: respuesta-IA no validada",
                 "tags:",
                 "  - conversacion-ia",
                 "  - gemini",
                 f"  - {cat}",
                 "---",
                 "",
                 f"# {bname}",
                 "",
                 "> [!info] Metadatos",
                 f"> - **Fuente:** {url or source}",
                 f"> - **Tema:** `{cat}`",
                 f"> - **Mensajes:** {len(prompts)} prompts del vocal, {len(resps)} respuestas de la IA",
                 ""]
        if n_ausente or n_fallido:
            lines += ["> [!warning] Adjuntos ausentes",
                      f"> El export de Gemini **no incluye los archivos adjuntos** "
                      f"({n_ausente} prompts los mencionan; {n_fallido} respuestas "
                      f"indican fallo de lectura). El criterio del vocal (prompts) se "
                      f"conserva; los datos del adjunto no visible NO se adoptan como "
                      f"hecho — verificar contra fuente primaria.",
                      ""]
        lines += ["> [!warning] Fiabilidad",
                  "> Los **prompts del vocal** son criterio confiable. Las **respuestas**",
                  "> de la IA son borradores NO validados: pueden ser erróneos o alucinados",
                  "> y el vocal no siempre los corrige. Verificar todo contra fuente primaria.",
                  "",
                  "## Prompts del vocal (criterio)",
                  ""]
        for n, p in enumerate(prompts, 1):
            lines += [f"### Turno {n} — prompt del vocal", ""]
            if adj_status[n - 1] == "fallido":
                lines += ["> [!warning] Adjunto fallido",
                          "> La respuesta de la IA indicó que no pudo leer el archivo adjunto. No usar como contenido.",
                          ""]
            elif adj_status[n - 1] == "ausente":
                lines += ["> [!note] Adjunto ausente",
                          "> El prompt menciona un adjunto que el export no incluye. El criterio del vocal se conserva; el contenido del archivo no es visible.",
                          ""]
            lines += [p, ""]

        lines += ["## Respuesta de la IA — primer borrador", "", first_resp, ""]

        if mid_resps:
            lines += ["## Correcciones intermedias (resumen)", ""]
            for n, r in enumerate(mid_resps, 2):
                lines += [f"- **Respuesta {n}** ({len(r)} chars): {summarize(r)}", ""]
            lines += [""]

        if last_resp and last_resp != first_resp:
            if RE_FALLIDO.search(last_resp):
                lines += ["## Última respuesta de la IA (no validada por el vocal)",
                          "",
                          "> [!warning] Adjunto fallido",
                          '> La respuesta fue un error de lectura del adjunto. No usar como criterio.',
                          ""]
            else:
                lines += ["## Última respuesta de la IA (no validada por el vocal)", "", last_resp, ""]

        fname = f"{slugify(bname)[:50]}.md"
        (out / fname).write_text("\n".join(lines), encoding="utf-8")
        creadas.append(fname)

    (out / "_hashes.json").write_text(json.dumps(hashes, ensure_ascii=False, indent=2),
                                      encoding="utf-8")
    print(f"Notas creadas: {len(creadas)} (jurídicas: {len(juridicas)}, excluidas: {len(excluidas)})")
    for f in creadas:
        print(f"  ok {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True, help="dir con los PDFs de Gemini")
    ap.add_argument("--out", default=None)
    ap.add_argument("--clasificacion", default=None)
    ap.add_argument("--source", default="gemini-parte-1")
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    global SOURCE_LABEL
    SOURCE_LABEL = args.source

    if args.listar:
        listar(args.dir)
    elif args.out and args.clasificacion:
        volcar(args.dir, args.out, args.clasificacion, args.source)
    else:
        ap.error("Usar --listar o --out con --clasificacion")


if __name__ == "__main__":
    main()
