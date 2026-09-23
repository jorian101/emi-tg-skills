#!/usr/bin/env python3
"""Parse Open WebUI chat export (chat-export-*.json) -> notas markdown.

Formato de cada archivo: lista de chats. Cada chat:
  id, user_id, title, chat.history.messages{uuid: msg} (arbol con
  parentId/childrenIds), chat.history.currentId (hoja de la rama activa).
Cada mensaje: role (user|assistant), content (puede venir VACIO en assistant
por perdida del export), models[], files[] (solo metadata + URL CDN con token
transitorio: se registra el nombre, NUNCA la URL).

Modo 1 (listar):  python parse_openwebui.py --dir <dir> --listar
Modo 2 (volcar):  python parse_openwebui.py --dir <dir> --out <dir> --clasificacion <json>
                  JSON: {"juridica": {"<basename sin extension>": "<categoria>"},
                         "excluida": {...}}
                  El basename es el nombre del archivo sin ".json".
"""
import argparse
import glob
import hashlib
import json
import re
from pathlib import Path

SOURCE_LABEL = "otros-chats-openwebui"


def basename_of(f):
    return Path(f).stem


def linear_path(history):
    """Reconstruye la rama activa: currentId -> parentId hasta la raiz."""
    msgs = history["messages"]
    cur = history.get("currentId")
    if cur and cur in msgs:
        chain, seen = [], set()
        while cur and cur in msgs and cur not in seen:
            seen.add(cur)
            chain.append(msgs[cur])
            cur = msgs[cur].get("parentId")
        return list(reversed(chain))
    # fallback: orden por timestamp
    return sorted(msgs.values(), key=lambda m: m.get("timestamp", 0))


def parse_chat(f):
    data = json.load(open(f, encoding="utf-8", errors="replace"))
    chats = []
    for c in data:
        hist = c["chat"]["history"]
        seq = linear_path(hist)
        reqs = [str(m.get("content", "")).strip() for m in seq if m["role"] == "user" and str(m.get("content", "")).strip()]
        resps = [str(m.get("content", "")).strip() for m in seq if m["role"] == "assistant" and str(m.get("content", ""))]
        n_resp_vacias = sum(1 for m in seq if m["role"] == "assistant" and not str(m.get("content", "")).strip())
        models = sorted({mm for m in seq if m.get("models") for mm in m["models"]})
        adjuntos = []
        for m in seq:
            for fi in m.get("files") or []:
                nombre = fi.get("name", "")
                if nombre and nombre not in adjuntos:
                    adjuntos.append(nombre)
        chats.append({
            "title": c.get("title") or basename_of(f),
            "chat_id": c.get("id", ""),
            "reqs": reqs,
            "resps": resps,
            "n_resp_vacias": n_resp_vacias,
            "models": models,
            "adjuntos": adjuntos,
        })
    return chats


def is_api_error(content):
    return bool(re.search(r"(?i)oops|high traffic|check back|error al procesar", content))


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "sin-titulo"


def summarize(content, n=220):
    return content[:n].replace("\n", " ") + ("…" if len(content) > n else "")


def listar(d):
    files = sorted(glob.glob(str(Path(d) / "*.json")))
    print(f"Total archivos: {len(files)}\n")
    for f in files:
        for p in parse_chat(f):
            first = p["reqs"][0] if p["reqs"] else "(sin prompts)"
            marca = "" if p["resps"] else f" [resp ausentes:{p['n_resp_vacias']}]"
            print(f"{p['title'][:44]:44} | {len(p['reqs']):2d} prompts | {len(p['resps']):2d} resp{marca} | {first[:60].replace(chr(10),' ')}")


def volcar(d, out, clasificacion_path):
    with open(clasificacion_path, encoding="utf-8") as fh:
        cla = json.load(fh)
    juridicas = cla.get("juridica", {})
    excluidas = cla.get("excluida", {})

    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    creadas, hashes = [], {}
    for f in sorted(glob.glob(str(Path(d) / "*.json"))):
        bname = basename_of(f)
        if bname not in juridicas:
            continue
        cat = juridicas[bname]
        hashes[bname] = hashlib.sha256(open(f, "rb").read()).hexdigest()[:16]
        for p in parse_chat(f):
            fname = f"{slugify(p['title'])[:50]}.md"
            lines = ["---",
                     f'title: "{SOURCE_LABEL} — {p["title"]}"',
                     "type: conversacion-ia",
                     f"source: {SOURCE_LABEL}",
                     f"categoria: {cat}",
                     "status: extraido",
                     "fiabilidad: respuesta-IA no validada",
                     "tags:",
                     "  - conversacion-ia",
                     "  - openwebui",
                     f"  - {cat}",
                     "---",
                     "",
                     f"# {p['title']}",
                     "",
                     "> [!info] Metadatos",
                     f"> - **Fuente:** export Open WebUI `{bname}.json` (chat_id `{p['chat_id'][:8]}…`)",
                     f"> - **Modelos:** {', '.join(p['models']) or 'no registrado'}",
                     f"> - **Tema:** `{cat}`",
                     f"> - **Mensajes:** {len(p['reqs'])} prompts del vocal, "
                     f"{len(p['resps'])} respuestas conservadas"
                     + (f", **{p['n_resp_vacias']} respuestas AUSENTES en el export**" if p["n_resp_vacias"] else ""),
                     ""]
            if p["adjuntos"]:
                lines += ["> [!warning] Adjuntos ausentes",
                          "> El export solo referencia archivos por nombre (URL CDN transitoria, no",
                          "> versionada). Contenido del adjunto NO disponible; no adoptar datos del",
                          "> adjunto no visibles. Archivos: " + "; ".join(p["adjuntos"]) + ".",
                          ""]
            lines += ["> [!warning] Fiabilidad",
                      "> Los **prompts del vocal** son criterio confiable. Las **respuestas**",
                      "> de la IA son borradores NO validados: pueden ser erróneos o alucinados",
                      "> y el vocal no siempre los corrige. Verificar todo contra fuente primaria.",
                      "",
                      "## Prompts del vocal (criterio)",
                      ""]
            for n, r in enumerate(p["reqs"], 1):
                lines += [f"### Turno {n} — prompt del vocal", "", r, ""]
            if not p["resps"]:
                lines += ["## Respuestas de la IA (no incluidas en el export)",
                          "",
                          "> [!warning] Respuestas ausentes",
                          "> Este export NO conserva el texto de las respuestas de la IA.",
                          "> Se conserva el criterio del vocal (prompts); nada de lo respondido",
                          "> es adoptable porque no está disponible.",
                          ""]
            else:
                lines += ["## Respuesta de la IA — primer borrador", "", p["resps"][0], ""]
                mid = p["resps"][1:-1]
                if len(p["resps"]) > 2:
                    lines += ["## Correcciones intermedias (resumen)", ""]
                    for n, r in enumerate(mid, 2):
                        lines += [f"- **Respuesta {n}** ({len(r)} chars): {summarize(r)}", ""]
                    lines += [""]
                last = p["resps"][-1]
                if last != p["resps"][0]:
                    if is_api_error(last):
                        lines += ["## Última respuesta de la IA (no validada por el vocal)", "",
                                  "> [!warning] Error de servicio",
                                  '> Esta "respuesta" fue un error del servicio (sin contenido). No usar como criterio.',
                                  ""]
                    else:
                        lines += ["## Última respuesta de la IA (no validada por el vocal)", "", last, ""]
            (out / fname).write_text("\n".join(lines), encoding="utf-8")
            creadas.append(fname)

    with open(Path(out) / "_hashes.json", "w", encoding="utf-8") as fh:
        json.dump(hashes, fh, ensure_ascii=False, indent=2)
    print(f"Notas creadas: {len(creadas)} (archivos jurídicos: {len(juridicas)}, excluidos: {len(excluidas)})")
    for c in creadas:
        print(f"  ok {c}")


def main():
    global SOURCE_LABEL
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dir", required=True, help="dir con chat-export-*.json de Open WebUI")
    ap.add_argument("--out", default=None)
    ap.add_argument("--clasificacion", default=None)
    ap.add_argument("--source", default=SOURCE_LABEL)
    ap.add_argument("--listar", action="store_true")
    args = ap.parse_args()

    SOURCE_LABEL = args.source

    if args.listar:
        listar(args.dir)
    elif args.out and args.clasificacion:
        volcar(args.dir, args.out, args.clasificacion)
    else:
        ap.error("Usar --listar o --out con --clasificacion")


if __name__ == "__main__":
    main()
