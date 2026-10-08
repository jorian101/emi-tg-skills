# Instalación (un estudiante, su agente y su vault)

Un usuario = **un clon de este repo + un vault propio + (opcional) el catálogo de docentes**. El vault es un repositorio
**nuevo y tuyo**; este repo es el motor y se actualiza con `git pull`.

```
emi-tg-skills/        motor (este repo)                       alias ~/.local/share/tg-skills
mi-vault/             tu repo nuevo: TG extraído, perfiles, defensa
catalogo-publico/     (dentro del clon) catálogo de docentes SIN nombres, opcional   →  ~/.local/share/tg-docentes (copia local tuya)
<tu proyecto>/        tu código; tu agente lo usa vía CODE_REPO
```

## Primera vez

```bash
git clone <url> ~/emi-tg-skills
cd ~/emi-tg-skills
./install.sh --destino ~/mi-vault --docx ~/TRABAJO-DE-GRADO.docx \
             --code-repo ~/mi-proyecto --agentes ~/.claude/skills [--remoto mi-vault] [--catalogo-publico]
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

## Catálogo de docentes (opcional, sin nombres) y cómo colaborar

Tres capas, para que cualquiera colabore **sin invitaciones** y los nombres no se publiquen:

| Capa | Dónde | Qué tiene |
|---|---|---|
| Pública | `catalogo-publico/` de este repo | perfiles **sin nombre**: código `d-xxxxxx`, huellas, qué suele revisar, criterios generales con iniciales y fecha |
| Privada | repo del mantenedor | los mismos perfiles **con** nombre y la fuente de verdad; nadie más la ve |
| Tuya | `~/.local/share/tg-docentes` y tu vault | tu copia local del catálogo y el nombre de **tus** docentes (`wiki/docentes/_nombres.local.yaml`, ignorado por git) |

- Trae también los **formatos oficiales** de cada docente (`formatos/<código>/`: medidas, orden y plantilla vacía del Word del TG, artículo, bíptico, tríptico
  y diapositivas); `scripts/verificar_formato.py` comprueba tus entregables contra los de tus evaluadores.
- **Descargarlo es opcional**: `./install.sh --catalogo-publico` (en una terminal el instalador te lo pregunta; por defecto no).
- **Reconocer a tu docente**: `python3 scripts/resolver_docente.py "Nombre Apellido" --vault <vault> --guardar`. Se calculan
  huellas del nombre en **tu** máquina y se comparan con las del catálogo: el nombre no sale de tu computadora. Con
  `asignar_evaluador.py --rol tutor --nombre "…"` queda vinculado; el tutor de la carátula se vincula solo si hay coincidencia fuerte.
  Si tu docente no está: `scripts/nuevo_docente.py --nombre "…" --rol "…" --vault <vault>` crea su perfil local (sin nombre).
- **Lo que te corrigen** se registra en tu catálogo local (`scripts/registrar_criterio.py`, rama `local/<usuario>`).
- **Aportar**: `scripts/contribuir.py` arma el aporte con el **código** (nunca el nombre) y se niega si en él aparece el nombre de
  alguno de tus docentes; con `--enviar` abre un issue en este repo. También sirve el formulario «Aporte de criterio» en la pestaña
  Issues. Cualquiera con cuenta de GitHub puede; no hay PR al catálogo porque `catalogo-publico/` es generado.
- **Novedades**: `bash scripts/actualizar_catalogo.sh` (tras un `git pull`) trae el snapshot nuevo y rebasa tu rama local.
- **Límites (es seudonimización, no anonimato)**: quien ya sepa el nombre de un docente puede comprobar si coincide con unas huellas, y el
  rol más los criterios pueden dar pistas. No hay nombres ni citas de informes; las fuentes llevan iniciales de estudiantes.

## Mantenedor: del aporte al catálogo público

1. El issue trae código y huellas. `python3 scripts/aplicar_contribucion.py <n.º de issue> --catalogo <privado> --commit --exportar`
   lo identifica en el catálogo privado (por código o por ≥3 pares de huellas), suma el criterio y regenera `catalogo-publico/`.
   Se niega si el issue contiene el nombre de un docente (es público: edítalo o bórralo).
2. `exportar_publico.py` tiene su propia puerta: aborta **sin escribir** si algún nombre o apellido del catálogo privado aparece en la salida.
3. Antes de publicar: `python3 scripts/preflight_publicar.py . --nombres-de <privado>` (0 hallazgos), y el PR a `main` lo abrís vos.

## Problemas frecuentes

| Síntoma | Causa y arreglo |
|---|---|
| El primer commit del vault fue rechazado | `bash <vault>/scripts/verificar-enlaces.sh` lista el wikilink roto o la nota huérfana |
| `wiki/docentes/<x>.md` roto en otra máquina | `python3 scripts/asignar_evaluador.py <vault> --sync` |
| No encuentro a mi docente en el catálogo | `nuevo_docente.py --nombre … --rol … --vault <vault>` lo crea en tu catálogo local; luego `contribuir.py` lo comparte sin nombre |
| La ruta crítica no exporta | Falta Chrome/Chromium (`CHROME=<ruta>`) o red para Excalidraw |
| `git` no tiene tu nombre | `git config --global user.name "…"` y `user.email` |
