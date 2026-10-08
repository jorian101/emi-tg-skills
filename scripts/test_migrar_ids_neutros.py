"""Los IDs con prefijo pasan a CR<n> y la migración es idempotente (python3 scripts/test_migrar_ids_neutros.py)."""

from migrar_ids_neutros import migrar

T = "| ID | Criterio |\n|---|---|\n| ABC1 | uno |\n| ABC2 | dos (ver ABC1) |\n| ABCF1 | forma |\n"
nuevo, mapa = migrar(T)
assert mapa == {"ABC1": "CR1", "ABC2": "CR2", "ABCF1": "CR3"}, mapa
assert "| CR2 | dos (ver CR1) |" in nuevo and "ABC" not in nuevo
assert migrar(nuevo) == (nuevo, {})
assert migrar(nuevo + "| XY9 | otro |\n")[1] == {"XY9": "CR4"}
print("ok test_migrar_ids_neutros")
