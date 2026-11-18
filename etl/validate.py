"""Chequeos antes de publicar. Errores bloquean la publicación; alertas se guardan para revisión."""
from __future__ import annotations

import json

import pandas as pd

from .transform import PROC, Universo


def validar() -> list[str]:
    u = Universo()
    df = pd.read_parquet(PROC / "indicadores.parquet")
    errores, alertas = [], []
    corte = u.inf["corte_informe"]
    ids = [e["id"] for e in u.ent["entidades"] if not e.get("licencia_2026")]

    # 1. Cuadre contable: activo = pasivo + patrimonio (tolerancia 1 %).
    w = df[df["indicador"].isin(["activo", "pasivo", "patrimonio"])].pivot_table(
        index=["entidad", "fecha"], columns="indicador", values="valor").dropna()
    if not w.empty:
        dif = (w["activo"] - w["pasivo"] - w["patrimonio"]).abs() / w["activo"].abs()
        malos = dif[dif > 0.01]
        for (ent, fecha), v in malos.items():
            errores.append(f"CUIF descuadrado {ent} {fecha}: {v:.1%}")

    # 2. Cobertura al corte del informe.
    for ind in ("activo", "depositos_total"):
        presentes = set(df[(df["indicador"] == ind) & (df["fecha"] == corte)]["entidad"])
        faltan = [i for i in ids if i not in presentes]
        if faltan:
            alertas.append(f"Sin {ind} a {corte}: {', '.join(faltan)}")
        if not presentes:
            errores.append(f"No hay datos de {ind} al corte {corte}")

    # 3. Meses faltantes en el 414 (universo).
    f = df[(df["indicador"] == "desembolsos") & (df["entidad"] == "universo")]["fecha"]
    if not f.empty:
        esperado = pd.date_range(f.min(), f.max(), freq="ME").strftime("%Y-%m-%d")
        huecos = sorted(set(esperado) - set(f))
        if huecos:  # el 414 se completa en varias corridas: alerta, no error
            alertas.append(f"Formato 414 sin meses todavía: {', '.join(huecos)}")

    # 4. Saltos atípicos (> ±50 % m/m) en saldos de entidades: alerta, no error.
    for ind in ("activo", "depositos_total", "cartera_bruta"):
        s = df[(df["indicador"] == ind) & df["entidad"].isin(ids)].sort_values("fecha")
        for ent, g in s.groupby("entidad"):
            g = g[g["valor"].abs() > 1e9]  # ignora saldos muy pequeños
            v = g.set_index("fecha")["valor"].pct_change()
            for fecha, x in v[(v.abs() > 0.5)].items():
                alertas.append(f"Salto {ind} {ent} {fecha}: {x:+.0%}")

    (PROC / "alertas.json").write_text(json.dumps({"errores": errores, "alertas": alertas}, ensure_ascii=False, indent=1),
                                       encoding="utf-8")
    print(f"validación: {len(errores)} errores, {len(alertas)} alertas")
    return errores
