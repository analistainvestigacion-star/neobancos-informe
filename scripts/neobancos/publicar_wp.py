"""Publica en colombiafintech.co (WordPress) los archivos de data/neobancos/web/.

Sube cada JSON a la biblioteca de Medios por la API REST de WordPress. Si ya existe un archivo
con el mismo nombre lo reemplaza (lo borra y lo vuelve a subir) para que la URL pública no
cambie de nombre. La página del informe lee esas URLs con JavaScript.

Variables de entorno (en GitHub Actions van como secretos):
    WP_URL           https://colombiafintech.co
    WP_USER          usuario de WordPress con permiso para subir medios
    WP_APP_PASSWORD  contraseña de aplicación de ese usuario
                     (Usuarios > Perfil > Contraseñas de aplicación)

Uso:
    uv run python -m scripts.neobancos.publicar_wp            # publica
    uv run python -m scripts.neobancos.publicar_wp --prueba   # solo muestra qué subiría
"""

from __future__ import annotations

import base64
import json
import os
import sys
import urllib.parse
import urllib.request

from .fuentes import WEB_DIR

ARCHIVOS = ["indicadores.json", "resumen.json", "metadatos.json"]
PREFIJO = "neobancos-"


def _peticion(
    metodo: str, url: str, datos: bytes | None = None, extra: dict | None = None
) -> dict | list:
    credencial = base64.b64encode(
        f"{os.environ['WP_USER']}:{os.environ['WP_APP_PASSWORD']}".encode()
    ).decode()
    headers = {"Authorization": f"Basic {credencial}", **(extra or {})}
    req = urllib.request.Request(url, data=datos, method=metodo, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        cuerpo = resp.read()
    return json.loads(cuerpo) if cuerpo else {}


def publicar(prueba: bool = False) -> int:
    base = os.environ.get("WP_URL", "").rstrip("/")
    if not prueba and not (
        base and os.environ.get("WP_USER") and os.environ.get("WP_APP_PASSWORD")
    ):
        print("Faltan WP_URL, WP_USER o WP_APP_PASSWORD.")
        return 1
    api = f"{base}/wp-json/wp/v2/media"
    for nombre in ARCHIVOS:
        ruta = WEB_DIR / nombre
        if not ruta.exists():
            print(f"No existe {ruta}; corra antes consolidar.py")
            return 1
        destino = PREFIJO + nombre
        if prueba:
            print(f"Subiría {ruta} como {destino} ({ruta.stat().st_size:,} bytes)")
            continue
        existentes = _peticion(
            "GET", f"{api}?search={urllib.parse.quote(destino.rsplit('.', 1)[0])}&per_page=20"
        )
        for m in existentes:
            if m.get("source_url", "").endswith("/" + destino):
                _peticion("DELETE", f"{api}/{m['id']}?force=true")
        subido = _peticion(
            "POST",
            api,
            ruta.read_bytes(),
            {
                "Content-Type": "application/json",
                "Content-Disposition": f'attachment; filename="{destino}"',
            },
        )
        print(f"{destino}: {subido.get('source_url')}")
    return 0


if __name__ == "__main__":
    sys.exit(publicar("--prueba" in sys.argv))
