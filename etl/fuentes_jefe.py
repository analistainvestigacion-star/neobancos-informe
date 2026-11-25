"""Puente entre la automatización de datos públicos (scripts/neobancos, la oficial) y el informe web.

La automatización descarga a data/neobancos/raw/<clave>.csv: las fuentes del universo (las 19
asociadas de scripts/neobancos/entidades.csv) y las fuentes "_sistema" (todas las entidades de
los tipos del sistema). Este módulo las lee y las entrega con la forma que usa etl/transform.py:
una columna "nivel" = entidad (universo) o sistema, y los nombres de columna de cada dataset.
"""
from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path

import pandas as pd
import yaml

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "neobancos" / "raw"
CONFIG = RAIZ / "config"
ENTIDADES_CSV = RAIZ / "scripts" / "neobancos" / "entidades.csv"

GRUPO_POR_TIPO = {"1": "banco", "4": "cf", "128": "sedpe"}
IDS_FIJOS = {"Lulo Bank": "lulo"}  # ids que ya usan los textos del informe


def _slug(texto: str) -> str:
    t = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", t.lower())


def entidades() -> list[dict]:
    """Universo oficial (entidades.csv del paquete) en el formato del informe web."""
    out = []
    with ENTIDADES_CSV.open(encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["incluir"].strip().lower() != "si":
                continue
            inicio = (r.get("inicio_operacion") or "").strip()
            nota = (r.get("nota") or "").strip()
            out.append({
                "id": IDS_FIJOS.get(r["marca"], _slug(r["marca"])),
                "marca": r["marca"],
                "grupo": GRUPO_POR_TIPO.get(r["tipo_sfc"], "otro"),
                "tipo": int(r["tipo_sfc"]),
                "codigo": int(r["codigo_sfc"]),
                "licencia": r["nombre_tipo_sfc"],
                "nit": r["nit"],
                "inicio_operacion": inicio or None,
                "licencia_2026": inicio >= "2026-01-01" if inicio else False,
                "fecha_autorizacion": nota if "Res." in nota else None,
            })
    return out


def cargar_config():
    ent = yaml.safe_load((CONFIG / "entidades.yaml").read_text(encoding="utf-8"))
    ent["entidades"] = entidades()
    inf = yaml.safe_load((CONFIG / "informe.yaml").read_text(encoding="utf-8"))
    ds = yaml.safe_load((CONFIG / "datasets.yaml").read_text(encoding="utf-8"))
    cuif = yaml.safe_load((CONFIG / "cuentas_cuif.yaml").read_text(encoding="utf-8"))
    return ent, inf, ds, cuif


def _csv(clave: str) -> pd.DataFrame:
    ruta = RAW / f"{clave}.csv"
    if not ruta.exists() or ruta.stat().st_size < 2:
        return pd.DataFrame()
    return pd.read_csv(ruta, dtype=str, keep_default_na=False, low_memory=False)


def _par(universo: str | list[str], sistema: str | list[str], renombrar: dict | None = None) -> pd.DataFrame:
    partes = []
    for claves, nivel in ((universo, "entidad"), (sistema, "sistema")):
        for c in [claves] if isinstance(claves, str) else claves:
            df = _csv(c)
            if not df.empty:
                partes.append(df.rename(columns=renombrar or {}).assign(nivel=nivel, _origen=c))
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def _414() -> pd.DataFrame:
    """Une el histórico y las semanas recientes; si una semana está en ambos, manda el histórico."""
    ren = {"monto_desembolsado": "monto", "numero_de_creditos": "n", "tasa_por_monto": "tasa_x_monto"}
    df = _par(["tasas_colocacion", "tasas_colocacion_recientes"],
              ["tasas_colocacion_sistema", "tasas_colocacion_recientes_sistema"], ren)
    if df.empty:
        return df
    df["_prioridad"] = df["_origen"].str.contains("recientes").astype(int)
    df["_semana"] = df["fecha_corte"].str.slice(0, 10)
    mejor = df.groupby(["nivel", "_semana"])["_prioridad"].transform("min")
    return df[df["_prioridad"] == mejor].drop(columns=["_prioridad", "_semana"])


def _441() -> pd.DataFrame:
    df = _par("tasas_captacion", "tasas_captacion_sistema", {"mes": "fechacorte", "tasa_por_monto": "tasa_x_monto"})
    if df.empty:
        return df
    # La fuente del universo trae también los días con tasa 0; sin tasa no hay costo que ponderar.
    return df[pd.to_numeric(df["tasa_x_monto"], errors="coerce").fillna(0) != 0]


LECTORES = {
    "cuif": lambda: _par("cuif", "cuif_sistema"),
    "captaciones": lambda: _par("captaciones", "captaciones_sistema"),
    "fogafin": lambda: _par("fogafin_productos", "fogafin_productos_sistema"),
    "depositantes": lambda: _par("fogafin_depositantes", "fogafin_depositantes_sistema"),
    "cartera": lambda: _par("cartera", "cartera_sistema"),
    "tarjetas": lambda: _par("tarjetas", "tarjetas_sistema"),
    "inclusion": lambda: _par("inclusion", "inclusion_sistema"),
    "dbm": lambda: _par("inclusion", "inclusion_sistema"),
    "solvencia": lambda: _par("solvencia", "solvencia_sistema"),
    "canales": lambda: _par("canales", [], {"cantidad_operaciones": "cantidad", "monto_operaciones": "monto"}),
    "f414": _414,
    "f441": _441,
}


def leer(nombre: str) -> pd.DataFrame:
    df = LECTORES[nombre]()
    return df.drop(columns=["_origen"], errors="ignore")
