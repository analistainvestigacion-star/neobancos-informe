## II. Las entidades

### Tamaño: activos y patrimonio
<!-- analisis:tamano -->
Las entidades del universo sumaron activos por {{v:activo:universo:informe:billones}} a {{corte}}, apenas {{part:activo:universo:sis_total:informe}} del sistema. Lo que las distingue es la velocidad: el saldo de activos {{verbo:activo:universo}} {{crec:activo:universo}} en el año, frente a {{crec:activo:sis_ec}} de los establecimientos de crédito.

El crecimiento está concentrado. {{lider:activo:informe}} reúne {{conc:activo:informe:1}} de los activos del grupo y las tres entidades más grandes, {{conc:activo:informe:3}}. Por eso el desempeño agregado depende en buena medida de una sola entidad.

Por licencia, las compañías de financiamiento digitales suman {{v:activo:grupo_cf:informe:billones}}, el banco digital {{v:activo:grupo_banco:informe:billones}} y las SEDPE {{v:activo:grupo_sedpe:informe:billones}}. Entre las entidades que ya operaban en {{base}}, la de mayor crecimiento fue {{mas_crec:activo}}.

Después del corte, el mapa cambió: en 2026 Nequi inició operaciones como compañía de financiamiento. En {{fecha:activo}} ya registraba activos por {{v:activo:nequi:ultimo:billones}}, lo que explica el salto de las series en 2026.
<!-- /analisis -->

```grafico
{"id": "activos", "tipo": "barras", "indicador": "activo", "fecha": "informe", "formato": "milm", "rotulo": "Activos", "titulo": "{{lider:activo:informe}} concentra {{conc:activo:informe:1}} de los activos del grupo"}
```

```grafico
{"id": "activos_crec", "tipo": "barras", "indicador": "activo", "crec": true, "formato": "pct", "comparadores": ["sis_ec"], "rotulo": "Crecimiento anual de los activos", "titulo": "Los activos del grupo crecieron {{crec:activo:universo}}; los de los establecimientos de crédito, {{crec:activo:sis_ec}}", "nota": "Solo entidades con activos en ambos cortes. La línea punteada es el crecimiento de los establecimientos de crédito."}
```

```grafico
{"id": "activos_part", "tipo": "lineas", "indicador": "activo", "part_de": "sis_total", "entidades": ["universo", "grupo_cf", "grupo_banco"], "formato": "pct", "escala_libre": true, "rotulo": "Participación en los activos del sistema", "titulo": "El grupo pasó de {{part:activo:universo:sis_total:base}} a {{part:activo:universo:sis_total:informe}} de los activos del sistema en un año"}
```

### Rentabilidad y solidez
<!-- analisis:solidez -->
La expansión todavía no se traduce en utilidades para el grupo. En {{anio}} registró un resultado neto de {{v:utilidad:universo:informe:milm}}, equivalente a {{ratio:utilidad:patrimonio:universo:informe}} de su patrimonio. Los establecimientos de crédito obtuvieron {{ratio:utilidad:patrimonio:sis_ec:informe}}.

Es el patrón de entidades en etapa de crecimiento, que invierten en adquirir clientes y en tecnología antes de alcanzar escala. Algunas, sobre todo SEDPE y negocios de pagos, ya reportan utilidades.

La pérdida no compromete la solidez. La relación de solvencia total del universo fue {{v:solvencia:universo:informe:dec}} %, frente a {{v:solvencia:sis_ec:informe:dec}} % de los establecimientos de crédito y un mínimo regulatorio de nueve por ciento. El patrimonio conjunto llegó a {{v:patrimonio:universo:informe:billones}}.
<!-- /analisis -->

```grafico
{"id": "roe", "tipo": "barras", "ratio": ["utilidad", "patrimonio"], "fecha": "informe", "formato": "pct", "comparadores": ["sis_ec"], "incluir_ceros": true, "rotulo": "Resultado del año sobre patrimonio", "titulo": "El grupo cerró {{anio}} con un resultado de {{ratio:utilidad:patrimonio:universo:informe}} sobre su patrimonio", "nota": "Utilidad o pérdida acumulada del año sobre el patrimonio al cierre. La línea punteada corresponde a los establecimientos de crédito."}
```

```grafico
{"id": "solvencia", "tipo": "barras", "indicador": "solvencia", "fecha": "informe", "formato": "tasa", "unidad": "Relación de solvencia total (%)", "comparadores": ["sis_ec"], "rotulo": "Solvencia", "titulo": "La solvencia del grupo ({{v:solvencia:universo:informe:dec}} %) supera el mínimo regulatorio de nueve por ciento", "nota": "Las SEDPE no reportan relación de solvencia en este formato."}
```

### Fichas por entidad

```grafico
{"tipo": "fichas"}
```
