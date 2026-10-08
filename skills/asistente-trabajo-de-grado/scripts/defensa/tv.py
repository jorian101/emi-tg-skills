#!/usr/bin/env python3
"""Página para la segunda pantalla (TV) de la defensa: videos en bucle, sin sonido, que se cambian con el teclado.

Uso: python3 tv.py TV.yaml          escribe index.html junto al yaml (abrir con el navegador, tecla F = pantalla completa)
TV.yaml: {titulo, items: [{tecla: "1", titulo: "Consulta simple", archivo: ruta/relativa/al/yaml.mp4}]}
  Los archivos pueden ser .mp4/.webm (video en bucle) o .png/.jpg/.gif (imagen). Si un archivo no existe se
  avisa y el item queda marcado «por grabar»: la tecla muestra el aviso en vez de una pantalla negra.
Teclas: las de cada item · flechas = siguiente/anterior · M = menú · F = pantalla completa.
"""

from __future__ import annotations

import html
import json
import sys
from pathlib import Path

import yaml

PLANTILLA = """<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(titulo)s</title><style>
:root{color-scheme:dark}html,body{margin:0;height:100%%;background:#000;color:#fff;font-family:system-ui,sans-serif;overflow:hidden}
#esc{position:fixed;inset:0;display:flex;align-items:center;justify-content:center}
#esc video,#esc img{max-width:100%%;max-height:100%%;object-fit:contain}
#aviso{font-size:4vw;opacity:.8;text-align:center;padding:4vw}
#menu{position:fixed;left:2vw;bottom:2vh;background:#000c;border-radius:12px;padding:1vh 1.5vw;font-size:2.2vh;line-height:1.6;transition:opacity .4s}
#menu b{display:inline-block;min-width:1.6em;color:#8ab4ff}#menu .on{color:#ffd54f}
</style></head><body><div id="esc"></div><div id="menu"></div><script>
const ITEMS=%(items)s;let i=0,t=0;const esc=document.getElementById('esc'),menu=document.getElementById('menu');
function pintarMenu(){menu.innerHTML=ITEMS.map((x,k)=>'<div class="'+(k==i?'on':'')+'"><b>'+x.tecla+'</b> '+x.titulo+(x.ok?'':' (por grabar)')+'</div>').join('');menu.style.opacity=1;clearTimeout(t);t=setTimeout(()=>menu.style.opacity=0,3500)}
function ir(k){i=(k+ITEMS.length)%%ITEMS.length;const x=ITEMS[i];esc.innerHTML='';
 if(!x.ok){esc.innerHTML='<div id="aviso">'+x.titulo+'<br><small>por grabar</small></div>'}
 else if(/\\.(mp4|webm)$/i.test(x.archivo)){const v=document.createElement('video');v.src=x.archivo;v.loop=true;v.muted=true;v.autoplay=true;v.playsInline=true;esc.appendChild(v);v.play().catch(()=>{})}
 else{const m=document.createElement('img');m.src=x.archivo;esc.appendChild(m)}
 pintarMenu()}
addEventListener('keydown',e=>{if(e.key=='ArrowRight')ir(i+1);else if(e.key=='ArrowLeft')ir(i-1);else if(e.key.toLowerCase()=='m')pintarMenu();
 else if(e.key.toLowerCase()=='f'){document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen()}
 else{const k=ITEMS.findIndex(x=>x.tecla==e.key);if(k>=0)ir(k)}});
ir(0)</script></body></html>
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    spec_path = Path(sys.argv[1]).resolve()
    spec = yaml.safe_load(spec_path.read_text(encoding="utf-8"))
    items, faltan = [], []
    for it in spec["items"]:
        ok = (spec_path.parent / it["archivo"]).exists()
        if not ok:
            faltan.append(it["titulo"])
        items.append(
            {
                "tecla": str(it["tecla"]),
                "titulo": it["titulo"],
                "archivo": it["archivo"],
                "ok": ok,
            }
        )
    teclas = [x["tecla"] for x in items]
    if len(set(teclas)) != len(teclas):
        raise SystemExit(f"teclas repetidas: {teclas}")
    salida = spec_path.parent / "index.html"
    salida.write_text(
        PLANTILLA
        % {
            "titulo": html.escape(spec.get("titulo", "TV")),
            "items": json.dumps(items, ensure_ascii=False),
        },
        encoding="utf-8",
    )
    print(f"ok {salida} ({len(items)} items)")
    if faltan:
        print("por grabar o copiar: " + ", ".join(faltan))
    return 0


if __name__ == "__main__":
    sys.exit(main())
