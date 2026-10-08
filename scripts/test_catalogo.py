"""Flujo completo del catálogo: registrar → contribuir → aplicar (mantenedor) → actualizar (python3 scripts/test_catalogo.py)."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

D = Path(__file__).resolve().parent
sys.path.insert(0, str(D))
from catalogo_lib import agregar_criterio, docente_nuevo


def py(script, *args, cwd=None, ok=True):
    r = subprocess.run([sys.executable, str(D / script), *map(str, args)], capture_output=True, text=True, cwd=cwd, check=False)
    assert (r.returncode == 0) == ok, f"{script} {args}\n{r.stdout}\n{r.stderr}"
    return r.stdout


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@x", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    principal, alumno = t / "principal", t / "alumno"
    (principal / "docentes").mkdir(parents=True)
    git(principal, "init", "-q", "-b", "main")
    base = docente_nuevo("ana", "Ing. Ana Prueba", "Revisor", "marco práctico", "fondo", "2026-01-01")
    base, _ = agregar_criterio(base, "ana", {"criterio": "Cifras con porcentaje", "fuente": "informe a X.Y., MP 1/03"})
    (principal / "docentes/ana.md").write_text(base, encoding="utf-8")
    git(principal, "add", "-A"); git(principal, "commit", "-q", "-m", "base")
    git(t, "clone", "-q", str(principal), str(alumno))
    os.environ["DOCENTES_EMI"] = str(alumno)

    # registrar: criterio nuevo, ocurrencia, docente nuevo; el nombre completo se rechaza
    py("registrar_criterio.py", "ana", "--criterio", "Diagrama de flujo en el análisis", "--capitulo", "análisis", "--fuente", "informe a L.P., MP 5/05")
    py("registrar_criterio.py", "ana", "--ocurrencia", "CR1", "--fuente", "informe a L.P., MP 5/05")
    py("registrar_criterio.py", "ana", "--criterio", "x", "--fuente", "informe a Luis Perez", ok=False)
    py("nuevo_docente.py", "beto", "--nombre", "Cnl. Beto Prueba", "--rol", "Docente de TG", "--alcance", "forma", "--privado")
    py("registrar_criterio.py", "beto", "--criterio", "Interlineado 1.5", "--fuente", "clase de B.T. 2026", "--capitulo", "formato")
    assert git(alumno, "rev-parse", "--abbrev-ref", "HEAD").strip().startswith("local/")
    assert "| 2 |" in (alumno / "docentes/ana.md").read_text(encoding="utf-8")  # Ocurrencias 1 -> 2

    # contribuir: sin enviar, saneado
    out = py("contribuir.py", cwd=t)
    c = (t / "contribucion.md").read_text(encoding="utf-8")
    assert "Diagrama de flujo" in c and "Ocurrencia +1" in c and "docente nuevo" in c and "Luis" not in c

    # mantenedor: aplica en main del catálogo principal
    py("aplicar_contribucion.py", t / "contribucion.md", "--catalogo", principal, "--commit")
    ana = (principal / "docentes/ana.md").read_text(encoding="utf-8")
    assert "Diagrama de flujo en el análisis" in ana and "CR2" in ana
    assert (principal / "docentes/beto.md").is_file() and "Interlineado 1.5" in (principal / "docentes/beto.md").read_text(encoding="utf-8")

    # el alumno actualiza: su aporte ya está integrado -> choque o duplicado; reiniciar guarda respaldo
    sh = subprocess.run(["bash", str(D / "actualizar_catalogo.sh"), "--reiniciar"], capture_output=True, text=True, check=False)
    assert sh.returncode == 0 and "respaldo" in sh.stdout, sh.stdout + sh.stderr
    assert "CR2" in (alumno / "docentes/ana.md").read_text(encoding="utf-8")
print("ok test_catalogo")
