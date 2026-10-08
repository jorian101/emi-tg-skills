"""Catálogo público de punta a punta: exportar sin nombres → reconocer en local → aportar por issue → integrar → republicar
(python3 scripts/test_publico_e2e.py). Nombres sintéticos."""

import os
import subprocess
import sys
import tempfile
from pathlib import Path

from catalogo_lib import claves_de_nombre, codigo_de_slug, docente_nuevo

D = Path(__file__).resolve().parent
PRIVADO = docente_nuevo("tarqui-vasquez", "Ing. Ana Tarqui Vásquez Rojas", "Docente revisor", "marco práctico", "fondo", "2026-01-01")
PRIVADO = PRIVADO.replace("| ID | Criterio | Estado | Ocurrencias | Fuente |\n|---|---|---|---|---|\n",
                          "| ID | Criterio | Estado | Ocurrencias | Fuente |\n|---|---|---|---|---|\n"
                          '| CR1 | Cifras con porcentaje | confirmado | 1 | "cita literal" (informe a X.Y., MP 1/03) |\n')


def py(script, *args, cwd=None, ok=True, **env):
    r = subprocess.run([sys.executable, str(D / script), *map(str, args)], capture_output=True, text=True, cwd=cwd, check=False,
                       env={**os.environ, **env})
    assert (r.returncode == 0) == ok, f"{script} {args}\n{r.stdout}\n{r.stderr}"
    return r.stdout + r.stderr


def git(cwd, *a):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@x", *a], cwd=cwd, capture_output=True, check=True)


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    privado, pub, local, vault = t / "privado", t / "skills/catalogo-publico", t / "local", t / "vault"
    (privado / "docentes").mkdir(parents=True)
    (privado / "docentes/tarqui-vasquez.md").write_text(PRIVADO, encoding="utf-8")
    (vault / "wiki/docentes").mkdir(parents=True)

    # 1. el mantenedor exporta: sin nombres
    py("exportar_publico.py", "--origen", privado, "--destino", pub)
    codigo = codigo_de_slug("tarqui-vasquez")
    assert "tarqui" not in (pub / f"docentes/{codigo}.md").read_text(encoding="utf-8").lower()

    # 2. el estudiante siembra su catálogo local (repo git propio) y reconoce a SU docente por huellas
    import shutil
    shutil.copytree(pub, local)
    git(local, "init", "-q", "-b", "main"); git(local, "add", "-A"); git(local, "commit", "-q", "-m", "snapshot")
    assert codigo in py("resolver_docente.py", "Ana Tarqui", "--catalogo", local)
    assert "Sin coincidencias" in py("resolver_docente.py", "Pedro Gómez", "--catalogo", local, ok=False)
    py("asignar_evaluador.py", vault, "--rol", "revisor_2", "--nombre", "Ana Tarqui Vásquez", "--catalogo", local, "--iniciales", "L.P.",
       TG_CONFIG=str(t / "config.md"))
    moc = vault / "wiki/docentes/_moc-docentes.md"
    (vault / "wiki/docentes").mkdir(exist_ok=True)
    assert (vault / f"wiki/docentes/{codigo}.md").is_symlink()
    assert "Ana Tarqui Vásquez" in (vault / "wiki/docentes/_nombres.local.yaml").read_text(encoding="utf-8")  # solo local

    # 3. aporta: criterio nuevo + ocurrencia + un docente nuevo; el aporte NO lleva nombres
    env = {"DOCENTES_EMI": str(local)}
    py("registrar_criterio.py", codigo, "--criterio", "Diagrama de flujo en el análisis", "--capitulo", "análisis", "--fuente", "informe a L.P., MP 5/05", **env)
    py("registrar_criterio.py", codigo, "--ocurrencia", "CR1", "--fuente", "informe a L.P., MP 5/05", **env)
    py("nuevo_docente.py", "--nombre", "Cnl. Beto Quispe Huanca", "--rol", "Docente de TG", "--alcance", "forma", "--vault", vault, **env)
    nuevo = next(p.stem for p in (local / "docentes").glob("d-*.md") if p.stem != codigo)
    py("registrar_criterio.py", nuevo, "--criterio", "Interlineado 1.5", "--capitulo", "formato", "--fuente", "clase de L.P. 2026", **env)
    py("contribuir.py", "--vault", vault, cwd=t, **env)
    aporte = (t / "contribucion.md").read_text(encoding="utf-8")
    (t / "aporte_ok.md").write_text(aporte, encoding="utf-8")
    assert codigo in aporte and nuevo in aporte and "Interlineado" in aporte and "huellas" in aporte
    for prohibido in ("tarqui", "vasquez", "quispe", "huanca"):
        assert prohibido not in aporte.lower()
    # si el criterio trae el nombre de uno de MIS docentes, contribuir se niega
    py("registrar_criterio.py", codigo, "--criterio", "Como siempre dice Tarqui, cifras", "--fuente", "informe a L.P., MP 6/05", **env)
    assert "tarqui" in py("contribuir.py", "--vault", vault, cwd=t, ok=False, **env).lower() and not (t / "contribucion.md").exists()
    git(local, "reset", "-q", "--hard", "HEAD~1")

    # 4. el mantenedor integra en el privado (el docente nuevo queda «por completar»), y vuelve a exportar
    git(privado, "init", "-q", "-b", "main"); git(privado, "add", "-A"); git(privado, "commit", "-q", "-m", "base")
    py("aplicar_contribucion.py", t / "aporte_ok.md", "--catalogo", privado, "--commit", "--exportar", "--destino", pub)
    assert "Diagrama de flujo en el análisis" in (pub / f"docentes/{codigo}.md").read_text(encoding="utf-8")
    privado_txt = (privado / "docentes/tarqui-vasquez.md").read_text(encoding="utf-8")
    assert "Diagrama de flujo en el análisis" in privado_txt and "| CR1 | Cifras con porcentaje | confirmado | 2 |" in privado_txt
    creados = [p for p in (privado / "docentes").glob("d-*.md")]
    assert len(creados) == 1 and "por completar" in creados[0].read_text(encoding="utf-8")
    # un segundo aporte del MISMO docente nuevo se reconoce por huellas (no crea otro perfil)
    (t / "otro.md").write_text("```yaml\ndocentes:\n  - docente: d-zzzzzz\n    nuevo: {rol: Docente de TG, revisa: x, alcance: forma, claves: "
                               + str(claves_de_nombre("Beto Quispe Huanca")) + "}\n    cambios:\n      - {tipo: criterio, criterio: Otro criterio, estado: confirmado, capitulo: x, ocurrencias: 1, fuente: informe a M.Q. 2026}\n```\n", encoding="utf-8")
    py("aplicar_contribucion.py", t / "otro.md", "--catalogo", privado)
    assert len(list((privado / "docentes").glob("d-*.md"))) == 1
    # el mismo aporte, hecho a mano con el formulario del repo (sin yaml): se reconoce el docente por su código
    (t / "form.md").write_text(f"### Código del docente\n\n{codigo}\n\n### Rol del docente con vos\n\nRevisor\n\n### Tipo de aporte\n\n"
                               "Criterio nuevo\n\n### Criterio, en general\n\nPide el cronograma con fechas\n\n### Capítulo o sección donde suele aplicarlo"
                               "\n\nmetodología\n\n### Fuente (iniciales y fecha)\n\ninforme a M.Q., MP 9/05\n\n### Huellas del nombre (solo si el docente es nuevo)\n\n_No response_\n", encoding="utf-8")
    py("aplicar_contribucion.py", t / "form.md", "--catalogo", privado)
    assert "Pide el cronograma con fechas" in (privado / "docentes/tarqui-vasquez.md").read_text(encoding="utf-8")
    # un aporte con el nombre de un docente (el issue es público) no se aplica
    (t / "malo.md").write_text("Lo dijo Tarqui\n```yaml\ndocentes: []\n```\n", encoding="utf-8")
    assert "público" in py("aplicar_contribucion.py", t / "malo.md", "--catalogo", privado, ok=False)
print("ok test_publico_e2e")
