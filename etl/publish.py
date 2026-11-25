"""Genera site/data/informe.json (todo lo que necesita el informe web) y CSV descargables."""
from __future__ import annotations

import json
from datetime import datetime, timezone

import pandas as pd

from .fuentes_jefe import RAIZ
from .transform import PROC, Universo

SITE = RAIZ / "site" / "data"


def secciones() -> list[dict]:
    """Plantillas de texto (content/secciones/*.md) con sus marcadores {{...}} sin resolver."""
    out = []
    for f in sorted((RAIZ / "content" / "secciones").glob("*.md")):
        md = f.read_text(encoding="utf-8")
        primera = next((l for l in md.splitlines() if l.startswith("## ")), "")
        titulo = primera[3:].split(". ", 1)[-1] if primera else ""
        out.append({"id": f.stem.split("_", 1)[-1], "titulo": titulo, "md": md})
    return out


def publicar() -> None:
    u = Universo()
    SITE.mkdir(parents=True, exist_ok=True)
    df = pd.read_parquet(PROC / "indicadores.parquet")
    tablas = json.loads((PROC / "tablas.json").read_text(encoding="utf-8"))
    estado = RAIZ / "data" / "neobancos" / "raw" / "_extraccion.json"  # registro de la automatización oficial

    series: dict = {}
    for (ind, ent), g in df.groupby(["indicador", "entidad"]):
        series.setdefault(ind, {})[ent] = [[f, round(float(v), 4)] for f, v in zip(g["fecha"], g["valor"])]
    fuentes = df.groupby("indicador")["fuente"].first().to_dict()
    ultimo = df.groupby("indicador")["fecha"].max().to_dict()

    salida = {
        "meta": {
            "titulo": u.inf["titulo"],
            "generado": datetime.now(timezone.utc).isoformat(timespec="minutes"),
            "corte_informe": u.inf["corte_informe"],
            "corte_base": u.inf["corte_base"],
            "fuentes_actualizadas": json.loads(estado.read_text(encoding="utf-8")) if estado.exists() else {},
        },
        "entidades": u.ent["entidades"],
        "grupos": u.ent["grupos"],
        "comparadores": u.ent["comparadores"],
        "fuente_indicador": fuentes,
        "ultimo": ultimo,
        "series": series,
        "tablas": tablas,
        "secciones": secciones(),
    }
    (SITE / "informe.json").write_text(json.dumps(salida, ensure_ascii=False, separators=(",", ":"), default=str),
                                       encoding="utf-8")
    # CSV completo para descarga
    nombres = {e["id"]: e["marca"] for e in u.ent["entidades"]}
    nombres.update({c["id"]: c["nombre"] for c in u.ent["comparadores"]})
    nombres.update({f"grupo_{k}": v for k, v in u.ent["grupos"].items()})
    nombres["universo"] = "Total neobancos y billeteras"
    df.assign(nombre=df["entidad"].map(nombres)).to_csv(SITE / "indicadores.csv", index=False, encoding="utf-8-sig")
    print(f"publicado: {SITE / 'informe.json'} ({(SITE / 'informe.json').stat().st_size / 1e6:.1f} MB)")
