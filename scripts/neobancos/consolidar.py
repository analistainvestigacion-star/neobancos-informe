"""Consolida las fuentes crudas del informe de Neobancos en un Excel y en archivos para la web.

Lee data/neobancos/raw/*.csv (salida de extraer.py) y produce:
- data/neobancos/Datos públicos Neobancos – SFC y Fogafín.xlsx
- data/neobancos/web/indicadores.json y .csv  (serie larga de indicadores clave)
- data/neobancos/web/resumen.json              (último corte y diciembres por entidad)
- data/neobancos/web/metadatos.json            (fuentes, cortes y fecha de extracción)
- data/neobancos/web/validacion.json           (entidades esperadas frente a encontradas)

Uso:
    uv run python -m scripts.neobancos.consolidar [--salida RUTA.xlsx]
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from .fuentes import DATA_DIR, FUENTES, FUENTES_POR_CLAVE, RAW_DIR, WEB_DIR, cargar_entidades

XLSX = DATA_DIR / "Datos públicos Neobancos – SFC y Fogafín.xlsx"
NAVY = "0B1F3A"

# Cuentas CUIF con nombre corto para los indicadores clave.
CUENTAS_CLAVE = {
    "100000": "Activo total",
    "200000": "Pasivo total",
    "300000": "Patrimonio",
    "590000": "Resultado del ejercicio (acumulado del año)",
    "140000": "Cartera de créditos neta",
    "210500": "Depósitos en cuenta corriente",
    "210700": "Certificados de depósito a término (CDT)",
    "210800": "Depósitos de ahorro",
    "211600": "Depósitos especiales",
    "212000": "Depósitos electrónicos",
}
DEPOSITOS = ["210500", "210700", "210800", "211600", "212000"]

PRODUCTOS_CAPTACION = {
    "cta_cte": (
        "Cuenta corriente",
        "cta_cte_nro_clientes",
        "cta_cte_nro_cuentas",
        "cta_cte_valor_total",
    ),
    "ahorro": (
        "Depósitos de ahorro",
        "depositos_ahorro_nro_clientes",
        "depositos_ahorro_nro_cuentas",
        "depositos_ahorro_valor_total",
    ),
    "cdt": ("CDT", "cdts_nro_clientes", "cdts_nro_cuentas", "cdts_valor_total"),
    "cdat": ("CDAT", "cdats_nro_clientes", "cdats_nro_cuentas", "cdats_valor_total"),
    "bonos": ("Bonos", "bonos_nro_clientes", "bonos_nro_cuentas", "bonos_valor_total"),
    "depositos": (
        "Depósitos electrónicos y de bajo monto (SEDPE)",
        "depositos_numero_clientes",
        "depositos_numero_cuenta",
        "depositos_valor_total",
    ),
}

# Indicadores que van al Resumen (columnas), en este orden.
RESUMEN = [
    ("Activo total", "COP"),
    ("Depósitos totales (CUIF)", "COP"),
    ("Depósitos de ahorro", "COP"),
    ("Certificados de depósito a término (CDT)", "COP"),
    ("Depósitos electrónicos", "COP"),
    ("Cartera de créditos neta", "COP"),
    ("Cuentas de depósito (todas)", "Número"),
    ("Clientes de depósito (suma por producto)", "Número"),
    ("Depositantes (Fogafín)", "Número"),
]


def leer(clave: str) -> pd.DataFrame:
    ruta = RAW_DIR / f"{clave}.csv"
    if not ruta.exists():
        return pd.DataFrame()
    return pd.read_csv(ruta, dtype=str, keep_default_na=False)


def numerico(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c].replace({"N/A": None, "": None}), errors="coerce")
    return df


def con_entidad(df: pd.DataFrame, campo_tipo: str, campo_codigo: str, mapa: dict) -> pd.DataFrame:
    if df.empty:
        return df
    if "tipo" in df.columns:  # inclusión financiera ya trae una columna "tipo" (tipo de registro)
        df = df.rename(columns={"tipo": "tipo_registro"})
    claves = list(
        zip(
            df[campo_tipo].astype(float).astype(int).astype(str),
            df[campo_codigo].astype(float).astype(int).astype(str),
            strict=True,
        )
    )
    df.insert(0, "entidad", [mapa.get(k, {}).get("marca", "") for k in claves])
    df.insert(1, "tipo", [mapa.get(k, {}).get("nombre_tipo_sfc", "") for k in claves])
    return df


def fila(entidad, tipo, fecha, indicador, valor, unidad, fuente) -> dict:
    return {
        "entidad": entidad,
        "tipo": tipo,
        "corte": fecha,
        "indicador": indicador,
        "valor": valor,
        "unidad": unidad,
        "fuente": fuente.nombre,
        "dataset": fuente.id,
    }


def indicadores_cuif(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    f = FUENTES_POR_CLAVE["cuif"]
    df = numerico(df, ["valor"])
    df["corte"] = pd.to_datetime(df["fecha_corte"]).dt.strftime("%Y-%m-%d")
    df = df[df["cuenta"].str.endswith("00")].copy()  # nivel de 4 dígitos
    out = []
    for (ent, tipo, corte), g in df.groupby(["entidad", "tipo", "corte"]):
        valores = dict(zip(g["cuenta"], g["valor"], strict=False))
        for cta, nombre in CUENTAS_CLAVE.items():
            if cta in valores:
                out.append(fila(ent, tipo, corte, nombre, valores[cta], "COP", f))
        dep = [valores[c] for c in DEPOSITOS if c in valores]
        if dep:
            out.append(fila(ent, tipo, corte, "Depósitos totales (CUIF)", sum(dep), "COP", f))
    hoja = df[["entidad", "tipo", "corte", "cuenta", "nombre_cuenta", "valor"]]
    return hoja, out


def indicadores_captaciones(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    f = FUENTES_POR_CLAVE["captaciones"]
    df = numerico(df, f.columnas_valor)
    df["corte"] = pd.to_datetime(df["fechacorte"]).dt.strftime("%Y-%m-%d")
    for _, _cli, _cta, val in PRODUCTOS_CAPTACION.values():
        if val in df.columns:
            df[val] = df[val] * 1000  # miles de COP -> COP
    out = []
    totales = df[df["subcuenta"] == "999"]
    for (ent, tipo, corte), g in totales.groupby(["entidad", "tipo", "corte"]):
        # La unidad "fuente de captación" (2) trae el total de todos los productos; si no
        # está, se usa la de rangos de saldo (1) o la de rangos en pesos (5).
        for uc in ("2", "1", "5"):
            sel = g[g["unidad_de_captura"] == uc]
            if not sel.empty:
                r = sel.iloc[0]
                break
        else:
            continue
        cuentas = clientes = 0.0
        for nombre, cli, cta, val in PRODUCTOS_CAPTACION.values():
            if pd.notna(r.get(cta)) and r.get(cta):
                out.append(fila(ent, tipo, corte, f"Clientes – {nombre}", r[cli], "Número", f))
                out.append(fila(ent, tipo, corte, f"Cuentas – {nombre}", r[cta], "Número", f))
                out.append(fila(ent, tipo, corte, f"Saldo – {nombre}", r[val], "COP", f))
                cuentas += r[cta] or 0
                clientes += r[cli] or 0
        out.append(fila(ent, tipo, corte, "Cuentas de depósito (todas)", cuentas, "Número", f))
        out.append(
            fila(
                ent, tipo, corte, "Clientes de depósito (suma por producto)", clientes, "Número", f
            )
        )
    cols = [
        "entidad",
        "tipo",
        "corte",
        "unidad_de_captura",
        "descripcion_uca",
        "subcuenta",
        "nombre_subcuenta",
    ] + [c for c in f.columnas_valor if c in df.columns]
    return df[cols], out


def indicadores_fogafin(
    dep: pd.DataFrame, prod: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, list[dict]]:
    f = FUENTES_POR_CLAVE["fogafin_depositantes"]
    dep = numerico(dep, ["numero_total_de_clientes", "saldo_depositos"])
    dep["corte"] = pd.to_datetime(dep["fecha_de_corte"], dayfirst=True).dt.strftime("%Y-%m-%d")
    dep["saldo_depositos"] = dep["saldo_depositos"] * 1000
    out = [
        fila(
            ent,
            tipo,
            corte,
            "Depositantes (Fogafín)",
            g["numero_total_de_clientes"].sum(),
            "Número",
            f,
        )
        for (ent, tipo, corte), g in dep.groupby(["entidad", "tipo", "corte"])
    ]
    prod = numerico(prod, ["numero_de_productos", "saldo_depositos"])
    prod["corte"] = pd.to_datetime(prod["fecha_de_corte"]).dt.strftime("%Y-%m-%d")
    prod["saldo_depositos"] = prod["saldo_depositos"] * 1000
    fp = FUENTES_POR_CLAVE["fogafin_productos"]
    act = prod[prod["estado_del_producto"].str.upper() == "ACTIVO"]
    out += [
        fila(
            ent,
            tipo,
            corte,
            "Productos de depósito activos (Fogafín)",
            g["numero_de_productos"].sum(),
            "Número",
            fp,
        )
        for (ent, tipo, corte), g in act.groupby(["entidad", "tipo", "corte"])
    ]
    hoja_dep = dep[
        [
            "entidad",
            "tipo",
            "corte",
            "tipo_de_persona",
            "numero_total_de_clientes",
            "saldo_depositos",
        ]
    ]
    hoja_prod = prod[
        [
            "entidad",
            "tipo",
            "corte",
            "tipo_de_producto_amparado",
            "estado_del_producto",
            "tipo_de_persona",
            "numero_de_productos",
            "saldo_depositos",
        ]
    ]
    return hoja_dep, hoja_prod, out


def indicadores_colocacion(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    f = FUENTES_POR_CLAVE["tasas_colocacion"]
    if df.empty:
        return df, []
    df = numerico(df, ["monto_desembolsado", "numero_de_creditos", "tasa_por_monto"])
    df["mes"] = (
        pd.to_datetime(df["fecha_corte"])
        .dt.to_period("M")
        .dt.to_timestamp("M")
        .dt.strftime("%Y-%m-%d")
    )
    claves = [
        "entidad",
        "tipo",
        "mes",
        "tipo_de_cr_dito",
        "producto_de_cr_dito",
        "tipo_de_persona",
        "sexo",
    ]
    hoja = df.groupby(claves, dropna=False)[
        ["monto_desembolsado", "numero_de_creditos", "tasa_por_monto"]
    ].sum()
    hoja = hoja.reset_index()
    hoja["tasa_ponderada_ea"] = hoja["tasa_por_monto"] / hoja["monto_desembolsado"].where(
        hoja["monto_desembolsado"] > 0
    )
    out = []
    por_tipo = (
        hoja.groupby(["entidad", "tipo", "mes", "tipo_de_cr_dito"])[
            ["monto_desembolsado", "numero_de_creditos", "tasa_por_monto"]
        ]
        .sum()
        .reset_index()
    )
    for r in por_tipo.itertuples():
        out.append(
            fila(
                r.entidad,
                r.tipo,
                r.mes,
                f"Desembolsos – {r.tipo_de_cr_dito}",
                r.monto_desembolsado,
                "COP",
                f,
            )
        )
        out.append(
            fila(
                r.entidad,
                r.tipo,
                r.mes,
                f"Créditos desembolsados – {r.tipo_de_cr_dito}",
                r.numero_de_creditos,
                "Número",
                f,
            )
        )
        if r.monto_desembolsado:
            out.append(
                fila(
                    r.entidad,
                    r.tipo,
                    r.mes,
                    f"Tasa ponderada – {r.tipo_de_cr_dito}",
                    r.tasa_por_monto / r.monto_desembolsado,
                    "% EA",
                    f,
                )
            )
    return hoja.drop(columns="tasa_por_monto").rename(columns={"mes": "corte"}), out


def hoja_simple(
    df: pd.DataFrame, clave: str, fecha: str, valores: list[str], fecha_fmt=None
) -> pd.DataFrame:
    if df.empty:
        return df
    df = numerico(df, valores)
    if fecha:
        df.insert(
            2,
            "corte",
            pd.to_datetime(df[fecha], dayfirst=fecha_fmt == "dmy").dt.strftime("%Y-%m-%d"),
        )
    return df


def escribir_excel(
    hojas: dict[str, pd.DataFrame],
    indicadores: pd.DataFrame,
    entidades: pd.DataFrame,
    metadatos: pd.DataFrame,
    salida: Path,
) -> None:
    diciembres = sorted({c for c in indicadores["corte"] if c.endswith("-12-31")})[-2:]
    with pd.ExcelWriter(salida, engine="openpyxl") as xw:
        pd.DataFrame().to_excel(xw, sheet_name="Léeme")
        pd.DataFrame().to_excel(xw, sheet_name="Resumen")
        entidades.to_excel(xw, sheet_name="Entidades", index=False)
        indicadores.to_excel(xw, sheet_name="Indicadores", index=False)
        for nombre, df in hojas.items():
            df.to_excel(xw, sheet_name=nombre[:31], index=False)
        metadatos.to_excel(xw, sheet_name="Fuentes", index=False)

    wb = load_workbook(salida)
    encabezado = PatternFill("solid", fgColor=NAVY)
    for ws in wb.worksheets:
        if ws.title in ("Léeme", "Resumen") or ws.max_row < 1:
            continue
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF", name="Arial", size=9)
            c.fill = encabezado
            c.alignment = Alignment(wrap_text=True, vertical="center")
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions
        for i, col in enumerate(ws.iter_cols(min_row=1, max_row=min(ws.max_row, 200)), 1):
            largo = max(len(str(c.value)) if c.value is not None else 0 for c in col)
            ws.column_dimensions[get_column_letter(i)].width = min(max(10, largo + 2), 60)

    # Resumen: fórmulas SUMIFS sobre la hoja Indicadores, una columna por indicador y corte.
    ws = wb["Resumen"]
    n_ind = len(indicadores) + 1
    ws["A1"] = "Resumen por entidad: diciembres comparables"
    ws["A1"].font = Font(bold=True, size=13, name="Arial", color=NAVY)
    ws["A2"] = (
        "Cada celda suma la hoja Indicadores (SUMIFS) para la entidad, el indicador y el corte de su columna."  # noqa: E501
    )
    ws["A3"], ws["A4"] = "Indicador", "Corte"
    ws["A5"] = "Entidad"
    col = 2
    for indicador, unidad in RESUMEN:
        for corte in diciembres:
            letra = get_column_letter(col)
            ws[f"{letra}3"] = indicador
            ws[f"{letra}4"] = corte
            ws[f"{letra}5"] = unidad
            col += 1
    fila_ent = 6
    for ent in entidades["marca"]:
        ws.cell(fila_ent, 1, ent)
        for c in range(2, col):
            letra = get_column_letter(c)
            ws[f"{letra}{fila_ent}"] = (
                f"=SUMIFS(Indicadores!$E$2:$E${n_ind},Indicadores!$A$2:$A${n_ind},$A{fila_ent},"
                f"Indicadores!$D$2:$D${n_ind},{letra}$3,Indicadores!$C$2:$C${n_ind},{letra}$4)"
            )
            ws[f"{letra}{fila_ent}"].number_format = "#,##0"
        fila_ent += 1
    ws.cell(fila_ent, 1, "Total universo").font = Font(bold=True)
    for c in range(2, col):
        letra = get_column_letter(c)
        ws[f"{letra}{fila_ent}"] = f"=SUM({letra}6:{letra}{fila_ent - 1})"
        ws[f"{letra}{fila_ent}"].number_format = "#,##0"
        ws[f"{letra}{fila_ent}"].font = Font(bold=True)
    for r in (3, 4, 5):
        for c in ws[r]:
            c.font = Font(bold=True, color="FFFFFF", name="Arial", size=9)
            c.fill = encabezado
            c.alignment = Alignment(wrap_text=True, vertical="center")
    ws.column_dimensions["A"].width = 22
    for c in range(2, col):
        ws.column_dimensions[get_column_letter(c)].width = 18
    ws.freeze_panes = "B6"

    ws = wb["Léeme"]
    lineas = [
        ("Datos públicos Neobancos – SFC y Fogafín", True),
        (
            f"Extracción: {datetime.now(UTC).date()} (ver hoja Fuentes para el último corte de cada fuente).",  # noqa: E501
            False,
        ),
        ("Universo: asociadas de Colombia Fintech vigiladas por la SFC (hoja Entidades).", False),
        (
            "Todas las cifras vienen de datos.gov.co (SFC y Fogafín); el script scripts/neobancos/ las regenera.",  # noqa: E501
            False,
        ),
        (
            "Unidades: valores en pesos colombianos (COP) salvo que la columna diga otra cosa; las fuentes que "  # noqa: E501
            "publican en miles de COP se convirtieron a COP en la hoja Indicadores.",
            False,
        ),
        (
            "Indicadores: tabla larga con los indicadores clave por entidad y corte; Resumen la consulta con SUMIFS.",  # noqa: E501
            False,
        ),
        (
            "Los clientes se cuentan por entidad y por producto: no se pueden sumar sin duplicar personas.",  # noqa: E501
            False,
        ),
        (
            "Hojas por fuente: copia de cada dataset filtrada al universo (y agregada cuando la fuente trae "  # noqa: E501
            "detalle municipal o semanal).",
            False,
        ),
    ]
    for i, (texto, negrita) in enumerate(lineas, 1):
        ws.cell(i, 1, texto).font = Font(
            bold=negrita, size=13 if negrita else 10, name="Arial", color=NAVY if negrita else None
        )
    ws.column_dimensions["A"].width = 120
    wb.save(salida)


def validar(hojas_crudas: dict[str, pd.DataFrame], entidades: list[dict]) -> dict:
    esperadas = {e["marca"] for e in entidades}
    res = {}
    for clave, df in hojas_crudas.items():
        presentes = set(df["entidad"]) - {""} if "entidad" in df.columns else set()
        res[clave] = {
            "filas": len(df),
            "entidades": len(presentes),
            "faltan": sorted(esperadas - presentes),
        }
    return res


def main(argv: list[str]) -> int:
    salida = Path(argv[argv.index("--salida") + 1]) if "--salida" in argv else XLSX
    entidades = cargar_entidades()
    mapa = {(e["tipo_sfc"], e["codigo_sfc"]): e for e in entidades}
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    crudas = {}
    for f in FUENTES:
        # Las fuentes de alcance "sistema" son de la ampliación para el informe web (etl/);
        # no se consolidan en el Excel ni en los JSON de esta automatización.
        if f.clave == "entidades_sfc" or f.alcance == "sistema":
            continue
        df = leer(f.clave)
        crudas[f.clave] = (
            con_entidad(df, f.campo_tipo, f.campo_codigo, mapa) if not df.empty else df
        )

    # Formato 414: el histórico manda; las semanas que aún no llegan a él salen de "recientes".
    hist, rec = crudas["tasas_colocacion"], crudas.pop("tasas_colocacion_recientes")
    if not rec.empty:
        nuevas = rec[~rec["fecha_corte"].isin(set(hist["fecha_corte"]))] if not hist.empty else rec
        crudas["tasas_colocacion"] = pd.concat([hist, nuevas], ignore_index=True)

    # Quejas: el último mes publicado viene incompleto (la SFC carga el mes siguiente parcial).
    q = crudas["quejas"]
    if not q.empty:
        q["periodo"] = q["a_o_creacion"].astype(int) * 100 + q["mes_creacion"].astype(int)
        por_mes = q.groupby("periodo").size().sort_index()
        if len(por_mes) > 2 and por_mes.iloc[-1] < 0.5 * por_mes.iloc[-4:-1].median():
            q = q[q["periodo"] != por_mes.index[-1]]
        crudas["quejas"] = q.drop(columns="periodo")

    indicadores: list[dict] = []
    hojas: dict[str, pd.DataFrame] = {}
    if not crudas["cuif"].empty:
        hojas["CUIF"], ind = indicadores_cuif(crudas["cuif"])
        indicadores += ind
    if not crudas["captaciones"].empty:
        hojas["Captaciones"], ind = indicadores_captaciones(crudas["captaciones"])
        indicadores += ind
    if not crudas["fogafin_depositantes"].empty and not crudas["fogafin_productos"].empty:
        hojas["Fogafín depositantes"], hojas["Fogafín productos"], ind = indicadores_fogafin(
            crudas["fogafin_depositantes"], crudas["fogafin_productos"]
        )
        indicadores += ind
    if not crudas["tasas_colocacion"].empty:
        hojas["Desembolsos y tasas (414)"], ind = indicadores_colocacion(crudas["tasas_colocacion"])
        indicadores += ind
    simples = [
        ("Inclusión financiera", "inclusion", "fecha_corte", None),
        ("Cartera por producto", "cartera", "fecha_corte", None),
        ("Tasas de captación (441)", "tasas_captacion", "mes", None),
        ("Tarjetas", "tarjetas", "fechacorte", None),
        ("Operaciones por canal", "canales", "fecha_corte", None),
        ("Quejas", "quejas", "", None),
    ]
    for nombre, clave, fecha, fmt in simples:
        df = crudas.get(clave, pd.DataFrame())
        if df.empty:
            continue
        valores = [
            c
            for c in df.columns
            if c not in ("entidad", "tipo")
            and (
                c.startswith("_")
                or c
                in (
                    "monto_total",
                    "tasa_por_monto",
                    "registros",
                    "persona_natural",
                    "persona_juridica",
                    "total_tarjetas",
                    "cantidad_operaciones",
                    "monto_operaciones",
                    "quejas",
                )
            )
        ]
        df = hoja_simple(df, clave, fecha, valores, fmt)
        if clave == "tasas_captacion":
            df["tasa_ponderada_ea"] = df["tasa_por_monto"] / df["monto_total"].where(
                df["monto_total"] > 0
            )
        hojas[nombre] = df

    ind = (
        pd.DataFrame(indicadores)
        .sort_values(["entidad", "indicador", "corte"])
        .reset_index(drop=True)
    )
    ind = ind[["entidad", "tipo", "corte", "indicador", "valor", "unidad", "fuente", "dataset"]]

    registro_path = RAW_DIR / "_extraccion.json"
    registro = (
        json.loads(registro_path.read_text(encoding="utf-8")) if registro_path.exists() else {}
    )
    r414 = DATA_DIR / "raw414" / "_extraccion.json"
    if r414.exists():
        registro.update(json.loads(r414.read_text(encoding="utf-8")))
    metadatos = pd.DataFrame(
        [
            {
                "clave": f.clave,
                "dataset": f.id,
                "nombre": f.nombre,
                "publicador": f.publicador,
                "url": f"https://www.datos.gov.co/d/{f.id}",
                "api": f"https://www.datos.gov.co/resource/{f.id}.json",
                "frecuencia": f.frecuencia,
                "unidad": f.unidad,
                "modo": f.modo,
                "filas_extraidas": registro.get(f.clave, {}).get("filas"),
                "ultimo_corte": registro.get(f.clave, {}).get("ultimo_corte"),
                "extraido": registro.get(f.clave, {}).get("extraido"),
                "nota": f.nota,
            }
            for f in FUENTES
        ]
    )
    ent_df = pd.DataFrame(entidades).drop(columns="incluir")

    escribir_excel(hojas, ind, ent_df, metadatos, salida)

    ind.to_csv(WEB_DIR / "indicadores.csv", index=False, encoding="utf-8")
    (WEB_DIR / "indicadores.json").write_text(
        ind.to_json(orient="records", force_ascii=False), encoding="utf-8"
    )
    resumen = {}
    for (ent, indic), g in ind.groupby(["entidad", "indicador"]):
        g = g.sort_values("corte")
        dic = g[g["corte"].str.endswith("-12-31")]
        resumen.setdefault(ent, {})[indic] = {
            "ultimo": {"corte": g.iloc[-1]["corte"], "valor": g.iloc[-1]["valor"]},
            "diciembres": dict(zip(dic["corte"].str[:4], dic["valor"], strict=True)),
            "unidad": g.iloc[-1]["unidad"],
        }
    (WEB_DIR / "resumen.json").write_text(
        json.dumps(resumen, ensure_ascii=False, default=float), encoding="utf-8"
    )
    (WEB_DIR / "metadatos.json").write_text(
        json.dumps(
            {
                "generado": datetime.now(UTC).isoformat(timespec="seconds"),
                "fuentes": metadatos.to_dict(orient="records"),
                "entidades": ent_df.to_dict(orient="records"),
            },
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )
    val = validar(crudas, entidades)
    (WEB_DIR / "validacion.json").write_text(
        json.dumps(val, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    print(f"Excel: {salida}")
    for nombre, df in hojas.items():
        print(f"  {nombre}: {len(df):,} filas")
    print(f"  Indicadores: {len(ind):,} filas")
    for clave, v in val.items():
        print(
            f"  [{clave}] {v['filas']:,} filas, {v['entidades']} entidades; sin datos: {', '.join(v['faltan']) or '-'}"  # noqa: E501
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
