#!/usr/bin/env python3
"""(Mantenedor) Genera `catalogo-publico/` desde el catálogo PRIVADO: perfiles sin nombre, con código y huellas.

Uso: exportar_publico.py [--origen <catalogo-privado>] [--destino <repo>/catalogo-publico] [--permitir palabra ...]
Los formatos (`formatos/<slug>/`) se publican bajo el código, con sus plantillas sin autor ni propiedades de persona. Por cada docente: código `d-<6hex>` (del slug), `claves` (huellas de pares del nombre), criterios con IDs neutros y fuentes
con iniciales y fecha pero SIN citas literales, y el historial de roles. No se exportan nombres, slugs, notas por docente ni
enlaces a ellas. Puerta: antes de escribir nada, ningún token del nombre ni del slug de ningún docente del catálogo privado
puede aparecer (sin distinguir mayúsculas ni acentos) en la salida; si aparece, se aborta SIN escribir. Una palabra común que
coincide con un apellido se declara con --permitir tras revisarla. Republicar = PR del mantenedor a main.
"""

from __future__ import annotations

import argparse
import datetime
import shutil
import sys
import tempfile
from pathlib import Path

import yaml
from catalogo_lib import (
    catalogo_default,
    codigo_de_slug,
    frontmatter,
    nombres_en,
    nombres_privados,
    perfil_publico,
    regenerar_moc,
    sanear_oficina,
    texto_de_oficina,
)

REPO = Path(__file__).resolve().parent.parent
ASSETS = REPO / "skills/asistente-trabajo-de-grado/assets"
README = """# Catálogo público de docentes (sin nombres)

Perfiles **generados** desde el catálogo privado del mantenedor: código, huellas del nombre, qué suele revisar, criterios
generales (con iniciales y fecha como fuente, sin citas) e historial de roles. **No se edita a mano**: para aportar,
abrí un issue con el formulario «Aporte de criterio».

- Descargar es **opcional**: `./install.sh --catalogo-publico`.
- Reconocer a TU docente, en tu máquina: `python3 scripts/resolver_docente.py "Nombre Apellido"`. El nombre no sale de tu
  computadora; solo se comparan huellas (SHA-256 con sal pública) de pares de nombres y apellidos.
- Es **seudonimización, no anonimato**: quien ya conozca un nombre puede comprobar si coincide, y el rol y los criterios
  pueden dar pistas. No hay nombres, citas de informes ni datos de estudiantes más allá de sus iniciales.
"""


def exportar_formatos(origen: Path, out: Path) -> int:
    """`formatos/<slug>/` del privado -> `formatos/<código>/`: el código reemplaza al slug y las plantillas salen sin propiedades de persona."""
    n = 0
    for f in sorted((origen / "formatos").glob("*/formato.yaml")):
        datos = yaml.safe_load(f.read_text(encoding="utf-8"))
        codigo = codigo_de_slug(f.parent.name)
        datos["docente"] = codigo
        destino = out / codigo
        destino.mkdir(parents=True)
        for seccion in datos.values():
            if isinstance(seccion, dict) and seccion.get("plantilla"):
                fuente = f.parent / seccion["plantilla"]
                if fuente.is_file():
                    sanear_oficina(fuente, destino / seccion["plantilla"])
                else:
                    del seccion["plantilla"]  # p. ej. el ejemplo de tríptico es trabajo de un estudiante: no se publica
            if isinstance(seccion, dict) and seccion.get("reglas"):
                shutil.copy(f.parent / seccion["reglas"], destino / seccion["reglas"])
        (destino / "formato.yaml").write_text(yaml.safe_dump(datos, allow_unicode=True, sort_keys=False), encoding="utf-8")
        n += 1
    return n


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origen", type=Path, default=catalogo_default())
    ap.add_argument("--destino", type=Path, default=REPO / "catalogo-publico")
    ap.add_argument("--permitir", nargs="*", default=[])
    a = ap.parse_args()
    if not (a.origen / "docentes").is_dir():
        sys.exit(f"No encuentro el catálogo privado en {a.origen}")
    prohibidos = nombres_privados(a.origen)
    permitir = frozenset(p.lower() for p in a.permitir)
    hoy = datetime.datetime.now().astimezone().date().isoformat()
    with tempfile.TemporaryDirectory() as t:
        out = Path(t) / "docentes"
        out.mkdir()
        codigos = {}
        for p in sorted((a.origen / "docentes").glob("*.md")):
            if frontmatter(p.read_text(encoding="utf-8")).get("type") != "docente":
                continue
            codigo, texto = perfil_publico(p.read_text(encoding="utf-8"), p.stem)
            if codigo in codigos:
                sys.exit(f"Colisión de código {codigo}: {codigos[codigo]} y {p.stem}")
            codigos[codigo] = p.stem
            (out / f"{codigo}.md").write_text(texto, encoding="utf-8")
        for nombre, origen in (("jerarquia-autoridad.md", "jerarquia-autoridad.md"), ("_plantilla-docente.md", "plantilla-docente.md")):
            (out / nombre).write_text((ASSETS / origen).read_text(encoding="utf-8").replace("YYYY-MM-DD", hoy), encoding="utf-8")
        regenerar_moc(Path(t))
        n_formatos = exportar_formatos(a.origen, Path(t) / "formatos")
        (Path(t) / "README.md").write_text(README, encoding="utf-8")
        hallazgos = []
        for f in sorted(Path(t).rglob("*")):
            if f.suffix in (".docx", ".pptx"):
                texto = texto_de_oficina(f)
            elif f.suffix in (".md", ".yaml"):
                texto = f.read_text(encoding="utf-8")
            else:
                continue
            for palabra in nombres_en(texto, prohibidos, permitir):
                hallazgos.append(f"{f.relative_to(t)}: «{palabra}»")
        if hallazgos:
            print("PUERTA ANTI-NOMBRES: no se escribió nada. Aparecen nombres o apellidos de docentes en la salida:\n  " + "\n  ".join(hallazgos))
            print("  Corregí el texto en el catálogo privado (o, si es una palabra común, pasala con --permitir).")
            return 1
        if a.destino.exists():
            shutil.rmtree(a.destino)
        shutil.copytree(t, a.destino)
    print(f"  ok    {len(codigos)} perfiles y {n_formatos} formatos públicos en {a.destino} (puerta anti-nombres: {len(prohibidos)} términos, 0 hallazgos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
