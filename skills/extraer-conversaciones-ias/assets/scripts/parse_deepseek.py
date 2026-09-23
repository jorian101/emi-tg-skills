#!/usr/bin/env python3
"""Parse deepseek-conversations.json -> notas markdown por conversación jurídica.

Modo 1 (listar):  python parse_deepseek.py --src <json> --listar
                  Emite la tabla (indice | titulo | primer prompt) para que el
                  agente clasifique cada conversación como jurídica o no.
Modo 2 (volcar):  python parse_deepseek.py --src <json> --out <dir>
                  --clasificacion <clasificacion.json> [--manifiesto <dir>]
                  Genera una nota por conversación jurídica + manifiesto de
                  clasificación. El JSON de clasificación debe tener forma:
                  {"juridica": {"<indice>": "<categoria>", ...},
                   "excluida": {"<indice>": "<motivo>", ...}}
                  La clasificación la decide el agente (no el script).
"""
import argparse
import json
import re
from pathlib import Path

REQ_HEADER = "### Turno {n} — prompt del vocal"
RESP_FIRST = "## Respuesta de la IA — primer borrador"
RESP_MID = "## Correcciones intermedias (resumen)"
RESP_LAST = "## Última respuesta de la IA (no validada por el vocal)"
ERR_WARN = (
    "## Última respuesta de la IA (no validada por el vocal)\n\n"
    "> [!warning] Error de servicio\n"
    '> Esta "respuesta" fue un error del servicio de la IA (sin contenido). '
    "No usar como criterio ni como contenido del documento."
)


def walk(mapping, nid, out):
    node = mapping[nid]
    m = node.get("message")
    if m:
        for frag in m.get("fragments", []):
            t = frag.get("type")
            if t in ("REQUEST", "RESPONSE") and frag.get("content", "").strip():
                out.append({"type": t, "content": frag["content"],
                            "model": m.get("model", ""), "ts": m.get("inserted_at", "")})
    for ch in node.get("children", []):
        walk(mapping, ch, out)


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "sin-titulo"


def summarize(content, n=220):
    return content[:n].replace("\n", " ") + ("…" if len(content) > n else "")


def is_api_error(content):
    return bool(re.search(r"(?i)oops|high traffic|check back|error al procesar", content))


def listar(src):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Total conversaciones: {len(data)}\n")
    for i, conv in enumerate(data):
        msgs = []
        walk(conv["mapping"], "root", msgs)
        first = next((m["content"] for m in msgs if m["type"] == "REQUEST"), "")
        print(f"{i} | {conv['title'][:70]} | {first[:110].replace(chr(10), ' ')}")


def volcar(src, out, clasificacion_path):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    with open(clasificacion_path, encoding="utf-8") as f:
        cla = json.load(f)
    juridicas = {int(k): v for k, v in cla.get("juridica", {}).items()}
    excluidas = {int(k): v for k, v in cla.get("excluida", {}).items()}

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    creadas = []
    for i, conv in enumerate(data):
        if i not in juridicas:
            continue
        msgs = []
        walk(conv["mapping"], "root", msgs)
        reqs = [m for m in msgs if m["type"] == "REQUEST"]
        resps = [m for m in msgs if m["type"] == "RESPONSE"]
        cat = juridicas[i]

        first_resp = resps[0]["content"] if resps else ""
        last_resp = resps[-1]["content"] if resps else ""
        mid_resps = resps[1:-1] if len(resps) > 2 else []

        lines = ["---",
                 f'title: "DeepSeek — {conv["title"]}"',
                 "type: conversacion-ia",
                 "source: deepseek",
                 f"conv_index: {i}",
                 f"categoria: {cat}",
                 f"created: {conv.get('inserted_at', '')[:10]}",
                 f"updated: {conv.get('updated_at', '')[:10]}",
                 "status: extraido",
                 "fiabilidad: respuesta-IA no validada",
                 "tags:",
                 "  - conversacion-ia",
                 "  - deepseek",
                 f"  - {cat}",
                 "---",
                 "",
                 f'# {conv["title"]}',
                 "",
                 "> [!info] Metadatos",
                 f"> - **Fuente:** deepseek-conversations.json (conversación #{i})",
                 f"> - **Tema:** `{cat}`",
                 f"> - **Fechas:** {conv.get('inserted_at','')[:19]} → {conv.get('updated_at','')[:19]}",
                 f"> - **Mensajes:** {len(reqs)} prompts del vocal, {len(resps)} respuestas de la IA",
                 f"> - **Adjuntos (FILE):** no disponibles en el export (vienen vacíos)",
                 "",
                 "> [!warning] Fiabilidad",
                 "> Los **prompts del vocal** son criterio confiable. Las **respuestas**",
                 "> de la IA son borradores NO validados: pueden ser erróneos o alucinados",
                 "> y el vocal no siempre los corrige. Verificar todo contra fuente primaria.",
                 "",
                 "## Prompts del vocal (criterio)",
                 ""]
        for n, m in enumerate(reqs, 1):
            lines += [REQ_HEADER.format(n=n), "", m["content"].strip(), ""]

        lines += [RESP_FIRST, "", first_resp.strip(), ""]

        if mid_resps:
            lines += [RESP_MID, ""]
            for n, m in enumerate(mid_resps, 2):
                lines += [f"- **Respuesta {n}** ({len(m['content'])} chars): {summarize(m['content'])}", ""]
            lines += [""]

        if last_resp and last_resp != first_resp:
            header = ERR_WARN if is_api_error(last_resp) else RESP_LAST
            if is_api_error(last_resp):
                lines += [header, "", "*(Respuesta no generada — error de servicio de la IA)*", ""]
            else:
                lines += [header, "", last_resp.strip(), ""]

        fname = f"{i:02d}-{cat}-{slugify(conv['title'])[:40]}.md"
        (out / fname).write_text("\n".join(lines), encoding="utf-8")
        creadas.append(fname)

    print(f"Notas creadas: {len(creadas)} (jurídicas: {len(juridicas)}, excluidas: {len(excluidas)})")
    for f in creadas:
        print(f"  ok {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True, help="ruta a deepseek-conversations.json")
    ap.add_argument("--out", default=None, help="dir de salida de notas")
    ap.add_argument("--clasificacion", default=None, help="json {juridica, excluida}")
    ap.add_argument("--listar", action="store_true", help="emitir tabla para clasificar")
    args = ap.parse_args()

    if args.listar:
        listar(args.src)
    elif args.out and args.clasificacion:
        volcar(args.src, args.out, args.clasificacion)
    else:
        ap.error("Usar --listar o --out con --clasificacion")


if __name__ == "__main__":
    main()
