"""Check mínimo de verificar_correcciones.py: python3 tests/test_verificar_correcciones.py"""

import tempfile
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verificar_correcciones as vc  # noqa: E402

TG = "Tabla 80. La TIR (34,6%) supera la tasa de referencia del 5%. Beneficio anual neto 32.435 Bs."

MD = """# Correcciones

### C-01 TIR en la nota
**Buscar:**
```
la TIR (34,98%) supera la tasa
```
**Reemplazar con:**
```
la TIR (34,6%) supera la tasa
```

### C-02 Beneficio neto
**Buscar:**
```
32.435 Bs
```
**Reemplazar con:**
```
32.195 Bs
```
"""


def test() -> None:
    tg = vc.norm(TG)
    assert vc.estado("la TIR (34,98%) supera", "la TIR (34,6%) supera", tg) == "APLICADA"
    assert vc.estado("neto 32.435 Bs", "neto 32.195 Bs", tg) == "PENDIENTE"
    assert vc.estado("texto que no existe", "otro que tampoco", tg) == "REVISAR"
    assert vc.estado("tasa de referencia", "tasa de referencia del 5%", tg) == "APLICADA"  # solo agrega
    assert vc.estado("14,0", "14,04", vc.norm("análisis 20 14,04 5,96 h")) == "APLICADA"  # no confunde 14,0 con 14,04
    assert vc.ventana("en «Beneficio anual neto»:", tg).startswith("beneficio anual neto")
    assert vc.ventana("en «fila que no está»:", tg) == ""

    vc.texto = lambda *_: TG  # sin pandoc ni Word
    with tempfile.TemporaryDirectory() as d:
        md = Path(d) / "correcciones-tg.md"
        md.write_text(MD, encoding="utf-8")
        assert vc.verificar_tg([md], mover=True) == 1  # C-02 pendiente
        cuerpo = md.read_text(encoding="utf-8")
        assert cuerpo.index("### C-02") < cuerpo.index("## Aplicadas") < cuerpo.index("### C-01")
    print("ok")


if __name__ == "__main__":
    test()
