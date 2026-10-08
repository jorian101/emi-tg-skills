"""verificar_formato.py: pasa con la plantilla oficial y falla con el desvío exacto (uv run --with python-docx --with python-pptx --with pyyaml python scripts/test_verificar_formato.py).

Usa el catálogo público del repo (`catalogo-publico/formatos/`): si no está, el test no corre.
"""

import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

D = Path(__file__).resolve().parent
CAT = D.parent / "catalogo-publico"


def verificar(*a):
    return subprocess.run([sys.executable, str(D / "verificar_formato.py"), "--catalogo", str(CAT), *map(str, a)], capture_output=True, text=True, check=False)


def modificar(origen: Path, destino: Path, parte: str, cambio) -> None:
    with zipfile.ZipFile(origen) as zin, zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            datos = zin.read(it.filename)
            zout.writestr(it, cambio(datos.decode("utf-8")).encode("utf-8") if it.filename == parte else datos)


def plantilla(tipo: str) -> Path:
    return next(CAT.glob(f"formatos/*/{ {'articulo': 'articulo.docx', 'biptico': 'biptico.docx', 'diapositivas': 'diapositivas.pptx'}[tipo]}"))


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    for tipo in ("articulo", "biptico", "diapositivas"):
        r = verificar(plantilla(tipo), "--tipo", tipo)
        assert r.returncode == 0 and "FALLA" not in r.stdout, r.stdout + r.stderr
    # artículo: un margen alterado
    roto = t / "articulo-roto.docx"
    modificar(plantilla("articulo"), roto, "word/document.xml", lambda x: re.sub(r'w:left="\d+"', 'w:left="2000"', x, count=1))
    r = verificar(roto, "--tipo", "articulo")
    assert r.returncode == 1 and "margen izq" in r.stdout, r.stdout
    # bíptico: un encabezado en otro orden (OE1 y OE3 intercambiados)
    roto = t / "biptico-roto.docx"
    def cambiar(x):
        return x.replace("OBJETIVO ESP. 1", "@@").replace("OBJETIVO ESP. 3", "OBJETIVO ESP. 1").replace("@@", "OBJETIVO ESP. 3")
    modificar(plantilla("biptico"), roto, "word/document.xml", cambiar)
    r = verificar(roto, "--tipo", "biptico")
    assert r.returncode == 1 and "fuera de orden" in r.stdout, r.stdout
    # diapositivas: falta HARDWARE
    roto = t / "mazo-roto.pptx"
    with zipfile.ZipFile(plantilla("diapositivas")) as zin, zipfile.ZipFile(roto, "w", zipfile.ZIP_DEFLATED) as zout:
        for it in zin.infolist():
            datos = zin.read(it.filename)
            if it.filename.startswith("ppt/slides/slide") and it.filename.endswith(".xml") and b"HARDWARE" in datos and b"NECESARIO" in datos:
                datos = datos.replace(b"HARDWARE", b"EQUIPOS")
            zout.writestr(it, datos)
    r = verificar(roto, "--tipo", "diapositivas")
    assert r.returncode == 1 and "HARDWARE" in r.stdout, r.stdout
print("ok test_verificar_formato")
