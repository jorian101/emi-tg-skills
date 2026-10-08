# Catálogo público de docentes (sin nombres)

Perfiles **generados** desde el catálogo privado del mantenedor: código, huellas del nombre, qué suele revisar, criterios
generales (con iniciales y fecha como fuente, sin citas) e historial de roles. **No se edita a mano**: para aportar,
abrí un issue con el formulario «Aporte de criterio».

- Descargar es **opcional**: `./install.sh --catalogo-publico`.
- Reconocer a TU docente, en tu máquina: `python3 scripts/resolver_docente.py "Nombre Apellido"`. El nombre no sale de tu
  computadora; solo se comparan huellas (SHA-256 con sal pública) de pares de nombres y apellidos.
- Es **seudonimización, no anonimato**: quien ya conozca un nombre puede comprobar si coincide, y el rol y los criterios
  pueden dar pistas. No hay nombres, citas de informes ni datos de estudiantes más allá de sus iniciales.
