"""La puerta de publicación detecta nombres (sin distinguir mayúsculas), docentes del catálogo y correos (python3 scripts/test_preflight_publicar.py)."""

import subprocess
import sys
import tempfile
from pathlib import Path

D = Path(__file__).resolve().parent


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@x", *a], cwd=cwd, capture_output=True, check=True)


def puerta(repo, cat, *extra):
    return subprocess.run([sys.executable, str(D / "preflight_publicar.py"), str(repo), "--catalogo", str(cat), *extra],
                          capture_output=True, text=True, check=False)


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    repo, cat = t / "repo", t / "cat"
    (cat / "docentes").mkdir(parents=True)
    (cat / "docentes/ana-prueba.md").write_text("---\ntype: docente\nnombre: Ing. Ana Pruebita\n---\n", encoding="utf-8")
    repo.mkdir()
    git(repo, "init", "-q", "-b", "main")
    (repo / ".pii-denylist.local").write_text("Zzapellido\n", encoding="utf-8")
    (repo / "a.md").write_text("base\n", encoding="utf-8")
    git(repo, "add", "a.md"); git(repo, "commit", "-q", "-m", "base"); git(repo, "branch", "origin/main")

    (repo / "b.md").write_text("texto limpio\n", encoding="utf-8")
    git(repo, "add", "b.md"); git(repo, "commit", "-q", "-m", "limpio")
    assert puerta(repo, cat).returncode == 0

    correo, ruta = "alguien" + "@" + "dominio.com", "/ho" + "me/persona/x"  # armados al vuelo: el pre-commit del repo los bloquearía
    for malo in ("informe de zzapellido\n", "p. ej. ana-prueba y Pruebita\n", f"escribime a {correo}\n", f"ver {ruta}\n"):
        (repo / "c.md").write_text(malo, encoding="utf-8")
        git(repo, "add", "c.md"); git(repo, "commit", "-q", "-m", "malo")
        r = puerta(repo, cat)
        assert r.returncode == 1 and "c.md:1" in r.stdout, (malo, r.stdout)
        git(repo, "reset", "-q", "--hard", "HEAD~1")
    # el propio catálogo: sus docentes son lo esperable, los estudiantes no
    (repo / "c.md").write_text("Pruebita enseña\n", encoding="utf-8")
    git(repo, "add", "c.md"); git(repo, "commit", "-q", "-m", "docente")
    assert puerta(repo, cat).returncode == 1 and puerta(repo, cat, "--sin-docentes").returncode == 0
print("ok test_preflight_publicar")
