#!/usr/bin/env python3
"""¿Qué entregable de defensa quedó viejo respecto del TG o del frontend, y qué falta copiar a mano?

Uso: python3 verificar_sincronizacion.py [--dir CARPETA]                  # informe; sale con 1 si hay algo pendiente
     python3 verificar_sincronizacion.py --marcar-al-dia triptico         # (o 'todos') lo da por revisado
     python3 verificar_sincronizacion.py --sin-word                       # salta el cruce con los Word (más rápido)
     python3 verificar_sincronizacion.py --nota                           # además reescribe la nota de estado del vault

Un entregable está DESACTUALIZADO si el contenido (hash) de una de sus fuentes cambió desde la última
vez que se dio por bueno y sus archivos son anteriores a ese cambio. Si se regeneró después del cambio
se da por bueno solo. El mapa vive en defensa.json (clave `entregables`); el estado, en .sync-estado.json
de la misma carpeta (no va a git).
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402

AQUI = Path(__file__).resolve().parent
DESFASE_S = 600  # ponytail: el reloj de Windows puede ir minutos detrás del de WSL; 10 min de margen


def archivos_fuente(ruta: Path) -> list[Path]:
    if ruta.is_file():
        return [ruta]
    return sorted(p for p in ruta.rglob("*") if p.is_file() and ".test." not in p.name)


def huella(ruta: Path) -> tuple[str, float]:
    """(hash del contenido, mtime más reciente) de un archivo o de un árbol."""
    h, ultimo = hashlib.sha256(), 0.0
    for p in archivos_fuente(ruta):
        h.update(str(p.relative_to(ruta.parent)).encode())
        h.update(hashlib.sha256(p.read_bytes()).digest())
        ultimo = max(ultimo, p.stat().st_mtime)
    return h.hexdigest(), ultimo


def _fuentes(mapa: dict, base: Path) -> dict[str, Path]:
    return {k: config.ruta(v, base) for k, v in mapa["fuentes"].items()}


def revisar(mapa: dict, estado: dict, base: Path) -> list[str]:
    fuentes = {k: huella(p) for k, p in _fuentes(mapa, base).items()}
    pendientes = []
    for e in mapa["entregables"]:
        visto = estado.setdefault(e["nombre"], {})
        rutas = [config.ruta(a, base) for a in e["archivos"]]
        if faltan := [r.name for r in rutas if not r.exists()]:
            pendientes.append(f"FALTA          {e['nombre']}: {', '.join(faltan)} · {e['como']} [{e['tipo']}]")
            continue
        mtime = min(r.stat().st_mtime for r in rutas)
        cambiadas = []
        for f in e["depende_de"]:
            h, t = fuentes[f]
            if visto.get(f) == h:
                continue
            if mtime + DESFASE_S >= t:  # se regeneró después del cambio: queda al día
                visto[f] = h
            else:
                cambiadas.append(f)
        if cambiadas:
            pendientes.append(f"DESACTUALIZADO {e['nombre']} (cambió {' y '.join(cambiadas)}) · {e['como']} [{e['tipo']}]")
    return pendientes


def marcar(mapa: dict, estado: dict, nombre: str, base: Path) -> None:
    fuentes = {k: huella(p)[0] for k, p in _fuentes(mapa, base).items()}
    for e in mapa["entregables"]:
        if nombre in ("todos", e["nombre"]):
            estado[e["nombre"]] = {f: fuentes[f] for f in e["depende_de"]}


def main() -> int:
    base = config.carpeta()
    mapa = config.cargar(base)
    archivo_estado = base / ".sync-estado.json"
    estado = json.loads(archivo_estado.read_text(encoding="utf-8")) if archivo_estado.exists() else {}
    args = config.args_sin_dir()
    if "--marcar-al-dia" in args:
        marcar(mapa, estado, args[args.index("--marcar-al-dia") + 1], base)
        archivo_estado.write_text(json.dumps(estado, indent=2), encoding="utf-8")
        print("ok: marcado al día")
        return 0
    pendientes = revisar(mapa, estado, base)
    archivo_estado.write_text(json.dumps(estado, indent=2), encoding="utf-8")
    print("\n".join(pendientes) or "Entregables al día con sus fuentes.")
    codigo = 1 if pendientes else 0
    resumen = []
    if "--sin-word" not in args:
        for extra in ([], ["--manual"]):  # lo que el autor tiene que copiar a mano
            r = subprocess.run([sys.executable, str(AQUI / "verificar_correcciones.py"), "--dir", str(base), *extra],
                               capture_output=True, text=True)
            linea = (r.stdout.strip().splitlines() or ["(sin salida)"])[-1]
            resumen.append(linea)
            print("\n" + linea, r.stderr.strip()[-300:])
            codigo |= r.returncode
    if "--nota" in args:
        import notas_vault

        print(f"ok nota: {notas_vault.escribir_estado(mapa, pendientes, resumen)}")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
