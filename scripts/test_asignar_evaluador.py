"""Check de asignar_evaluador.py con un vault y un catálogo temporales (python3 scripts/test_asignar_evaluador.py)."""

import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("asignar_evaluador.py")
DOCENTE = """---
title: Ing. Ana Prueba
type: docente
status: activo
revisa: marco práctico
alcance: fondo
nombre: Ana Prueba Rojas
---

# Ing. Ana Prueba

## Criterios de fondo

| ID | Criterio | Estado | Ocurrencias | Fuente |
|---|---|---|---|---|
| ANA1 | Cifras con porcentaje | confirmado | 2 | informe a X.Y. |

## Historial de roles

| Rol | Estudiante | Desde |
|---|---|---|
| — | — | — |

## Relaciones
- [[_moc-docentes]]
"""


def correr(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], capture_output=True, text=True, check=False)


with tempfile.TemporaryDirectory() as t:
    t = Path(t)
    cat, vault = t / "cat", t / "vault"
    (cat / "docentes").mkdir(parents=True)
    (cat / "docentes/ana.md").write_text(DOCENTE, encoding="utf-8")
    (cat / "docentes/ana-reglas.md").write_text("# reglas\n", encoding="utf-8")
    (cat / "docentes/beto.md").write_text(DOCENTE.replace("Ana", "Beto").replace("ANA1", "BET1"), encoding="utf-8")
    (vault / "wiki/docentes").mkdir(parents=True)
    (vault / "proyecto.yaml").write_text("tg:\n  estudiante: LUIS PEREZ\n  tutor: Ana Prueba Rojas\n", encoding="utf-8")
    (vault / "wiki/docentes/beto.md").write_text("copia vieja\n", encoding="utf-8")

    (vault / "wiki/revisores").mkdir(parents=True)  # frontmatter inválido heredado de un vault viejo
    (vault / "wiki/revisores/Revisor_1.md").write_text("---\ntitle: x\nsources:\n  - algo: dos\n    seguido\n---\ncuerpo\n", encoding="utf-8")
    r = correr(vault, "--check", "--catalogo", cat)
    assert r.returncode == 1 and "no te evalúa" in r.stdout and "Ana Prueba Rojas" in r.stdout, r.stdout
    (vault / "wiki/docentes/beto.md").unlink()

    r = correr(vault, "--rol", "revisor_2", "--por-asignar", "--catalogo", cat)
    assert r.returncode == 0 and "SEM" in r.stdout, r.stderr
    r = correr(vault, "--rol", "revisor_2", "--docente", "ana", "--catalogo", cat, "--fecha", "2026-10-08")
    assert r.returncode == 0 and "ANA1" in r.stdout, r.stderr
    assert (vault / "wiki/docentes/ana.md").is_symlink() and (vault / "wiki/docentes/ana-reglas.md").is_symlink()
    assert 'docente: "[[ana]]"' in (vault / "wiki/revisores/Revisor_2.md").read_text(encoding="utf-8")
    assert "| Revisor 2 | L.P. | 2026-10 |" in (cat / "docentes/ana.md").read_text(encoding="utf-8")

    # le reasignan el Revisor 2: el docente anterior deja de verse en el vault
    r = correr(vault, "--rol", "revisor_2", "--docente", "beto", "--catalogo", cat)
    assert r.returncode == 0 and not (vault / "wiki/docentes/ana.md").exists(), r.stdout
    assert (vault / "wiki/docentes/beto.md").is_symlink()
print("ok test_asignar_evaluador")
