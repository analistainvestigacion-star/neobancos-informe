## V. Crédito

```cifras
[{"valor": "{{v:cartera_bruta:universo:informe:billones}}", "texto": "cartera bruta a {{corte}}"},
 {"valor": "{{ratio:cartera_bruta:depositos_total:universo:informe}}", "texto": "de los depósitos se destina a crédito, frente a {{ratio:cartera_bruta:depositos_total:sis_ec:informe}} en el sistema"},
 {"valor": "{{ratio:cartera_vencida:cartera_consumo_dist:universo:informe}}", "texto": "cartera de consumo vencida, frente a {{ratio:cartera_vencida:cartera_consumo_dist:sis_ec:informe}} en el sistema"}]
```

### Cartera por modalidad y crecimiento
<!-- analisis:cartera -->
La cartera bruta del universo sumó {{v:cartera_bruta:universo:informe:billones}} a {{corte}} y {{verbo:cartera_bruta:universo}} {{crec:cartera_bruta:universo}} en el año, frente a {{crec:cartera_bruta:sis_ec}} de los establecimientos de crédito. Es una cartera casi enteramente de consumo ({{ratio:cartera_consumo:cartera_bruta:universo:informe}} del total), con un peso muy alto de la tarjeta de crédito. {{lider:cartera_bruta:informe}} concentra {{conc:cartera_bruta:informe:1}} del saldo.

El dato que más diferencia a este grupo del sistema es la intermediación. Por cada peso captado, las entidades del universo prestan {{ratio:cartera_bruta:depositos_total:universo:informe}}, mientras que los establecimientos de crédito prestan {{ratio:cartera_bruta:depositos_total:sis_ec:informe}}. El resto de los recursos se mantiene en liquidez e inversiones. Esto refleja una etapa en la que la captación avanzó más rápido que la capacidad de originar crédito con riesgo controlado, y señala el espacio que tiene el segmento para crecer en crédito.
<!-- /analisis -->

```grafico
{"id": "cartera_modalidad", "tipo": "apiladas", "fecha": "informe", "formato": "milm", "titulo": "Cartera bruta por modalidad",
 "indicadores": [{"id": "cartera_consumo", "nombre": "Consumo"}, {"id": "cartera_comercial", "nombre": "Comercial"}, {"id": "cartera_microcredito", "nombre": "Microcrédito"}, {"id": "cartera_vivienda", "nombre": "Vivienda"}]}
```

```grafico
{"id": "intermediacion", "tipo": "barras", "ratio": ["cartera_bruta", "depositos_total"], "fecha": "informe", "formato": "pct", "titulo": "Cartera bruta sobre depósitos", "comparadores": ["sis_ec"], "nota": "Solo entidades que otorgan crédito. La línea punteada corresponde a los establecimientos de crédito."}
```

```grafico
{"id": "cartera_serie", "tipo": "lineas", "indicador": "cartera_bruta", "entidades": ["universo", "grupo_cf", "grupo_banco"], "formato": "billones", "titulo": "Evolución de la cartera bruta", "nota": "El salto de 2026 corresponde al inicio de operaciones de Nequi como compañía de financiamiento."}
```

### Calidad de cartera: mora y calificación por riesgo
<!-- analisis:calidad -->
La cartera de consumo vencida representó {{ratio:cartera_vencida:cartera_consumo_dist:universo:informe}} de la cartera de consumo del universo a {{corte}}, frente a {{ratio:cartera_vencida:cartera_consumo_dist:sis_ec:informe}} en los establecimientos de crédito y {{ratio:cartera_vencida:cartera_consumo_dist:sis_cf:informe}} en las compañías de financiamiento. Que la mora del grupo sea comparable o inferior a la del sistema, a pesar de atender a clientes con menos historial crediticio, es una señal de que los modelos de originación digital están funcionando; con todo, una cartera que crece rápido tiende a mostrar una mora menor de la que tendrá cuando madure.

La calificación por riesgo debe leerse con cautela: no todas las entidades la reportan para todos sus productos, y solo {{ratio:cartera_calif_total:cartera_dist_total:universo:informe}} de la cartera del grupo trae calificación. Sobre esa porción, la cartera calificada en categorías B a E fue {{ratio:cartera_calif_be:cartera_calif_total:universo:informe}}, frente a {{ratio:cartera_calif_be:cartera_calif_total:sis_ec:informe}} en los establecimientos de crédito.
<!-- /analisis -->

```grafico
{"id": "icv", "tipo": "barras", "ratio": ["cartera_vencida", "cartera_consumo_dist"], "fecha": "informe", "formato": "pct", "titulo": "Cartera de consumo vencida sobre cartera de consumo", "comparadores": ["sis_ec"], "fuente": "SFC, distribución de cartera por producto"}
```

```grafico
{"id": "icv_serie", "tipo": "lineas", "ratio": ["cartera_vencida", "cartera_consumo_dist"], "entidades": ["universo", "sis_ec", "sis_cf"], "formato": "pct", "titulo": "Evolución de la cartera de consumo vencida", "escala_libre": true, "fuente": "SFC, distribución de cartera por producto"}
```

```grafico
{"id": "calificacion", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Cartera calificada por categoría de riesgo",
 "comparadores": ["sis_ec"],
 "indicadores": [{"id": "cartera_calif_a", "nombre": "A"}, {"id": "cartera_calif_b", "nombre": "B"}, {"id": "cartera_calif_c", "nombre": "C"}, {"id": "cartera_calif_d", "nombre": "D"}, {"id": "cartera_calif_e", "nombre": "E"}],
 "nota": "Solo la cartera con calificación reportada; algunas entidades no la reportan para todos sus productos."}
```

### Desembolsos, número de créditos y tasas frente al sistema
<!-- analisis:desembolsos -->
En {{anio}}, las entidades del universo desembolsaron {{anual:desembolsos:universo:informe:billones}} en {{anual:creditos:universo:informe:millones}} de créditos, sin contar el uso de tarjetas de crédito. La tasa promedio ponderada de los créditos de consumo en {{fecha:tasa_consumo}} fue {{v:tasa_consumo:universo:ultimo:tasa}}, frente a {{v:tasa_consumo:sis_ec:ultimo:tasa}} en los establecimientos de crédito. La diferencia refleja tanto el perfil de riesgo de los clientes como el peso de los créditos de bajo monto y corto plazo.
<!-- /analisis -->

```grafico
{"id": "desembolsos", "tipo": "barras", "indicador": "desembolsos", "anual": "informe", "formato": "milm", "titulo": "Desembolsos del año por entidad (sin tarjetas)"}
```

```grafico
{"id": "tasa_consumo", "tipo": "lineas", "indicador": "tasa_consumo", "entidades": ["universo", "sis_ec", "sis_bancos"], "formato": "tasa", "titulo": "Tasa promedio ponderada de los desembolsos de consumo", "escala_libre": true}
```

### Tarjetas de crédito y débito
<!-- analisis:tarjetas -->
El universo tenía {{v:tarjetas_credito:universo:informe:millones}} de tarjetas de crédito vigentes a {{corte}}, {{part:tarjetas_credito:universo:sis_total:informe}} de las tarjetas de crédito del sistema, y {{v:tarjetas_debito:universo:informe:millones}} de tarjetas débito. En el mes del corte, sus tarjetas de crédito registraron compras nacionales por {{v:tc_compras_monto:universo:informe:milm}}, con un valor promedio de {{ratio:tc_compras_monto:tc_compras_n:universo:informe:entero}} pesos por compra, frente a {{ratio:tc_compras_monto:tc_compras_n:sis_ec:informe:entero}} pesos en el sistema. Tickets más bajos indican un uso más cotidiano de la tarjeta.
<!-- /analisis -->

```grafico
{"id": "tarjetas", "tipo": "apiladas", "fecha": "informe", "formato": "millones", "titulo": "Tarjetas vigentes",
 "indicadores": [{"id": "tarjetas_credito", "nombre": "Crédito"}, {"id": "tarjetas_debito", "nombre": "Débito"}]}
```

```grafico
{"id": "ticket_tc", "tipo": "barras", "ratio": ["tc_compras_monto", "tc_compras_n"], "fecha": "informe", "formato": "miles", "unidad": "Miles de pesos por compra", "titulo": "Valor promedio de las compras con tarjeta de crédito (mes del corte)", "comparadores": ["sis_ec"]}
```
