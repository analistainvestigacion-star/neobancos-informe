"""Informe web a partir de los datos de la automatización oficial (scripts/neobancos).

Uso:
  python -m etl.cli transformar   indicadores del informe desde data/neobancos/raw/
  python -m etl.cli validar       cuadres y alertas (los errores bloquean la publicación)
  python -m etl.cli publicar      site/data/informe.json y CSV descargable
  python -m etl.cli todo          las tres anteriores

La descarga de datos la hace scripts/neobancos/extraer.py (ver docs/neobancos/).
"""
from __future__ import annotations

import sys


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    cmd = argv[0]
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
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
