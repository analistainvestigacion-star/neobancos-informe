"""Herramientas para revisar los párrafos de análisis (sin API de pago).

Los párrafos se redactan desde Claude Code con el skill /actualizar-textos-neobancos.
Este módulo le da las cifras actuales y valida que los textos cumplan las reglas.

Uso:
  python -m etl.textos cifras    -> data/processed/cifras_textos.csv y lista de bloques
  python -m etl.textos validar   -> revisa todos los bloques; sale con código 1 si hay errores

Marcadores disponibles en los textos (ent = id de entidad, grupo_banco, grupo_cf, grupo_sedpe,
universo o comparador sis_ec/sis_bancos/sis_cf/sis_sedpe; corte = informe | base | ultimo):
  {{v:indicador:ent:corte:formato}}      valor (formato: billones, milm, millones, miles, pct, tasa, entero)
  {{crec:indicador:ent}}                 variación corte del informe vs. corte base (saldos)
  {{anual:indicador:ent:informe:formato}} suma del año del informe (flujos; n.d. si faltan meses)
  {{crec_anual:indicador:ent}}           variación anual de un flujo
  {{part:indicador:ent:comparador:corte}} participación de ent en el comparador
  {{ratio:numerador:denominador:ent:corte}} cociente en porcentaje
  {{verbo:indicador:ent}}                "creció" o "se redujo"
  {{lider:indicador:corte}}              entidad con el mayor valor
  {{n_ent:indicador:corte}}              número de entidades con dato
  {{conc:indicador:corte:n}}             participación de las n entidades más grandes en el universo
  {{rank:indicador:ent:corte}}           posición de la entidad en el universo
  {{crec_rel:indicador:ent:comparador}}  diferencia de crecimiento en puntos porcentuales
  {{veces:indicador:ent:comparador}}     cuántas veces creció ent frente al comparador
  {{mas_crec:indicador}}                 entidad con mayor crecimiento anual
  {{nombre:ent}} {{corte}} {{base}} {{anio}} {{fecha:indicador}} {{csv}}
"""
from __future__ import annotations

import re
import sys

import pandas as pd

from .extract import RAIZ
from .transform import PROC, Universo

SECCIONES = RAIZ / "content" / "secciones"
BLOQUE = re.compile(r"(<!-- analisis:(?P<id>[\w-]+) -->\n)(?P<texto>.*?)(\n<!-- /analisis -->)", re.S)
MARCADOR = re.compile(r"\{\{([^}]+)\}\}")
OPS = {"v", "crec", "crec_anual", "anual", "part", "ratio", "verbo", "fecha", "nombre", "corte", "base", "anio",
       "lider", "n_ent", "csv", "conc", "rank", "crec_rel", "veces", "mas_crec"}
PALABRAS_OK = {"informe", "base", "ultimo", "anual", "billones", "milm", "millones", "miles", "pct", "tasa",
               "entero", "pp", "dec"}


def leer_bloques() -> dict[str, dict]:
    out = {}
    for f in sorted(SECCIONES.glob("*.md")):
        for m in BLOQUE.finditer(f.read_text(encoding="utf-8")):
            out[m["id"]] = {"archivo": f.name, "texto": m["texto"]}
    return out


def tabla_cifras(u: Universo) -> pd.DataFrame:
    """Valor de cada indicador por entidad al corte del informe, al corte base y en el último dato."""
    df = pd.read_parquet(PROC / "indicadores.parquet")
    cortes = {"informe": u.inf["corte_informe"], "base": u.inf["corte_base"]}
    filas = []
    for ind, g in df.groupby("indicador"):
        ultimo = g["fecha"].max()
        for ent, h in g.groupby("entidad"):
            s = h.set_index("fecha")["valor"]
            filas.append({"indicador": ind, "entidad": ent,
                          "informe": s.get(cortes["informe"]), "base": s.get(cortes["base"]),
                          "ultimo": s.get(ultimo), "fecha_ultimo": ultimo})
    return pd.DataFrame(filas)


def validar_texto(texto: str, indicadores: set[str], entidades: set[str]) -> list[str]:
    errores = []
    # Se permiten años de hechos pasados y números de normas (no cambian con los datos).
    estatico = re.sub(r"\b(Ley|Decreto|Circular Externa|Resolución)\s+\d+\s+de\s+\d{4}\b", "", MARCADOR.sub("", texto))
    estatico = re.sub(r"\b(19|20)\d{2}\b", "", estatico)
    estatico = re.sub(r"(?m)^\s*\d+\.\s", "", estatico)  # numeración de listas
    if re.search(r"\d", estatico):
        errores.append("contiene cifras literales (deben ir como marcadores)")
    if re.search(r"\b(nuestr[oa]s?|observamos|encontramos|leímos|creemos)\b", texto, re.I):
        errores.append("usa primera persona")
    if re.search(r"plan nacional de desarrollo|\bPND\b", texto, re.I):
        errores.append("menciona el PND")
    for expr in MARCADOR.findall(texto):
        p = expr.split(":")
        if p[0] not in OPS:
            errores.append(f"marcador desconocido {{{{{expr}}}}}")
            continue
        for x in p[1:]:
            if x in indicadores or x in entidades or x in PALABRAS_OK or re.fullmatch(r"\d{4}(-\d{2})?|\d{1,2}", x):
                continue
            errores.append(f"referencia inexistente '{x}' en {{{{{expr}}}}}")
    return errores


def main(argv: list[str]) -> int:
    cmd = argv[0] if argv else ""
    u = Universo()
    df = pd.read_parquet(PROC / "indicadores.parquet", columns=["indicador", "entidad"])
    indicadores, entidades = set(df["indicador"]), set(df["entidad"])
    if cmd == "cifras":
        t = tabla_cifras(u)
        ruta = PROC / "cifras_textos.csv"
        t.to_csv(ruta, index=False, encoding="utf-8")
        print(f"Cifras: {ruta} ({len(t)} filas). Corte del informe {u.inf['corte_informe']}, base {u.inf['corte_base']}.")
        for k, v in leer_bloques().items():
            print(f"- {k} ({v['archivo']})")
        return 0
    if cmd == "validar":
        malos = 0
        for k, v in leer_bloques().items():
            errores = validar_texto(v["texto"], indicadores, entidades)
            if errores:
                malos += 1
                print(f"✗ {k} ({v['archivo']}): {'; '.join(errores)}")
        print("Textos OK" if not malos else f"{malos} bloque(s) con errores")
        return 1 if malos else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
