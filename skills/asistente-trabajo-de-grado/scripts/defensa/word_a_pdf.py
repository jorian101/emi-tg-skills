#!/usr/bin/env python3
"""Convierte documentos de Office a PDF de forma fiel y sin bloquear tus apps (WSL + Office en segundo plano).

Soporta .docx (Word) y .pptx (PowerPoint). Estrategia:
  1) Si existe LibreOffice (`soffice`), lo usa headless (proceso aparte, liviano).
  2) Si no, usa la app de Office por COM en segundo plano (invisible) via VBScript + cscript
     (late binding: evita el error TYPE_E_CANTLOADLIBRARY que da PowerShell con Office).
     - Word: actualiza campos y crea marcadores del PDF a partir de los TITULOS (indice navegable).
     - NO cierra tu Word/PowerPoint si ya estaban abiertos.

Uso:
    python3 scripts/word_a_pdf.py "archivo.docx" "presentacion.pptx" [--outdir DIR] [--no-bookmarks] [--no-field-update]
"""

from __future__ import annotations

import argparse
import glob
import shutil
import subprocess
from pathlib import Path

def _system32() -> Path:
    """System32 de Windows visto desde WSL: $WINDOWS_SYSTEM32 o lo que diga `wslpath` (sin suponer la unidad)."""
    import os

    if os.environ.get("WINDOWS_SYSTEM32"):
        return Path(os.environ["WINDOWS_SYSTEM32"])
    try:
        return Path(subprocess.check_output(["wslpath", "-u", r"C:\Windows\System32"], stderr=subprocess.DEVNULL)
                    .decode().strip())
    except (OSError, subprocess.CalledProcessError):
        return Path("System32-no-encontrado")


SYSTEM32 = _system32()
CSCRIPT = str(SYSTEM32 / "cscript.exe")
TASKLIST = str(SYSTEM32 / "tasklist.exe")
TASKKILL = str(SYSTEM32 / "taskkill.exe")
WD_FORMAT_PDF = 17
WD_BOOKMARKS_HEADINGS = 1
PPT_SAVEAS_PDF = 32

VBS_WORD = """On Error Resume Next
Set w = CreateObject("Word.Application")
If Err.Number <> 0 Then
  WScript.Echo "ERR-create:" & Err.Description
  WScript.Quit 2
End If
w.Visible = False
w.DisplayAlerts = 0
Set d = w.Documents.Open(WScript.Arguments(0), False, True)
If Err.Number <> 0 Then
  WScript.Echo "ERR-open:" & Err.Description
  If WScript.Arguments(5) = "1" Then w.Quit
  WScript.Quit 3
End If
If WScript.Arguments(3) = "1" Then d.Fields.Update
d.ExportAsFixedFormat WScript.Arguments(1), {fmt}, False, 0, 0, 0, 0, 0, True, True, {bm}, True, True, False
If Err.Number <> 0 Then
  WScript.Echo "ERR-export:" & Err.Description
  d.Close False
  If WScript.Arguments(5) = "1" Then w.Quit
  WScript.Quit 4
End If
d.Close False
If WScript.Arguments(5) = "1" Then w.Quit
WScript.Echo "OK"
"""

VBS_PPT = """On Error Resume Next
Set p = CreateObject("PowerPoint.Application")
If Err.Number <> 0 Then
  WScript.Echo "ERR-create:" & Err.Description
  WScript.Quit 2
End If
Set pres = p.Presentations.Open(WScript.Arguments(0), True, False, False)
If Err.Number <> 0 Then
  WScript.Echo "ERR-open:" & Err.Description
  If WScript.Arguments(4) = "1" Then p.Quit
  WScript.Quit 3
End If
pres.SaveAs WScript.Arguments(1), {sa}
If Err.Number <> 0 Then
  WScript.Echo "ERR-export:" & Err.Description
  pres.Close
  If WScript.Arguments(4) = "1" Then p.Quit
  WScript.Quit 4
End If
pres.Close
If WScript.Arguments(4) = "1" Then p.Quit
WScript.Echo "OK"
"""


def hay(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def win_path(linux_path: str) -> str:
    return subprocess.check_output(["wslpath", "-w", linux_path]).decode().strip()


def win_temp() -> str:
    out = subprocess.check_output(
        [str(SYSTEM32 / "cmd.exe"), "/c", "echo %TEMP%"], stderr=subprocess.DEVNULL
    ).decode().strip()
    return out.rstrip("\\")


def linux_de(win: str) -> Path:
    return Path(subprocess.check_output(["wslpath", "-u", win]).decode().strip())


def pids(proc: str) -> set[int]:
    """PIDs actuales del proceso (WINWORD.EXE / POWERPNT.EXE)."""
    res = subprocess.run([TASKLIST, "/FI", f"IMAGENAME eq {proc}", "/FO", "CSV", "/NH"], capture_output=True)
    salida = (res.stdout or b"").decode("cp1252", errors="replace")
    ids: set[int] = set()
    for linea in salida.splitlines():
        partes = [p.strip('"') for p in linea.split('","')]
        if partes and partes[0].upper() == proc.upper():
            try:
                ids.add(int(partes[1]))
            except (IndexError, ValueError):
                pass
    return ids


def tipo(ext: str) -> str | None:
    ext = ext.lower()
    if ext in (".docx", ".doc", ".rtf"):
        return "word"
    if ext in (".pptx", ".ppt"):
        return "ppt"
    return None


def convertir_office(kind: str, src: Path, out_pdf: Path, bookmarks: bool, actualizar: bool) -> str:
    tmp_win = win_temp()
    tmp_lin = linux_de(tmp_win)
    salida_en_mnt = not win_path(str(out_pdf)).startswith("\\\\")  # en una unidad de Windows (D:\…), no \\wsl…
    win_out = win_path(str(out_pdf)) if salida_en_mnt else f"{tmp_win}\\{out_pdf.name}"
    proc = "WINWORD.EXE" if kind == "word" else "POWERPNT.EXE"
    antes = pids(proc)
    if kind == "word":
        vbs_txt = VBS_WORD.format(fmt=WD_FORMAT_PDF, bm=WD_BOOKMARKS_HEADINGS if bookmarks else 0)
        args = [win_path(str(src)), win_out, "0", "1" if actualizar else "0", "0", "0"]
    else:
        vbs_txt = VBS_PPT.format(sa=PPT_SAVEAS_PDF)
        args = [win_path(str(src)), win_out, "0", "0", "0"]

    vbs = tmp_lin / "office_a_pdf_tmp.vbs"
    vbs.write_text(vbs_txt, encoding="utf-8")
    res = subprocess.run([CSCRIPT, "//nologo", f"{tmp_win}\\office_a_pdf_tmp.vbs", *args], capture_output=True)
    vbs.unlink(missing_ok=True)
    salida = (res.stdout or b"").decode("cp1252", errors="replace").strip().replace("\r", " ")

    # Cierra las instancias OCULTAS que creo la automatizacion (no toca tu Office abierto).
    for pid in pids(proc) - antes:
        subprocess.run([TASKKILL, "/PID", str(pid), "/F"], capture_output=True)

    if not salida_en_mnt:
        origen = tmp_lin / out_pdf.name
        if origen.exists():
            shutil.move(str(origen), str(out_pdf))
    return salida


def convertir_libreoffice(src: Path, out_pdf: Path, bookmarks: bool) -> str:
    filtro = 'pdf:writer_pdf_Export:{"ExportBookmarks":{"type":"boolean","value":"%s"}}' % (
        "true" if bookmarks else "false"
    )
    subprocess.run(["soffice", "--headless", "--convert-to", filtro, "--outdir", str(out_pdf.parent), str(src)], check=True)
    return "OK"


def convertir(src: Path, outdir: Path | None, bookmarks: bool = True, actualizar: bool = True) -> bool:
    kind = tipo(src.suffix)
    if kind is None:
        print(f"saltado (no soportado): {src}")
        return False
    out_pdf = (outdir / (src.stem + ".pdf")) if outdir else src.with_suffix(".pdf")
    print(f"-> {src}\n   {out_pdf}")
    if hay("soffice") or hay("libreoffice"):
        msg = convertir_libreoffice(src, out_pdf, bookmarks)
    elif Path(CSCRIPT).exists():
        msg = convertir_office(kind, src, out_pdf, bookmarks, actualizar)
    else:
        print("   sin LibreOffice ni cscript.exe: no se puede convertir")
        return False
    ok = out_pdf.exists()
    print(f"   {msg}")
    return ok


def main() -> None:
    ap = argparse.ArgumentParser(description="Office -> PDF fiel, sin bloquear Word/PowerPoint.")
    ap.add_argument("entradas", nargs="+", help="archivos .docx/.pptx o patrones glob")
    ap.add_argument("--outdir", default=None)
    ap.add_argument("--no-bookmarks", action="store_true")
    ap.add_argument("--no-field-update", action="store_true")
    args = ap.parse_args()

    outdir = Path(args.outdir) if args.outdir else None
    if outdir:
        outdir.mkdir(parents=True, exist_ok=True)

    archivos: list[Path] = []
    for patron in args.entradas:
        encontrados = sorted(glob.glob(patron))
        archivos.extend(Path(p) for p in (encontrados or [patron]))

    for src in archivos:
        convertir(src, outdir, not args.no_bookmarks, not args.no_field_update)


if __name__ == "__main__":
    main()
