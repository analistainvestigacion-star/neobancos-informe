## IV. Depósitos

```cifras
[{"valor": "{{v:depositos_total:universo:informe:billones}}", "texto": "saldo de depósitos a {{corte}}"},
 {"valor": "{{crec:depositos_total:universo}}", "texto": "crecimiento anual, frente a {{crec:depositos_total:sis_ec}} de los establecimientos de crédito"},
 {"valor": "{{v:tasa_ahorro:universo:informe:tasa}}", "texto": "tasa promedio pagada en ahorro, frente a {{v:tasa_ahorro:sis_ec:informe:tasa}} del sistema"}]
```

### Saldo por producto
<!-- analisis:depositos -->
Los depósitos del universo sumaron {{v:depositos_total:universo:informe:billones}} a {{corte}}: {{v:dep_ahorro_total:universo:informe:billones}} en ahorro, {{v:dep_cdt:universo:informe:billones}} en CDT y {{v:dep_electronicos:universo:informe:billones}} en depósitos electrónicos. La composición es distinta a la del sistema: el ahorro pesa {{ratio:dep_ahorro_total:depositos_total:universo:informe}} de los depósitos del grupo, frente a {{ratio:dep_ahorro_total:depositos_total:sis_ec:informe}} en los establecimientos de crédito, y no hay cuentas corrientes. El modelo se apoya en cuentas de ahorro remuneradas que se abren y se usan desde el celular.
<!-- /analisis -->

```grafico
{"id": "dep_producto", "tipo": "apiladas", "fecha": "informe", "formato": "milm", "titulo": "Depósitos por producto y entidad",
 "indicadores": [{"id": "dep_ahorro_total", "nombre": "Ahorro"}, {"id": "dep_cdt", "nombre": "CDT"}, {"id": "dep_electronicos", "nombre": "Depósitos electrónicos"}, {"id": "dep_cuenta_corriente", "nombre": "Cuenta corriente"}]}
```

```grafico
{"id": "dep_composicion", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Composición de los depósitos: universo frente al sistema",
 "entidades": ["universo", "grupo_cf", "grupo_banco", "grupo_sedpe"], "comparadores": ["sis_ec"],
 "indicadores": [{"id": "dep_ahorro_total", "nombre": "Ahorro"}, {"id": "dep_cdt", "nombre": "CDT"}, {"id": "dep_electronicos", "nombre": "Depósitos electrónicos"}, {"id": "dep_cuenta_corriente", "nombre": "Cuenta corriente"}]}
```

### Crecimiento 2024-2025
<!-- analisis:dep_crec -->
El saldo de depósitos del grupo {{verbo:depositos_total:universo}} {{crec:depositos_total:universo}} entre {{base}} y {{corte}}, frente a {{crec:depositos_total:sis_ec}} de los establecimientos de crédito. La diferencia es de {{crec_rel:depositos_total:universo:sis_ec}} Parte de ese salto se explica por entidades que empezaron a captar durante el periodo, como lo muestra la serie mensual. En 2026 la serie da un nuevo salto con la entrada de Nequi como compañía de financiamiento: en {{fecha:depositos_total}} sus depósitos sumaban {{v:depositos_total:nequi:ultimo:billones}}.
<!-- /analisis -->

```grafico
{"id": "dep_crec", "tipo": "barras", "indicador": "depositos_total", "crec": true, "formato": "pct", "titulo": "Crecimiento anual de los depósitos por entidad", "comparadores": ["sis_ec"], "nota": "Solo entidades con depósitos en ambos cortes."}
```

```grafico
{"id": "dep_serie", "tipo": "lineas", "indicador": "depositos_total", "entidades": ["universo", "grupo_cf", "grupo_banco", "grupo_sedpe"], "formato": "billones", "titulo": "Evolución de los depósitos", "nota": "El salto de 2026 corresponde al inicio de operaciones de Nequi como compañía de financiamiento."}
```

### Participación en el sistema financiero
<!-- analisis:dep_part -->
El universo pasó a representar {{part:depositos_total:universo:sis_total:informe}} de los depósitos del sistema (establecimientos de crédito y SEDPE) a {{corte}}, frente a {{part:depositos_total:universo:sis_total:base}} un año antes. En depósitos electrónicos, donde están las SEDPE, su peso es de {{part:dep_electronicos:universo:sis_total:informe}}.
<!-- /analisis -->

```grafico
{"id": "dep_part", "tipo": "lineas", "indicador": "depositos_total", "part_de": "sis_total", "entidades": ["universo"], "formato": "pct", "titulo": "Participación en los depósitos del sistema", "escala_libre": true}
```

### Saldo promedio y distribución por rangos de saldo
<!-- analisis:saldo_prom -->
El saldo promedio por cuenta de ahorro en el universo fue de {{ratio:saldo_capt_ahorro:cuentas_ahorro:universo:informe:entero}} pesos, frente a {{ratio:saldo_capt_ahorro:cuentas_ahorro:sis_ec:informe:entero}} pesos en los establecimientos de crédito. En los depósitos electrónicos el saldo promedio es mucho menor, {{ratio:saldo_capt_depelec:cuentas_depelec:universo:informe:entero}} pesos, lo que confirma que funcionan como medio de pago más que como ahorro. La gran mayoría de las cuentas tiene saldos inferiores a tres salarios mínimos.
<!-- /analisis -->

```grafico
{"id": "saldo_prom", "tipo": "barras", "ratio": ["saldo_capt_ahorro", "cuentas_ahorro"], "fecha": "informe", "formato": "millones", "unidad": "Millones de pesos por cuenta", "titulo": "Saldo promedio por cuenta de ahorro", "comparadores": ["sis_ec"], "fuente": "SFC, captaciones por rangos"}
```

```grafico
{"id": "rangos", "tipo": "rangos", "titulo": "Cuentas de depósito por rango de saldo (SMMLV)"}
```

### Tasas y montos de CDT
<!-- analisis:cdt -->
Las entidades digitales compiten por depósitos con tasa. En {{corte}} pagaron en promedio {{v:tasa_ahorro:universo:informe:tasa}} por los saldos de ahorro, frente a {{v:tasa_ahorro:sis_ec:informe:tasa}} en los establecimientos de crédito; en el último dato disponible ({{fecha:tasa_ahorro}}) las tasas fueron {{v:tasa_ahorro:universo:ultimo:tasa}} y {{v:tasa_ahorro:sis_ec:ultimo:tasa}}, respectivamente. En CDT, en cambio, las tasas del grupo están en línea con las del mercado: {{v:tasa_cdt:universo:informe:tasa}} frente a {{v:tasa_cdt:sis_ec:informe:tasa}} en {{corte}}. Como el ahorro es la mayor parte de sus depósitos, esto implica un costo de fondeo más alto que el de la banca tradicional, que estas entidades compensan con estructuras de costos operativos más livianas. En {{anio}}, el grupo emitió CDT por {{anual:cdt_emitido:universo:informe:billones}}.
<!-- /analisis -->

```grafico
{"id": "tasa_ahorro", "tipo": "lineas", "indicador": "tasa_ahorro", "entidades": ["universo", "sis_ec", "sis_bancos"], "formato": "tasa", "titulo": "Tasa promedio pagada por los depósitos de ahorro", "escala_libre": true, "nota": "Promedio ponderado por saldo de las tasas reportadas en el formato 441."}
```

```grafico
{"id": "cdt_plazos", "tipo": "cdt_plazos", "fecha": "informe", "titulo": "Tasa promedio de los CDT emitidos por plazo", "fuente": "SFC, formato 441"}
```

```grafico
{"id": "tasa_cdt", "tipo": "lineas", "indicador": "tasa_cdt", "entidades": ["universo", "sis_ec"], "formato": "tasa", "titulo": "Tasa promedio de captación en CDT", "escala_libre": true}
```
