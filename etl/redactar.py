"""Borrador de los párrafos de análisis con la API de Claude.

Lee los bloques <!-- analisis:id --> ... <!-- /analisis --> de content/secciones/*.md,
le da a Claude las cifras actuales y le pide reescribir cada bloque usando SOLO marcadores
{{...}} para las cifras (así siguen actualizándose solas). El resultado se escribe en los
mismos archivos y el workflow abre un PR para revisión humana: nada se publica sin aprobación.

Uso: python -m etl.redactar      (requiere ANTHROPIC_API_KEY)
"""
from __future__ import annotations

import json
import re
import sys

import anthropic
import pandas as pd

from .extract import RAIZ
from .transform import PROC, Universo

SECCIONES = RAIZ / "content" / "secciones"
BLOQUE = re.compile(r"(<!-- analisis:(?P<id>[\w-]+) -->\n)(?P<texto>.*?)(\n<!-- /analisis -->)", re.S)
MARCADOR = re.compile(r"\{\{([^}]+)\}\}")
OPS = {"v", "crec", "crec_anual", "anual", "part", "ratio", "verbo", "fecha", "nombre", "corte", "base", "anio",
       "lider", "n_ent", "csv"}

SISTEMA = """Eres analista de Colombia Fintech y redactas los párrafos de análisis de un informe web sobre neobancos y billeteras digitales vigiladas por la Superintendencia Financiera de Colombia. Las cifras de la web se recalculan solas: en el texto NUNCA escribas un número literal; toda cifra, fecha, año o nombre de entidad que dependa de los datos va como marcador {{...}}.

Marcadores disponibles (ent = id de entidad, grupo_banco, grupo_cf, grupo_sedpe, universo o comparador sis_ec/sis_bancos/sis_cf/sis_sedpe; corte = informe | base | ultimo):
- {{v:indicador:ent:corte:formato}} valor (formato: billones, milm, millones, miles, pct, tasa, entero)
- {{crec:indicador:ent}} variación del corte del informe frente al corte base (saldos)
- {{anual:indicador:ent:informe:formato}} suma del año del informe (flujos como desembolsos)
- {{crec_anual:indicador:ent}} variación anual de un flujo
- {{part:indicador:ent:comparador:corte}} participación de ent en el comparador
- {{ratio:numerador:denominador:ent:corte}} cociente en porcentaje
- {{verbo:indicador:ent}} devuelve "creció" o "se redujo" según el signo de la variación
- {{lider:indicador:corte}} entidad con el mayor valor; {{n_ent:indicador:corte}} número de entidades con dato
- {{nombre:ent}}, {{corte}}, {{base}}, {{anio}}, {{fecha:indicador}} (mes del último dato)

Reglas de redacción:
- Español de Colombia, registro técnico y claro, en tercera persona o impersonal ("el gremio", "las entidades"). Nunca primera persona ("nuestro", "observamos").
- No mencionar el Plan Nacional de Desarrollo ni la participación del gremio en él.
- Cada bloque: como máximo tres cifras clave y una frase sobre qué implica. Las salvedades metodológicas no van en el texto.
- Solo afirmaciones que las cifras entregadas sustenten. Si una cifra no está disponible (n.d.), no la uses.
- Usa únicamente indicadores y entidades que aparezcan en la tabla de cifras.
- Conserva el formato Markdown del bloque (párrafo o viñetas). No agregues títulos."""

ESQUEMA = {
    "type": "object",
    "properties": {
        "bloques": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "texto": {"type": "string"}},
                "required": ["id", "texto"],
                "additionalProperties": False,
            },
        },
        "resumen_cambios": {"type": "string"},
    },
    "required": ["bloques", "resumen_cambios"],
    "additionalProperties": False,
}


def leer_bloques() -> dict[str, dict]:
    out = {}
    for f in sorted(SECCIONES.glob("*.md")):
        for m in BLOQUE.finditer(f.read_text(encoding="utf-8")):
            out[m["id"]] = {"archivo": f, "texto": m["texto"]}
    return out


def tabla_cifras(u: Universo) -> str:
    """Cifras actuales (corte del informe, base y último dato) para que el modelo razone."""
    df = pd.read_parquet(PROC / "indicadores.parquet")
    cortes = {"informe": u.inf["corte_informe"], "base": u.inf["corte_base"]}
    filas = []
    for ind, g in df.groupby("indicador"):
        ultimo = g["fecha"].max()
        for ent, h in g.groupby("entidad"):
            s = h.set_index("fecha")["valor"]
            vals = {k: s.get(f) for k, f in cortes.items()}
            vals["ultimo"] = s.get(ultimo)
            filas.append({"indicador": ind, "entidad": ent, **{k: (None if v is None else round(float(v), 4)) for k, v in vals.items()},
                          "fecha_ultimo": ultimo})
    return pd.DataFrame(filas).to_csv(index=False)


def validar_texto(texto: str, indicadores: set[str], entidades: set[str]) -> list[str]:
    errores = []
    sin_marcadores = MARCADOR.sub("", texto)
    if re.search(r"\d", sin_marcadores):
        errores.append("contiene cifras literales")
    if re.search(r"\b(nuestr[oa]s?|observamos|encontramos|leímos)\b", texto, re.I):
        errores.append("usa primera persona")
    if re.search(r"plan nacional de desarrollo|\bPND\b", texto, re.I):
        errores.append("menciona el PND")
    for expr in MARCADOR.findall(texto):
        p = expr.split(":")
        if p[0] not in OPS:
            errores.append(f"marcador desconocido {{{{{expr}}}}}")
            continue
        for x in p[1:]:
            if x in indicadores or x in entidades or x in {"informe", "base", "ultimo", "anual"} or \
                    x in {"billones", "milm", "millones", "miles", "pct", "tasa", "entero", "pp"} or re.fullmatch(r"\d{4}(-\d{2})?", x):
                continue
            errores.append(f"referencia inexistente '{x}' en {{{{{expr}}}}}")
    return errores


def main() -> int:
    u = Universo()
    bloques = leer_bloques()
    df = pd.read_parquet(PROC / "indicadores.parquet", columns=["indicador", "entidad"])
    indicadores, entidades = set(df["indicador"]), set(df["entidad"])

    pedido = (
        "Cifras actuales (CSV; valores en pesos, conteos o tasas en % E.A.):\n" + tabla_cifras(u) +
        "\n\nBloques actuales (id y texto):\n" +
        json.dumps({k: v["texto"] for k, v in bloques.items()}, ensure_ascii=False, indent=1) +
        "\n\nReescribe cada bloque para que el análisis refleje las cifras actuales. Si un bloque sigue siendo "
        "correcto, devuélvelo igual. Devuelve todos los ids. En resumen_cambios explica en dos o tres frases qué "
        "cambió en las cifras y en los textos, con cifras literales (este resumen es para el revisor, no se publica)."
    )
    client = anthropic.Anthropic()
    with client.beta.messages.stream(
        model="claude-opus-5-5",
        max_tokens=64000,
        betas=["server-side-fallback-2026-07-01"],
        fallbacks="default",
        output_config={"effort": "high", "format": {"type": "json_schema", "schema": ESQUEMA}},
        system=SISTEMA,
        messages=[{"role": "user", "content": pedido}],
    ) as stream:
        respuesta = stream.get_final_message()
    if respuesta.stop_reason == "refusal":
        print("El modelo declinó la solicitud; no se cambia ningún texto.")
        return 1
    if respuesta.stop_reason == "max_tokens":
        print("Respuesta truncada; no se cambia ningún texto.")
        return 1
    datos = json.loads(next(b.text for b in respuesta.content if b.type == "text"))

    informe = [f"## Borrador automático de textos\n\n{datos['resumen_cambios']}\n"]
    cambios = 0
    for b in datos["bloques"]:
        actual = bloques.get(b["id"])
        if not actual or b["texto"].strip() == actual["texto"].strip():
            continue
        errores = validar_texto(b["texto"], indicadores, entidades)
        if errores:
            informe.append(f"- `{b['id']}`: descartado ({'; '.join(errores)}).")
            continue
        f = actual["archivo"]
        contenido = f.read_text(encoding="utf-8")
        nuevo = BLOQUE.sub(lambda m: m.group(1) + b["texto"].strip() + m.group(4) if m["id"] == b["id"] else m.group(0),
                           contenido)
        f.write_text(nuevo, encoding="utf-8")
        cambios += 1
        informe.append(f"- `{b['id']}` ({f.name}): actualizado.")
    informe.append(f"\nBloques modificados: {cambios}. Revisar el texto en la vista previa antes de aprobar.")
    (PROC / "redaccion.md").write_text("\n".join(informe), encoding="utf-8")
    print("\n".join(informe))
    return 0


if __name__ == "__main__":
    sys.exit(main())
