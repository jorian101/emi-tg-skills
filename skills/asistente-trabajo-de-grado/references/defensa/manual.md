# Modo defensa — manual de usuario

Motor: `scripts/defensa/manual.py manual.yaml` (`uv run --with python-docx --with pillow --with pyyaml`).
Capturas: `scripts/defensa/capturas.py` (ver [capturas.md](capturas.md)). Modelo: `assets/defensa/manual.example.yaml`.
Solo aplica si el TG tiene un producto de software con interfaz; si no, el entregable no existe.

## Estructura (manuales EMI)

1. **Capítulo 1 — Introducción:** propósito, alcance, roles (tabla de roles con los cargos del caso) y conceptos básicos
   del área (tabla de conceptos, en lenguaje llano).
2. **Capítulo 2 — Instalación y requisitos:** hardware y software (tablas), instalación paso a paso, problemas frecuentes.
3. **Capítulo 3 — Uso, por los módulos del TG:** 3.1 acceso, 3.2 pantalla principal con la tabla «módulos, pantallas y
   roles», luego **una sección por cada módulo (sprint/fase) que declara el TG** con sus pantallas como subsecciones, el
   flujo completo y las preguntas frecuentes. Los nombres de los módulos son los del TG, no los del código.
4. Glosario (`{{TABLA-GLOSARIO}}`) y, si el TG lo tiene, diccionario de datos.

## Reglas (las mismas del TG)

- **Mismo formato que el Word del TG:** H1 «CAPÍTULO N», H2 en mayúsculas, H3/H4 en tipo título, cuerpo con el estilo
  del TG, sin sangría. Cada tabla y figura con título numerado **arriba** («Tabla N:», «Figura N:») y «*Nota.* …
  Elaboración propia, AÑO.» **abajo**. Entre dos títulos va siempre un párrafo (el motor falla si no).
- **Solo lo que el TG afirma.** El manual lo revisa alguien que no ve el código: una función que el TG deja como mejora
  futura no se promete; una que el producto tiene y el TG no menciona entra solo si el autor lo decide.
- **El producto se nombra como lo nombra el TG** (`convenciones.producto` de `proyecto.yaml`); «software» solo al hablar
  de instalarlo o de su dirección.
- «Consejo:», «¡Atención!» y comandos como texto, **sin recuadros ni sombreado**; títulos de figura «Pantalla de X»;
  después de «Etiqueta:» va mayúscula; registro formal («usted»), nunca voseo ni tuteo.
- **Capturas con cuentas reales de cada rol**, nunca de prueba (QA), a 1366×768; la clave se lee de una variable de
  entorno, nunca del repo. Lo que muestre datos sensibles o de desarrollo (contadores de pruebas) se recorta.
- Marcadores rojos numerados sobre la captura y, en el texto, los pasos con el mismo número.
- Las citas internas van como `{{REF: captura}}` / `{{REF-TABLA: NOMBRE}}`: el motor numera por orden de aparición y
  falla si una referencia no existe.

## Ciclo

1. Recapturar si cambió la interfaz (`capturas.py`), con las cuentas reales.
2. `manual.py manual.yaml` → Word; abrirlo y aceptar «actualizar campos» (índices).
3. `verificar_correcciones.py --manual` compara con el manual oficial sección por sección; el autor copia a mano.
4. Lo que el manual no puede afirmar porque el código no lo cumple va a una lista de **pendientes del código**, no al manual.
