"""Configuración del modo defensa: una carpeta por proyecto con su `defensa.json`.

La carpeta de defensa se toma, en este orden, de `--dir <ruta>` en la línea de comandos, de la variable
`DEFENSA_DIR` o del directorio actual. El motor no tiene rutas propias: todo sale de esa config, y las
rutas admiten `~` y variables de entorno (`$VAULT`, `$CORPUS`…). Si falta una clave, se dice cuál.
Modelo comentado: assets/defensa/defensa.example.json.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

NOMBRE = "defensa.json"


def carpeta(argv: list[str] | None = None) -> Path:
    argv = sys.argv if argv is None else argv
    if "--dir" in argv:
        return Path(os.path.expanduser(argv[argv.index("--dir") + 1])).resolve()
    if os.environ.get("DEFENSA_DIR"):
        return Path(os.path.expanduser(os.environ["DEFENSA_DIR"])).resolve()
    return Path.cwd()


def args_sin_dir(argv: list[str] | None = None) -> list[str]:
    """Los argumentos del script sin `--dir <ruta>`."""
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--dir" in argv:
        i = argv.index("--dir")
        del argv[i:i + 2]
    return argv


def ruta(valor: str, base: Path) -> Path:
    """Expande `~` y `$VAR`; si queda relativa, es relativa a la carpeta de defensa."""
    p = Path(os.path.expandvars(os.path.expanduser(valor)))
    return p if p.is_absolute() else (base / p)


def cargar(base: Path | None = None) -> dict:
    base = base or carpeta()
    archivo = base / NOMBRE
    if not archivo.exists():
        sys.exit(f"No encuentro {archivo}. Copiá assets/defensa/defensa.example.json a esa carpeta y completalo.")
    cfg = json.loads(archivo.read_text(encoding="utf-8"))
    cfg["_base"] = str(base)
    return cfg


def clave(cfg: dict, nombre: str, ayuda: str = "") -> Path:
    """Ruta obligatoria de la config; falla diciendo qué falta en vez de adivinar."""
    actual = cfg
    for parte in nombre.split("."):
        if not isinstance(actual, dict) or parte not in actual:
            sys.exit(f"Falta la clave «{nombre}» en {NOMBRE}. {ayuda}".strip())
        actual = actual[parte]
    return ruta(actual, Path(cfg["_base"]))
