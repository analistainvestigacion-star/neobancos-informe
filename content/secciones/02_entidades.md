## II. Las entidades

```cifras
[{"valor": "{{v:activo:universo:informe:billones}}", "texto": "activos totales a {{corte}}"},
 {"valor": "{{crec:activo:universo}}", "texto": "crecimiento anual, frente a {{crec:activo:sis_ec}} de los establecimientos de crédito"},
 {"valor": "{{part:activo:universo:sis_total:informe}}", "texto": "de los activos del sistema (establecimientos de crédito y SEDPE)"}]
```

### Tamaño: activos y patrimonio
<!-- analisis:tamano -->
Las entidades del universo sumaron activos por {{v:activo:universo:informe:billones}} a {{corte}}. Es un segmento todavía pequeño frente al sistema: equivale a {{part:activo:universo:sis_total:informe}} de los activos del sistema (establecimientos de crédito y SEDPE). Lo que lo distingue es la velocidad: el saldo de activos {{verbo:activo:universo}} {{crec:activo:universo}} en el año, frente a {{crec:activo:sis_ec}} del conjunto de establecimientos de crédito, es decir, crecieron unas {{veces:activo:universo:sis_ec}} veces más rápido.

El crecimiento está muy concentrado. {{lider:activo:informe}} reúne {{conc:activo:informe:1}} de los activos del grupo y las tres entidades más grandes, {{conc:activo:informe:3}}. Por tipo de licencia, las compañías de financiamiento digitales suman {{v:activo:grupo_cf:informe:billones}}, el banco digital {{v:activo:grupo_banco:informe:billones}} y las SEDPE {{v:activo:grupo_sedpe:informe:billones}}. Entre las entidades que ya operaban en {{base}}, la de mayor crecimiento fue {{mas_crec:activo}}.

Después del corte, el mapa cambió: en 2026 Nequi inició operaciones como compañía de financiamiento y en {{fecha:activo}} ya registraba activos por {{v:activo:nequi:ultimo:billones}}, con lo que se convirtió en la segunda entidad más grande del grupo. Por eso las series mensuales muestran un salto en 2026.
<!-- /analisis -->

```grafico
{"id": "activos", "tipo": "barras", "indicador": "activo", "fecha": "informe", "formato": "milm", "titulo": "Activos por entidad"}
```

```grafico
{"id": "activos_crec", "tipo": "barras", "indicador": "activo", "crec": true, "formato": "pct", "titulo": "Crecimiento anual de los activos por entidad", "comparadores": ["sis_ec"], "nota": "Solo entidades con activos en ambos cortes. La línea punteada es el crecimiento de los establecimientos de crédito."}
```

```grafico
{"id": "activos_part", "tipo": "lineas", "indicador": "activo", "part_de": "sis_total", "entidades": ["universo", "grupo_cf", "grupo_banco"], "formato": "pct", "titulo": "Participación en los activos del sistema", "escala_libre": true}
```

### Rentabilidad y solidez
<!-- analisis:solidez -->
La expansión todavía no se traduce en utilidades para el grupo en conjunto. En {{anio}}, el universo registró un resultado neto de {{v:utilidad:universo:informe:milm}}, equivalente a {{ratio:utilidad:patrimonio:universo:informe}} de su patrimonio, mientras que los establecimientos de crédito obtuvieron una rentabilidad sobre el patrimonio de {{ratio:utilidad:patrimonio:sis_ec:informe}}. Es el patrón típico de entidades en etapa de crecimiento, que invierten en adquirir clientes y en tecnología antes de alcanzar escala; algunas entidades del grupo, en especial entre las SEDPE y los negocios de pagos, ya reportan utilidades.

La pérdida no compromete la solidez: la relación de solvencia total del universo fue de {{v:solvencia:universo:informe:dec}} %, frente a {{v:solvencia:sis_ec:informe:dec}} % en los establecimientos de crédito y a un mínimo regulatorio de nueve por ciento. El patrimonio conjunto llegó a {{v:patrimonio:universo:informe:billones}}.
<!-- /analisis -->

```grafico
{"id": "roe", "tipo": "barras", "ratio": ["utilidad", "patrimonio"], "fecha": "informe", "formato": "pct", "titulo": "Resultado del año sobre patrimonio", "comparadores": ["sis_ec"], "incluir_ceros": true, "nota": "Utilidad o pérdida acumulada del año sobre el patrimonio al cierre. La línea punteada corresponde a los establecimientos de crédito."}
```

```grafico
{"id": "solvencia", "tipo": "barras", "indicador": "solvencia", "fecha": "informe", "formato": "tasa", "unidad": "Relación de solvencia total (%)", "titulo": "Relación de solvencia por entidad", "comparadores": ["sis_ec"], "nota": "Las SEDPE no reportan relación de solvencia en este formato."}
```

### Fichas por entidad

```grafico
{"tipo": "fichas"}
```
