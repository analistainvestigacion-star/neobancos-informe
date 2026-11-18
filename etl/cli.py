"""Uso:
  python -m etl.cli extraer [dataset ...] [--forzar]
  python -m etl.cli transformar
  python -m etl.cli publicar
  python -m etl.cli todo            (extraer + transformar + validar + publicar)
  python -m etl.cli revisar         (sale con código 0 si alguna fuente cambió, 1 si no)
"""
from __future__ import annotations

import json
import sys

from .extract import RAIZ, cambio_en_fuentes, extraer

ESTADO = RAIZ / "data" / "estado_fuentes.json"


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd, resto = argv[0], argv[1:]
    forzar = "--forzar" in resto
    nombres = [a for a in resto if not a.startswith("--")] or None
    if cmd == "revisar":
        cambio, actual = cambio_en_fuentes(ESTADO)
        print(json.dumps({k: v["rows_updated_at"] for k, v in actual.items()}, indent=1))
        print("CAMBIO" if cambio else "SIN CAMBIOS")
        return 0 if cambio else 1
    if cmd in ("extraer", "todo"):
        print(extraer(nombres, forzar=forzar))
    if cmd in ("transformar", "todo"):
        from .transform import construir
        construir()
    if cmd in ("validar", "todo"):
        from .validate import validar
        errores = validar()
        if errores:
            print("VALIDACIÓN FALLIDA:\n- " + "\n- ".join(errores))
            return 3
    if cmd in ("publicar", "todo"):
        from .publish import publicar
        publicar()
    if cmd == "todo":
        _, actual = cambio_en_fuentes(ESTADO)
        ESTADO.write_text(json.dumps(actual, indent=1, ensure_ascii=False), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
