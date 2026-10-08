# Correcciones pendientes al documento del trabajo de grado

**Único archivo de correcciones.** No se crean propuestas sueltas: cada corrección es una sección
`### C-NN`. El autor la copia a mano en Word, **celda por celda**. `verificar_correcciones.py --mover`
reconoce sola lo ya copiado y lo pasa a «Aplicadas».

- Cada bloque dice **dónde** (tabla, fila y columna, o párrafo), el **texto actual** y el **texto nuevo**.
- `**Buscar** en «ancla»:` limita la búsqueda al tramo que sigue al ancla (p. ej. el rótulo de la fila),
  para que una celda corta no se confunda con otra igual.
- Para insertar un párrafo nuevo, el bloque Buscar va vacío; para borrar, el bloque Reemplazar va vacío.
- Las ecuaciones de Word no se editan con Ctrl+H: se corrigen a mano.

## Pendientes

### C-01 Tabla N «Nombre de la tabla» · fila «Rótulo de la fila», columna «Columna»

**Buscar** en «Rótulo de la fila»:
```
texto actual exacto
```
**Reemplazar con:**
```
texto nuevo
```

## Aplicadas
