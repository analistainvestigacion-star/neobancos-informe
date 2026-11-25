"""Descarga de datos.gov.co las fuentes públicas del informe de Neobancos.

Guarda una copia cruda por fuente en data/neobancos/raw/<clave>.csv y un registro de la
extracción en data/neobancos/raw/_extraccion.json (fecha, filas, último corte, errores).

Uso:
    uv run python -m scripts.neobancos.extraer                  # todas las fuentes
    uv run python -m scripts.neobancos.extraer cuif captaciones # solo algunas
    uv run python -m scripts.neobancos.extraer --desde 2024-01-01 tasas_colocacion

Variables de entorno opcionales:
    SOCRATA_APP_TOKEN   token de aplicación de datos.gov.co (sube el límite de consultas)
    NEOBANCOS_HILOS     consultas en paralelo para el modo por_fecha (por defecto 6)
"""

from __future__ import annotations

import concurrent.futures as cf
import http.client
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime

import pandas as pd

from .fuentes import (
    API,
    FUENTES,
    FUENTES_POR_CLAVE,
    PAGINA,
    RAW_DIR,
    Fuente,
    cargar_entidades,
    filtro_entidades,
)

TIMEOUT = 600
REINTENTOS = 4


def consultar(fuente: Fuente, params: dict[str, str]) -> list[dict]:
    url = API.format(id=fuente.id) + "?" + urllib.parse.urlencode(params)
    headers = {"Accept": "application/json"}
    if token := os.environ.get("SOCRATA_APP_TOKEN"):
        headers["X-App-Token"] = token
    for intento in range(1, REINTENTOS + 1):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.load(resp)
        except (urllib.error.URLError, http.client.HTTPException, OSError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 400:
                raise RuntimeError(
                    f"{fuente.clave}: consulta inválida: {exc.read()[:300]!r}"
                ) from exc
            if intento == REINTENTOS:
                raise RuntimeError(f"{fuente.clave}: {exc}") from exc
            time.sleep(10 * intento)
    return []


def paginar(
    fuente: Fuente, where: str, select: str, group: str = "", orden: str = ""
) -> list[dict]:
    filas: list[dict] = []
    offset = 0
    while True:
        params = {"$select": select, "$where": where, "$limit": str(PAGINA), "$offset": str(offset)}
        if group:
            params["$group"] = group
        if orden or group:
            params["$order"] = orden or group
        lote = consultar(fuente, params)
        filas.extend(lote)
        if len(lote) < PAGINA:
            return filas
        offset += PAGINA


def fechas_disponibles(fuente: Fuente, where: str) -> list[str]:
    params = {
        "$select": f"distinct {fuente.campo_fecha}",
        "$where": where,
        "$order": fuente.campo_fecha,
        "$limit": "10000",
    }
    return [r[fuente.campo_fecha] for r in consultar(fuente, params) if fuente.campo_fecha in r]


def extraer_por_fecha(fuente: Fuente, where: str, desde: str | None) -> pd.DataFrame:
    """Un corte por consulta, guardando cada uno en raw/_cortes/<clave>/ apenas llega.

    Si una corrida se cae, la siguiente solo pide los cortes que faltan. Los cortes que
    fallan se reportan al final; con alguno pendiente la fuente queda en error para que el
    workflow lo note, pero lo descargado no se pierde.
    """
    # Las fechas se listan sin filtro de entidad (mucho más rápido).
    base = f"{fuente.campo_fecha} >= '{desde}T00:00:00'" if desde else "1=1"
    fechas = fechas_disponibles(fuente, base)
    cache = RAW_DIR / "_cortes" / fuente.clave
    cache.mkdir(parents=True, exist_ok=True)

    def archivo(fecha: str):
        return cache / f"{fecha[:10]}.csv"

    pendientes = [f for f in fechas if not archivo(f).exists()]
    print(f"    {fuente.clave}: {len(fechas)} cortes, {len(pendientes)} por descargar", flush=True)

    def bajar(fecha: str) -> None:
        filas = paginar(
            fuente, f"{where} AND {fuente.campo_fecha}='{fecha}'", fuente.select, fuente.group
        )
        tmp = archivo(fecha).with_suffix(".tmp")
        pd.DataFrame(filas).to_csv(tmp, index=False, encoding="utf-8")
        tmp.replace(archivo(fecha))

    fallidos = []
    hilos = int(os.environ.get("NEOBANCOS_HILOS", "6"))
    with cf.ThreadPoolExecutor(hilos) as ex:
        futuros = {ex.submit(bajar, f): f for f in pendientes}
        for i, fut in enumerate(cf.as_completed(futuros), 1):
            if fut.exception():
                fallidos.append(futuros[fut])
            if i % 10 == 0 or i == len(pendientes):
                print(
                    f"    {fuente.clave}: {i}/{len(pendientes)} (fallidos {len(fallidos)})",
                    flush=True,
                )

    partes = [
        pd.read_csv(archivo(f), dtype=str, keep_default_na=False)
        for f in fechas
        if archivo(f).exists() and archivo(f).stat().st_size > 1
    ]
    if fallidos:
        muestra = ", ".join(sorted(fallidos)[:5])
        raise RuntimeError(
            f"{fuente.clave}: {len(fallidos)} cortes sin descargar ({muestra}...); "
            "vuelva a correr para completarlos"
        )
    return pd.concat(partes, ignore_index=True) if partes else pd.DataFrame()


def extraer_fuente(
    fuente: Fuente, entidades: list[dict[str, str]], desde: str | None
) -> pd.DataFrame:
    if fuente.clave == "entidades_sfc":
        where = filtro_entidades(fuente, entidades)
        return pd.DataFrame(paginar(fuente, where, fuente.select, orden="tipo_entidad,cod_entidad"))

    where = filtro_entidades(fuente, entidades)
    if fuente.filtro:
        where += f" AND {fuente.filtro}"
    if desde and fuente.campo_fecha in ("fecha_corte", "fechacorte"):
        where += f" AND {fuente.campo_fecha} >= '{desde}T00:00:00'"

    if fuente.modo == "por_fecha":
        return extraer_por_fecha(fuente, where, desde)

    if fuente.modo == "agregado":
        return pd.DataFrame(paginar(fuente, where, fuente.select, fuente.group))

    return pd.DataFrame(paginar(fuente, where, fuente.select, orden=fuente.orden))


def ultimo_corte(df: pd.DataFrame, fuente: Fuente) -> str:
    for col in (fuente.campo_fecha, "mes", "fecha_corte", "fechacorte"):
        if col and col in df.columns and not df.empty:
            if col == "fecha_de_corte" and fuente.clave == "fogafin_depositantes":
                return str(pd.to_datetime(df[col], dayfirst=True).max().date())
            if col == "a_o_creacion":
                ultimo = df.assign(a=df[col].astype(int), m=df["mes_creacion"].astype(int))
                fila = ultimo.sort_values(["a", "m"]).iloc[-1]
                return f"{fila.a}-{fila.m:02d}"
            return str(pd.to_datetime(df[col]).max().date())
    return ""


def main(argv: list[str]) -> int:
    desde = None
    if "--desde" in argv:
        i = argv.index("--desde")
        desde = argv[i + 1]
        argv = argv[:i] + argv[i + 2 :]
    claves = argv or [f.clave for f in FUENTES]
    entidades = cargar_entidades()
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    registro_path = RAW_DIR / "_extraccion.json"
    registro = (
        json.loads(registro_path.read_text(encoding="utf-8")) if registro_path.exists() else {}
    )

    errores = 0
    for clave in claves:
        fuente = FUENTES_POR_CLAVE[clave]
        inicio = time.time()
        print(f"[{clave}] {fuente.id} ...", flush=True)
        try:
            df = extraer_fuente(fuente, entidades, desde)
        except Exception as exc:  # noqa: BLE001  (se registra y se sigue con las demás)
            errores += 1
            print(f"  ERROR {exc}", flush=True)
            registro[clave] = {
                **registro.get(clave, {}),
                "error": str(exc),
                "intento": datetime.now(UTC).isoformat(timespec="seconds"),
            }
            continue
        destino = RAW_DIR / f"{clave}.csv"
        if desde and destino.exists() and fuente.campo_fecha in df.columns:
            # Extracción incremental: se conserva lo ya descargado antes de --desde.
            previo = pd.read_csv(destino, dtype=str, keep_default_na=False)
            previo = previo[pd.to_datetime(previo[fuente.campo_fecha]) < pd.Timestamp(desde)]
            df = pd.concat([previo, df.astype(str)], ignore_index=True)
        df.to_csv(destino, index=False, encoding="utf-8")
        registro[clave] = {
            "dataset": fuente.id,
            "filas": len(df),
            "ultimo_corte": ultimo_corte(df, fuente),
            "extraido": datetime.now(UTC).isoformat(timespec="seconds"),
            "segundos": round(time.time() - inicio, 1),
            "desde": desde,
        }
        print(
            f"  {len(df):,} filas, último corte {registro[clave]['ultimo_corte']}, "
            f"{registro[clave]['segundos']} s",
            flush=True,
        )
        registro_path.write_text(
            json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8"
        )
    registro_path.write_text(json.dumps(registro, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
