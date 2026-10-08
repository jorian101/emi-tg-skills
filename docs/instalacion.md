# Instalación (un estudiante, su agente y su vault)

Un usuario = **un clon de este repo + un vault propio + (opcional) el catálogo de docentes**. El vault es un repositorio
**nuevo y tuyo**; este repo es el motor y se actualiza con `git pull`.

```
emi-tg-skills/        motor (este repo)                       alias ~/.local/share/tg-skills
mi-vault/             tu repo nuevo: TG extraído, perfiles, defensa
catalogo/             catálogo de docentes (submódulo privado)  alias ~/.local/share/tg-docentes
<tu proyecto>/        tu código; tu agente lo usa vía CODE_REPO
```

## Primera vez

```bash
git clone --recurse-submodules <url> ~/emi-tg-skills     # sin acceso al catálogo privado, se instala uno local vacío
cd ~/emi-tg-skills
./install.sh --destino ~/mi-vault --docx ~/TRABAJO-DE-GRADO.docx \
             --code-repo ~/mi-proyecto --agentes ~/.claude/skills [--remoto mi-vault]
```

Qué hace, en orden: revisa dependencias (obligatorias: bash, python3, git, pyyaml; opcionales por entregable, con el
comando para instalarlas) → crea el vault desde el andamiaje → obtiene el catálogo de docentes → extrae tu TG y arma
`proyecto.yaml` → vincula a tu tutor si lo nombra la carátula y está en el catálogo → rehace los enlaces y `config.md` →
`git init` del vault con su pre-commit y un primer commit → enlaza las skills a tus agentes. `--remoto` crea el repo
**privado** en GitHub con `gh`, **sin push**: publicás vos con `git push -u origin main`.

El pre-commit del vault rechaza un commit con wikilinks rotos, notas huérfanas o enlaces simbólicos.

## Después, con tu agente

1. «inicializá el vault desde mi TG» (completa `proyecto.yaml`, te pregunta tus evaluadores y qué anexos llevan QR).
2. «ingerir informe» y «registrar corrección» con cada revisión.
3. Modo defensa: diapositivas, tríptico, ruta crítica, manual, anexos con QR, diagramas animados y guion.

## Mover de máquina o actualizar

- Otra máquina: `git clone <tu-vault>` + `./install.sh --destino <tu-vault>`. Los enlaces (`scripts/`, `wiki/docentes/<docente>.md`)
  y el `config.md` llevan rutas de **esa** máquina, por eso no se versionan: el instalador los rehace
  (`scripts/asignar_evaluador.py <vault> --sync`).
- Actualizar el motor: `git pull` en el clon (y `git submodule update --remote catalogo` si seguís el catálogo del repo).
- `./install.sh --check`: estado de dependencias, agentes, catálogo, hook del vault, evaluadores y gates.

## Catálogo de docentes y colaboración

- Cada vault enlaza **solo** a sus evaluadores (tutor, revisores, docente de TG). Cualquier docente puede estar en el
  catálogo, en cualquier rol; si no está: `scripts/nuevo_docente.py`.
- Lo que te corrigen se registra en tu **catálogo local** (rama `local/<usuario>`): `scripts/registrar_criterio.py`.
- Para compartirlo: `scripts/contribuir.py` (muestra la contribución saneada: criterio, capítulo, iniciales; nunca el
  informe) → `--enviar` abre un issue con `gh`, `--pr` imprime los comandos de un PR desde tu fork. El mantenedor lo integra
  con `scripts/aplicar_contribucion.py`; vos traés las novedades con `scripts/actualizar_catalogo.sh`.
- Sin acceso al catálogo compartido todo funciona con tus propios informes; pedí acceso y corré `./install.sh --catalogo <url>`.

## Quién ve el catálogo (mantenedor)

El catálogo es un repo **privado** (`catalogo/`, submódulo) porque tiene nombres de docentes y criterios sacados de informes.
Este repo público solo guarda su **dirección** en `.gitmodules`, nunca su contenido. Para dar acceso a un estudiante:

```bash
gh api -X PUT repos/<owner>/emi-docentes/collaborators/<usuario-de-github> -f permission=push
```

Quien no tiene acceso instala igual: el instalador avisa («sin acceso al catálogo privado») y crea un catálogo local vacío.
Antes de publicar cualquier cosa: `python3 scripts/preflight_publicar.py .` (nombres sin distinguir mayúsculas, docentes del
catálogo, correos y rutas personales en las líneas a publicar) y, en el catálogo, `... --sin-docentes` (estudiantes = 0).

## Problemas frecuentes

| Síntoma | Causa y arreglo |
|---|---|
| El primer commit del vault fue rechazado | `bash <vault>/scripts/verificar-enlaces.sh` lista el wikilink roto o la nota huérfana |
| `wiki/docentes/<x>.md` roto en otra máquina | `python3 scripts/asignar_evaluador.py <vault> --sync` |
| «sin acceso al catálogo privado» | Seguís con un catálogo local vacío; pedí que te inviten al repo del catálogo |
| La ruta crítica no exporta | Falta Chrome/Chromium (`CHROME=<ruta>`) o red para Excalidraw |
| `git` no tiene tu nombre | `git config --global user.name "…"` y `user.email` |
