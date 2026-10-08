"""Huellas del nombre, código y perfil público sin nombres (python3 scripts/test_pseudonimos.py)."""

from catalogo_lib import (claves_de_nombre, codigo_de_slug, coincidencias, frontmatter, nombres_en, normalizar, perfil_publico,
                          tokens_nombre)

assert tokens_nombre("Cnl. DAEN Ramiro Óscar Tarqui Vásquez") == ["oscar", "ramiro", "tarqui", "vasquez"]
assert normalizar("Zúñiga") == "zuniga"
assert claves_de_nombre("Tarqui, Ramiro Óscar") == claves_de_nombre("ramiro oscar TARQUI")  # orden, acentos y mayúsculas no importan
perfiles = {"a": claves_de_nombre("Cnl. Ramiro Óscar Tarqui Vásquez"), "b": claves_de_nombre("Ana María Prueba Rojas")}
assert coincidencias("Ramiro Tarqui", perfiles) == [("a", 1)]
assert coincidencias("Pedro Gómez", perfiles) == []
assert coincidencias("Ana Prueba Rojas", perfiles)[0] == ("b", 3)
assert codigo_de_slug("apellido-a") == codigo_de_slug("apellido-a") and codigo_de_slug("apellido-a") != codigo_de_slug("otro")

PRIVADO = '''---
title: Ing. Ana Prueba Rojas
type: docente
revisa: "marco práctico"
alcance: fondo
nombre: Ing. Ana Prueba Rojas
rol: Docente revisor
updated: 2026-10-08
---

# Ing. Ana Prueba Rojas

## Criterios de fondo

| ID | Criterio | Estado | Ocurrencias | Fuente |
|---|---|---|---|---|
| CR1 | Cifras con porcentaje | confirmado | 2 | "texto literal del informe" (informe a X.Y., MP 15/05) |

## Criterios de forma (fuera del alcance)

| ID | Criterio | Estado | Fuente |
|---|---|---|---|
| CR2 | Tablas sin cortes | confirmado | informe a X.Y. «cita» |

## Cómo trabaja
Ana Prueba firma con el aval.

## Historial de roles

| Rol | Estudiante | Desde |
|---|---|---|
| Revisor 2 | L.P. | 2026-09 |

## Relaciones
- [[ana-prueba]]
'''
codigo, publico = perfil_publico(PRIVADO, "ana-prueba")
fm = frontmatter(publico)
assert codigo == fm["codigo"] == codigo_de_slug("ana-prueba") and fm["rol"] == "Revisor" and "nombre" not in fm
assert fm["claves"] == claves_de_nombre("Ana Prueba Rojas")
assert "Cómo trabaja" not in publico and "[[ana-prueba]]" not in publico
assert "texto literal" not in publico and "cita" not in publico.split("Criterios de forma")[1]
assert "informe a X.Y., MP 15/05" in publico and "| Revisor 2 | L.P. | 2026-09 |" in publico
assert nombres_en(publico, {"prueba", "rojas"}) == []  # el nombre quedó afuera
assert nombres_en("firma Ana Prueba", {"prueba"}) == ["prueba"]
print("ok test_pseudonimos")
