#!/usr/bin/env python3
"""Notas del vault (Obsidian) para los materiales de defensa, generadas desde defensa.json.

Uso: python3 notas_vault.py [--dir CARPETA]
Escribe en `vault.raiz`/`vault.notas` (por defecto wiki/defensa):
  _moc-defensa.md        hub: cada entregable, su estado y de qué depende; enlaza al hub padre del vault
  defensa-<nombre>.md    una nota por entregable: archivos, fuentes, cómo se regenera, si es final
  estado-defensa.md      la reescribe verificar_sincronizacion.py --nota (qué quedó viejo, qué falta copiar)
Las capturas (capturas.py) y los diagramas agregan sus propias notas en subcarpetas y enlazan al hub.
Las notas llevan el frontmatter obligatorio del vault (type, created/updated, sources, tags, aliases) y la
marca «generado»: se reescriben enteras, así que lo propio del autor va en otra nota enlazada.
"""

from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

MARCA = "<!-- generado por el modo defensa (notas_vault.py): se reescribe entero; no editar a mano -->"
IMAGEN = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"}


def _destino(cfg: dict) -> tuple[Path, Path]:
    raiz = config.clave(cfg, "vault.raiz", "Es la raíz del vault de Obsidian.")
    return raiz, raiz / cfg["vault"].get("notas", "wiki/defensa")


def _frontmatter(tipo: str, titulo: str, fuentes: list[str], tags: list[str], alias: list[str]) -> str:
    hoy = dt.date.today().isoformat()
    def lista(xs: list[str]) -> str:
        return "\n".join(f"  - \"{x}\"" for x in xs) or "  []"
    return (f"---\ntype: {tipo}\ntitle: \"{titulo}\"\ncreated: {hoy}\nupdated: {hoy}\nsources:\n{lista(fuentes)}\n"
            f"tags:\n{lista(tags)}\naliases:\n{lista(alias)}\n---\n{MARCA}\n\n")


def _rel(p: Path, raiz: Path) -> str:
    try:
        return str(p.resolve().relative_to(raiz.resolve()))
    except ValueError:
        return str(p)


def imagen(archivo: Path, carpeta_nota: Path) -> str:
    """Imagen en Markdown estándar con ruta relativa a la nota (Obsidian la muestra y no cuenta como wikilink)."""
    import os

    return f"![{archivo.stem}](<{os.path.relpath(archivo.resolve(), carpeta_nota.resolve())}>)"


def escribir_hub_y_entregables(cfg: dict) -> list[Path]:
    raiz, notas = _destino(cfg)
    notas.mkdir(parents=True, exist_ok=True)
    base = Path(cfg["_base"])
    padre = cfg["vault"].get("hub_padre", "_moc")
    escritas = []
    filas = []
    for e in cfg["entregables"]:
        nombre = f"defensa-{e['nombre']}"
        archivos = [config.ruta(a, base) for a in e["archivos"]]
        cuerpo = [f"# {e['nombre']}\n", "Entregable de defensa. Hub: [[_moc-defensa]].\n",
                  f"- **Depende de:** {', '.join(e['depende_de'])}",
                  f"- **Cómo se regenera:** {e['como']}",
                  f"- **Tipo:** {e['tipo']}" + (" · se publica en finales" if e.get("final") else ""), "",
                  "## Archivos", ""]
        for a in archivos:
            r = _rel(a, raiz)
            cuerpo.append(imagen(a, notas) if a.suffix.lower() in IMAGEN and not r.startswith("/") else f"- `{r}`")
        texto = _frontmatter("entregable-defensa", e["nombre"], [_rel(a, raiz) for a in archivos],
                             ["defensa", "entregable"], [e["nombre"]]) + "\n".join(cuerpo) + "\n"
        p = notas / f"{nombre}.md"
        p.write_text(texto, encoding="utf-8")
        escritas.append(p)
        filas.append(f"| [[{nombre}\\|{e['nombre']}]] | {', '.join(e['depende_de'])} | {e['tipo']} | {'sí' if e.get('final') else ''} |")
    hub = (_frontmatter("moc", "Materiales de defensa", ["defensa.json"], ["defensa", "moc"], ["Defensa", "Materiales de defensa"])
           + "# Materiales de defensa\n\n"
           + f"Parte de [[{padre}]]. Estado al día: [[estado-defensa]].\n\n"
           + "La fuente de verdad del contenido es el documento del trabajo de grado; cada entregable se regenera "
             "desde él (o desde el código, para las capturas). El autor copia a mano solo las correcciones al documento "
             "y el manual.\n\n"
           + "| Entregable | Depende de | Tipo | Final |\n|---|---|---|---|\n" + "\n".join(filas) + "\n")
    p = notas / "_moc-defensa.md"
    p.write_text(hub, encoding="utf-8")
    return [p, *escritas]


def escribir_estado(cfg: dict, pendientes: list[str], resumen: list[str]) -> Path:
    _, notas = _destino(cfg)
    notas.mkdir(parents=True, exist_ok=True)
    ahora = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    lineas = [f"- {p}" for p in pendientes] or ["- Todo al día con sus fuentes."]
    texto = (_frontmatter("estado", "Estado de los materiales de defensa", ["defensa.json"], ["defensa", "estado"],
                          ["Estado de la defensa"])
             + f"# Estado de los materiales de defensa\n\nHub: [[_moc-defensa]]. Revisado: {ahora}.\n\n"
             + "## Entregables\n\n" + "\n".join(lineas) + "\n\n## Lo que falta copiar a mano\n\n"
             + ("\n".join(f"- {r}" for r in resumen) or "- (no se cruzó con los Word: --sin-word)") + "\n")
    p = notas / "estado-defensa.md"
    p.write_text(texto, encoding="utf-8")
    return p


if __name__ == "__main__":
    for p in escribir_hub_y_entregables(config.cargar()):
        print(f"ok {p}")
