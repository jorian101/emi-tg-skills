# Plantilla draw.io para Caso de Uso Expandido

Alternativa opcional a PlantUML para los diagramas de **Caso de Uso Expandido**
(Sprints 1, 2, 4, 5, 6). El usuario elige al pedir el diagrama: si dice
"con draw.io" se usa esta plantilla; si dice "con PlantUML" (o no especifica,
default) se usa `assets/plantillas-puml.md`. Cualquiera de las dos termina
embebiendo su PNG en el Word via Pandoc (Hard Rule 25).

## ADVERTENCIA: dos paletas distintas, NO confundir

- La **paleta AMBAR UML** (Hard Rule 15) es la unica valida para diagramas UML,
  incluido este. Valores: ambar claro `#FFF7D6`, ambar medio `#FDE68A`,
  ambar muy claro `#FFFBEB`, marron oscuro `#78350F`, marron medio `#92400E`,
  texto `#4A3B1F`. Tipografia Georgia.
- La **paleta AZUL institucional del sistema** (`#032154`, `#0a3a82`, `#062a66`,
  Open Sans / Nunito Sans) aplica SOLO a mockups e interfaz del asistente
  (Hard Rule 33, `assets/patrones-mockups.md`). JAMAS se usa en diagramas UML.
- Antes de generar un diagrama UML con draw.io, verificar que TODOS los
  `fillColor`/`strokeColor`/`fontColor` son de la paleta ambar de arriba.

## Mapeo de paleta UML a atributos XML draw.io

| Elemento UML                    | Shape draw.io          | fillColor | strokeColor | fontColor |
| ------------------------------- | ---------------------- | --------- | ----------- | --------- |
| Actor                           | `shape=umlActor`       | `#FDE68A` | `#78350F`   | `#4A3B1F` |
| Caso de Uso                     | `ellipse`              | `#FFF7D6` | `#92400E`   | `#4A3B1F` |
| Limite del sistema              | `swimlane` (container) | `#FFFBEB` | `#92400E`   | `#4A3B1F` |
| Flecha (asociacion)             | edge                   | —         | `#92400E`   | `#4A3B1F` |
| Flecha <<include>> / <<extend>> | edge                   | —         | `#92400E`   | `#4A3B1F` |

Todas las formas y edges llevan `fontFamily=Georgia` y `fontColor=#4A3B1F`
(Hard Rule 19). Lineas rectas con `edgeStyle=orthogonalEdgeStyle` (Hard Rule 17).

## Reglas obligatorias (equivalente draw.io de las Hard Rules UML)

- **Sin titulo en el XML** (Hard Rule 16): el titulo vive solo en el H2 del `.md`.
  El `<diagram>` arranca directo con el modelo, sin label global de titulo.
- **Actores FUERA del limite del sistema** (Hard Rule 18): los `shape=umlActor`
  se colocan como celdas sueltas fuera del container `swimlane`; dentro del
  container van solo los `ellipse` de los casos de uso.
- **Lineas rectas** (Hard Rule 17): `edgeStyle=orthogonalEdgeStyle` en cada edge.
- **Georgia** (Hard Rule 19): `fontFamily=Georgia` y `fontColor=#4A3B1F` en
  cada forma y edge.
- **Labels de usecase** = verbo permitido de `assets/plantillas-puml.md`
  (Iniciar Sesion, Cerrar Sesion, Crear Usuario, Listar Usuarios, Modificar Rol,
  Cambiar Estado de Cuenta, Restablecer Contrasena, Consultar, Ver, Crear Norma,
  Consultar Fragmentos, Ver Integridad del Corpus). Sin parentesis ni
  tecnicismos; sin `\n(login)`, sin `[Regla N]`.
- **`<<include>>` / `<<extend>>`** se representan como edges con etiqueta
  `<<include>>` o `<<extend>>` sobre la linea (mismas reglas de PlantUML).
- No modelar pasos tecnicos internos como casos de uso (refresco de token,
  reranking NO son casos de uso).

## Composicion visual (equivalente al layout de PlantUML)

La plantilla reproduce el layout horizontal de PlantUML
(`left to right direction`):

- Actores en columna izquierda (secundarios pueden ir a la derecha),
  DISTRIBUIDOS verticalmente: cada actor queda aproximadamente a la altura
  del caso de uso principal con el que se asocia.
- Casos de uso dentro del limite en 1-2 columnas, elipses de ~180x60 con
  separacion vertical >=40px. PROHIBIDO `childLayout=stackLayout`: produce
  una grilla rigida tipo tabla que arruina el dibujo.
- `<<include>>`/`<<extend>>` solo entre casos de uso cercanos dentro del
  limite, con la etiqueta centrada sobre la linea.
- Antes de exportar: ningun edge debe cruzar el borde del limite mas de una
  vez ni superponerse con otra linea; si ocurre, reordenar filas/columnas.

## Plantilla canónica XML

```xml
<mxfile host="app.diagrams.net">
  <diagram id="<id-diagrama>" name="Page-1">
    <mxGraphModel dx="900" dy="700" grid="1" gridSize="10" guides="1"
      tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1"
      pageWidth="1169" pageHeight="827" math="0" shadow="0">
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />

        <!-- ACTORES: fuera del container (Hard Rule 18) -->
        <mxCell id="ACT1" value="Administrador"
          style="shape=umlActor;verticalLabelPosition=bottom;verticalAlign=top;
                 fillColor=#FDE68A;strokeColor=#78350F;fontFamily=Georgia;
                 fontColor=#4A3B1F;fontSize=11;"
          vertex="1" parent="1">
          <mxGeometry x="70" y="85" width="30" height="60" as="geometry" />
        </mxCell>

        <!-- LIMITE DEL SISTEMA: container (Hard Rule 18); SIN stackLayout -->
        <mxCell id="SYS1" value="&lt;b&gt;Gestion de Usuarios&lt;/b&gt;"
          style="swimlane;rounded=1;startSize=30;swimlaneFillColor=#FFFBEB;
                 fillColor=#FFFBEB;strokeColor=#92400E;fontFamily=Georgia;
                 fontColor=#4A3B1F;"
          vertex="1" parent="1">
          <mxGeometry x="300" y="80" width="520" height="520" as="geometry" />
        </mxCell>

        <!-- CASOS DE USO: dentro del container, posicion libre -->
        <mxCell id="UC1" value="Iniciar Sesion"
          style="ellipse;whiteSpace=wrap;html=1;fillColor=#FFF7D6;
                 strokeColor=#92400E;fontFamily=Georgia;fontColor=#4A3B1F;"
          vertex="1" parent="SYS1">
          <mxGeometry x="70" y="70" width="180" height="60" as="geometry" />
        </mxCell>
        <mxCell id="UC2" value="Cerrar Sesion"
          style="ellipse;whiteSpace=wrap;html=1;fillColor=#FFF7D6;
                 strokeColor=#92400E;fontFamily=Georgia;fontColor=#4A3B1F;"
          vertex="1" parent="SYS1">
          <mxGeometry x="310" y="70" width="180" height="60" as="geometry" />
        </mxCell>

        <!-- ASOCIACION actor -> usecase (linea recta) -->
        <mxCell id="E1"
          style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;
                 jettySize=auto;html=1;strokeColor=#92400E;fontFamily=Georgia;
                 fontColor=#4A3B1F;"
          edge="1" parent="1" source="ACT1" target="UC1">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>

        <!-- INCLUDE/EXTEND entre casos de uso -->
        <mxCell id="E2"
          style="edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;
                 jettySize=auto;html=1;strokeColor=#92400E;fontFamily=Georgia;
                 fontColor=#4A3B1F;dashed=1;"
          edge="1" parent="SYS1" source="UC2" target="UC1">
          <mxGeometry relative="1" as="geometry" />
          <mxPoint x="0" y="-10" as="offset" />
        </mxCell>
        <mxCell id="E2label" value="&lt;&lt;extend&gt;&gt;" vertex="1"
          connectable="0" parent="E2">
          <mxGeometry x="-0.1" relative="1" as="geometry">
            <mxPoint as="offset" />
          </mxGeometry>
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
```

Notas sobre la plantilla:

- La etiqueta `<<include>>` / `<<extend>>` va como `mxCell` hijo del edge con
  `connectable="0"` y `value="&lt;&lt;include&gt;&gt;"` (escapado).
- El container es un `swimlane` SIMPLE, SIN `childLayout=stackLayout`: los
  usecases se posicionan libremente dentro (el stackLayout apila en grilla
  rigida y arruina el layout). Los actores SIEMPRE fuera (Hard Rule 18).
- `parent="SYS1"` en usecases y edges internos; `parent="1"` en actores y edges
  de asociacion externos.

## Flujo de generacion (Modo agente)

1. Generar el XML siguiendo la plantilla de arriba con la paleta ambar y los
   verbos permitidos.
2. Guardar el `.drawio` en el vault:
   `sprints/sprint-N/diagramas/caso-uso-<nombre>.drawio`
3. Exportar el PNG con el CLI oficial `drawio`, SIEMPRE con sufijo `-drawio`
   para NO pisar el PNG del `.puml`:
   ```bash
   drawio --export caso-uso-<nombre>.drawio --format png \
     --output caso-uso-<nombre>-drawio.png --scale 1
   ```
4. ABRIR EL EDITOR INMEDIATAMENTE (obligatorio al generar o regenerar) para
   que el usuario ajuste el dibujo:
   ```bash
   $LOCAL_BIN/drawio sprints/sprint-N/diagramas/caso-uso-<nombre>.drawio \
     >/dev/null 2>&1 & disown
   ```
   - Comando NO bloqueante. Requiere sesion grafica activa (WSLg /
     `DISPLAY=:0`). Sin sesion grafica, entregar como fallback el link de
     preview `https://app.diagrams.net/?#U<URL-encoded-XML>`.
   - El usuario edita y guarda con Ctrl+S sobre el MISMO `.drawio`.
5. GATE DE ADOPCION (solo la primera vez): NO actualizar el `.md` del
   entregable y NO reensamblar el Word. Solo cuando el usuario lo pide
   explicitamente (ej. "ponelo en el Word del sprint N"): cambiar el `.md`
   para que apunte al PNG draw.io (Hard Rule 25:
   `![caso-uso-<nombre>-drawio.png](caso-uso-<nombre>-drawio.png){ width=15cm }`)
   y reensamblar el Word con Pandoc. ESE CAMBIO en el `.md` es el marcador
   de fase adoptada.
6. Si el usuario pide ajustes (propios o hechos por el en el editor),
   repetir pasos 1-5 con el `.drawio` vigente. Iterar hasta OK.
7. El `.puml` previo (si existia) se PRESERVA en el mismo directorio; no se
   borra.

## Sincronizacion tras guardados del usuario

Guardar en el editor SOLO escribe el `.drawio`; el PNG NO se regenera solo.
Al retomar la sesion (o cuando el usuario avisa que guardo), detectar
staleness comparando fechas de modificacion y re-exportar:

```bash
[ caso-uso-<nombre>.drawio -nt caso-uso-<nombre>-drawio.png ] && \
  drawio --export caso-uso-<nombre>.drawio --format png \
    --output caso-uso-<nombre>-drawio.png --scale 1
```

Fase segun el marcador del `.md` (cero estado extra):

| Fase     | Marcador                                           | Al detectar cambio en el `.drawio`                                                                                           |
| -------- | -------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Borrador | el `.md` aun apunta al PNG del `.puml`             | Solo re-exportar el PNG draw.io. El Word queda intacto.                                                                      |
| Adoptada | el `.md` referencia `caso-uso-<nombre>-drawio.png` | Re-exportar PNG Y reensamblar el Word del sprint con el flujo Pandoc existente (post-procesamiento incluido), SIN preguntar. |

La adopcion es decision unica del usuario; despues de ella, todo cambio en
el `.drawio` se propaga automaticamente a PNG y Word.

## CLI oficial draw.io (export headless)

- Binario: `drawio` (viene del repo oficial `jgraph/drawio-desktop`,
  instalado local en `$LOCAL_BIN/drawio`). **NO** usar paquetes npm
  alternativos (`draw.io-export` esta abandonado, 67 stars; `drawio-cli`
  de terceros, 0 stars).
- Verificacion: `which drawio && drawio --version` -> debe imprimir la
  version (ej. 31.1.8).
- Requiere display grafico o `xvfb-run` en servidores headless. En equipos
  con sesion grafica activa (`DISPLAY=:0`) funciona directo.
