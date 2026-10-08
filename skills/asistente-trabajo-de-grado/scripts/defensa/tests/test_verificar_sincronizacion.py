"""Check mínimo de verificar_sincronizacion.py: python3 tests/test_verificar_sincronizacion.py"""

import os
import sys
import tempfile
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import verificar_sincronizacion as vs  # noqa: E402


def test() -> None:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        tg, folleto = d / "tg.docx", d / "folleto.docx"
        tg.write_text("v1")
        folleto.write_text("folleto")
        mapa = {"fuentes": {"tg": str(tg)},
                "entregables": [{"nombre": "folleto", "archivos": ["folleto.docx"], "depende_de": ["tg"],
                                 "como": "regenerar", "tipo": "automático"}]}
        estado: dict = {}
        vs.marcar(mapa, estado, "todos", d)
        assert vs.revisar(mapa, estado, d) == []

        tg.write_text("v2")  # cambia el TG; el folleto es de hace una hora
        hace_una_hora = time.time() - 3600
        os.utime(folleto, (hace_una_hora, hace_una_hora))
        assert vs.revisar(mapa, estado, d)[0].startswith("DESACTUALIZADO folleto")

        folleto.write_text("regenerado")  # se regenera después del cambio: al día solo
        assert vs.revisar(mapa, estado, d) == []

        folleto.unlink()
        assert vs.revisar(mapa, estado, d)[0].startswith("FALTA")
    print("ok")


if __name__ == "__main__":
    test()
