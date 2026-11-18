## V. Crédito

```cifras
[{"valor": "{{v:cartera_bruta:universo:informe:billones}}", "texto": "cartera bruta a {{corte}}"},
 {"valor": "{{crec:cartera_bruta:universo}}", "texto": "variación anual de la cartera"},
 {"valor": "{{anual:desembolsos:universo:informe:billones}}", "texto": "desembolsados en {{anio}} (sin tarjetas)"}]
```

### Cartera por modalidad y crecimiento
<!-- analisis:cartera -->
La cartera bruta del universo sumó {{v:cartera_bruta:universo:informe:billones}} a {{corte}} y {{verbo:cartera_bruta:universo}} {{crec:cartera_bruta:universo}} en el año. La cartera de consumo representa {{ratio:cartera_consumo:cartera_bruta:universo:informe}} del total.
<!-- /analisis -->

```grafico
{"id": "cartera_modalidad", "tipo": "apiladas", "fecha": "informe", "formato": "milm", "titulo": "Cartera bruta por modalidad",
 "indicadores": [{"id": "cartera_consumo", "nombre": "Consumo"}, {"id": "cartera_comercial", "nombre": "Comercial"}, {"id": "cartera_microcredito", "nombre": "Microcrédito"}, {"id": "cartera_vivienda", "nombre": "Vivienda"}]}
```

### Calidad de cartera
<!-- analisis:calidad -->
La cartera de consumo vencida representó {{ratio:cartera_vencida:cartera_consumo_dist:universo:informe}} de la cartera de consumo del universo a {{corte}}, frente a {{ratio:cartera_vencida:cartera_consumo_dist:sis_ec:informe}} en los establecimientos de crédito.
<!-- /analisis -->

```grafico
{"id": "icv", "tipo": "barras", "ratio": ["cartera_vencida", "cartera_consumo_dist"], "fecha": "informe", "formato": "pct", "titulo": "Cartera de consumo vencida sobre cartera de consumo", "comparadores": ["sis_ec"], "fuente": "SFC, distribución de cartera por producto"}
```

### Desembolsos, número de créditos y tasas frente al sistema
<!-- analisis:desembolsos -->
En {{anio}}, las entidades del universo desembolsaron {{anual:desembolsos:universo:informe:billones}} en {{anual:creditos:universo:informe:millones}} de créditos, sin contar las tarjetas de crédito. La tasa promedio ponderada de los créditos de consumo en {{fecha:tasa_consumo}} fue {{v:tasa_consumo:universo:ultimo:tasa}}, frente a {{v:tasa_consumo:sis_ec:ultimo:tasa}} en los establecimientos de crédito.
<!-- /analisis -->

```grafico
{"id": "desembolsos", "tipo": "barras", "indicador": "desembolsos", "anual": "informe", "formato": "milm", "titulo": "Desembolsos del año por entidad (sin tarjetas)"}
```

```grafico
{"id": "tasa_consumo", "tipo": "lineas", "indicador": "tasa_consumo", "entidades": ["universo", "sis_ec", "sis_bancos"], "formato": "tasa", "titulo": "Tasa promedio ponderada de los desembolsos de consumo", "escala_libre": true}
```

### Tarjetas de crédito y débito
```grafico
{"id": "tarjetas", "tipo": "apiladas", "fecha": "informe", "formato": "millones", "titulo": "Tarjetas vigentes",
 "indicadores": [{"id": "tarjetas_credito", "nombre": "Crédito"}, {"id": "tarjetas_debito", "nombre": "Débito"}]}
```
