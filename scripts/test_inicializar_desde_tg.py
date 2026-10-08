"""Check de inicializar_desde_tg.py con un TG mínimo (python3 scripts/test_inicializar_desde_tg.py)."""

import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

TG = """ESCUELA MILITAR DE INGENIERÍA

# TRABAJO DE GRADO

SISTEMA DE PRUEBA

CASO: INSTITUCIÓN DE PRUEBA

EST. ANA PEREZ

**TUTOR: ING. LUIS ROJAS**

LA PAZ, 2026

**DEDICATORIA**

# ÍNDICE

## 1.4.1. Objetivo General

## 1.2.1. Antecedentes Institucionales

La institución de prueba nace en 1990.

## 1.4.1. Objetivo General

Desarrollar un sistema de prueba para medir algo.

## 1.4.2. Objetivos Específicos

Los objetivos específicos son:

- Analizar el proceso actual de la institución.
- Validar el sistema con usuarios reales.

# Figura 1: Organigrama

# ANEXO A: ÁRBOL DE PROBLEMAS
"""

with tempfile.TemporaryDirectory() as t:
    v = Path(t)
    (v / "sources").mkdir()
    (v / "sources/tg.md").write_text(TG, encoding="utf-8")
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("inicializar_desde_tg.py")), t, "tg"],
                       capture_output=True, text=True, check=False)
    assert r.returncode == 0, r.stderr
    d = yaml.safe_load((v / "proyecto.yaml").read_text(encoding="utf-8"))["tg"]
    assert (d["titulo"], d["caso"], d["estudiante"]) == ("SISTEMA DE PRUEBA", "INSTITUCIÓN DE PRUEBA", "ANA PEREZ")
    assert d["tutor"] == "ING. LUIS ROJAS"
    assert d["objetivo_general"]["texto"].startswith("Desarrollar")  # el del índice (sin cuerpo) se saltea
    assert d["objetivos_especificos"]["items"] == ["Analizar el proceso actual de la institución.",
                                                   "Validar el sistema con usuarios reales."]
    assert d["figuras"] == [{"n": 1, "titulo": "Organigrama"}]
    assert d["anexos"][0]["letra"] == "A" and d["problema"]["causa"] == "PENDIENTE"
    r = subprocess.run([sys.executable, str(Path(__file__).with_name("inicializar_desde_tg.py")), t, "tg"],
                       capture_output=True, text=True, check=False)
    assert r.returncode != 0  # no pisa un proyecto.yaml existente
print("ok test_inicializar_desde_tg")
