"""Check de diagrama_flujo.py --vertical (uv run --with pyyaml --with pillow python este_archivo.py). Sin exportar: no abre Chrome."""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

D = Path(__file__).resolve().parent.parent
EJEMPLO = D.parent.parent / "assets/defensa/flujo.example.yaml"


def crear(spec: Path, *extra: str) -> dict:
    r = subprocess.run([sys.executable, str(D / "diagrama_flujo.py"), "crear", str(spec), *extra],
                       capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
    slug = yaml.safe_load(spec.read_text(encoding="utf-8"))["slug"] + ("-vertical" if extra else "")
    return json.loads((spec.parent / f"{slug}.excalidraw").read_text(encoding="utf-8"))


with tempfile.TemporaryDirectory() as t:
    spec = Path(t) / "flujo.yaml"
    shutil.copy(EJEMPLO, spec)
    ancho = lambda doc: max(e["x"] + e["width"] for e in doc["elements"])  # noqa: E731
    horizontal, traspuesto = crear(spec), crear(spec, "--vertical")
    assert ancho(traspuesto) < ancho(horizontal)  # 3 columnas pasan a 2
    sp = yaml.safe_load(spec.read_text(encoding="utf-8"))
    for i, n in enumerate(sp["nodos"]):
        n["vertical"] = [i, 0]  # una sola columna
    spec.write_text(yaml.safe_dump(sp, allow_unicode=True), encoding="utf-8")
    columna = crear(spec, "--vertical")
    xs = {e["x"] for e in columna["elements"] if (e.get("customData") or {}).get("nodo")}
    assert len(xs) == 1, xs
    vuelta = next(e for e in columna["elements"] if e["type"] == "arrow" and e.get("strokeStyle") == "dashed")
    assert min(p[0] for p in vuelta["points"]) < 0  # la vuelta va por el costado izquierdo, no atraviesa nodos
print("ok test_diagrama_flujo")
