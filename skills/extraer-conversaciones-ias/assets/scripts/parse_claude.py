#!/usr/bin/env python3
"""Parse claude-conversations.json -> notas markdown por conversación jurídica.

Formato de Claude: lista de conversaciones con chat_messages[{sender,
content:[{type:text,...}]}]. Solo se extrae el texto de bloques type=text;
thinking/tool_use/tool_result son ruido del razonamiento de Claude.

Modo 1 (listar):  python parse_claude.py --src <json> --listar
Modo 2 (volcar):  python parse_claude.py --src <json> --out <dir> --clasificacion <json>
                  JSON: {"juridica": {"<indice>": "<categoria>"}, "excluida": {...}}
"""
import argparse
import json
import re
from pathlib import Path


def conv_size(c):
    t = 0
    for m in c.get("chat_messages", []):
        for ct in m.get("content", []) or []:
            if ct.get("type") == "text":
                t += len(ct.get("text", "") or "")
    return t


def first_text(c, sender):
    for m in c.get("chat_messages", []):
        if m.get("sender") != sender:
            continue
        for ct in m.get("content", []) or []:
            if ct.get("type") == "text" and (ct.get("text", "") or "").strip():
                return ct["text"].strip()
    return ""


def is_api_error(content):
    return bool(re.search(r"(?i)oops|high traffic|check back|error|file doesn't seem to have come through|upload", content))


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "sin-titulo"


def summarize(content, n=220):
    return content[:n].replace("\n", " ") + ("…" if len(content) > n else "")


def listar(src):
    with open(src, encoding="utf-8") as f:
        data = json.load(f)
    print(f"Total conversaciones: {len(data)}\n")
    for i, c in enumerate(data):
        h = first_text(c, "human")
        print(f"{i} | {c.get('name','')[:60]:60s} | {conv_size(c):7d} | {h[:90].replace(chr(10),' ')}")


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
    for i, c in enumerate(data):
        if i not in juridicas:
            continue
        msgs = [m for m in c.get("chat_messages", [])]
        humans = [m for m in msgs if m.get("sender") == "human"]
        assistants = [m for m in msgs if m.get("sender") == "assistant"]
        cat = juridicas[i]

        def texts_of(msg):
            return " ".join(ct.get("text", "") or ""
                            for ct in msg.get("content", []) or []
                            if ct.get("type") == "text").strip()

        reqs = [texts_of(m) for m in humans if texts_of(m)]
        resps = [texts_of(m) for m in assistants if texts_of(m)]

        first_resp = resps[0] if resps else ""
        last_resp = resps[-1] if resps else ""
        mid_resps = resps[1:-1] if len(resps) > 2 else []

        name = c.get("name", "") or (reqs[0][:60] if reqs else "sin-titulo")
        lines = ["---",
                 f'title: "Claude — {name}"',
                 "type: conversacion-ia",
                 "source: claude-conversations.json",
                 f"conv_index: {i}",
                 f"categoria: {cat}",
                 f"created: {c.get('created_at','')[:10]}",
                 f"updated: {c.get('updated_at','')[:10]}",
                 "status: extraido",
                 "fiabilidad: respuesta-IA no validada",
                 "tags:",
                 "  - conversacion-ia",
                 "  - claude",
                 f"  - {cat}",
                 "---",
                 "",
                 f'# {name}',
                 "",
                 "> [!info] Metadatos",
                 f"> - **Fuente:** claude-conversations.json (conversación #{i})",
                 f"> - **Tema:** `{cat}`",
                 f"> - **Fechas:** {c.get('created_at','')[:19]} → {c.get('updated_at','')[:19]}",
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
                          '> Esta "respuesta" fue un error del servicio (archivo no recibido o error de la IA). No usar como criterio.',
                          ""]
            else:
                lines += ["## Última respuesta de la IA (no validada por el vocal)", "", last_resp, ""]

        fname = f"{i:02d}-{cat}-{slugify(name)[:40]}.md"
        (out / fname).write_text("\n".join(lines), encoding="utf-8")
        creadas.append(fname)

    print(f"Notas creadas: {len(creadas)} (jurídicas: {len(juridicas)}, excluidas: {len(excluidas)})")
    for f in creadas:
        print(f"  ok {f}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--clasificacion", default=None)
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    if args.listar:
        listar(args.src)
    elif args.out and args.clasificacion:
        volcar(args.src, args.out, args.clasificacion)
    else:
        ap.error("Usar --listar o --out con --clasificacion")


if __name__ == "__main__":
    main()
