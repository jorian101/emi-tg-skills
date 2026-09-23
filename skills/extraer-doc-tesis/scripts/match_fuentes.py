#!/usr/bin/env python3
"""Match citations detected in a thesis document against the Zotero snapshot.

Reads the citations extracted from the bibliography section and crosses them
against sources/_zotero/library-snapshot.json by DOI, title and author+year.
Produces sources/_zotero/fuentes-por-documento/<slug>.fuentes.md.
"""

from __future__ import annotations

import json
import os
import re
import unicodedata
from pathlib import Path

def ruta_de_env(nombre: str, ayuda: str) -> Path:
    """Resuelve una ruta desde el entorno del usuario.

    El motor no hardcodea rutas: falla explicando qué falta en vez de adivinar.
    Las claves se documentan en .env.example.
    """
    valor = os.environ.get(nombre, "").strip()
    if not valor:
        raise SystemExit(f"Falta la variable {nombre}: {ayuda} Ver .env.example.")
    return Path(os.path.expanduser(valor))

VAULT = ruta_de_env("VAULT", "Raíz de tu vault (datos).")
SNAPSHOT = VAULT / "sources/_zotero/library-snapshot.json"
FUENTES_DIR = VAULT / "sources/_zotero/fuentes-por-documento"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()


def first_surname(author: str) -> str:
    author = author.split("(", 1)[0].strip()
    if "," in author:
        parts = [p.strip() for p in author.replace("&", ",").split(",") if p.strip()]
        return norm(parts[0]) if parts else ""
    words = norm(author).split()
    return words[0] if words else ""


GENERIC_AUTHORS = (
    "asamblea", "gobierno", "honorable", "congreso", "corte", "ministerio",
    "tribunal", "omg", "oecd", "ceja", "cumbre", "fundacion", "rbd", "weaviate",
    "oracle", "databricks", "organizacion",
)


def match_citation(cit: dict, snapshot: dict) -> dict:
    candidates = []
    for item in snapshot["items"]:
        score = 0
        reasons = []
        if cit.get("doi") and item.get("doi") and norm(cit["doi"]) == norm(item["doi"]):
            score += 100
            reasons.append("doi exacto")
        if cit.get("year") and item.get("date") and cit["year"] in item["date"]:
            score += 10
            reasons.append("año")
        ca = first_surname(cit.get("author", ""))
        author_useful = bool(ca) and not any(g.startswith(ca[:5]) or ca.startswith(g[:5]) for g in GENERIC_AUTHORS)
        if author_useful:
            for creator in item.get("creators", []):
                if norm(creator).startswith(ca) or ca in norm(creator):
                    score += 20
                    reasons.append("autor")
                    break
        if score:
            candidates.append((score, reasons, item))
    if not candidates:
        return {"status": "pendiente", "matches": []}
    candidates.sort(key=lambda x: -x[0])
    best_score, reasons, item = candidates[0]
    if best_score >= 100:
        status = "confirmada"
    elif author_useful:
        status = "coincidencia probable"
    else:
        return {"status": "pendiente", "matches": []}
    return {
        "status": status,
        "matches": [
            {
                "item_key": item.get("key"),
                "title": item.get("title", ""),
                "creators": item.get("creators", []),
                "date": item.get("date", ""),
                "doi": item.get("doi", ""),
                "attachment_pdf": item.get("attachment_pdf", ""),
                "collections": item.get("collections", []),
                "reasons": reasons,
            }
        ],
    }


def build(citations: list[dict], snapshot: dict) -> dict:
    rows = []
    counts = {"confirmada": 0, "coincidencia probable": 0, "pendiente": 0}
    for cit in citations:
        result = match_citation(cit, snapshot)
        counts[result["status"]] = counts.get(result["status"], 0) + 1
        rows.append({**cit, **result})
    return {
        "total": len(rows),
        "confirmadas": counts["confirmada"],
        "probables": counts["coincidencia probable"],
        "pendientes": counts["pendiente"],
        "rows": rows,
    }


def render_markdown(payload: dict, slug: str, source: str) -> str:
    lines = [
        f"# Fuentes vinculadas — {slug}",
        "",
        f"Documento fuente: `{source}`",
        "",
        f"Total citas: {payload['total']} | Confirmadas: {payload['confirmadas']} | "
        f"Probables: {payload['probables']} | Pendientes: {payload['pendientes']}",
        "",
        "| Cita (autor, año) | Estado | Item Zotero | PDF | Revisar en Zotero |",
        "|---|---|---|---|---|",
    ]
    for r in payload["rows"]:
        author = r.get("author", "")[:45]
        year = r.get("year", "")
        if r["status"] == "pendiente":
            lines.append(f"| {author} ({year}) | ⚠️ pendiente | — | — | Buscar/descargar la fuente |")
            continue
        m = r["matches"][0]
        pdf = m.get("attachment_pdf", "")
        pdf_md = f"[PDF]({pdf})" if pdf else "—"
        lines.append(
            f"| {author} ({year}) | {'✅' if r['status']=='confirmada' else '🟡'} {r['status']} | "
            f"`{m.get('item_key')}` — {m.get('title','')[:40]} | {pdf_md} | "
            f"{' / '.join(m.get('collections', []))} |"
        )
    return "\n".join(lines) + "\n"


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("citations_json", type=Path)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--source", default="")
    args = parser.parse_args()
    citations = json.loads(args.citations_json.read_text(encoding="utf-8"))
    if isinstance(citations, dict) and "citations" in citations:
        citations = citations["citations"]
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    payload = build(citations, snapshot)
    FUENTES_DIR.mkdir(parents=True, exist_ok=True)
    out = FUENTES_DIR / f"{args.slug}.fuentes.md"
    out.write_text(render_markdown(payload, args.slug, args.source), encoding="utf-8")
    print(json.dumps({"total": payload["total"], "confirmadas": payload["confirmadas"], "pendientes": payload["pendientes"], "out": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
