#!/usr/bin/env python3
"""Extract a thesis document into vault-friendly Markdown, HTML, media and report."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
import zipfile
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
from xml.etree import ElementTree

BACKUP = ruta_de_env("CORPUS", "Carpeta de tus documentos fuente.") / "BACKUP TG"
VAULT = ruta_de_env("VAULT", "Raíz de tu vault (datos).") / "sources"
NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def slugify(name: str) -> str:
    stem = Path(name).stem
    ascii_name = unicodedata.normalize("NFKD", stem).encode("ascii", "ignore").decode()
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", ascii_name.lower())).strip("-")


def docx_counts(source: Path) -> dict[str, int]:
    with zipfile.ZipFile(source) as archive:
        xml = ElementTree.fromstring(archive.read("word/document.xml"))
        return {
            "tables": len(xml.findall(".//w:tbl", NS)),
            "images": len(xml.findall(".//w:drawing", NS)),
            "bookmarks": len(xml.findall(".//w:bookmarkStart", NS)),
            "fields": len(xml.findall(".//w:instrText", NS)),
        }


def run_pandoc(source: Path, output: Path, media: Path, target: str) -> None:
    command = [
        "pandoc",
        str(source),
        "--from=docx",
        f"--to={target}",
        "--wrap=none",
        "--extract-media=media",
        "--output",
        output.name,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True, cwd=output.parent)


def normalize_markdown(markdown: str) -> str:
    """Turn Word's numbered anchor paragraphs into searchable Markdown headings."""
    anchors: dict[str, tuple[int, str]] = {}
    for label, anchor in re.findall(r"\[([^\]]+)\]\(#(_Toc[^)]+)\)", markdown):
        plain = re.sub(r"\s+\[(?:\d+|Error![^\]]*)\]", "", label)
        plain = re.sub(r"\s+\[(?:\d+|Error![^\]]*)$", "", plain)
        plain = re.sub(r"[*`]", "", plain).strip()
        number = re.match(r"(\d+(?:\.\d+)*)\b", plain)
        level = number.group(1).count(".") + 1 if number else 1
        anchors[anchor] = (level, plain)

    normalized: list[str] = []
    for line in markdown.splitlines():
        image_match = re.search(r'<img src="/tmp/[^/]+/media/media/([^"?]+)', line)
        if image_match:
            line = re.sub(r'/tmp/[^/]+/media/media/', 'media/', line)
        line = line.replace("media/media/", "media/")
        anchor_match = re.search(r'<span id="(_Toc[^"]+)"[^>]*></span>', line)
        if anchor_match and anchor_match.group(1) in anchors:
            level, title = anchors[anchor_match.group(1)]
            line = f"{'#' * level} {title}"
        normalized.append(line)
    return "\n".join(normalized).rstrip() + "\n"


def validate(markdown: str, html: str, expected: dict[str, int]) -> dict[str, object]:
    headings = len(re.findall(r"^#{1,6} ", markdown, re.MULTILINE))
    markdown_tables = len(re.findall(r"^\|", markdown, re.MULTILINE))
    images = len(re.findall(r"!\[[^\]]*\]\([^)]*\)|<img\s", markdown))
    report = {
        "headings": headings,
        "markdown_table_rows": markdown_tables,
        "markdown_images": images,
        "html_tables": html.count("<table"),
        "html_images": html.count("<img"),
        "contains_data_uri": "data:image" in markdown or "data:image" in html,
        "expected": expected,
    }
    report["warnings"] = []
    if not headings:
        report["warnings"].append("No se detectaron headings Markdown")
    if not markdown_tables and expected["tables"]:
        report["warnings"].append("El conversor no generó tablas Markdown")
    if report["contains_data_uri"]:
        report["warnings"].append("Se detectaron imágenes Base64")
    return report


def detect_bibliography(markdown: str) -> list[dict[str, str]]:
    """Extract citation records from the BIBLIOGRAFIA section and inline references."""
    entries: list[dict[str, str]] = []
    in_bib = False
    buffer = ""
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped == "# BIBLIOGRAFÍA":
            in_bib = True
            continue
        if in_bib and re.match(r"^# ", line):
            in_bib = False
        if not in_bib or not stripped or stripped.startswith("<img"):
            continue
        looks_like_new_entry = (
            bool(re.match(r"^[A-ZÁÉÍÓÚÑÖ]", stripped))
            and re.search(r"\b(20\d{2}|19\d{2})\b", stripped)
        )
        continuation = stripped.startswith(("Recuperado de", "En ", "doi:", "http", "Presentado"))
        if buffer and looks_like_new_entry and not continuation:
            entries.append(_parse_citation(buffer))
            buffer = ""
        buffer = (buffer + " " + stripped) if buffer else stripped
    if buffer:
        entries.append(_parse_citation(buffer))
    return entries


def _parse_citation(entry: str) -> dict[str, str]:
    year = re.search(r"\b(20\d{2}|19\d{2})\b", entry)
    doi = re.search(r"doi:\s*([0-9]{2}\.[^\s,]+)", entry)
    url = re.search(r"https?://[^\s<>\]]+", entry)
    author = re.match(r"^(.*?)\s*(?:\(?\d{4})", entry)
    return {
        "raw": entry[:400],
        "author": (author.group(1).strip(" .,&") if author else ""),
        "year": (year.group(1) if year else ""),
        "doi": (doi.group(1) if doi else ""),
        "url": (url.group(0) if url else ""),
    }


def check_manual_changes(destination: Path) -> list[str]:
    """Report whether the existing Markdown has uncommitted or modified content."""
    if not destination.exists():
        return []
    warnings = []
    try:
        result = subprocess.run(
            ["git", "-C", str(destination.parent.parent), "status", "--short", str(destination)],
            capture_output=True, text=True, timeout=15,
        )
        if result.stdout.strip():
            warnings.append("El destino tiene cambios sin commitear; comparar antes de sobrescribir")
    except Exception:
        pass
    return warnings


def extraction_state(slug: str, source: Path, report: dict[str, object]) -> dict[str, object]:
    sha = hashlib.sha256()
    with open(source, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            sha.update(chunk)
    return {
        "slug": slug,
        "source": source.name,
        "source_sha256": sha.hexdigest(),
        "extracted_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "report": report,
    }


def extract(filename: str, force: bool = False) -> dict[str, object]:
    if filename.startswith("~") or "~WRL" in filename:
        raise ValueError("No se permiten locks ni temporales de Word")
    source = BACKUP / filename
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() != ".docx":
        raise ValueError("La versión 2 del extractor rápido requiere un DOCX")

    slug = slugify(filename)
    VAULT.mkdir(parents=True, exist_ok=True)
    destination = VAULT / f"{slug}.md"
    html_destination = VAULT / f"{slug}.html"
    report_destination = VAULT / f"{slug}.extraction.json"
    state_destination = VAULT / f"{slug}.state.json"
    expected = docx_counts(source)

    manual_changes = check_manual_changes(destination)
    if manual_changes and not force:
        raise RuntimeError(
            "Cambios manuales detectados en el destino. Comparar antes de sobrescribir: "
            + "; ".join(manual_changes)
        )

    with tempfile.TemporaryDirectory(prefix=f"{slug}-") as staging_name:
        staging = Path(staging_name)
        media = staging / "media"
        markdown = staging / f"{slug}.md"
        html = staging / f"{slug}.html"
        run_pandoc(source, markdown, media, "gfm")
        run_pandoc(source, html, media, "html5")
        md_text = normalize_markdown(markdown.read_text(encoding="utf-8"))
        html_text = html.read_text(encoding="utf-8").replace("media/media/", "media/")
        report = validate(md_text, html_text, expected)
        report.update({"source": filename, "slug": slug, "tool": "pandoc"})
        citations = detect_bibliography(md_text)
        report["citations"] = len(citations)
        if report["contains_data_uri"] or not md_text.strip():
            raise RuntimeError(f"Validación fallida: {report}")

        destination.write_text(md_text, encoding="utf-8")
        html_destination.write_text(html_text, encoding="utf-8")
        target_media = VAULT / "media"
        if target_media.exists():
            shutil.rmtree(target_media)
        extracted_media = media / "media" if (media / "media").exists() else media
        shutil.copytree(extracted_media, target_media)
        report_destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        state = extraction_state(slug, source, report)
        state_destination.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        fuentes_destination = VAULT / "_zotero" / "fuentes-por-documento" / f"{slug}.fuentes.json"
        fuentes_destination.parent.mkdir(parents=True, exist_ok=True)
        fuentes_destination.write_text(
            json.dumps({"slug": slug, "source": filename, "citations": citations}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("filename")
    parser.add_argument("--force", action="store_true", help="Sobrescribir aunque haya cambios manuales")
    args = parser.parse_args()
    print(json.dumps(extract(args.filename, force=args.force), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
