"""Check de capturas.py con una página local (sin app real ni cuentas):
uv run --with playwright --with pyyaml python tests/test_capturas.py

Comprueba: pantalla simple, modal abierto con marcadores medidos, nota en el vault y que un clic sobre un
botón que escribe («Guardar») queda bloqueado.
"""

import json
import sys
import tempfile
import threading
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import capturas  # noqa: E402

HTML = """<!doctype html><meta charset="utf-8"><title>Prueba</title>
<h1>Expedientes</h1><button onclick="document.getElementById('d').hidden=false">Editar</button>
<div id="d" role="dialog" aria-label="Editar expediente" hidden>
  <label>Nombre <input id="nombre"></label>
  <button onclick="document.getElementById('d').hidden=true">Cancelar</button>
  <button onclick="document.title='ESCRIBIO'">Guardar</button>
</div>"""

SPEC = """base_url: http://127.0.0.1:{puerto}
salida: capturas
notas_vault: true
espera_ms: 200
seguridad:
  prohibidos: [Guardar, Crear, Eliminar]
roles:
  operador:
    pantallas:
      - {{id: 10-inicio, ruta: /index.html, titulo: "Pantalla de expedientes"}}
    operaciones:
      - id: 60-editar
        ruta: /index.html
        titulo: "Ventana de edición"
        pasos:
          - clic: {{rol: button, nombre: Editar}}
          - esperar: dialogo
          - llenar: {{css: "#nombre", valor: "Expediente de ejemplo", dentro: dialogo}}
        marcadores:
          - {{css: "#nombre", dentro: dialogo}}
          - {{rol: button, nombre: Cancelar, dentro: dialogo}}
      - id: 61-guardar-prohibido
        ruta: /index.html
        pasos:
          - clic: {{rol: button, nombre: Editar}}
          - esperar: dialogo
          - clic: {{rol: button, nombre: Guardar, dentro: dialogo}}
"""


def test() -> None:
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)
        (d / "web").mkdir()
        (d / "web" / "index.html").write_text(HTML, encoding="utf-8")
        srv = HTTPServer(("127.0.0.1", 0), partial(SimpleHTTPRequestHandler, directory=str(d / "web")))
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        (d / "defensa.json").write_text(json.dumps({"fuentes": {}, "entregables": [], "vault": {"raiz": str(d / "vault")}}))
        spec = d / "capturas.yaml"
        spec.write_text(SPEC.format(puerto=srv.server_port), encoding="utf-8")
        r = capturas.correr(spec, None, False, base=d)
        srv.shutdown()
        assert (d / "capturas" / "10-inicio.png").exists()
        assert (d / "capturas" / "60-editar.png").exists()
        assert len(r["marcas"]["60-editar"]) == 2, r["marcas"]
        assert any("61-guardar-prohibido" in f and "bloqueado" in f for f in r["fallos"]), r["fallos"]
        assert not (d / "capturas" / "61-guardar-prohibido.png").exists()
        nota = (d / "vault" / "wiki" / "defensa" / "capturas" / "60-editar.md").read_text(encoding="utf-8")
        assert "[[_moc-defensa]]" in nota and "type: captura" in nota
    print("ok")


if __name__ == "__main__":
    test()
