import pandas as pd

from etl.textos import validar_texto
from etl.transform import Universo, a_largo


def test_a_largo_separa_entidades_y_comparadores():
    u = Universo()
    df = pd.DataFrame({
        "nivel": ["entidad", "sistema", "sistema", "sistema"],
        "tipo": ["4", "4", "4", "1"],
        "codigo": ["128", "128", "124", "7"],
        "fecha": ["2025-12-31"] * 4,
        "x": [10.0, 10.0, 5.0, 100.0],
    })
    out = a_largo(df, u, "tipo", "codigo", {"activo": "x"}, "prueba")
    v = out.set_index("entidad")["valor"]
    assert v["nu"] == 10
    assert v["sis_cf"] == 15          # solo compañías de financiamiento
    assert v["sis_bancos"] == 100
    assert v["sis_ec"] == 115         # bancos + CF


def test_validar_texto_rechaza_cifras_literales_y_primera_persona():
    ind, ent = {"activo"}, {"universo"}
    assert validar_texto("Los activos sumaron {{v:activo:universo:informe:billones}}.", ind, ent) == []
    assert any("cifras literales" in e for e in validar_texto("Los activos sumaron 15 billones.", ind, ent))
    assert "usa primera persona" in validar_texto("Nuestro análisis {{crec:activo:universo}}.", ind, ent)
    assert any("inexistente" in e for e in validar_texto("{{v:pasivo:universo:informe:billones}}", ind, ent))
