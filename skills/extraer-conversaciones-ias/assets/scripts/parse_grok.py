#!/usr/bin/env python3
"""Parse grok-conversations.json -> notas markdown por conversación jurídica.

Formato de Grok: {"conversations": [{conversation: {title,...}, responses:
[{response: {message, sender: human|assistant, model, file_attachments}}]}],
"projects": [{name, custom_personality}], "tasks": [], "media_posts": []}.
Los file_attachments son solo IDs (sin contenido) — no inventar.

Modo 1 (listar):  python parse_grok.py --src <json> --listar
Modo 2 (volcar):  python parse_grok.py --src <json> --out <dir> --clasificacion <json>
Modo 3 (project): python parse_grok.py --src <json> --project --out <dir>
                  Vuelca custom_personality de cada proyecto.
"""
import argparse
import json
import re
from pathlib import Path


def conv_size(c):
    t = 0
    for r in c.get("responses", []):
        t += len(r.get("response", {}).get("message", "") or "")
    return t


def first_text(c, sender):
    for r in c.get("responses", []):
        m = r.get("response", {})
        if m.get("sender") == sender and (m.get("message") or "").strip():
            return m["message"].strip()
    return ""


def is_api_error(content):
    return bool(re.search(r"(?i)oops|high traffic|check back|error al procesar|no pude procesar|upload.*(fail|not)", content))


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "sin-titulo"


def summarize(content, n=220):
    return content[:n].replace("\n", " ") + ("…" if len(content) > n else "")


def listar(src):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    convs = data.get("conversations", [])
    print(f"Total conversaciones: {len(convs)}\n")
    for i, c in enumerate(convs):
        title = c.get("conversation", {}).get("title", "") or ""
        h = first_text(c, "human")
        n = len(c.get("responses", []))
        print(f"{i} | {conv_size(c):8d} | {n:2d} msgs | {title[:55]:55s} | {h[:70].replace(chr(10),' ')}")


def volcar(src, out, clasificacion_path):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    with open(clasificacion_path, encoding="utf-8") as f:
        cla = json.load(f)
    juridicas = {int(k): v for k, v in cla.get("juridica", {}).items()}
    excluidas = {int(k): v for k, v in cla.get("excluida", {}).items()}
    convs = data.get("conversations", [])

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    creadas = []
    for i, c in enumerate(convs):
        if i not in juridicas:
            continue
        cat = juridicas[i]
        reqs = []
        resps = []
        for r in c.get("responses", []):
            m = r.get("response", {})
            msg = (m.get("message") or "").strip()
            if not msg:
                continue
            if m.get("sender") == "human":
                reqs.append(msg)
            else:
                resps.append(msg)

        first_resp = resps[0] if resps else ""
        last_resp = resps[-1] if resps else ""
        mid_resps = resps[1:-1] if len(resps) > 2 else []
        conv = c.get("conversation", {})
        title = conv.get("title", "") or (reqs[0][:60] if reqs else "sin-titulo")
        model = next((r.get("response", {}).get("model", "") for r in c.get("responses", []) if r.get("response", {}).get("model")), "grok")

        lines = ["---",
                 f'title: "Grok — {title}"',
                 "type: conversacion-ia",
                 "source: grok-conversations.json",
                 f"conv_index: {i}",
                 f"categoria: {cat}",
                 f"created: {conv.get('create_time','')[:10]}",
                 f"updated: {conv.get('modify_time','')[:10]}",
                 f"modelo: {model}",
                 "status: extraido",
                 "fiabilidad: respuesta-IA no validada",
                 "tags:",
                 "  - conversacion-ia",
                 "  - grok",
                 f"  - {cat}",
                 "---",
                 "",
                 f"# {title}",
                 "",
                 "> [!info] Metadatos",
                 f"> - **Fuente:** grok-conversations.json (conversación #{i})",
                 f"> - **Tema:** `{cat}`",
                 f"> - **Modelo:** {model}",
                 f"> - **Fechas:** {conv.get('create_time','')[:19]} → {conv.get('modify_time','')[:19]}",
                 f"> - **Mensajes:** {len(reqs)} prompts del vocal, {len(resps)} respuestas de la IA",
                 f"> - **Adjuntos (file_attachments):** solo IDs, sin contenido en el export",
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

        fname = f"{i:02d}-{cat}-{slugify(title)[:40]}.md"
        (out / fname).write_text("\n".join(lines), encoding="utf-8")
        creadas.append(fname)

    print(f"Notas creadas: {len(creadas)} (jurídicas: {len(juridicas)}, excluidas: {len(excluidas)})")
    for f in creadas:
        print(f"  ok {f}")


def project(src, out):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for p in data.get("projects", []):
        name = p.get("name") or "proyecto-sin-nombre"
        personality = p.get("custom_personality") or ""
        slug = slugify(name)
        lines = ["---",
                 f'title: "Proyecto Grok — {name}"',
                 "type: proyecto-grok",
                 "source: grok-conversations.json",
                 "status: extraido",
                 "fiabilidad: custom_personality = instrucciones del vocal (criterio)",
                 "tags:",
                 "  - grok",
                 "  - proyecto-grok",
                 "---",
                 "",
                 f"# Proyecto Grok — {name}",
                 "",
                 f"> **Modelo preferido:** {p.get('preferred_model','')}",
                 "",
                 "## Personalidad del proyecto (criterio del vocal)",
                 "",
                 personality or "*(sin custom_personality)*",
                 ""]
        (out / f"{slug}.md").write_text("\n".join(lines), encoding="utf-8")
        print(f"ok: {slug}.md")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--clasificacion", default=None)
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--project", action="store_true")
    args = ap.parse_args()

    if args.listar:
        listar(args.src)
    elif args.project and args.out:
        project(args.src, args.out)
    elif args.out and args.clasificacion:
        volcar(args.src, args.out, args.clasificacion)
    else:
        ap.error("Usar --listar, --project --out, o --out con --clasificacion")


if __name__ == "__main__":
    main()
