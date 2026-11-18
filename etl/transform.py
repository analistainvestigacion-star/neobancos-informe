"""Convierte los datos crudos en indicadores (formato largo) y tablas para el informe.

Salida: data/processed/indicadores.parquet con columnas
  entidad (id del universo, grupo_*, universo o id de comparador), fecha (AAAA-MM-DD),
  indicador, valor, fuente
y data/processed/tablas.json con tablas de distribución al corte.
"""
from __future__ import annotations

import json

import numpy as np
import pandas as pd

from .extract import RAIZ, RAW, cargar_config

PROC = RAIZ / "data" / "processed"


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------

def leer(nombre: str) -> pd.DataFrame:
    archivos = sorted((RAW / nombre).glob("*.parquet"))
    if not archivos:
        return pd.DataFrame()
    return pd.concat([pd.read_parquet(a) for a in archivos], ignore_index=True)


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.replace({"N/A": np.nan, "None": np.nan, "nan": np.nan}), errors="coerce")


def fin_de_mes(s: pd.Series) -> pd.Series:
    f = pd.to_datetime(s.str.slice(0, 10), errors="coerce")
    return (f + pd.offsets.MonthEnd(0)).dt.strftime("%Y-%m-%d")


class Universo:
    def __init__(self):
        self.ent, self.inf, self.ds, self.cuif = cargar_config()
        self.por_codigo = {(str(e["tipo"]), str(e["codigo"])): e for e in self.ent["entidades"]}
        self.tipo_a_comp = {}
        for c in self.ent["comparadores"]:
            for t in c["tipos"]:
                self.tipo_a_comp.setdefault(str(t), []).append(c["id"])

    def id_entidad(self, tipo, codigo):
        e = self.por_codigo.get((str(tipo), str(codigo)))
        return e["id"] if e else None

    def grupo(self, eid):
        for e in self.ent["entidades"]:
            if e["id"] == eid:
                return e["grupo"]
        return None


def a_largo(df: pd.DataFrame, u: Universo, campo_tipo: str, campo_codigo: str | None, columnas: dict,
            fuente: str) -> pd.DataFrame:
    """df ya tiene columna 'fecha' y 'nivel'. columnas: {indicador: columna_numérica}."""
    if df.empty:
        return pd.DataFrame(columns=["entidad", "fecha", "indicador", "valor", "fuente"])
    filas = []
    ent = df[df["nivel"] == "entidad"].copy()
    if not ent.empty:
        ent["entidad"] = [u.id_entidad(t, c) for t, c in zip(ent[campo_tipo], ent[campo_codigo])]
        ent = ent[ent["entidad"].notna()]
        for ind, col in columnas.items():
            g = ent.groupby(["entidad", "fecha"], as_index=False)[col].sum(min_count=1)
            filas.append(g.rename(columns={col: "valor"}).assign(indicador=ind))
    sis = df[df["nivel"] == "sistema"].copy()
    if not sis.empty:
        for tipo, comps in u.tipo_a_comp.items():
            sub = sis[sis[campo_tipo].astype(str) == tipo]
            if sub.empty:
                continue
            for comp in comps:
                for ind, col in columnas.items():
                    g = sub.groupby("fecha", as_index=False)[col].sum(min_count=1)
                    filas.append(g.rename(columns={col: "valor"}).assign(indicador=ind, entidad=comp))
    out = pd.concat(filas, ignore_index=True) if filas else pd.DataFrame()
    if out.empty:
        return pd.DataFrame(columns=["entidad", "fecha", "indicador", "valor", "fuente"])
    # Los comparadores que suman varios tipos se agregan aquí.
    out = out.groupby(["entidad", "fecha", "indicador"], as_index=False)["valor"].sum(min_count=1)
    return out.assign(fuente=fuente)


# ---------------------------------------------------------------------------
# indicadores por fuente
# ---------------------------------------------------------------------------

def ind_cuif(u: Universo) -> pd.DataFrame:
    df = leer("cuif")
    if df.empty:
        return pd.DataFrame()
    df["fecha"] = fin_de_mes(df["fecha_corte"])
    df["valor"] = num(df["valor"])
    # La fuente repite filas idénticas en algunos meses (p. ej. feb-2024, feb-2026).
    df = df.drop_duplicates(subset=["nivel", "tipo_entidad", "codigo_entidad", "fecha", "cuenta"])
    inv = {v: k for k, v in u.cuif.items()}
    df["ind"] = df["cuenta"].map(inv)
    piv = df.pivot_table(index=["nivel", "tipo_entidad", "codigo_entidad", "fecha"], columns="ind",
                         values="valor", aggfunc="sum", dropna=False).reset_index()
    for c in u.cuif:
        if c not in piv:
            piv[c] = np.nan
    piv["codigo_entidad"] = piv["codigo_entidad"].fillna("")
    z = lambda c: piv[c].fillna(0)
    piv["depositos_total"] = z("dep_cuenta_corriente") + z("dep_cdt") + z("dep_ahorro") + z("dep_ahorro_especial") + z("dep_electronicos")
    piv["dep_ahorro_total"] = z("dep_ahorro") + z("dep_ahorro_especial")
    piv["cartera_bruta"] = z("cartera_consumo") + z("cartera_comercial") + z("cartera_vivienda") + z("cartera_microcredito")
    cols = {c: c for c in ["activo", "pasivo", "patrimonio", "utilidad", "cartera_consumo", "cartera_comercial",
                           "cartera_vivienda", "cartera_microcredito", "cartera_bruta", "dep_cuenta_corriente",
                           "dep_cdt", "dep_ahorro_total", "dep_electronicos", "depositos_total"]}
    return a_largo(piv, u, "tipo_entidad", "codigo_entidad", cols, u.ds["cuif"]["fuente"])


PRODUCTOS_CAPT = {"ahorro": "depositos_ahorro", "cdt": "cdts", "depelec": "depositos", "ctacte": "cta_cte"}


def ind_captaciones(u: Universo) -> tuple[pd.DataFrame, dict]:
    df = leer("captaciones")
    if df.empty:
        return pd.DataFrame(), {}
    df["fecha"] = fin_de_mes(df["fechacorte"])
    for c in df.columns:
        if c.endswith(("_clientes", "_cuentas", "_cuenta", "_valor_total")):
            df[c] = num(df[c])
    for c in df.columns:
        if c.endswith("_valor_total"):
            df[c] = df[c] * 1000  # la SFC reporta los saldos en miles de pesos
    df = df.drop_duplicates(subset=["nivel", "tipoentidad", "codigoentidad", "fecha", "unidad_de_captura", "subcuenta"])
    df["uca"] = df["unidad_de_captura"].astype(str)
    df["sub"] = df["subcuenta"].astype(str)
    total = df[(df["uca"] == "1") & (df["sub"] == "999")].copy()
    cols = {}
    for p, pref in PRODUCTOS_CAPT.items():
        cuentas = f"{pref}_nro_cuentas" if f"{pref}_nro_cuentas" in total else f"{pref}_numero_cuenta"
        clientes = f"{pref}_nro_clientes" if f"{pref}_nro_clientes" in total else f"{pref}_numero_clientes"
        cols[f"clientes_{p}"] = clientes
        cols[f"cuentas_{p}"] = cuentas
        cols[f"saldo_capt_{p}"] = f"{pref}_valor_total"
    largo = [a_largo(total, u, "tipoentidad", "codigoentidad", cols, u.ds["captaciones"]["fuente"])]
    # Personas naturales / jurídicas (UCA 3): subcuenta 5 = PN, 10 = PJ. Suma ahorro + depósitos electrónicos.
    tc = df[df["uca"] == "3"].copy()
    tc["clientes_dep"] = tc["depositos_ahorro_nro_clientes"].fillna(0) + tc["depositos_numero_clientes"].fillna(0)
    for sub, nombre in (("5", "clientes_pn"), ("10", "clientes_pj")):
        largo.append(a_largo(tc[tc["sub"] == sub], u, "tipoentidad", "codigoentidad", {nombre: "clientes_dep"},
                             u.ds["captaciones"]["fuente"]))
    # Tabla: distribución por rangos de saldo (UCA 1, subcuentas distintas de 999) al corte del informe.
    rangos = df[(df["uca"] == "1") & (df["sub"] != "999") & (df["nivel"] == "entidad")].copy()
    rangos["entidad"] = [u.id_entidad(t, c) for t, c in zip(rangos["tipoentidad"], rangos["codigoentidad"])]
    rangos["cuentas_dep"] = rangos["depositos_ahorro_nro_cuentas"].fillna(0) + rangos["depositos_numero_cuenta"].fillna(0)
    rangos["orden"] = pd.to_numeric(rangos["sub"], errors="coerce")
    tabla = {}
    for fecha, g in rangos.groupby("fecha"):
        t = g.groupby(["orden", "nombre_subcuenta"], as_index=False)["cuentas_dep"].sum().sort_values("orden")
        tabla[fecha] = [{"rango": r.nombre_subcuenta, "cuentas": float(r.cuentas_dep)} for r in t.itertuples()]
    return pd.concat(largo, ignore_index=True), {"rangos_saldo": tabla}


def ind_fogafin(u: Universo) -> pd.DataFrame:
    df = leer("fogafin")
    if df.empty:
        return pd.DataFrame()
    df["fecha"] = fin_de_mes(df["fecha_de_corte"])
    df["n"] = num(df["numero_de_productos"])
    df["saldo"] = num(df["saldo_depositos"])
    df["estado"] = df["estado_del_producto"].str.upper().str.strip()
    df["dbm"] = df["tipo_de_producto_amparado"].str.contains("BAJO MONTO", case=False, na=False)
    filas = []
    for est, nombre in (("ACTIVO", "productos_activos"), ("INACTIVO", "productos_inactivos"),
                        ("ABANDONADO", "productos_abandonados")):
        filas.append(a_largo(df[df["estado"] == est], u, "codigo_tipo_entidad_sfc", "codigo_entidad_sfc",
                             {nombre: "n"}, u.ds["fogafin"]["fuente"]))
    filas.append(a_largo(df, u, "codigo_tipo_entidad_sfc", "codigo_entidad_sfc", {"productos_total": "n"},
                         u.ds["fogafin"]["fuente"]))
    d = df[df["dbm"]]
    filas.append(a_largo(d, u, "codigo_tipo_entidad_sfc", "codigo_entidad_sfc", {"dbm_productos": "n"},
                         u.ds["fogafin"]["fuente"]))
    filas.append(a_largo(d[d["estado"] == "ACTIVO"], u, "codigo_tipo_entidad_sfc", "codigo_entidad_sfc",
                         {"dbm_activos": "n"}, u.ds["fogafin"]["fuente"]))
    return pd.concat(filas, ignore_index=True)


# Productos de consumo en la distribución de cartera: rotativo, tarjetas, libre inversión, libranza,
# vehículo, otros, bajo monto y empleados.
UNICAP_CONSUMO = {"1", "2", "3", "4", "5", "6", "29", "30"}


def ind_cartera(u: Universo) -> pd.DataFrame:
    """Calidad de cartera de consumo por producto (distribución de cartera)."""
    df = leer("cartera")
    if df.empty:
        return pd.DataFrame()
    df["fecha"] = fin_de_mes(df["fecha_corte"])
    df["saldo"] = num(df["_1_saldo_de_la_cartera_a"])
    df["vigente"] = num(df["_2_vigente"])
    df["clientes_mora"] = num(df["_16_n_mero_de_clientes_mora"])
    df["renglon"] = df["renglon"].astype(str)
    df["unicap"] = df["unicap"].astype(str)
    df["codigo_entidad"] = df["codigo_entidad"].fillna("")
    # El renglón 5 es el total de cada producto; los demás lo desagregan.
    df = df[df["renglon"] == "5"]
    df = df.drop_duplicates(subset=["nivel", "tipo_entidad", "codigo_entidad", "fecha", "unicap"])
    df["vencida"] = df["saldo"] - df["vigente"]
    f = u.ds["cartera"]["fuente"]
    consumo = df[df["unicap"].isin(UNICAP_CONSUMO)]
    return pd.concat([
        a_largo(consumo, u, "tipo_entidad", "codigo_entidad",
                {"cartera_consumo_dist": "saldo", "cartera_vencida": "vencida", "clientes_mora": "clientes_mora"}, f),
        a_largo(df, u, "tipo_entidad", "codigo_entidad",
                {"cartera_dist_total": "saldo", "cartera_vencida_total": "vencida"}, f),
    ], ignore_index=True)


def ind_414(u: Universo) -> tuple[pd.DataFrame, dict]:
    df = leer("f414")
    if df.empty:
        return pd.DataFrame(), {}
    df["fecha"] = fin_de_mes(df["fecha_corte"])
    for c in ("monto", "n", "tasa_x_monto"):
        df[c] = num(df[c])
    df["codigo_entidad"] = df["codigo_entidad"].fillna("")
    df["es_tc"] = df["producto_de_cr_dito"].str.contains("Tarjeta", case=False, na=False)
    fuente = u.ds["f414"]["fuente"]
    filas = []
    for tc, suf in ((False, ""), (True, "_tc")):
        sub = df[df["es_tc"] == tc]
        filas.append(a_largo(sub, u, "tipo_entidad", "codigo_entidad",
                             {f"desembolsos{suf}": "monto", f"creditos{suf}": "n", f"_txm{suf}": "tasa_x_monto"}, fuente))
        for tipo in ("Consumo", "Comercial ordinario", "Crédito productivo", "Vivienda"):
            if tc:
                break
            s2 = sub[sub["tipo_de_cr_dito"] == tipo]
            clave = {"Consumo": "consumo", "Comercial ordinario": "comercial", "Crédito productivo": "productivo",
                     "Vivienda": "vivienda"}[tipo]
            filas.append(a_largo(s2, u, "tipo_entidad", "codigo_entidad",
                                 {f"desembolsos_{clave}": "monto", f"_txm_{clave}": "tasa_x_monto"}, fuente))
    # Por sexo (solo entidades del universo, personas naturales).
    sx = df[(df["nivel"] == "entidad") & (df["tipo_de_persona"] == "Natural") & (~df["es_tc"])].copy()
    for sexo, clave in (("Femenino", "mujer"), ("Masculino", "hombre")):
        filas.append(a_largo(sx[sx["sexo"] == sexo], u, "tipo_entidad", "codigo_entidad",
                             {f"desembolsos_{clave}": "monto", f"creditos_{clave}": "n"}, fuente))
    return pd.concat(filas, ignore_index=True), {}


def ind_441(u: Universo) -> pd.DataFrame:
    df = leer("f441")
    if df.empty:
        return pd.DataFrame()
    df["fecha"] = fin_de_mes(df["fechacorte"])
    df["monto"] = num(df["monto_total"])
    df["txm"] = num(df["tasa_x_monto"])
    df["codigoentidad"] = df["codigoentidad"].fillna("")
    # Excluye la fila 900 (total por red de oficinas) para no duplicar.
    df = df[df["subcuenta"].astype(str) != "900"]
    return a_largo(df, u, "tipoentidad", "codigoentidad", {"cdt_emitido": "monto", "_txm_cdt": "txm"},
                   u.ds["f441"]["fuente"])


def ind_tarjetas(u: Universo) -> pd.DataFrame:
    df = leer("tarjetas")
    if df.empty:
        return pd.DataFrame()
    df["fecha"] = fin_de_mes(df["fechacorte"])
    df["total"] = num(df["total_tarjetas"])
    df["codigoentidad"] = df["codigoentidad"].fillna("")
    df["uca"] = df["cod_uca"].astype(str)
    df["sub"] = df["subcuenta"].astype(str)
    vig = df[df["sub"] == "5"].drop_duplicates(subset=["nivel", "tipoentidad", "codigoentidad", "fecha", "uca"])
    f = u.ds["tarjetas"]["fuente"]
    return pd.concat([
        a_largo(vig[vig["uca"] != "6"], u, "tipoentidad", "codigoentidad", {"tarjetas_credito": "total"}, f),
        a_largo(vig[vig["uca"] == "6"], u, "tipoentidad", "codigoentidad", {"tarjetas_debito": "total"}, f),
    ], ignore_index=True)


def ind_inclusion(u: Universo) -> pd.DataFrame:
    df = leer("inclusion")
    if df.empty:
        return pd.DataFrame()
    df["fecha"] = fin_de_mes(df["fecha_corte"])
    df["codigo_entidad"] = df["codigo_entidad"].fillna("")
    m = {"ctas_ahorro_activas": "_25_nro_ctas_ahorro_activas", "ctas_ahorro_mujeres": "_27_nro_ctas_ahorro_mujeres",
         "ctas_ahorro_hombres": "_29_nro_ctas_ahorro_hombres", "ctas_ahorro_total": "_31_nro_ctas_ahorro"}
    for c in m.values():
        df[c] = num(df[c])
    df = df.drop_duplicates(subset=["nivel", "tipo_entidad", "codigo_entidad", "fecha"])
    return a_largo(df, u, "tipo_entidad", "codigo_entidad", m, u.ds["inclusion"]["fuente"])


def ind_canales(u: Universo) -> tuple[pd.DataFrame, dict]:
    import yaml
    df = leer("canales")
    if df.empty:
        return pd.DataFrame(), {}
    nombres = yaml.safe_load((RAIZ / "config" / "canales_444.yaml").read_text(encoding="utf-8")) or {}
    canal_nombre = {str(k): v for k, v in (nombres.get("canales") or {}).items()}
    df["fecha"] = fin_de_mes(df["fecha_corte"])
    df["cantidad"] = num(df["cantidad"])
    df["monto"] = num(df["monto"])
    largo = a_largo(df, u, "tipo_entidad", "codigo_entidad", {"operaciones": "cantidad", "monto_operaciones": "monto"},
                    u.ds["canales"]["fuente"])
    df["entidad"] = [u.id_entidad(t, c) for t, c in zip(df["tipo_entidad"], df["codigo_entidad"])]
    df["canal"] = df["codigo_canal_distribucion"].astype(str).map(lambda c: canal_nombre.get(c, f"Canal {c}"))
    tabla = {}
    for fecha, g in df.groupby("fecha"):
        t = g.groupby(["entidad", "canal"], as_index=False)[["cantidad", "monto"]].sum()
        tabla[fecha] = t.to_dict(orient="records")
    return largo, {"canales": tabla}


# ---------------------------------------------------------------------------

# Tasas promedio ponderadas por monto = sum(tasa*monto)/sum(monto): (numerador, denominador, nombre)
TASAS = [("_txm", "desembolsos", "tasa_desembolsos"), ("_txm_tc", "desembolsos_tc", "tasa_tc"),
         ("_txm_consumo", "desembolsos_consumo", "tasa_consumo"), ("_txm_comercial", "desembolsos_comercial", "tasa_comercial"),
         ("_txm_cdt", "cdt_emitido", "tasa_cdt")]


def calcular_tasas(df: pd.DataFrame) -> pd.DataFrame:
    w = df.pivot_table(index=["entidad", "fecha"], columns="indicador", values="valor", aggfunc="sum").reset_index()
    fuentes = df.groupby("indicador")["fuente"].first()
    tasas = []
    for txm, monto, nombre in TASAS:
        if txm in w and monto in w:
            t = w[["entidad", "fecha"]].assign(valor=w[txm] / w[monto].replace(0, np.nan), indicador=nombre,
                                               fuente=fuentes.get(monto))
            tasas.append(t[t["valor"].notna()])
    return pd.concat([df[~df["indicador"].str.startswith("_")]] + tasas, ignore_index=True)


def agregar_grupos(df: pd.DataFrame, u: Universo) -> pd.DataFrame:
    """Suma por grupo (banco/cf/sedpe) y universo (los numeradores de tasas también se suman)."""
    ent_ids = {e["id"] for e in u.ent["entidades"]}
    base = df[df["entidad"].isin(ent_ids)].copy()
    base["grupo"] = base["entidad"].map(u.grupo)
    g = base.groupby(["grupo", "fecha", "indicador", "fuente"], as_index=False)["valor"].sum(min_count=1)
    g["entidad"] = "grupo_" + g["grupo"]
    t = base.groupby(["fecha", "indicador", "fuente"], as_index=False)["valor"].sum(min_count=1).assign(entidad="universo")
    return pd.concat([df, g.drop(columns="grupo"), t], ignore_index=True)


def construir() -> pd.DataFrame:
    u = Universo()
    PROC.mkdir(parents=True, exist_ok=True)
    partes, tablas = [], {}
    for f in (ind_cuif, ind_captaciones, ind_fogafin, ind_cartera, ind_414, ind_441, ind_tarjetas, ind_inclusion,
              ind_canales):
        r = f(u)
        if isinstance(r, tuple):
            r, t = r
            tablas.update(t)
        if r is not None and not r.empty:
            partes.append(r)
        print(f"  {f.__name__}: {0 if r is None else len(r)} filas")
    df = pd.concat(partes, ignore_index=True)
    df = df[df["valor"].notna()]
    df = agregar_grupos(df, u)
    df = calcular_tasas(df)
    df = df.sort_values(["indicador", "entidad", "fecha"]).reset_index(drop=True)
    df.to_parquet(PROC / "indicadores.parquet", index=False)
    (PROC / "tablas.json").write_text(json.dumps(tablas, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"indicadores: {len(df)} filas, {df['indicador'].nunique()} indicadores")
    return df
