## Qué cambia

<!-- Una o dos frases. Si arregla un issue, citá el número: "Closes #12". -->

## Por qué

<!-- El problema real, no la implementación. Si es una regla nueva, de dónde sale. -->

## Cómo lo probaste

- [ ] `bash scripts/auditar-rutas.sh` → verde
- [ ] `bash scripts/auditar-pii.sh` → verde
- [ ] `bash install.sh --check` → verde
- [ ] Si toqué el instalador o el andamiaje: instalé en un `HOME` falso y el vault nuevo quedó con
      0 enlaces rotos y 0 huérfanas

## Checklist

- [ ] No agregué nombres reales, informes ni datos personales
- [ ] Si es un criterio nuevo, es **general** y no un caso particular presentado como norma
- [ ] Si toqué una regla, actualicé su fila de verificación
- [ ] El commit sigue Conventional Commits
