#!/usr/bin/env python3
"""Build a reproducible read-only snapshot of the Zotero library into the vault.

Works without Zotero running: copies zotero.sqlite to a temp file and queries it
with SQLite in read-only mode. Never writes to the Zotero database.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sqlite3
import tempfile
from datetime import datetime, timezone
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

ZOTERO_DB = ruta_de_env("ZOTERO_DB", "Ruta al archivo zotero.sqlite.")
VAULT_ZOTERO = ruta_de_env("VAULT", "Raíz de tu vault (datos).") / "sources/_zotero"

BIBLIO_FIELDS = {
    "title": "title",
    "date": "date",
    "DOI": "doi",
    "url": "url",
    "publisher": "publisher",
    "publicationTitle": "publication",
    "ISBN": "isbn",
    "archive": "archive",
    "callNumber": "call_number",
    "series": "series",
    "volume": "volume",
    "issue": "issue",
    "pages": "pages",
    "place": "place",
    "edition": "edition",
    "language": "language",
    "shortTitle": "short_title",
    "abstractNote": "abstract_note",
    "extra": "extra",
    "reportNumber": "report_number",
    "university": "university",
    "thesisType": "thesis_type",
    "genre": "genre",
    "proceedingsTitle": "proceedings_title",
    "bookTitle": "book_title",
    "issueDate": "issue_date",
    "dateAdded": "date_added",
}


def snapshot(db_path: Path) -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="zotero-snap-") as tmp:
        tmp_db = Path(tmp) / "zotero.sqlite"
        shutil.copy2(db_path, tmp_db)
        con = sqlite3.connect(f"file:{tmp_db}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        field_names = {
            r["fieldID"]: r["fieldName"]
            for r in cur.execute("SELECT fieldID, fieldName FROM fields")
        }
        collections = {
            r["collectionID"]: r["collectionName"]
            for r in cur.execute("SELECT collectionID, collectionName FROM collections")
        }
        collection_items: dict[int, list[int]] = {}
        for r in cur.execute("SELECT collectionID, itemID FROM collectionItems"):
            collection_items.setdefault(r["itemID"], []).append(
                collections.get(r["collectionID"], "sin colección")
            )

        type_name = {
            r["itemTypeID"]: r["typeName"]
            for r in cur.execute("SELECT itemTypeID, typeName FROM itemTypes")
        }
        skip_types = {tid for tid, tn in type_name.items() if tn in ("attachment", "note", "annotation")}
        item_rows = cur.execute(
            "SELECT itemID, itemTypeID, key FROM items WHERE itemTypeID NOT IN ({})".format(
                ",".join(str(t) for t in skip_types)
            )
        ).fetchall()
        att = {
            r["parentItemID"]: (r["contentType"], r["path"], r["linkMode"], r["att_key"])
            for r in cur.execute(
                """SELECT ia.parentItemID, ia.contentType, ia.path, ia.linkMode, i.key AS att_key
                   FROM itemAttachments ia JOIN items i ON i.itemID = ia.itemID
                   WHERE ia.parentItemID IS NOT NULL AND ia.contentType IS NOT NULL"""
            )
        }

        items = []
        for row in item_rows:
            iid = row["itemID"]
            data = {}
            for r in cur.execute(
                "SELECT id.fieldID, idv.value FROM itemData id JOIN itemDataValues idv ON idv.valueID = id.valueID WHERE id.itemID = ?",
                (iid,),
            ):
                fname = field_names.get(r["fieldID"], "")
                key = BIBLIO_FIELDS.get(fname)
                if key:
                    data[key] = r["value"]
            creators = []
            for r in cur.execute(
                "SELECT c.firstName, c.lastName, c.fieldMode FROM itemCreators ic JOIN creators c ON c.creatorID = ic.creatorID WHERE ic.itemID = ? ORDER BY ic.orderIndex",
                (iid,),
            ):
                if r["fieldMode"] == 0:
                    creators.append(f"{r['firstName']} {r['lastName']}".strip())
                else:
                    creators.append(r["lastName"])
            attachment = att.get(iid)
            item = {
                "item_id": iid,
                "key": row["key"],
                "type": type_name.get(row["itemTypeID"], "unknown"),
                "creators": creators,
                "collections": sorted(set(collection_items.get(iid, []))),
            }
            item.update(data)
            if attachment:
                content_type, path, link_mode, att_key = attachment
                if path and path.startswith("storage:") and link_mode in (0, 1):
                    fname = Path(path.split(":", 1)[1]).name
                    item["attachment_pdf"] = str(ruta_de_env("ZOTERO_STORAGE", "Carpeta storage de Zotero.") / att_key / fname)
                elif path and not path.startswith("http"):
                    item["attachment_path"] = path
            items.append(item)

        con.close()

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_db": str(db_path),
        "total_items": len(items),
        "items": items,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=ZOTERO_DB)
    parser.add_argument("--out", type=Path, default=VAULT_ZOTERO / "library-snapshot.json")
    args = parser.parse_args()
    if not args.db.is_file():
        raise FileNotFoundError(args.db)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result = snapshot(args.db)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Snapshot: {args.out} ({result['total_items']} items)")


if __name__ == "__main__":
    main()
