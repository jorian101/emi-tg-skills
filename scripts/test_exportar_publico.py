"""exportar_publico.py: sin nombres, y la puerta aborta sin escribir si uno se cuela (python3 scripts/test_exportar_publico.py)."""

import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from catalogo_lib import claves_de_nombre, codigo_de_slug

D = Path(__file__).resolve().parent
PERFIL = """---
title: Ing. Ana Prueba Rojas
type: docente
revisa: "marco práctico"
alcance: fondo
nombre: Ing. Ana Prueba Rojas
rol: Docente revisor
---

# Ing. Ana Prueba Rojas

## Criterios de fondo

| ID | Criterio | Estado | Ocurrencias | Fuente |
|---|---|---|---|---|
| CR1 | {criterio} | confirmado | 2 | "cita literal" (informe a X.Y., MP 15/05) |

## Historial de roles

| Rol | Estudiante | Desde |
|---|---|---|
| Revisor 2 | L.P. | 2026-09 |
"""


def exportar(origen, destino, *extra):
    return subprocess.run([sys.executable, str(D / "exportar_publico.py"), "--origen", str(origen), "--destino", str(destino), *extra],
                          capture_output=True, text=True, check=False)


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    origen, destino = t / "privado", t / "pub"
    (origen / "docentes").mkdir(parents=True)
    (origen / "docentes/ana-prueba.md").write_text(PERFIL.format(criterio="Cifras con porcentaje"), encoding="utf-8")
    r = exportar(origen, destino)
    assert r.returncode == 0, r.stdout + r.stderr
    codigo = codigo_de_slug("ana-prueba")
    publico = (destino / f"docentes/{codigo}.md").read_text(encoding="utf-8")
    assert "prueba" not in publico.lower() and "rojas" not in publico.lower() and "cita literal" not in publico
    assert claves_de_nombre("Ana Prueba Rojas")[0] in publico and "informe a X.Y., MP 15/05" in publico
    assert (destino / "README.md").is_file() and (destino / "docentes/_moc-docentes.md").is_file()
    anterior = (destino / f"docentes/{codigo}.md").read_text(encoding="utf-8")

    # un nombre que se cuela en un criterio: la puerta aborta y NO toca lo ya exportado
    (origen / "docentes/ana-prueba.md").write_text(PERFIL.format(criterio="Como dice Ana Prueba, siempre cifras"), encoding="utf-8")
    r = exportar(origen, destino)
    assert r.returncode == 1 and "PUERTA ANTI-NOMBRES" in r.stdout and "prueba" in r.stdout.lower()
    assert (destino / f"docentes/{codigo}.md").read_text(encoding="utf-8") == anterior
    # una palabra común que coincide con un apellido se declara y pasa
    assert exportar(origen, destino, "--permitir", "prueba", "rojas").returncode == 0

    # formatos: la plantilla sale sin autor bajo el código; un nombre dentro de la plantilla aborta sin escribir
    def plantilla(path, autor, cuerpo):
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("docProps/core.xml", f"<cp:coreProperties><dc:creator>{autor}</dc:creator></cp:coreProperties>")
            z.writestr("word/document.xml", f"<w:document><w:p><w:t>{cuerpo}</w:t></w:p></w:document>")

    fdir = origen / "formatos/ana-prueba"
    fdir.mkdir(parents=True)
    (fdir / "formato.yaml").write_text("docente: ana-prueba\nbiptico:\n  plantilla: biptico.docx\n  orden:\n    - {clave: titulo, titulos: [TITULO]}\n", encoding="utf-8")
    plantilla(fdir / "biptico.docx", "Ana Prueba", "TITULO")
    (origen / "docentes/ana-prueba.md").write_text(PERFIL.format(criterio="Cifras con porcentaje"), encoding="utf-8")
    destino2 = t / "pub2"
    r = exportar(origen, destino2)
    assert r.returncode == 0, r.stdout + r.stderr
    salida = destino2 / f"formatos/{codigo}"
    assert codigo in (salida / "formato.yaml").read_text(encoding="utf-8") and "ana-prueba" not in (salida / "formato.yaml").read_text(encoding="utf-8")
    assert "Ana" not in zipfile.ZipFile(salida / "biptico.docx").read("docProps/core.xml").decode()
    plantilla(fdir / "biptico.docx", "", "Elaborado por Ana Prueba")
    r = exportar(origen, t / "pub3")
    assert r.returncode == 1 and "formatos" in r.stdout and not (t / "pub3").exists()
print("ok test_exportar_publico")
