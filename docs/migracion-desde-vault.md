# Migración: de skills dentro del vault a repo independiente

Esta guía es para **el autor de este repo**, que tenía las skills viviendo dentro de su vault
(`<vault>/.opencode/skills/`). Si estás instalando desde cero, no la necesitás: usá `install.sh`.

**Todo es reversible.** Está escrito así a propósito: el paso que toca tu entorno vivo se hace una
vez, con el rollback anotado al lado, y recién después de haber probado el resto.

## Qué cambia

| Antes | Después |
|---|---|
| Las skills se editan en `<vault>/.opencode/skills/` y se versionan en el repo del vault | Se editan **solo** en este repo y se versionan acá |
| El alias `~/.local/share/tg-skills` apunta al vault | Apunta a `<este-repo>/skills` |
| Los gates viven en `<vault>/scripts/` | Viven acá; el vault los symlinkea |
| `config.md` apuntaba al vault | Sigue apuntando al vault, pero ahora es config **privada** (gitignoreada) |

El **dato** no se mueve: tus perfiles, tus informes y tus reglas siguen en el vault.

## Orden de los pasos

### 1. Copiar y limpiar (sin tocar el vault)

Verificá que la copia sea fiel antes de editar nada:

```bash
diff -r <este-repo>/skills <vault>/.opencode/skills   # solo debe faltar config.md
```

### 2. Sacar las skills del control de versiones del vault

En el repo del vault:

```bash
printf '\n# Las skills viven en el repo tg-skills\n.opencode/skills/\n' >> .gitignore
git rm -r --cached .opencode/skills      # el working tree NO se toca
```

**Rollback:** `git checkout <sha-anterior> -- .opencode/skills` y quitá la línea del `.gitignore`.

### 3. Reemplazar la carpeta por un symlink

Así existe **una sola copia** y no hay dos ramas que puedan divergir:

```bash
rm -rf <vault>/.opencode/skills
ln -s <este-repo>/skills <vault>/.opencode/skills
```

`.opencode/` está excluido del verificador de enlaces por diseño, así que el symlink no rompe nada.

**Rollback:** `rm <vault>/.opencode/skills && git checkout <sha> -- .opencode/skills`

### 4. Repuntar el alias

```bash
ln -sfn <este-repo>/skills ~/.local/share/tg-skills
bash <este-repo>/scripts/verificar-skills.sh
```

Los directorios de cada agente (`~/.agents/skills`, `~/.claude/skills`, `~/.config/opencode/skills`,
`~/.codex/skills`, `~/.gemini/antigravity-cli/skills`) ya apuntaban al alias, así que no hay que
tocarlos: repuntar el alias alcanza. Si alguno apuntaba al vault directamente, repuntalo también.

**Rollback:** `ln -sfn <vault>/.opencode/skills ~/.local/share/tg-skills`

### 5. Actualizar la documentación que describe este mapa

Cualquier doc que diga "las skills viven en el vault" queda mintiendo. En este setup son cuatro:

- `ORDEN-DEL-VAULT.md` del vault (§ de skills)
- `AGENTS.md` del vault (§ de skills)
- `AGENTS.md` del repo de código (reglas de skills)
- `docs/agentes/entorno-agentes.md` del repo de código (mapa de symlinks)

### 6. Probar el ciclo completo

Es la prueba que justifica todo lo demás:

1. Hacé un cambio trivial en este repo (por ejemplo, subir el `version:` de un `SKILL.md`).
2. Comprobá que el proyecto lo ve **sin pasos extra** (el agente lee por el alias).
3. Comprobá que **no quedó una segunda copia** que pueda divergir (`find` por `SKILL.md` con ese
   nombre fuera de acá).
4. Corré los gates: `auditar-rutas.sh`, `auditar-pii.sh`, `verificar-skills.sh` y
   `verificar-enlaces.sh` sobre el vault.

## Después de migrar

- Para actualizar las skills en cualquier máquina: `git pull` en este repo. El alias hace el resto.
- Nunca edites las skills desde el vault: el symlink te va a dejar escribir, pero el commit
  correspondería al repo equivocado.
