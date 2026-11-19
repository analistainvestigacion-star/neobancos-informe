## IV. Depósitos

### Saldo por producto
<!-- analisis:depositos -->
Los depósitos del universo sumaron {{v:depositos_total:universo:informe:billones}} a {{corte}}. De ese total, {{v:dep_ahorro_total:universo:informe:billones}} estaban en ahorro, {{v:dep_cdt:universo:informe:billones}} en CDT y {{v:dep_electronicos:universo:informe:billones}} en depósitos electrónicos.

La composición difiere de la del sistema. El ahorro pesa {{ratio:dep_ahorro_total:depositos_total:universo:informe}} de los depósitos del grupo, frente a {{ratio:dep_ahorro_total:depositos_total:sis_ec:informe}} en los establecimientos de crédito, y no hay cuentas corrientes. El modelo se apoya en cuentas de ahorro remuneradas que se abren y se usan desde el celular.
<!-- /analisis -->

```grafico
{"id": "dep_producto", "tipo": "apiladas", "fecha": "informe", "formato": "milm", "rotulo": "Depósitos por producto y entidad", "titulo": "El ahorro es el principal producto de depósito del grupo",
 "indicadores": [{"id": "dep_ahorro_total", "nombre": "Ahorro"}, {"id": "dep_cdt", "nombre": "CDT"}, {"id": "dep_electronicos", "nombre": "Depósitos electrónicos"}, {"id": "dep_cuenta_corriente", "nombre": "Cuenta corriente"}]}
```

```grafico
{"id": "dep_composicion", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "rotulo": "Composición de los depósitos", "titulo": "El ahorro pesa {{ratio:dep_ahorro_total:depositos_total:universo:informe}} de los depósitos del grupo y {{ratio:dep_ahorro_total:depositos_total:sis_ec:informe}} en los establecimientos de crédito",
 "entidades": ["universo", "grupo_cf", "grupo_banco", "grupo_sedpe"], "comparadores": ["sis_ec"],
 "indicadores": [{"id": "dep_ahorro_total", "nombre": "Ahorro"}, {"id": "dep_cdt", "nombre": "CDT"}, {"id": "dep_electronicos", "nombre": "Depósitos electrónicos"}, {"id": "dep_cuenta_corriente", "nombre": "Cuenta corriente"}]}
```

### Crecimiento 2024-2025
<!-- analisis:dep_crec -->
El saldo de depósitos del grupo {{verbo:depositos_total:universo}} {{crec:depositos_total:universo}} entre {{base}} y {{corte}}, frente a {{crec:depositos_total:sis_ec}} de los establecimientos de crédito: una diferencia de {{crec_rel:depositos_total:universo:sis_ec}}. Parte del salto se explica por entidades que empezaron a captar durante el periodo.

En 2026 la serie da un nuevo salto con la entrada de Nequi como compañía de financiamiento. En {{fecha:depositos_total}} sus depósitos sumaban {{v:depositos_total:nequi:ultimo:billones}}.
<!-- /analisis -->

```grafico
{"id": "dep_crec", "tipo": "barras", "indicador": "depositos_total", "crec": true, "formato": "pct", "comparadores": ["sis_ec"], "rotulo": "Crecimiento anual de los depósitos", "titulo": "Los depósitos del grupo crecieron {{crec:depositos_total:universo}}; los de los establecimientos de crédito, {{crec:depositos_total:sis_ec}}", "nota": "Solo entidades con depósitos en ambos cortes."}
```

```grafico
{"id": "dep_serie", "tipo": "lineas", "indicador": "depositos_total", "entidades": ["universo", "grupo_cf", "grupo_banco", "grupo_sedpe"], "formato": "billones", "rotulo": "Evolución de los depósitos", "titulo": "Los depósitos del grupo llegaron a {{v:depositos_total:universo:ultimo:billones}} en {{fecha:depositos_total}}", "nota": "El salto de 2026 corresponde al inicio de operaciones de Nequi como compañía de financiamiento."}
```

### Participación en el sistema financiero
<!-- analisis:dep_part -->
El universo pasó a representar {{part:depositos_total:universo:sis_total:informe}} de los depósitos del sistema, con las SEDPE incluidas, frente a {{part:depositos_total:universo:sis_total:base}} un año antes. En depósitos electrónicos, el producto de las SEDPE, su peso es mucho mayor: {{part:dep_electronicos:universo:sis_total:informe}}.
<!-- /analisis -->

```grafico
{"id": "dep_part", "tipo": "lineas", "indicador": "depositos_total", "part_de": "sis_total", "entidades": ["universo"], "formato": "pct", "escala_libre": true, "rotulo": "Participación en los depósitos del sistema", "titulo": "El grupo pasó de {{part:depositos_total:universo:sis_total:base}} a {{part:depositos_total:universo:sis_total:informe}} de los depósitos del sistema"}
```

### Saldo promedio y distribución por rangos de saldo
<!-- analisis:saldo_prom -->
El saldo promedio por cuenta de ahorro en el universo fue de {{ratio:saldo_capt_ahorro:cuentas_ahorro:universo:informe:entero}} pesos, frente a {{ratio:saldo_capt_ahorro:cuentas_ahorro:sis_ec:informe:entero}} pesos en los establecimientos de crédito. En depósitos electrónicos baja a {{ratio:saldo_capt_depelec:cuentas_depelec:universo:informe:entero}} pesos.

Estos saldos confirman que los depósitos electrónicos funcionan más como medio de pago que como ahorro. La gran mayoría de las cuentas del grupo tiene saldos inferiores a tres salarios mínimos.
<!-- /analisis -->

```grafico
{"id": "saldo_prom", "tipo": "barras", "ratio": ["saldo_capt_ahorro", "cuentas_ahorro"], "fecha": "informe", "formato": "millones", "unidad": "Millones de pesos por cuenta", "comparadores": ["sis_ec"], "fuente": "SFC, captaciones por rangos", "rotulo": "Saldo promedio por cuenta de ahorro", "titulo": "Una cuenta de ahorro del grupo tiene en promedio {{ratio:saldo_capt_ahorro:cuentas_ahorro:universo:informe:millones}} de pesos"}
```

```grafico
{"id": "rangos", "tipo": "rangos", "rotulo": "Cuentas de depósito por rango de saldo (SMMLV)", "titulo": "Casi todas las cuentas del grupo tienen menos de tres salarios mínimos"}
```

### Tasas y montos de CDT
<!-- analisis:cdt -->
Las entidades digitales compiten por depósitos con tasa. En {{corte}} pagaron en promedio {{v:tasa_ahorro:universo:informe:tasa}} por el ahorro, frente a {{v:tasa_ahorro:sis_ec:informe:tasa}} en los establecimientos de crédito. Como el ahorro es la mayor parte de sus depósitos, su costo de fondeo es más alto que el de la banca tradicional.

En CDT, en cambio, las tasas del grupo están en línea con las del mercado: {{v:tasa_cdt:universo:informe:tasa}} frente a {{v:tasa_cdt:sis_ec:informe:tasa}}. En {{anio}} el grupo emitió CDT por {{anual:cdt_emitido:universo:informe:billones}}.
<!-- /analisis -->

```grafico
{"id": "tasa_ahorro", "tipo": "lineas", "indicador": "tasa_ahorro", "entidades": ["universo", "sis_ec", "sis_bancos"], "formato": "tasa", "escala_libre": true, "rotulo": "Tasa pagada por los depósitos de ahorro", "titulo": "El grupo paga por el ahorro {{v:tasa_ahorro:universo:informe:tasa}}; los establecimientos de crédito, {{v:tasa_ahorro:sis_ec:informe:tasa}}", "nota": "Promedio ponderado por saldo de las tasas reportadas en el formato 441."}
```

```grafico
{"id": "cdt_plazos", "tipo": "cdt_plazos", "fecha": "informe", "fuente": "SFC, formato 441", "rotulo": "Tasa de los CDT emitidos por plazo", "titulo": "En CDT, las tasas del grupo son similares a las del mercado en casi todos los plazos", "nota": "Solo plazos con emisiones relevantes del grupo (al menos 0,5 % de lo emitido)."}
```

```grafico
{"id": "tasa_cdt", "tipo": "lineas", "indicador": "tasa_cdt", "entidades": ["universo", "sis_ec"], "formato": "tasa", "escala_libre": true, "rotulo": "Tasa de captación en CDT", "titulo": "La tasa promedio de los CDT del grupo sigue la del mercado"}
```
