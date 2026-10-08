"""sanear_plantilla.py borra las propiedades de persona y detecta nombres en el texto (python3 scripts/test_sanear_plantilla.py)."""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from catalogo_lib import texto_de_oficina

D = Path(__file__).resolve().parent
CORE = ('<?xml version="1.0"?><cp:coreProperties xmlns:cp="c" xmlns:dc="d"><dc:title>Plantilla</dc:title>'
        "<dc:creator>Ana Tarqui</dc:creator><cp:lastModifiedBy>Beto Quispe</cp:lastModifiedBy></cp:coreProperties>")


def docx(destino: Path, cuerpo: str) -> None:
    with zipfile.ZipFile(destino, "w") as z:
        z.writestr("docProps/core.xml", CORE)
        z.writestr("docProps/app.xml", "<Properties><Company>EMI Tarqui</Company></Properties>")
        z.writestr("word/document.xml", f"<w:document><w:p><w:t>{cuerpo}</w:t></w:p></w:document>")


def correr(*a):
    return subprocess.run([sys.executable, str(D / "sanear_plantilla.py"), *map(str, a)], capture_output=True, text=True, check=False)


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "cat/docentes").mkdir(parents=True)
    (t / "cat/docentes/tarqui-quispe.md").write_text("---\ntype: docente\nnombre: Ana Tarqui Quispe\n---\n", encoding="utf-8")
    docx(t / "limpio.docx", "TITULO del trabajo")
    r = correr(t / "limpio.docx", t / "out/limpio.docx", "--nombres-de", t / "cat")
    assert r.returncode == 0, r.stderr
    propiedades = texto_de_oficina(t / "out/limpio.docx")
    assert "tarqui" not in propiedades.lower() and "quispe" not in propiedades.lower() and "Plantilla" not in propiedades
    docx(t / "sucio.docx", "Elaborado por Ana Tarqui")
    r = correr(t / "sucio.docx", t / "out/sucio.docx", "--nombres-de", t / "cat")
    assert r.returncode != 0 and "tarqui" in r.stderr.lower() and not (t / "out/sucio.docx").exists()
    # imágenes: la ajena se reemplaza por un píxel; el logo (por hash) se conserva
    import hashlib

    from catalogo_lib import LOGOS_PLANTILLA

    ajena = b"imagen-de-otro-proyecto"
    with zipfile.ZipFile(t / "img.docx", "w") as z:
        z.writestr("word/document.xml", "<w:document/>")
        z.writestr("word/media/image1.png", ajena)
    r = correr(t / "img.docx", t / "out/img.docx")
    assert r.returncode == 0, r.stderr
    with zipfile.ZipFile(t / "out/img.docx") as z:
        assert z.read("word/media/image1.png") != ajena and z.read("word/media/image1.png").startswith(b"\x89PNG")
    assert all(len(h) == 64 for h in LOGOS_PLANTILLA) and hashlib.sha256(ajena).hexdigest() not in LOGOS_PLANTILLA
print("ok test_sanear_plantilla")
