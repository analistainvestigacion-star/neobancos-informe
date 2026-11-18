"""Cliente mínimo para la API Socrata de datos.gov.co (sin token)."""
from __future__ import annotations

import os
import time
from datetime import datetime, timezone

import pandas as pd
import requests

BASE = "https://www.datos.gov.co"
SESSION = requests.Session()
SESSION.headers["User-Agent"] = "neobancos-informe/1.0"
if os.environ.get("SOCRATA_APP_TOKEN"):
    SESSION.headers["X-App-Token"] = os.environ["SOCRATA_APP_TOKEN"]

PAGE = 50_000


def _get(url: str, params: dict, timeout: int = 600, retries: int = 6):
    for intento in range(retries):
        try:
            r = SESSION.get(url, params=params, timeout=timeout)
            if r.status_code in (429, 500, 502, 503, 504):
                raise requests.HTTPError(f"{r.status_code}: {r.text[:200]}")
            if r.status_code >= 400:  # error de la consulta: no se reintenta
                raise ValueError(f"{r.status_code}: {r.text[:300]} | params={params}")
            r.raise_for_status()
            return r.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            if intento == retries - 1:
                raise
            espera = 30 * (intento + 1)  # datos.gov.co se satura: esperas crecientes
            print(f"  reintento {intento + 1} en {espera}s ({e})")
            time.sleep(espera)


def query(dataset: str, **soql) -> pd.DataFrame:
    """Ejecuta una consulta SoQL con paginación. soql: select, where, group, order, limit."""
    params = {f"${k}": v for k, v in soql.items() if v is not None}
    if "$limit" in params:
        return pd.DataFrame(_get(f"{BASE}/resource/{dataset}.json", params))
    params.setdefault("$order", ":id" if "$group" not in params and "$select" not in params else None)
    if params["$order"] is None:
        del params["$order"]
    filas, offset = [], 0
    while True:
        params.update({"$limit": PAGE, "$offset": offset})
        lote = _get(f"{BASE}/resource/{dataset}.json", params)
        filas.extend(lote)
        if len(lote) < PAGE:
            break
        offset += PAGE
    return pd.DataFrame(filas)


_TIPOS: dict[str, dict[str, str]] = {}


def tipos_columnas(dataset: str) -> dict[str, str]:
    if dataset not in _TIPOS:
        m = _get(f"{BASE}/api/views/{dataset}.json", {}, timeout=60)
        _TIPOS[dataset] = {c["fieldName"]: c["dataTypeName"] for c in m["columns"]}
    return _TIPOS[dataset]


def lit(dataset: str, campo: str, valor) -> str:
    """Literal SoQL según el tipo de la columna (número sin comillas, texto con comillas)."""
    return str(valor) if tipos_columnas(dataset).get(campo) == "number" else f"'{valor}'"


def metadata(dataset: str) -> dict:
    m = _get(f"{BASE}/api/views/{dataset}.json", {}, timeout=60)
    return {
        "id": dataset,
        "nombre": m.get("name"),
        "rows_updated_at": datetime.fromtimestamp(m.get("rowsUpdatedAt", 0), tz=timezone.utc).isoformat(),
    }
