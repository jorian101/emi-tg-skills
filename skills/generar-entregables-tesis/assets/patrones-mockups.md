# Patrones de mockups

## Fuente visual obligatoria

Antes de crear un mockup, leer en este orden:

1. `$CODE_REPO/DESIGN.md`.
2. `$CODE_REPO/frontend/src/index.css`.
3. El CSS y el componente de la pantalla que se representa, por ejemplo `Corpus.tsx`, `AdminLayout.tsx` y `DataTable.tsx`.

El mockup representa la interfaz del asistente, no el estilo de los diagramas UML.
La paleta ámbar de PlantUML nunca se usa en mockups.

### Tokens del asistente

| Uso | Valor |
| --- | --- |
| Autoridad, barra lateral y marca | `#032154` |
| Acción primaria, enlace activo y foco | `#0a3a82` |
| Hover de acción | `#062a66` |
| Fondo general | `#f8fafc` |
| Superficie de tarjetas, tablas e inputs | `#ffffff` |
| Borde | `#d8e0ea` |
| Borde fuerte | `#cbd5e1` |
| Texto principal | `#1f2933` |
| Texto secundario | `#475569` |
| Éxito | `#047857` sobre `#ecfdf5` |
| Advertencia | `#b45309` sobre `#fffbeb` |
| Error | `#b91c1c` sobre `#fef2f2` |

Usar Open Sans para títulos y Nunito Sans para cuerpo, etiquetas y tablas. Mantener
la cuadrícula de barra lateral de 240 px, superficies blancas, bordes discretos,
radios de 4/6/8 px y sombras azules suaves. No inventar gradientes, colores de
diagramas, tipografías serif ni componentes que no existan en la pantalla fuente.

El HTML de importación usa colores hexadecimales directos, no variables `:root`.
Mantener un DOM plano con cinco niveles como máximo y usar `position: absolute`
para la composición de 1200 por 800 px. El importador de OpenPencil 0.14.0 puede
colapsar elementos anidados o ignorar `grid` y `flex`.

## Flujo reproducible de OpenPencil

Cada mockup debe conservar tres artefactos:

- `mockup-<nombre>.html`: fuente estática HTML/CSS basada en la pantalla real.
- `mockup-<nombre>.fig`: documento editable generado por OpenPencil.
- `mockup-<nombre>.png`: captura final del HTML usada por el Word.

Ejecutar desde la carpeta del mockup:

```bash
node "$SKILL_DIR/scripts/openpencil-cli.mjs" import mockup-<nombre>.html -o mockup-<nombre>.fig
node "$SKILL_DIR/scripts/openpencil-cli.mjs" lint mockup-<nombre>.fig
node "$SKILL_DIR/scripts/openpencil-cli.mjs" info mockup-<nombre>.fig
node "$SKILL_DIR/scripts/openpencil-cli.mjs" analyze colors mockup-<nombre>.fig
uv run --directory $CODE_REPO/backend python \
  "$SKILL_DIR/scripts/mockup-html-to-png.py" mockup-<nombre>.html mockup-<nombre>.png
```

El wrapper evita el error `Bun is not defined` del shim Node del CLI. El PNG se
captura con Playwright porque `openpencil export` puede deformar el layout de
documentos importados desde HTML en la versión 0.14.0. El `.fig` sigue siendo el
artefacto editable y se valida; no abrir PNG como documento, importar JSX ni usar
PIL o ImageMagick como fuente oficial. Los avisos de contraste del lint se anotan
si provienen de tokens reales del frontend y no bloquean el entregable.

Para el panel Corpus, reproducir las tres pestañas reales `Normas`, `Indexar` y
`Segmentos`, las tarjetas de normas, el botón `Reconciliar Qdrant` y los textos
de `AdminLayout`. No sustituir tarjetas por tablas ni agregar acciones ausentes.

## Selección de entregables

Usar el modo más específico que corresponda:

| Pedido | Acción |
| --- | --- |
| `Genera los entregables del Sprint X` | Generar el sprint completo por primera vez |
| `Regenera TODO el Sprint X` | Regenerar todos los entregables del sprint |
| `Regenera la Figura N del Sprint X` | Regenerar una figura y sus fuentes |
| `Regenera los mockups del Sprint X` | Regenerar solo las figuras de mockup |
| `Regenera las Tablas N y M del Sprint X` | Regenerar solo las tablas indicadas |
| `Regenera las Figuras N, M y P del Sprint X` | Regenerar solo las figuras indicadas |

Nunca interpretar "mockups del sprint" como regeneración total. Resolver los
archivos exactos en `assets/mapa-entregables.md` y reensamblar el Word desde cero
solo después de regenerar el subconjunto pedido.
