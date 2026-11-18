## IV. Depósitos

```cifras
[{"valor": "{{v:depositos_total:universo:informe:billones}}", "texto": "saldo de depósitos a {{corte}}"},
 {"valor": "{{crec:depositos_total:universo}}", "texto": "variación anual"},
 {"valor": "{{part:depositos_total:universo:sis_ec:informe}}", "texto": "de los depósitos de los establecimientos de crédito"}]
```

### Saldo por producto
<!-- analisis:depositos -->
Los depósitos del universo sumaron {{v:depositos_total:universo:informe:billones}} a {{corte}}: {{v:dep_ahorro_total:universo:informe:billones}} en ahorro, {{v:dep_cdt:universo:informe:billones}} en CDT y {{v:dep_electronicos:universo:informe:billones}} en depósitos electrónicos. Frente a {{base}}, el saldo total {{verbo:depositos_total:universo}} {{crec:depositos_total:universo}}.
<!-- /analisis -->

```grafico
{"id": "dep_producto", "tipo": "apiladas", "fecha": "informe", "formato": "milm", "titulo": "Depósitos por producto y entidad",
 "indicadores": [{"id": "dep_ahorro_total", "nombre": "Ahorro"}, {"id": "dep_cdt", "nombre": "CDT"}, {"id": "dep_electronicos", "nombre": "Depósitos electrónicos"}, {"id": "dep_cuenta_corriente", "nombre": "Cuenta corriente"}]}
```

### Crecimiento y participación en el sistema
```grafico
{"id": "dep_serie", "tipo": "lineas", "indicador": "depositos_total", "entidades": ["universo", "grupo_banco", "grupo_cf", "grupo_sedpe"], "formato": "billones", "titulo": "Evolución de los depósitos"}
```

### Saldo promedio y distribución por rangos de saldo
El saldo promedio por cuenta de ahorro en las entidades del universo fue de {{ratio:saldo_capt_ahorro:cuentas_ahorro:universo:informe:entero}} pesos a {{corte}}.

```grafico
{"id": "rangos", "tipo": "rangos", "titulo": "Cuentas de depósito por rango de saldo (SMMLV)"}
```

### Tasas y montos de CDT
<!-- analisis:cdt -->
La tasa promedio ponderada de los CDT emitidos por las entidades del universo en {{fecha:tasa_cdt}} fue {{v:tasa_cdt:universo:ultimo:tasa}}, frente a {{v:tasa_cdt:sis_ec:ultimo:tasa}} en el conjunto de establecimientos de crédito.
<!-- /analisis -->

```grafico
{"id": "tasa_cdt", "tipo": "lineas", "indicador": "tasa_cdt", "entidades": ["universo", "sis_ec"], "formato": "tasa", "titulo": "Tasa promedio de captación en CDT", "escala_libre": true}
```
