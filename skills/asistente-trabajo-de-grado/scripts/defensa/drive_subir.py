#!/usr/bin/env python3
"""Sube (o actualiza) los PDF de anexos a la carpeta publica de Google Drive con rclone.

- Sube cada anexos-sueltos/ANEXO-<X>.pdf a la carpeta del manifiesto, con el nombre 'archivo_drive'.
- Refresca drive_id/drive_link en el manifiesto (leyendo la carpeta con rclone).
Requisitos: rclone con un remoto 'gdrive' (ya configurado).

Uso: python3 scripts/drive_subir.py            # sube todos
     python3 scripts/drive_subir.py G P        # solo esos
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

_CFG = config.cargar()
BASE = config.clave(_CFG, "anexos.dir", "Es la carpeta de los anexos con QR (manifiesto, documento y salidas).")
DOCUMENTO = BASE / _CFG["anexos"].get("documento", "anexos-qr.docx")
MANIFIESTO = BASE / "manifiesto-anexos.json"
SUELTOS = BASE / "anexos-sueltos"


def subir(local: Path, nombre: str, remoto: str) -> None:
    subprocess.run(["rclone", "copyto", str(local), f"{remoto}/{nombre}"], check=True)


def refrescar_links(datos: dict, remoto: str) -> None:
    out = subprocess.check_output(["rclone", "lsjson", remoto], text=True)
    por_nombre = {f["Name"]: f["ID"] for f in json.loads(out)}
    for a in datos["anexos"]:
        fid = por_nombre.get(a["archivo_drive"])
        if fid:
            a["drive_id"] = fid
            a["drive_link"] = f"https://drive.google.com/file/d/{fid}/view"


def main() -> None:
    datos = json.loads(MANIFIESTO.read_text(encoding="utf-8"))
    remoto = datos["carpeta_drive"]["remoto_rclone"]
    solo = set(config.args_sin_dir())
    elegidos = [a for a in datos["anexos"] if not solo or a["letra"] in solo]
    # Todo o nada: subir los que hay y saltar el resto dejaba en Drive PDFs de corridas viejas.
    if faltan := [a["letra"] for a in elegidos if not (SUELTOS / f"ANEXO-{a['letra']}.pdf").exists()]:
        sys.exit(f"ERROR: faltan los PDF de los anexos {', '.join(faltan)}; corré anexos_dividir.py")
    for a in elegidos:
        local = SUELTOS / f"ANEXO-{a['letra']}.pdf"
        subir(local, a["archivo_drive"], remoto)
        print(f"  subido ANEXO {a['letra']} -> {a['archivo_drive']}")
    refrescar_links(datos, remoto)
    MANIFIESTO.write_text(json.dumps(datos, ensure_ascii=False, indent=2), encoding="utf-8")
    print("ok: manifiesto con links actualizados")


if __name__ == "__main__":
    main()
