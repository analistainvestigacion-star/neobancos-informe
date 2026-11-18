"""Descarga incremental desde datos.gov.co.

Cada dataset se guarda por mes en data/raw/<dataset>/<AAAA-MM>.parquet.
Los meses ya descargados no se vuelven a pedir, salvo los últimos N
(la SFC retransmite cifras), que se refrescan siempre.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd
import yaml

from .socrata import lit, metadata, query

RAIZ = Path(__file__).resolve().parents[1]
RAW = RAIZ / "data" / "raw"
CONFIG = RAIZ / "config"
REFRESCAR_ULTIMOS = 3


def cargar_config():
    ent = yaml.safe_load((CONFIG / "entidades.yaml").read_text(encoding="utf-8"))
    inf = yaml.safe_load((CONFIG / "informe.yaml").read_text(encoding="utf-8"))
    ds = yaml.safe_load((CONFIG / "datasets.yaml").read_text(encoding="utf-8"))
    cuif = yaml.safe_load((CONFIG / "cuentas_cuif.yaml").read_text(encoding="utf-8"))
    return ent, inf, ds, cuif


def meses(desde: str, hasta: date) -> list[pd.Timestamp]:
    return list(pd.date_range(pd.Timestamp(desde), pd.Timestamp(hasta), freq="ME"))


def filtro_entidades(ent: dict, d: dict) -> str:
    ds_id, campo_tipo, campo_codigo = d["id"], d["tipo"], d["codigo"]
    por_tipo: dict[int, list[int]] = {}
    for e in ent["entidades"]:
        por_tipo.setdefault(e["tipo"], []).append(e["codigo"])
    partes = [
        f"({campo_tipo}={lit(ds_id, campo_tipo, t)} AND "
        f"{campo_codigo} in({','.join(lit(ds_id, campo_codigo, c) for c in cods)}))"
        for t, cods in por_tipo.items()
    ]
    return "(" + " OR ".join(partes) + ")"


def tipos_sistema(ent: dict, d: dict) -> str:
    tipos = sorted({t for c in ent["comparadores"] for t in c["tipos"]})
    return f"{d['tipo']} in(" + ",".join(lit(d["id"], d["tipo"], t) for t in tipos) + ")"


def rango_mes(campo: str, mes: pd.Timestamp, texto: bool = False) -> str:
    ini = mes.replace(day=1)
    if texto:
        return f"{campo} between '{ini:%Y-%m-%d}' and '{mes:%Y-%m-%d}'"
    return f"{campo} between '{ini:%Y-%m-%d}T00:00:00' and '{mes:%Y-%m-%d}T23:59:59'"


# ---------------------------------------------------------------------------
# Consultas por dataset. Cada función devuelve un DataFrame para un mes,
# con una columna "nivel" = entidad | sistema.
# ---------------------------------------------------------------------------

def q_cuif(ent, ds, cuif, mes):
    d = ds["cuif"]
    cuentas = ",".join(repr(c) for c in cuif.values())
    base = f"{rango_mes(d['fecha'], mes)} AND moneda='0' AND cuenta in({cuentas})"
    e = query(d["id"], select="tipo_entidad,codigo_entidad,fecha_corte,cuenta,valor",
              where=f"{base} AND {filtro_entidades(ent, d)}")
    # Sin agregar en el servidor: la fuente trae filas duplicadas que se depuran en transform.
    s = query(d["id"], select="tipo_entidad,codigo_entidad,fecha_corte,cuenta,valor",
              where=f"{base} AND {tipos_sistema(ent, d)}")
    return pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)


def q_captaciones(ent, ds, cuif, mes):
    d = ds["captaciones"]
    base = rango_mes(d["fecha"], mes)
    e = query(d["id"], where=f"{base} AND {filtro_entidades(ent, d)}")
    # Las columnas de valores son texto (con "N/A"): se bajan filas completas y se agregan localmente.
    s = query(d["id"], where=f"{base} AND {tipos_sistema(ent, d)}")
    return pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)


def q_fogafin(ent, ds, cuif, mes):
    d = ds["fogafin"]
    base = rango_mes(d["fecha"], mes, texto=True)
    e = query(d["id"], where=f"{base} AND {filtro_entidades(ent, d)}")
    return e.assign(nivel="entidad")


def q_cartera(ent, ds, cuif, mes):
    d = ds["cartera"]
    base = rango_mes(d["fecha"], mes)
    e = query(d["id"], where=f"{base} AND {filtro_entidades(ent, d)}")
    s = query(d["id"], where=f"{base} AND {tipos_sistema(ent, d)} AND renglon=5")
    return pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)


def _q414(dataset, ent, d, mes):
    base = rango_mes(d["fecha"], mes)
    agg = ("sum(montos_desembolsados) as monto, sum(numero_de_creditos) as n, "
           "sum(tasa_efectiva_promedio * montos_desembolsados) as tasa_x_monto")
    e = query(dataset, select=f"tipo_entidad,codigo_entidad,tipo_de_cr_dito,producto_de_cr_dito,sexo,tipo_de_persona,{agg}",
              where=f"{base} AND {filtro_entidades(ent, d)}",
              group="tipo_entidad,codigo_entidad,tipo_de_cr_dito,producto_de_cr_dito,sexo,tipo_de_persona")
    s = query(dataset, select=f"tipo_entidad,tipo_de_cr_dito,producto_de_cr_dito,{agg}",
              where=f"{base} AND {tipos_sistema(ent, d)}",
              group="tipo_entidad,tipo_de_cr_dito,producto_de_cr_dito")
    out = pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)
    return out.assign(fecha_corte=mes.strftime("%Y-%m-%d"))


def q_f414(ent, ds, cuif, mes):
    # El histórico llega hasta ~2 meses atrás; los meses recientes salen del dataset "últimos dos meses".
    df = _q414(ds["f414"]["id"], ent, ds["f414"], mes)
    if df.empty or df["monto"].isna().all():
        df = _q414(ds["f414_reciente"]["id"], ent, ds["f414_reciente"], mes)
    return df


def q_f441(ent, ds, cuif, mes):
    d = ds["f441"]
    base = f"{rango_mes(d['fecha'], mes)} AND uca=1 AND tasa > 0"
    agg = "sum(monto) as monto_total, sum(tasa * monto) as tasa_x_monto"
    e = query(d["id"], select=f"tipoentidad,codigoentidad,subcuenta,descripcion,{agg}",
              where=f"{base} AND {filtro_entidades(ent, d)}",
              group="tipoentidad,codigoentidad,subcuenta,descripcion")
    s = query(d["id"], select=f"tipoentidad,subcuenta,descripcion,{agg}",
              where=f"{base} AND {tipos_sistema(ent, d)}",
              group="tipoentidad,subcuenta,descripcion")
    out = pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)
    return out.assign(fechacorte=mes.strftime("%Y-%m-%d"))


def q_tarjetas(ent, ds, cuif, mes):
    d = ds["tarjetas"]
    base = rango_mes(d["fecha"], mes)
    e = query(d["id"], where=f"{base} AND {filtro_entidades(ent, d)}")
    s = query(d["id"], where=f"{base} AND {tipos_sistema(ent, d)} AND subcuenta=5")
    return pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)


def q_inclusion(ent, ds, cuif, mes):
    d = ds["inclusion"]
    if mes.month not in (3, 6, 9, 12):
        return pd.DataFrame()
    cols = ["_25_nro_ctas_ahorro_activas", "_26_saldo_ctas_ahorro_activas", "_27_nro_ctas_ahorro_mujeres",
            "_28_saldo_ctas_ahorro_mujeres", "_29_nro_ctas_ahorro_hombres", "_30_saldo_ctas_ahorro_hombres",
            "_31_nro_ctas_ahorro", "_32_saldo_ctas_ahorro"]
    sel = ",".join(cols)
    # unicap 34 = TOTAL NACIONAL (los demás son departamentos y municipios).
    base = f"{rango_mes(d['fecha'], mes)} AND unicap=34 AND renglon=999 AND tipo='Cuentas de Ahorro'"
    e = query(d["id"], select=f"tipo_entidad,codigo_entidad,fecha_corte,{sel}",
              where=f"{base} AND {filtro_entidades(ent, d)}")
    s = query(d["id"], select=f"tipo_entidad,codigo_entidad,fecha_corte,{sel}",
              where=f"{base} AND {tipos_sistema(ent, d)}")
    return pd.concat([e.assign(nivel="entidad"), s.assign(nivel="sistema")], ignore_index=True)


def q_canales(ent, ds, cuif, mes):
    d = ds["canales"]
    base = rango_mes(d["fecha"], mes)
    agg = "sum(cantidad_operaciones) as cantidad, sum(monto_operaciones) as monto"
    e = query(d["id"], select=f"tipo_entidad,codigo_entidad,fecha_corte,codigo_canal_distribucion,codigo_operacion,{agg}",
              where=f"{base} AND {filtro_entidades(ent, d)}",
              group="tipo_entidad,codigo_entidad,fecha_corte,codigo_canal_distribucion,codigo_operacion")
    return e.assign(nivel="entidad")


CONSULTAS = {
    "cuif": q_cuif,
    "captaciones": q_captaciones,
    "fogafin": q_fogafin,
    "cartera": q_cartera,
    "f414": q_f414,
    "f441": q_f441,
    "tarjetas": q_tarjetas,
    "inclusion": q_inclusion,
    "canales": q_canales,
}


# Primer mes por dataset (el 414 es pesado: ~6 min por mes).
DESDE = {"f414": "2024-01-31", "f441": "2024-01-31", "canales": "2024-01-31"}
# Consultas en paralelo por dataset. El 414 va de a una: en paralelo datos.gov.co lo frena.
HILOS = {"f414": 1, "f441": 3}
# Fuentes lentas a las que aplica el tope de meses por corrida.
LENTOS = {"f414"}


def _pendientes(nombre: str, lista, forzar: bool):
    carpeta = RAW / nombre
    carpeta.mkdir(parents=True, exist_ok=True)
    existentes = sorted(p.stem for p in carpeta.glob("*.parquet"))
    # Refresca los últimos meses con datos y todos los meses sin archivo.
    refrescar = set(existentes[-REFRESCAR_ULTIMOS:])
    out = []
    for mes in lista:
        clave = mes.strftime("%Y-%m")
        archivo = carpeta / f"{clave}.parquet"
        vacio = carpeta / f"{clave}.vacio"
        if not forzar and archivo.exists() and clave not in refrescar:
            continue
        # Meses vacíos antiguos (antes del último mes con datos) no se reintentan.
        if not forzar and vacio.exists() and existentes and clave < existentes[-1]:
            continue
        out.append(mes)
    return carpeta, out


def extraer(nombres: list[str] | None = None, hasta: date | None = None, forzar: bool = False) -> dict:
    import os
    from concurrent.futures import ThreadPoolExecutor

    ent, inf, ds, cuif = cargar_config()
    hasta = hasta or date.today()
    # Tope de meses por corrida para fuentes lentas (en GitHub Actions: MAX_MESES_POR_CORRIDA=6).
    tope = int(os.environ.get("MAX_MESES_POR_CORRIDA", "0")) or None
    resumen, errores = {}, {}
    for nombre in nombres or CONSULTAS:
        lista = meses(DESDE.get(nombre, inf["inicio_series"]), hasta)
        carpeta, pendientes = _pendientes(nombre, lista, forzar)
        # Lo más reciente primero: si la corrida se corta, quedan los meses que más importan.
        pendientes = sorted(pendientes, reverse=True)
        if tope and nombre in LENTOS:
            pendientes = pendientes[:tope]

        def bajar(mes, nombre=nombre, carpeta=carpeta):
            clave = mes.strftime("%Y-%m")
            print(f"[{nombre}] {clave} ...", flush=True)
            df = CONSULTAS[nombre](ent, ds, cuif, mes)
            if df.empty:
                (carpeta / f"{clave}.vacio").touch()
                return 0
            (carpeta / f"{clave}.vacio").unlink(missing_ok=True)
            df.astype(str).to_parquet(carpeta / f"{clave}.parquet", index=False)
            print(f"[{nombre}] {clave} ok ({len(df)} filas)", flush=True)
            return 1

        try:
            with ThreadPoolExecutor(max_workers=HILOS.get(nombre, 2)) as ex:
                resumen[nombre] = sum(ex.map(bajar, pendientes))
        except Exception as e:  # una fuente caída no detiene las demás
            errores[nombre] = str(e)[:300]
            print(f"[{nombre}] ERROR: {errores[nombre]}", flush=True)
    if errores:
        resumen["errores"] = errores
    return resumen


def estado_fuentes() -> dict:
    """Fecha de última actualización de cada dataset en datos.gov.co."""
    _, _, ds, _ = cargar_config()
    return {k: metadata(v["id"]) for k, v in ds.items()}


def cambio_en_fuentes(ruta_estado: Path) -> tuple[bool, dict]:
    actual = estado_fuentes()
    previo = json.loads(ruta_estado.read_text(encoding="utf-8")) if ruta_estado.exists() else {}
    cambio = any(previo.get(k, {}).get("rows_updated_at") != v["rows_updated_at"] for k, v in actual.items())
    return cambio, actual
