# AGENTS.md — Vault de trabajo de grado

Este es **tu vault**: acá viven tus datos. El *motor* (las skills y los gates) es un repo aparte;
este repo solo guarda criterio, perfiles y evidencia.

> **Fuente de verdad del orden: [`ORDEN-DEL-VAULT.md`](ORDEN-DEL-VAULT.md).** Leerlo antes de
> extraer, renombrar, mover o reconciliar cualquier documento. Este archivo es el contrato mínimo.

---

## 1. Dos capas: `sources/` y `wiki/`

| Capa | Rol | Se puede escribir |
| --- | --- | --- |
| `sources/` | Material **extraído** de fuentes externas (Word, informes de revisión, Zotero). Crudo y trazable. | **No** — regenerable, no editable |
| `wiki/` | Capa **destilada**: perfiles de evaluadores, criterios de docentes, reglas, contradicciones. | Sí, es la capa de trabajo |

Separarlas evita el problema clásico: que una re-extracción pise tus correcciones manuales.

## 2. Fiabilidad de cada punto

Todo criterio lleva **uno** de tres estados: `confirmado` (el evaluador lo dijo, con cita),
`inferido` (hipótesis, no validada) o `abierto` (hay que preguntar). **No se le inventa la
intención a nadie.**

## 3. Verificación obligatoria antes de commitear

```bash
bash scripts/verificar-enlaces.sh   # 0 wikilinks rotos, 0 huérfanas fuera de allowlist
```

Sale 1 y bloquea. La allowlist se declara en `ORDEN-DEL-VAULT.md`, no en el código del script.

## 4. Reglas duras

1. **No modificar el Word fuente.** Entregar propuestas textuales primero.
2. **Extraer no es fusionar.** Si el Markdown destino tiene cambios manuales sin commitear, generar
   el `git diff` y **detenerse** antes de sobrescribir.
3. **Nunca inventar** autores, fechas, DOI ni datos. Lo no confirmado queda pendiente.
4. **Un dato, un lugar.** No duplicar el mismo criterio en dos notas.
5. **Las contradicciones no se resuelven en silencio**: se documentan en `wiki/contradictions/`
   y se preguntan.

## 5. Herramientas

- Las skills viven en el repo del motor y se comparten con tus agentes por symlink.
- `config.local.md` (en el repo del motor) dice dónde está este vault. Está fuera de git.
- Los gates están en `<este-vault>/scripts/`, symlinkeados al repo del motor: no edites ahí.
