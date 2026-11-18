## II. Las entidades

### Tamaño: activos y patrimonio

```cifras
[{"valor": "{{v:activo:universo:informe:billones}}", "texto": "activos totales a {{corte}}"},
 {"valor": "{{crec:activo:universo}}", "texto": "variación anual de los activos"},
 {"valor": "{{part:activo:universo:sis_ec:informe}}", "texto": "de los activos de los establecimientos de crédito"}]
```

<!-- analisis:tamano -->
Los activos de las entidades del universo sumaron {{v:activo:universo:informe:billones}} a {{corte}} y {{verbo:activo:universo}} {{crec:activo:universo}} frente a {{base}}. {{lider:activo:informe}} es la entidad con mayores activos. El patrimonio conjunto llegó a {{v:patrimonio:universo:informe:billones}}.
<!-- /analisis -->

```grafico
{"id": "activos", "tipo": "barras", "indicador": "activo", "fecha": "informe", "formato": "milm", "titulo": "Activos por entidad"}
```

```grafico
{"id": "activos_serie", "tipo": "lineas", "indicador": "activo", "entidades": ["grupo_banco", "grupo_cf", "grupo_sedpe"], "formato": "billones", "titulo": "Evolución de los activos por grupo"}
```

```grafico
{"id": "patrimonio", "tipo": "barras", "indicador": "patrimonio", "fecha": "informe", "formato": "milm", "titulo": "Patrimonio por entidad"}
```
