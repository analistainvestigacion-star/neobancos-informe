## III. Clientes y cuentas

```cifras
[{"valor": "{{v:clientes_ahorro:universo:informe:millones}}", "texto": "clientes de depósitos de ahorro (suma por entidad)"},
 {"valor": "{{v:clientes_depelec:universo:informe:millones}}", "texto": "clientes de depósitos electrónicos (suma por entidad)"},
 {"valor": "{{part:clientes_depelec:universo:sis_total:informe}}", "texto": "de los clientes de depósitos electrónicos del sistema"}]
```

### Número de clientes por producto de depósito
<!-- analisis:clientes -->
A {{corte}}, las entidades del universo atendían {{v:clientes_ahorro:universo:informe:millones}} de clientes en depósitos de ahorro y {{v:clientes_depelec:universo:informe:millones}} en depósitos electrónicos. Son dos públicos distintos. Los clientes de ahorro se concentran en {{lider:clientes_ahorro:informe}}, que atiende {{conc:clientes_ahorro:informe:1}} de ellos, y en el banco digital; los clientes de depósitos electrónicos están sobre todo en las SEDPE, encabezadas por {{lider:clientes_depelec:informe}}.

En el producto de ahorro, el grupo todavía es pequeño frente al sistema ({{part:clientes_ahorro:universo:sis_total:informe}} de los clientes de ahorro del sistema), pero creció {{crec:clientes_ahorro:universo}} en el año. En depósitos electrónicos su peso es mucho mayor: {{part:clientes_depelec:universo:sis_total:informe}} de los clientes de ese producto en el sistema.
<!-- /analisis -->

```grafico
{"id": "clientes_ahorro", "tipo": "barras", "indicador": "clientes_ahorro", "fecha": "informe", "formato": "millones", "titulo": "Clientes de depósitos de ahorro"}
```

```grafico
{"id": "clientes_depelec", "tipo": "barras", "indicador": "clientes_depelec", "fecha": "informe", "formato": "millones", "titulo": "Clientes de depósitos electrónicos"}
```

```grafico
{"id": "clientes_serie", "tipo": "lineas", "indicador": "clientes_ahorro", "entidades": ["universo", "grupo_cf", "grupo_banco"], "formato": "millones", "titulo": "Evolución de los clientes de ahorro"}
```

### Número de cuentas por producto
<!-- analisis:cuentas -->
Las entidades del universo administraban {{v:cuentas_ahorro:universo:informe:millones}} de cuentas de ahorro, {{v:cuentas_depelec:universo:informe:millones}} de depósitos electrónicos y {{v:cuentas_cdt:universo:informe:miles}} CDT. En las entidades digitales la relación entre cuentas y clientes es cercana a uno: cada cliente suele tener una sola cuenta por producto, a diferencia de la banca tradicional, donde es común que una persona tenga varias.
<!-- /analisis -->

```grafico
{"id": "cuentas_producto", "tipo": "apiladas", "fecha": "informe", "formato": "millones", "titulo": "Cuentas de depósito por producto",
 "indicadores": [{"id": "cuentas_ahorro", "nombre": "Ahorro"}, {"id": "cuentas_depelec", "nombre": "Depósitos electrónicos"}, {"id": "cuentas_cdt", "nombre": "CDT"}]}
```

### Cuentas activas e inactivas
<!-- analisis:activas -->
Tener una cuenta no es lo mismo que usarla. Según el reporte de inclusión financiera de la SFC, {{ratio:ctas_ahorro_activas:ctas_ahorro_total:universo:informe}} de las cuentas de ahorro de las entidades del universo estaban activas a {{corte}}, frente a {{ratio:ctas_ahorro_activas:ctas_ahorro_total:sis_ec:informe}} en los establecimientos de crédito: las cuentas de las entidades digitales se usan con más frecuencia, porque suelen ser la cuenta de uso diario de sus clientes y no una cuenta secundaria. Con la información de Fogafín, que incluye los depósitos electrónicos y de bajo monto, {{ratio:productos_activos:productos_total:universo:informe}} de los productos de depósito del grupo estaban activos en el corte trimestral más cercano.
<!-- /analisis -->

```grafico
{"id": "activas_sfc", "tipo": "barras", "ratio": ["ctas_ahorro_activas", "ctas_ahorro_total"], "fecha": "informe", "formato": "pct", "titulo": "Cuentas de ahorro activas sobre el total", "comparadores": ["sis_ec"], "fuente": "SFC, inclusión financiera"}
```

```grafico
{"id": "activas", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Productos de depósito por estado",
 "indicadores": [{"id": "productos_activos", "nombre": "Activos"}, {"id": "productos_inactivos", "nombre": "Inactivos"}, {"id": "productos_abandonados", "nombre": "Abandonados"}],
 "nota": "Fogafín publica cortes trimestrales; se usa el más cercano anterior al corte."}
```

### Personas naturales y jurídicas
<!-- analisis:pn_pj -->
El grupo atiende casi exclusivamente a personas naturales: las personas jurídicas son apenas {{ratio:clientes_pj:clientes_pn:universo:informe}} frente a las naturales. La oferta para empresas se concentra en pocas entidades orientadas a comercios y pagos.
<!-- /analisis -->

```grafico
{"id": "pn_pj", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Clientes de depósito por tipo de persona",
 "indicadores": [{"id": "clientes_pn", "nombre": "Personas naturales"}, {"id": "clientes_pj", "nombre": "Personas jurídicas"}]}
```
