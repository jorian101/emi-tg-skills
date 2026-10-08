"""Check de manual.py sin plantilla (uv run --with python-docx --with pillow --with pyyaml python este_archivo.py)."""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml
from docx import Document
from PIL import Image

D = Path(__file__).resolve().parent.parent
MD = """## CAPÍTULO 1: Uso del producto

Así se ingresa, como muestra la {{REF: login}} y resume la {{REF-TABLA: ROLES}}.

### 1.1. Acceso

1. Escriba su **Usuario:** carnet.
2. Presione Ingresar.

{{FIG: login | Pantalla de inicio de sesión | La figura muestra el ingreso.}}

{{TABLA-ROLES}}
"""

with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    (t / "capturas").mkdir()
    Image.new("RGB", (1366, 768), "white").save(t / "capturas/login.png")
    (t / "m.md").write_text(MD, encoding="utf-8")
    cfg = {"fuente": "m.md", "salida": "m.docx", "anio": 2026, "marcadores": {"login": [[100, 100]]},
           "tablas": {"ROLES": {"titulo": "roles del producto", "nota": "La tabla presenta los roles.",
                                "encabezados": ["Rol"], "filas": [["Usuario"]]}}}
    (t / "m.yaml").write_text(yaml.safe_dump(cfg, allow_unicode=True), encoding="utf-8")
    correr = lambda: subprocess.run([sys.executable, str(D / "manual.py"), str(t / "m.yaml")],  # noqa: E731
                                    capture_output=True, text=True, check=False)
    r = correr()
    assert r.returncode == 0, r.stderr
    texto = "\n".join(p.text for p in Document(t / "m.docx").paragraphs)
    assert "como muestra la Figura 1 y resume la Tabla 1" in texto
    assert "Nota. La figura muestra el ingreso. Elaboración propia, 2026." in texto
    assert "Roles del Producto" in texto and "Usuario: Carnet" in texto  # tipo título y mayúscula tras la etiqueta
    (t / "m.md").write_text(MD.replace("{{REF: login}}", "{{REF: no-existe}}"), encoding="utf-8")
    assert correr().returncode != 0  # una referencia rota no se escribe
    (t / "m.md").write_text(MD.replace("### 1.1. Acceso\n\n1.", "### 1.1. Acceso\n#### Otro\n\n1."), encoding="utf-8")
    assert correr().returncode != 0  # dos títulos seguidos sin párrafo
print("ok test_manual")
