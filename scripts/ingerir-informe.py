#!/usr/bin/env python3
"""Ingesta de informes de revisores al vault (material crudo, trazable).

Lee `$INFORMES/<docente>/<informe>` (PDF, JPG o .txt ya
transcripto), extrae texto —con OCR si el PDF es un escaneo— y escribe
`sources/informes-revisores/<docente>/<slug>.md` (verbatim, `tipo: evidencia`).

Idempotente por sha256: si el crudo no cambió no reescribe nada y respeta las
correcciones manuales de `registro.md`. Nunca escribe en la carpeta de origen.

Uso:
    python3 scripts/ingerir-informe.py                 # ingesta completa
    python3 scripts/ingerir-informe.py --only magueno  # un docente
    python3 scripts/ingerir-informe.py --check         # solo verificar (exit 1 si hay pendientes)
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
import tempfile
import unicodedata
from datetime import date
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

_INFORMES = os.environ.get("INFORMES", "").strip()
ROOT_DEFAULT = Path(os.path.expanduser(_INFORMES)) if _INFORMES else None
VAULT = Path(__file__).resolve().parent.parent
DEST = VAULT / "sources" / "informes-revisores"
REGISTRO = DEST / "registro.md"

SKIP_NAMES = {"Thumbs.db", ".DS_Store", "desktop.ini"}
SKIP_SUFFIXES = {".tmp", ".lnk"}
FUENTE_EXT = {".pdf", ".jpg", ".jpeg", ".png", ".txt", ".docx"}

HEADER = ("| informe | docente | estudiante | rol | tipo | fecha | sha256 | fuente_texto | estado |\n"
          "| --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")


def slugify(name: str) -> str:
    stem = Path(name).stem
    ascii_name = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", ascii_name.lower())).strip("-")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def infer_tipo(name: str) -> str:
    up = name.upper()
    if re.search(r"\bMT(\d+)?(?![A-Za-z])", up) or "MARCO TEORIC" in up or "MARCO TEÓRIC" in up:
        return "MT"
    if re.search(r"\bMP(\d+)?(?![A-Za-z])", up) or "MARCO PRACTIC" in up or "MARCO PRÁCTIC" in up:
        return "MP"
    if "PERFIL" in up:
        return "perfil"
    return "desconocido"


def infer_rol(name: str) -> str:
    up = name.upper()
    if re.search(r"REVISOR[\s_-]*2|\b2DO\b|\bREV\.?[\s_-]*2\b", up):
        return "R2"
    if re.search(r"REVISOR[\s_-]*1|\bREV\.?[\s_-]*1\b", up):
        return "R1"
    if "TUTOR" in up:
        return "Tutor"
    return "desconocido"


def infer_estudiante(name: str) -> str:
    """Nombre del estudiante: lo que precede a la primera palabra-clave del informe."""
    stem = Path(name).stem
    m = re.split(r"\s+(?=INFORME|AVALES|AVAL|REVISOR|REVIOR|REV\b|MARCO|BITACORA|FOTO|\dDO|\dTO)", stem, maxsplit=1,
                 flags=re.IGNORECASE)
    out = re.sub(r"\([^)]*\)", "", m[0])
    out = re.sub(r"\s*-\s*$", "", out).strip(" -_")
    out = re.sub(r"\s{2,}", " ", out)
    return out or stem


def infer_fecha(texto: str) -> str:
    m = re.search(r"FECHA\s*:?\s*(\d{1,2})\s*/\s*(\d{1,2})\s*/\s*(\d{4})", texto, re.IGNORECASE)
    if not m:
        return "—"
    d, mo, y = (int(g) for g in m.groups())
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return "—"  # el OCR leyó mal el mes/día: mejor vacío que una fecha inventada
    return f"{y:04d}-{mo:02d}-{d:02d}"


def ocr_image(path: Path) -> str:
    out = subprocess.run(
        ["tesseract", str(path), "stdout", "-l", "spa"],
        capture_output=True, text=True, timeout=600,
    )
    return out.stdout


def pdf_text(path: Path) -> str:
    out = subprocess.run(["pdftotext", "-layout", str(path), "-"],
                         capture_output=True, text=True, timeout=600)
    return out.stdout


def pdf_ocr(path: Path) -> str:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "150", "-jpeg", str(path), str(Path(tmp) / "p")],
                       check=True, capture_output=True, timeout=600)
        chunks = [ocr_image(page) for page in sorted(Path(tmp).glob("p-*.jpg"))]
    return "\n\n".join(chunks)


def extract(path: Path) -> tuple[str, str]:
    """Devuelve (texto, fuente_texto)."""
    ext = path.suffix.lower()
    if ext == ".txt":
        return path.read_text(encoding="utf-8", errors="replace"), "transcripcion-manual"
    if ext in {".jpg", ".jpeg", ".png"}:
        return ocr_image(path), "ocr"
    if ext == ".pdf":
        texto = pdf_text(path)
        if len(re.sub(r"\W", "", texto)) >= 200:
            return texto, "pdf"
        return pdf_ocr(path), "ocr"
    raise ValueError(f"extensión no soportada: {ext}")


def read_registro() -> dict[str, list[str]]:
    rows: dict[str, list[str]] = {}
    if not REGISTRO.exists():
        return rows
    for line in REGISTRO.read_text(encoding="utf-8").splitlines():
        if not line.startswith("| ") or line.startswith("| informe") or line.startswith("| ---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) == 9:
            rows[cells[0]] = cells
    return rows


def write_registro(rows: dict[str, list[str]]) -> None:
    body = "".join("| " + " | ".join(r) + " |\n" for _, r in sorted(rows.items()))
    REGISTRO.write_text(
        "---\n"
        "title: Registro de informes de revisores\n"
        "type: indice\n"
        "created: 2026-09-23\n"
        f"updated: {date.today().isoformat()}\n"
        "sources: []\n"
        "tags:\n  - revisores\n  - informes\n  - registro\n"
        "---\n\n"
        "# Registro de informes de revisores\n\n"
        "> Material crudo en `sources/informes-revisores/<docente>/`. Esta tabla la mantiene\n"
        "> `scripts/ingerir-informe.py` (idempotente por sha256). El `estado` es **derivado, no\n"
        "> escrito a mano**: `procesado` = el perfil del docente ya cita su carpeta; `sin-texto` =\n"
        "> el OCR no dejó texto utilizable; `pendiente` = falta destilar. `rol`/`tipo`/`estudiante`\n"
        "> son best-effort desde el nombre del archivo.\n\n"
        + HEADER + body,
        encoding="utf-8",
    )


def texto_del_vault() -> str:
    """Todo el texto de wiki/ junto: sirve para saber si un docente ya fue destilado."""
    partes = []
    for f in (VAULT / "wiki").rglob("*.md"):
        partes.append(f.read_text(encoding="utf-8", errors="ignore"))
    return "\n".join(partes)


def estado_de(informe: str, fuente: str, wiki: str) -> str:
    """Estado derivado, nunca escrito a mano.

    - `sin-texto`: el OCR no produjo texto utilizable (no se puede destilar).
    - `procesado`: el perfil del docente cita su carpeta `sources/informes-revisores/<slug>/`,
      es decir ya se destilaron sus criterios.
    - `pendiente`: falta destilar.
    """
    if fuente == "ocr" and not informe:
        return "pendiente"
    docente = informe.split("/", 1)[0]
    if f"sources/informes-revisores/{slugify(docente)}/" in wiki:
        return "sin-texto" if fuente == "sin-texto" else "procesado"
    return "pendiente"


def recalcular(rows: dict[str, list[str]], wiki: str) -> None:
    for informe, fila in rows.items():
        ruta = DEST / slugify(fila[1]) / (slugify(informe.split("/", 1)[1]) + ".md")
        chars, fuente = 0, fila[7]
        if ruta.exists():
            cabeza = ruta.read_text(encoding="utf-8", errors="ignore")[:900]
            m = re.search(r"^texto_chars:\s*(\d+)", cabeza, re.MULTILINE)
            chars = int(m.group(1)) if m else 0
            m = re.search(r"^fuente_texto:\s*(\S+)", cabeza, re.MULTILINE)
            fuente = m.group(1) if m else fuente
            fila[7] = fuente
        if fuente == "ocr" and chars < 200:
            fila[8] = "sin-texto"
        else:
            fila[8] = estado_de(informe, fuente, wiki)


def render(fm: dict[str, str], texto: str) -> str:
    tags = "".join(f"  - {t}\n" for t in ("revisores", "informes", "evidencia"))
    head = [
        "---",
        f'title: "{fm["title"]}"',
        "type: evidencia",
        f'docente: "{fm["docente"]}"',
        f'estudiante: "{fm["estudiante"]}"',
        f'rol: {fm["rol"]}',
        f'tipo_informe: {fm["tipo_informe"]}',
        f'fecha_informe: {fm["fecha_informe"]}',
        f'fuente_texto: {fm["fuente_texto"]}',
        f'sha256: {fm["sha256"]}',
        f'original: "{fm["original"]}"',
        f'texto_chars: {fm["texto_chars"]}',
        f'created: {fm["created"]}',
        f'updated: {fm["updated"]}',
        "sources: []",
        "tags:",
        tags.rstrip("\n"),
        "---",
        "",
        f'> Evidencia verbatim del informe de **{fm["docente"]}** sobre **{fm["estudiante"]}** '
        f'(`{fm["tipo_informe"]}`, rol `{fm["rol"]}`, texto vía `{fm["fuente_texto"]}`).\n'
        "> Es material crudo: se cita tal cual, no se corrige su redacción ni su ortografía.\n",
        "",
    ]
    return "\n".join(head) + texto.rstrip() + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", type=Path, default=ROOT_DEFAULT)
    ap.add_argument("--only", default=None, help="slug del docente a procesar")
    ap.add_argument("--check", action="store_true", help="no ingiere; exit 1 si hay pendientes")
    args = ap.parse_args()

    if args.root is None:
        print("ERROR: indicá --root o definí la variable INFORMES (ver .env.example).",
              file=sys.stderr)
        return 2
    if not args.root.is_dir():
        print(f"ERROR: no existe {args.root}", file=sys.stderr)
        return 2

    rows = read_registro()
    if args.check:
        recalcular(rows, texto_del_vault())
        dups = len(rows) - len({r[6] for r in rows.values() if r[6] != "—"})
        pend = sorted(k for k, r in rows.items() if r[8] == "pendiente")
        sin = sorted(k for k, r in rows.items() if r[8] == "sin-texto")
        for k in pend:
            print(f"PENDIENTE  {k}")
        for k in sin:
            print(f"SIN TEXTO  {k}")
        print(f"Informes: {len(rows)} | pendientes: {len(pend)} | sin texto: {len(sin)} | "
              f"sha duplicados: {dups}")
        return 1 if (pend or dups) else 0

    nuevos = actualizados = iguales = 0
    for docente_dir in sorted(p for p in args.root.iterdir() if p.is_dir()):
        docente = docente_dir.name
        slug_doc = slugify(docente)
        if args.only and slug_doc != args.only:
            continue
        for src in sorted(docente_dir.iterdir()):
            if not src.is_file():
                continue
            if src.name in SKIP_NAMES or src.name.startswith("~$") or src.suffix.lower() in SKIP_SUFFIXES:
                continue
            if src.suffix.lower() not in FUENTE_EXT:
                print(f"SALTADO (extensión no soportada): {docente}/{src.name}")
                continue

            rel = f"{docente}/{src.name}"
            digest = sha256(src)
            prev = rows.get(rel)
            if prev and prev[6] == digest:
                iguales += 1
                continue

            out_dir = DEST / slug_doc
            out_dir.mkdir(parents=True, exist_ok=True)
            destino = out_dir / f"{slugify(src.name)}.md"
            creado_prev = ""
            if prev and destino.exists():
                m = re.search(r"^created:\s*(.+)$", destino.read_text(encoding="utf-8")[:800],
                              re.MULTILINE)
                creado_prev = m.group(1).strip() if m else ""

            texto, fuente = extract(src)
            tipo = infer_tipo(src.name)
            if tipo == "desconocido":
                arriba = texto.upper()
                if "MARCO PRÁCTICO" in arriba or "MARCO PRACTICO" in arriba:
                    tipo = "MP"
                elif "MARCO TEÓRICO" in arriba or "MARCO TEORICO" in arriba:
                    tipo = "MT"
            rol = infer_rol(src.name)
            estudiante = infer_estudiante(src.name)
            hoy = date.today().isoformat()
            fm = {
                "title": f"{docente} — informe de {estudiante} ({tipo}, {rol})",
                "docente": docente,
                "estudiante": estudiante,
                "rol": rol,
                "tipo_informe": tipo,
                "fecha_informe": infer_fecha(texto),
                "fuente_texto": fuente,
                "sha256": digest,
                "original": str(src),
                "texto_chars": len(texto),
                "created": creado_prev or hoy,
                "updated": hoy,
            }
            destino.write_text(render(fm, texto), encoding="utf-8")

            fila = [rel, docente, estudiante, rol, tipo,
                    fm["fecha_informe"], digest, fuente, "pendiente"]
            if prev:
                actualizados += 1
                print(f"ACTUALIZADO {rel} ({fuente}, {fm['texto_chars']} chars) → {destino.relative_to(VAULT)}")
            else:
                nuevos += 1
                print(f"NUEVO {rel} ({fuente}, {fm['texto_chars']} chars) → {destino.relative_to(VAULT)}")
            rows[rel] = fila

    recalcular(rows, texto_del_vault())
    write_registro(rows)
    pend = sum(1 for r in rows.values() if r[8] == "pendiente")
    sin = sum(1 for r in rows.values() if r[8] == "sin-texto")
    print(f"\nNuevos: {nuevos} | actualizados: {actualizados} | sin cambios: {iguales} | "
          f"total registro: {len(rows)}")
    print(f"Procesados: {len(rows) - pend - sin} | pendientes: {pend} | sin texto: {sin}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
