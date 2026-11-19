## III. Clientes y cuentas

### Número de clientes por producto de depósito
<!-- analisis:clientes -->
A {{corte}}, las entidades del universo atendían {{v:clientes_ahorro:universo:informe:millones}} de clientes en depósitos de ahorro y {{v:clientes_depelec:universo:informe:millones}} en depósitos electrónicos. Son dos públicos distintos, con productos y saldos diferentes.

Los clientes de ahorro se concentran en {{lider:clientes_ahorro:informe}}, con {{conc:clientes_ahorro:informe:1}} del total del grupo. Los de depósitos electrónicos están sobre todo en las SEDPE, encabezadas por {{lider:clientes_depelec:informe}}.

En ahorro el grupo es pequeño: {{part:clientes_ahorro:universo:sis_total:informe}} de los clientes del sistema, aunque creció {{crec:clientes_ahorro:universo}} en el año. En depósitos electrónicos su peso es mayor, {{part:clientes_depelec:universo:sis_total:informe}}.

Fogafín permite una medida sin duplicados dentro de cada entidad: en {{fecha:depositantes}} el universo tenía {{v:depositantes:universo:ultimo:millones}} de depositantes.
<!-- /analisis -->

```grafico
{"id": "clientes_ahorro", "tipo": "barras", "indicador": "clientes_ahorro", "fecha": "informe", "formato": "millones", "rotulo": "Clientes de depósitos de ahorro", "titulo": "{{lider:clientes_ahorro:informe}} atiende {{conc:clientes_ahorro:informe:1}} de los clientes de ahorro del grupo"}
```

```grafico
{"id": "clientes_depelec", "tipo": "barras", "indicador": "clientes_depelec", "fecha": "informe", "formato": "millones", "rotulo": "Clientes de depósitos electrónicos", "titulo": "Las SEDPE concentran los clientes de depósitos electrónicos"}
```

```grafico
{"id": "clientes_serie", "tipo": "lineas", "indicador": "clientes_ahorro", "entidades": ["universo", "grupo_cf", "grupo_banco"], "formato": "millones", "rotulo": "Evolución de los clientes de ahorro", "titulo": "Los clientes de ahorro del grupo crecieron {{crec:clientes_ahorro:universo}} en el año"}
```

### Número de cuentas por producto
<!-- analisis:cuentas -->
El universo administraba {{v:cuentas_ahorro:universo:informe:millones}} de cuentas de ahorro, {{v:cuentas_depelec:universo:informe:millones}} de depósitos electrónicos y {{v:cuentas_cdt:universo:informe:miles}} CDT. En estas entidades la relación entre cuentas y clientes es cercana a uno: cada cliente suele tener una sola cuenta por producto, a diferencia de la banca tradicional.
<!-- /analisis -->

```grafico
{"id": "cuentas_producto", "tipo": "apiladas", "fecha": "informe", "formato": "millones", "rotulo": "Cuentas de depósito por producto", "titulo": "Los depósitos electrónicos suman más cuentas que el ahorro en el grupo",
 "indicadores": [{"id": "cuentas_ahorro", "nombre": "Ahorro"}, {"id": "cuentas_depelec", "nombre": "Depósitos electrónicos"}, {"id": "cuentas_cdt", "nombre": "CDT"}]}
```

### Cuentas activas e inactivas
<!-- analisis:activas -->
Tener una cuenta no es lo mismo que usarla. Según la SFC, {{ratio:ctas_ahorro_activas:ctas_ahorro_total:universo:informe}} de las cuentas de ahorro del universo estaban activas a {{corte}}, frente a {{ratio:ctas_ahorro_activas:ctas_ahorro_total:sis_ec:informe}} en los establecimientos de crédito.

La diferencia sugiere que las cuentas digitales suelen ser la cuenta de uso diario de sus clientes, no una cuenta secundaria. Con Fogafín, que incluye depósitos electrónicos y de bajo monto, {{ratio:productos_activos:productos_total:universo:informe}} de los productos del grupo estaban activos.
<!-- /analisis -->

```grafico
{"id": "activas_sfc", "tipo": "barras", "ratio": ["ctas_ahorro_activas", "ctas_ahorro_total"], "fecha": "informe", "formato": "pct", "comparadores": ["sis_ec"], "fuente": "SFC, inclusión financiera", "rotulo": "Cuentas de ahorro activas", "titulo": "{{ratio:ctas_ahorro_activas:ctas_ahorro_total:universo:informe}} de las cuentas de ahorro del grupo están activas; en los establecimientos de crédito, {{ratio:ctas_ahorro_activas:ctas_ahorro_total:sis_ec:informe}}"}
```

```grafico
{"id": "activas", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "rotulo": "Productos de depósito por estado", "titulo": "La mayoría de los productos de depósito del grupo está activa",
 "indicadores": [{"id": "productos_activos", "nombre": "Activos"}, {"id": "productos_inactivos", "nombre": "Inactivos"}, {"id": "productos_abandonados", "nombre": "Abandonados"}],
 "nota": "Fogafín publica cortes trimestrales; se usa el más cercano anterior al corte."}
```

### Personas naturales y jurídicas
<!-- analisis:pn_pj -->
El grupo atiende casi solo a personas naturales: los depositantes que son personas jurídicas equivalen a {{ratio:depositantes_pj:depositantes_pn:universo:ultimo}} de los que son personas naturales. La oferta para empresas se concentra en pocas entidades orientadas a comercios y pagos.
<!-- /analisis -->

```grafico
{"id": "pn_pj", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "rotulo": "Clientes de depósito por tipo de persona", "titulo": "Las personas naturales son casi la totalidad de los clientes del grupo",
 "indicadores": [{"id": "clientes_pn", "nombre": "Personas naturales"}, {"id": "clientes_pj", "nombre": "Personas jurídicas"}]}
```
