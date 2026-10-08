"""Check del chequeo geométrico de escenas.py (uv run --with pillow python este_archivo.py)."""

import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import escenas as e  # noqa: E402


def modulo(paso):
    return types.SimpleNamespace(TITULO="T", PASOS=[("Paso", "Rótulo", paso)], CIERRE="Fin")


bien = modulo(lambda c, t: (c.texto((100, 300), "Uno", 32), c.texto((100, 400), "Dos", 32)))
pisado = modulo(lambda c, t: (c.texto((100, 300), "Uno", 32), c.texto((110, 305), "Dos", 32)))
afuera = modulo(lambda c, t: c.texto((e.ESCENA[2] - 20, 300), "Se sale del escenario", 32))
assert e.problemas_geometricos(e.cuadro(bien, 0, 1.0)) == []
assert any("se pisan" in m for m in e.problemas_geometricos(e.cuadro(pisado, 0, 1.0)))
assert any("fuera del escenario" in m for m in e.problemas_geometricos(e.cuadro(afuera, 0, 1.0)))
print("ok test_escenas_geometria")
