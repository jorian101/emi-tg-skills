#!/usr/bin/env python3
"""Copia los entregables finales a la carpeta de finales (clave `finales` de defensa.json).

Uso: python3 publicar_finales.py [--dir CARPETA]   # se niega si algún final está desactualizado
     python3 publicar_finales.py --forzar          # publica igual y lo avisa
Publica los entregables con "final": true (su lista "publicar", o "archivos" si no hay). Solo copia lo
que cambió (por hash) y no borra nada en el destino.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402
import verificar_sincronizacion as vs  # noqa: E402


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    base = config.carpeta()
    mapa = config.cargar(base)
    finales_dir = config.clave(mapa, "finales", "Es la carpeta donde quedan los entregables finales.")
    archivo_estado = base / ".sync-estado.json"
    estado = json.loads(archivo_estado.read_text(encoding="utf-8")) if archivo_estado.exists() else {}
    finales = [e for e in mapa["entregables"] if e.get("final")]
    nombres = {e["nombre"] for e in finales}
    viejos = [p for p in vs.revisar(mapa, estado, base) if p.split()[1] in nombres]
    if viejos:
        print("\n".join(viejos))
        if "--forzar" not in sys.argv:
            print("\nNo publico: hay finales desactualizados (regeneralos o usá --forzar).")
            return 1
        print("\nAVISO: publico igual (--forzar).")
    finales_dir.mkdir(parents=True, exist_ok=True)
    copiados = 0
    for e in finales:
        for a in e.get("publicar", e["archivos"]):
            src = config.ruta(a, base)
            dst = finales_dir / src.name
            if not dst.exists() or sha(dst) != sha(src):
                shutil.copy2(src, dst)
                copiados += 1
                print(f"  copiado {src.name}")
    print(f"ok: {copiados} archivo(s) copiados a {finales_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
