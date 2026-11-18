## III. Clientes y cuentas

```cifras
[{"valor": "{{v:clientes_ahorro:universo:informe:millones}}", "texto": "clientes de depósitos de ahorro (suma por entidad)"},
 {"valor": "{{v:clientes_depelec:universo:informe:millones}}", "texto": "clientes de depósitos electrónicos (suma por entidad)"},
 {"valor": "{{crec:clientes_ahorro:universo}}", "texto": "variación anual de los clientes de ahorro"}]
```

### Número de clientes y de cuentas por producto
<!-- analisis:clientes -->
A {{corte}}, las entidades del universo reportaron {{v:clientes_ahorro:universo:informe:millones}} de clientes en depósitos de ahorro y {{v:clientes_depelec:universo:informe:millones}} en depósitos electrónicos. {{lider:clientes_ahorro:informe}} concentra el mayor número de clientes de ahorro.
<!-- /analisis -->

```grafico
{"id": "clientes_ahorro", "tipo": "barras", "indicador": "clientes_ahorro", "fecha": "informe", "formato": "millones", "titulo": "Clientes de depósitos de ahorro"}
```

```grafico
{"id": "clientes_depelec", "tipo": "barras", "indicador": "clientes_depelec", "fecha": "informe", "formato": "millones", "titulo": "Clientes de depósitos electrónicos"}
```

```grafico
{"id": "clientes_serie", "tipo": "lineas", "indicador": "clientes_ahorro", "entidades": ["grupo_banco", "grupo_cf", "grupo_sedpe"], "formato": "millones", "titulo": "Evolución de los clientes de ahorro por grupo"}
```

### Cuentas activas e inactivas
<!-- analisis:activas -->
Según Fogafín, {{ratio:productos_activos:productos_total:universo:informe}} de los productos de depósito de las entidades del universo estaban activos al corte trimestral más cercano a {{corte}}.
<!-- /analisis -->

```grafico
{"id": "activas", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Productos de depósito por estado",
 "indicadores": [{"id": "productos_activos", "nombre": "Activos"}, {"id": "productos_inactivos", "nombre": "Inactivos"}, {"id": "productos_abandonados", "nombre": "Abandonados"}],
 "nota": "Fogafín publica cortes trimestrales; se usa el más cercano anterior al corte."}
```

### Personas naturales y jurídicas
```grafico
{"id": "pn_pj", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Clientes de depósito por tipo de persona",
 "indicadores": [{"id": "clientes_pn", "nombre": "Personas naturales"}, {"id": "clientes_pj", "nombre": "Personas jurídicas"}]}
```
