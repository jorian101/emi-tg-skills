#!/usr/bin/env python3
"""Capturas de la interfaz por rol, declarativas: pantallas, modales abiertos y pantallas tras una acción.

Uso: uv run --with playwright --with pyyaml python capturas.py <capturas.yaml> [--dir CARPETA] [--solo id1,id2]
       [--ensayo]   # recorre y valida sin guardar imágenes

Todo se declara en el YAML (modelo comentado: assets/defensa/capturas.example.yaml):
  - por rol: la cuenta (usuario y clave salen de variables de entorno; nunca se escriben en el archivo),
  - `pantallas`: ruta + espera (+ recorte),
  - `operaciones`: pasos (clic, llenar, elegir, tecla, esperar) que abren un modal o dejan la pantalla
    tras una acción, y los `marcadores` numerados que se miden solos sobre los elementos indicados.
Salida (en `salida`, relativa a la carpeta de defensa): <id>.png, marcadores.json (lo lee el generador del
manual, sin copiar coordenadas a mano) y, si `notas_vault: true`, una nota por captura en el vault.

Seguridad (no se negocia): un clic sobre un botón cuyo nombre esté en `seguridad.prohibidos` (Crear,
Guardar, Aprobar…) aborta la operación, salvo que el paso diga `escribe: true` y quede cupo en
`seguridad.escrituras_permitidas`. Al terminar una operación con modal, se cierra con Cancelar/Cerrar o
Escape. Material para la institución: usar sus cuentas reales, no cuentas de prueba (regla del autor).
"""

from __future__ import annotations

import glob
import json
import os
import re
import sys
import time
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config  # noqa: E402


class Prohibido(RuntimeError):
    pass


def navegador() -> str | None:
    """Chrome a usar: $CHROME, el chrome-headless-shell de Puppeteer, o None (el que trae Playwright)."""
    if os.environ.get("CHROME"):
        return os.environ["CHROME"]
    for patron in ("~/.cache/puppeteer/chrome-headless-shell/*/chrome-headless-shell-linux64/chrome-headless-shell",
                   "~/.cache/puppeteer/chrome/*/chrome-linux64/chrome"):
        hallados = sorted(glob.glob(os.path.expanduser(patron)))
        if hallados:
            return hallados[-1]
    return None


# ---------------------------------------------------------------- localizadores
def localizar(pg, spec: dict):
    """Gramática: {rol, nombre[, exacto]} | {css} | {texto} | {titulo_empieza}; + {dentro: dialogo}, {n} o {ultimo}."""
    raiz = pg
    if spec.get("dentro") == "dialogo":
        raiz = pg.get_by_role("dialog").last
    if "rol" in spec:
        loc = raiz.get_by_role(spec["rol"], name=spec.get("nombre"), exact=spec.get("exacto", False))
    elif "css" in spec:
        loc = raiz.locator(spec["css"])
    elif "texto" in spec:
        loc = raiz.get_by_text(spec["texto"], exact=spec.get("exacto", False))
    elif "titulo_empieza" in spec:
        loc = raiz.locator(f'[title^="{spec["titulo_empieza"]}"]')
    else:
        raise ValueError(f"localizador sin rol/css/texto/titulo_empieza: {spec}")
    if "n" in spec:
        return loc.nth(spec["n"])
    return loc.last if spec.get("ultimo") else loc.first


def _nombre(loc) -> str:
    try:
        return (loc.get_attribute("aria-label") or loc.inner_text(timeout=2000) or "").strip()
    except Exception:  # noqa: BLE001
        return ""


class Recorrido:
    def __init__(self, cfg: dict, pg, ensayo: bool):
        self.cfg, self.pg, self.ensayo = cfg, pg, ensayo
        seg = cfg.get("seguridad", {})
        self.prohibidos = [p.lower() for p in seg.get("prohibidos", [])]
        self.cupo = int(seg.get("escrituras_permitidas", 0))
        self.cerrar_con = seg.get("cerrar_con", ["Cancelar", "Cerrar"])

    def ir(self, ruta: str):
        self.pg.goto(self.cfg["base_url"].rstrip("/") + ruta, wait_until="load")
        self.pg.wait_for_timeout(int(self.cfg.get("espera_ms", 1500)))

    def clic(self, spec: dict, escribe=False):
        loc = localizar(self.pg, spec)
        nombre = (spec.get("nombre") or _nombre(loc)).lower()
        if any(re.search(rf"\b{re.escape(p)}\b", nombre) for p in self.prohibidos):
            if not escribe or self.cupo <= 0:
                raise Prohibido(f"clic bloqueado sobre «{nombre}»: es un botón que escribe (seguridad.prohibidos)")
            self.cupo -= 1
        loc.click()

    def paso(self, p: dict):
        if "clic" in p:
            self.clic(p["clic"], p.get("escribe", False))
        elif "llenar" in p:
            localizar(self.pg, p["llenar"]).fill(str(p["llenar"]["valor"]))
        elif "elegir" in p:
            localizar(self.pg, p["elegir"]).select_option(str(p["elegir"]["valor"]))
        elif "tecla" in p:
            self.pg.keyboard.press(p["tecla"])
        elif "esperar" in p:
            e = p["esperar"]
            if isinstance(e, int):
                self.pg.wait_for_timeout(e)
            elif e == "dialogo":
                self.pg.get_by_role("dialog").last.wait_for(timeout=15000)
            elif isinstance(e, dict) and "respuesta" in e:
                with self.pg.expect_response(lambda r: e["respuesta"] in r.url, timeout=20000):
                    pass
            else:
                localizar(self.pg, e).wait_for(timeout=15000)
        else:
            raise ValueError(f"paso desconocido: {p}")
        self.pg.wait_for_timeout(int(p.get("despues_ms", 300)))

    def cerrar_dialogo(self):
        dlg = self.pg.get_by_role("dialog")
        if not dlg.count():
            return
        for nombre in self.cerrar_con:
            b = dlg.last.get_by_role("button", name=nombre, exact=True)
            if b.count():
                b.first.click()
                return
        self.pg.keyboard.press("Escape")

    def marcadores(self, specs: list[dict]) -> list[list[float]]:
        """Punto de cada marcador: a la izquierda del elemento, a media altura (dentro si no hay margen)."""
        puntos = []
        for s in specs:
            caja = localizar(self.pg, s).bounding_box()
            if not caja:
                continue
            x = caja["x"] - 17 if caja["x"] >= 16 else caja["x"] + 14
            puntos.append([round(x), round(caja["y"] + caja["height"] / 2)])
        return puntos


def entrar(rec: Recorrido, rol: dict):
    lg = rec.cfg.get("login")
    if not lg:
        return
    usuario = rol.get("usuario") or os.environ.get(rol.get("usuario_env", ""), "")
    clave = os.environ.get(rol.get("clave_env", ""), "")
    if not usuario or not clave:
        sys.exit(f"Faltan las credenciales del rol (variables {rol.get('usuario_env')} / {rol.get('clave_env')}).")
    rec.ir(lg["ruta"])
    rec.pg.fill(lg["usuario"], usuario)
    rec.pg.fill(lg["clave"], clave)
    rec.pg.click(lg["enviar"])
    fin = time.time() + 30
    while lg.get("listo_si_url_no_contiene", "/login") in rec.pg.url and time.time() < fin:
        rec.pg.wait_for_timeout(300)


def nota_vault(cfg_def: dict, cfg: dict, item: dict, rol: str, png: Path, tipo: str):
    import notas_vault as nv

    raiz, notas = nv._destino(cfg_def)
    carpeta = notas / "capturas"
    carpeta.mkdir(parents=True, exist_ok=True)
    titulo = item.get("titulo", item["id"])
    cuerpo = (nv._frontmatter("captura", titulo, [nv._rel(png, raiz)], ["defensa", "captura", rol], [item["id"]])
              + f"# {titulo}\n\nRol: {rol} · {tipo} · ruta `{item.get('ruta', '')}`. Hub: [[_moc-defensa]]"
              + (f" · sección del manual: {item['seccion']}" if item.get("seccion") else "") + ".\n\n"
              + nv.imagen(png, carpeta) + "\n")
    (carpeta / f"{item['id']}.md").write_text(cuerpo, encoding="utf-8")


def correr(spec_path: Path, solo: set[str] | None, ensayo: bool, base: Path | None = None) -> dict:
    from playwright.sync_api import sync_playwright

    cfg = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    base = base or config.carpeta()
    cfg_def = config.cargar(base) if (base / config.NOMBRE).exists() else None
    salida = config.ruta(cfg.get("salida", "capturas"), base)
    salida.mkdir(parents=True, exist_ok=True)
    archivo_marcas = salida / "marcadores.json"
    marcas = json.loads(archivo_marcas.read_text(encoding="utf-8")) if archivo_marcas.exists() else {}
    fallos: list[str] = []
    w, h = cfg.get("viewport", [1366, 768])
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=navegador(), args=["--no-sandbox"])
        for nombre_rol, rol in cfg["roles"].items():
            items = [("pantalla", x) for x in rol.get("pantallas", [])] + [("operacion", x) for x in rol.get("operaciones", [])]
            items = [it for it in items if not solo or it[1]["id"] in solo]
            if not items:
                continue
            ctx = b.new_context(viewport={"width": w, "height": h})
            pg = ctx.new_page()
            rec = Recorrido(cfg, pg, ensayo)
            entrar(rec, rol)
            for tipo, it in items:
                try:
                    if it.get("ruta"):
                        rec.ir(it["ruta"])
                    for paso in it.get("pasos", []):
                        rec.paso(paso)
                    pg.mouse.move(3, h - 3)  # sin hover en la captura
                    pg.wait_for_timeout(500)
                    if it.get("marcadores"):
                        marcas[it["id"]] = rec.marcadores(it["marcadores"])
                    png = salida / f"{it['id']}.png"
                    if not ensayo:
                        pg.screenshot(path=str(png), clip=dict(zip("xywh", it["recorte"])) if it.get("recorte") else None)
                        if cfg.get("notas_vault") and cfg_def:
                            nota_vault(cfg_def, cfg, it, nombre_rol, png, tipo)
                    print(f"  ok {it['id']}" + (f" ({len(marcas.get(it['id'], []))} marcadores)" if it.get("marcadores") else ""))
                except Exception as exc:  # noqa: BLE001 — se registra y se sigue con la siguiente
                    fallos.append(f"{it['id']}: {exc}")
                    print(f"  FALLO {it['id']}: {exc}")
                finally:
                    if tipo == "operacion":
                        rec.cerrar_dialogo()
            ctx.close()
        b.close()
    if not ensayo:
        archivo_marcas.write_text(json.dumps(marcas, indent=1), encoding="utf-8")
    return {"fallos": fallos, "marcas": marcas, "salida": str(salida)}


if __name__ == "__main__":
    args = config.args_sin_dir()
    solo = set(args[args.index("--solo") + 1].split(",")) if "--solo" in args else None
    r = correr(Path(args[0]).resolve(), solo, "--ensayo" in args)
    print(f"{len(r['fallos'])} fallo(s); salida en {r['salida']}")
    sys.exit(1 if r["fallos"] else 0)
