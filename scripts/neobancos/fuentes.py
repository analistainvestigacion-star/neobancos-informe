"""Definición de las fuentes públicas del informe de Neobancos (datos.gov.co, API Socrata).

Cada fuente dice en qué campos están el tipo de entidad, el código de entidad y la fecha,
qué columnas traer y cómo se consulta:
- "filas": trae las filas tal cual, paginadas.
- "agregado": la API agrupa y suma antes de entregar (para datasets con detalle municipal).
- "por_fecha": una consulta agregada por cada fecha de corte (datasets muy pesados).

Para agregar una fuente basta con una entrada nueva en FUENTES; extraer.py y consolidar.py
la recorren completa.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data" / "neobancos"
RAW_DIR = DATA_DIR / "raw"
WEB_DIR = DATA_DIR / "web"
ENTIDADES_CSV = Path(__file__).with_name("entidades.csv")

API = "https://www.datos.gov.co/resource/{id}.json"
PAGINA = 50_000


@dataclass(frozen=True)
class Fuente:
    clave: str
    id: str
    nombre: str
    publicador: str
    campo_tipo: str
    campo_codigo: str
    campo_fecha: str
    modo: str = "filas"
    select: str = "*"
    group: str = ""
    filtro: str = ""
    orden: str = ""
    frecuencia: str = ""
    unidad: str = ""
    nota: str = ""
    columnas_valor: list[str] = field(default_factory=list)


FUENTES: list[Fuente] = [
    Fuente(
        clave="cuif",
        id="mxk5-ce6w",
        nombre="Información financiera con fines de supervisión (CUIF) por moneda",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="fecha_corte",
        select="tipo_entidad,codigo_entidad,fecha_corte,cuenta,nombre_cuenta,valor",
        filtro="moneda='0' AND (cuenta in ('100000','200000','300000','590000') "
        "OR starts_with(cuenta,'14') OR starts_with(cuenta,'21'))",
        orden="fecha_corte,tipo_entidad,codigo_entidad,cuenta",
        frecuencia="Mensual",
        unidad="COP",
        nota="moneda = 0 (total). Se traen activo, pasivo, patrimonio, resultado del ejercicio, "
        "cartera (14) y pasivos de captación (21); en la consolidación se dejan las cuentas "
        "de 4 dígitos (terminadas en 00).",
        columnas_valor=["valor"],
    ),
    Fuente(
        clave="captaciones",
        id="p22c-4r9c",
        nombre="Captaciones por rangos",
        publicador="SFC",
        campo_tipo="tipoentidad",
        campo_codigo="codigoentidad",
        campo_fecha="fechacorte",
        orden="fechacorte,tipoentidad,codigoentidad,unidad_de_captura,subcuenta",
        frecuencia="Mensual",
        unidad="Número y miles de COP",
        nota="Los *_valor_total vienen en miles de COP. subcuenta 999 = total de cada unidad de captura.",  # noqa: E501
        columnas_valor=[
            "cta_cte_nro_clientes",
            "cta_cte_nro_cuentas",
            "cta_cte_valor_total",
            "depositos_ahorro_nro_clientes",
            "depositos_ahorro_nro_cuentas",
            "depositos_ahorro_valor_total",
            "cdts_nro_clientes",
            "cdts_nro_cuentas",
            "cdts_valor_total",
            "cdats_nro_clientes",
            "cdats_nro_cuentas",
            "cdats_valor_total",
            "bonos_nro_clientes",
            "bonos_nro_cuentas",
            "bonos_valor_total",
            "depositos_numero_clientes",
            "depositos_numero_cuenta",
            "depositos_valor_total",
        ],
    ),
    Fuente(
        clave="fogafin_productos",
        id="frdr-biuv",
        nombre="Saldos por producto de depósito y entidad inscrita",
        publicador="Fogafín",
        campo_tipo="codigo_tipo_entidad_sfc",
        campo_codigo="codigo_entidad_sfc",
        campo_fecha="fecha_de_corte",
        orden="fecha_de_corte,codigo_tipo_entidad_sfc,codigo_entidad_sfc",
        frecuencia="Trimestral (cortes de enero, abril, julio y octubre)",
        unidad="Número y miles de COP",
        nota="No hay corte de diciembre.",
        columnas_valor=["numero_de_productos", "saldo_depositos"],
    ),
    Fuente(
        clave="fogafin_depositantes",
        id="uhdk-a4i6",
        nombre="Saldos de depósitos y depositantes por entidad inscrita",
        publicador="Fogafín",
        campo_tipo="codigo_tipo_entidad_sfc",
        campo_codigo="codigo_entidad_sfc",
        campo_fecha="fecha_de_corte",
        orden="ano,fecha_de_corte,codigo_tipo_entidad_sfc,codigo_entidad_sfc",
        frecuencia="Trimestral (cortes de enero, abril, julio y octubre)",
        unidad="Número y miles de COP",
        nota="fecha_de_corte viene como texto dd/mm/aaaa.",
        columnas_valor=["numero_total_de_clientes", "saldo_depositos"],
    ),
    Fuente(
        clave="inclusion",
        id="kx2f-xjdq",
        nombre="Inclusión financiera",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="fecha_corte",
        filtro="unicap in ('34','35','36','37','38','39','40','41','42','43','44','45')",
        orden="fecha_corte,tipo_entidad,codigo_entidad,unicap,renglon",
        frecuencia="Trimestral",
        unidad="Número y COP",
        nota="Solo las unidades de captura nacionales (34 total nacional y 35 en adelante: "
        "depósitos ordinarios, de bajo monto, cuentas de ahorro, corresponsales). Las "
        "unidades 1 a 33 son departamentos y no se suman con estas.",
    ),
    Fuente(
        clave="cartera",
        id="rvii-eis8",
        nombre="Distribución de cartera por producto",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="fecha_corte",
        orden="fecha_corte,tipo_entidad,codigo_entidad,unicap,renglon",
        frecuencia="Mensual",
        unidad="COP y número",
    ),
    Fuente(
        clave="tasas_colocacion",
        id="w9zh-vetq",
        nombre="Tasas de interés activas por tipo de crédito (formato 414), histórico",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="fecha_corte",
        modo="por_fecha",
        select="tipo_entidad,codigo_entidad,fecha_corte,tipo_de_cr_dito,producto_de_cr_dito,"
        "tipo_de_persona,sexo,sum(montos_desembolsados) as monto_desembolsado,"
        "sum(numero_de_creditos) as numero_de_creditos,"
        "sum(tasa_efectiva_promedio * montos_desembolsados) as tasa_por_monto",
        group="tipo_entidad,codigo_entidad,fecha_corte,tipo_de_cr_dito,producto_de_cr_dito,"
        "tipo_de_persona,sexo",
        frecuencia="Semanal",
        unidad="COP, número y % EA",
        nota="Dataset muy pesado: se consulta una fecha de corte a la vez, agregado del lado del "
        "servidor. Tasa ponderada = tasa_por_monto / monto_desembolsado.",
    ),
    Fuente(
        clave="tasas_colocacion_recientes",
        id="qzsc-9esp",
        nombre="Tasas de interés activas por tipo de crédito (formato 414), últimos dos meses",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="fecha_corte",
        modo="por_fecha",
        select="tipo_entidad,codigo_entidad,fecha_corte,tipo_de_cr_dito,producto_de_cr_dito,"
        "tipo_de_persona,sexo,sum(montos_desembolsados) as monto_desembolsado,"
        "sum(numero_de_creditos) as numero_de_creditos,"
        "sum(tasa_efectiva_promedio * montos_desembolsados) as tasa_por_monto",
        group="tipo_entidad,codigo_entidad,fecha_corte,tipo_de_cr_dito,producto_de_cr_dito,"
        "tipo_de_persona,sexo",
        frecuencia="Semanal",
        unidad="COP, número y % EA",
        nota="El histórico (w9zh-vetq) llega hasta dos meses antes del corte actual; las semanas "
        "recientes solo están aquí. La consolidación une ambos y prefiere el histórico.",
    ),
    Fuente(
        clave="tasas_captacion",
        id="axk9-g2nh",
        nombre="Tasas de interés de captación y operaciones del mercado monetario (formato 441)",
        publicador="SFC",
        campo_tipo="tipoentidad",
        campo_codigo="codigoentidad",
        campo_fecha="fechacorte",
        modo="agregado",
        # Los alias no pueden repetir el nombre de una columna (la API responde 400).
        select="tipoentidad,codigoentidad,date_trunc_ym(fechacorte) as mes,uca,"
        "nombre_unidad_de_captura,subcuenta,descripcion,sum(monto) as monto_total,"
        "sum(tasa * monto) as tasa_por_monto,count(*) as registros",
        group="tipoentidad,codigoentidad,date_trunc_ym(fechacorte),uca,nombre_unidad_de_captura,"
        "subcuenta,descripcion",
        frecuencia="Diaria (se agrega por mes)",
        unidad="COP y % EA",
        nota="Se agrega por mes. Tasa ponderada = tasa_por_monto / monto_total.",
    ),
    Fuente(
        clave="tarjetas",
        id="h2jg-r3zg",
        nombre="Tarjetas de crédito y débito",
        publicador="SFC",
        campo_tipo="tipoentidad",
        campo_codigo="codigoentidad",
        campo_fecha="fechacorte",
        orden="fechacorte,tipoentidad,codigoentidad,cod_uca,subcuenta",
        frecuencia="Mensual",
        unidad="Número",
        columnas_valor=["persona_natural", "persona_juridica", "total_tarjetas"],
    ),
    Fuente(
        clave="canales",
        id="bzdm-fkaz",
        nombre="Operaciones efectuadas a través de los canales de distribución o servicios transaccionales",  # noqa: E501
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="fecha_corte",
        modo="agregado",
        select="tipo_entidad,codigo_entidad,fecha_corte,unidad_captura,nombre_unidad_captura,"
        "codigo_canal_distribucion,codigo_serrvicio_transaccional,"
        "sum(cantidad_operaciones) as cantidad_operaciones,sum(monto_operaciones) as monto_operaciones",  # noqa: E501
        group="tipo_entidad,codigo_entidad,fecha_corte,unidad_captura,nombre_unidad_captura,"
        "codigo_canal_distribucion,codigo_serrvicio_transaccional",
        frecuencia="Mensual",
        unidad="Número y COP",
        nota="Se agrega sin municipio, CIIU, operación ni tipo de persona. Los códigos de canal y "
        "servicio se interpretan con la guía de reporte de la SFC.",
    ),
    Fuente(
        clave="quejas",
        id="xyy7-rn7p",
        nombre="Quejas en Smartsupervision",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="codigo_entidad",
        campo_fecha="a_o_creacion",
        modo="agregado",
        select="tipo_entidad,codigo_entidad,a_o_creacion,mes_creacion,producto,motivo,"
        "sum(cantidad_quejas_recibidas) as quejas",
        group="tipo_entidad,codigo_entidad,a_o_creacion,mes_creacion,producto,motivo",
        frecuencia="Mensual",
        unidad="Número",
        nota="Se agrega sin departamento, municipio ni instancia de recepción.",
    ),
    Fuente(
        clave="entidades_sfc",
        id="sr9n-792w",
        nombre="Entidades vigiladas por la Superfinanciera",
        publicador="SFC",
        campo_tipo="tipo_entidad",
        campo_codigo="cod_entidad",
        campo_fecha="",
        select="tipo_entidad,cod_entidad,razon_social,numeroidentificacion,ciudad,uripaginaweb",
        frecuencia="Continua",
        unidad="Texto",
    ),
]

FUENTES_POR_CLAVE = {f.clave: f for f in FUENTES}


def cargar_entidades() -> list[dict[str, str]]:
    with ENTIDADES_CSV.open(encoding="utf-8") as fh:
        return [row for row in csv.DictReader(fh) if row["incluir"].strip().lower() == "si"]


def filtro_entidades(fuente: Fuente, entidades: list[dict[str, str]]) -> str:
    """Condición SoQL que deja solo las entidades del universo, agrupadas por tipo."""
    por_tipo: dict[str, list[str]] = {}
    for e in entidades:
        por_tipo.setdefault(e["tipo_sfc"], []).append(e["codigo_sfc"])
    partes = [
        f"({fuente.campo_tipo}='{t}' AND {fuente.campo_codigo} in ("
        + ",".join(f"'{c}'" for c in codigos)
        + "))"
        for t, codigos in sorted(por_tipo.items())
    ]
    return "(" + " OR ".join(partes) + ")"
