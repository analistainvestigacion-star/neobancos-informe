## V. Crédito

### Cartera por modalidad y crecimiento
<!-- analisis:cartera -->
La cartera bruta del universo sumó {{v:cartera_bruta:universo:informe:billones}} a {{corte}} y {{verbo:cartera_bruta:universo}} {{crec:cartera_bruta:universo}} en el año, frente a {{crec:cartera_bruta:sis_ec}} de los establecimientos de crédito. Es casi toda de consumo ({{ratio:cartera_consumo:cartera_bruta:universo:informe}}), con un peso muy alto de la tarjeta de crédito.

El rasgo que más distingue al grupo es la baja intermediación. Por cada peso captado presta {{ratio:cartera_bruta:depositos_total:universo:informe}}; los establecimientos de crédito prestan {{ratio:cartera_bruta:depositos_total:sis_ec:informe}}. El resto de los recursos se mantiene en liquidez e inversiones.

La brecha indica que la captación avanzó más rápido que la capacidad de originar crédito con riesgo controlado. También muestra el espacio que tiene el segmento para crecer en crédito.
<!-- /analisis -->

```grafico
{"id": "cartera_modalidad", "tipo": "apiladas", "fecha": "informe", "formato": "milm", "rotulo": "Cartera bruta por modalidad", "titulo": "El consumo es {{ratio:cartera_consumo:cartera_bruta:universo:informe}} de la cartera del grupo",
 "indicadores": [{"id": "cartera_consumo", "nombre": "Consumo"}, {"id": "cartera_comercial", "nombre": "Comercial"}, {"id": "cartera_microcredito", "nombre": "Microcrédito"}, {"id": "cartera_vivienda", "nombre": "Vivienda"}]}
```

```grafico
{"id": "intermediacion", "tipo": "barras", "ratio": ["cartera_bruta", "depositos_total"], "fecha": "informe", "formato": "pct", "comparadores": ["sis_ec"], "rotulo": "Cartera bruta sobre depósitos", "titulo": "El grupo presta {{ratio:cartera_bruta:depositos_total:universo:informe}} de lo que capta; los establecimientos de crédito, {{ratio:cartera_bruta:depositos_total:sis_ec:informe}}", "nota": "Solo entidades que otorgan crédito. La línea punteada corresponde a los establecimientos de crédito."}
```

```grafico
{"id": "cartera_serie", "tipo": "lineas", "indicador": "cartera_bruta", "entidades": ["universo", "grupo_cf", "grupo_banco"], "formato": "billones", "rotulo": "Evolución de la cartera bruta", "titulo": "La cartera del grupo llegó a {{v:cartera_bruta:universo:ultimo:billones}} en {{fecha:cartera_bruta}}"}
```

### Calidad de cartera: mora y calificación por riesgo
<!-- analisis:calidad -->
La cartera de consumo vencida fue {{ratio:cartera_vencida:cartera_consumo_dist:universo:informe}} de la cartera de consumo del universo a {{corte}}. En los establecimientos de crédito fue {{ratio:cartera_vencida:cartera_consumo_dist:sis_ec:informe}} y en las compañías de financiamiento, {{ratio:cartera_vencida:cartera_consumo_dist:sis_cf:informe}}.

Es una señal de que la originación digital funciona, aunque se dirige a clientes con menos historial crediticio. Con todo, una cartera que crece rápido muestra menos mora de la que tendrá cuando madure.

La calificación por riesgo debe leerse con cautela: solo {{ratio:cartera_calif_total:cartera_dist_total:universo:informe}} de la cartera del grupo la reporta. Sobre esa porción, las categorías B a E suman {{ratio:cartera_calif_be:cartera_calif_total:universo:informe}}, frente a {{ratio:cartera_calif_be:cartera_calif_total:sis_ec:informe}} en los establecimientos de crédito.
<!-- /analisis -->

```grafico
{"id": "icv", "tipo": "barras", "ratio": ["cartera_vencida", "cartera_consumo_dist"], "fecha": "informe", "formato": "pct", "comparadores": ["sis_ec"], "fuente": "SFC, distribución de cartera por producto", "rotulo": "Cartera de consumo vencida", "titulo": "La mora de consumo del grupo ({{ratio:cartera_vencida:cartera_consumo_dist:universo:informe}}) frente a la de los establecimientos de crédito ({{ratio:cartera_vencida:cartera_consumo_dist:sis_ec:informe}})"}
```

```grafico
{"id": "icv_serie", "tipo": "lineas", "ratio": ["cartera_vencida", "cartera_consumo_dist"], "entidades": ["universo", "sis_ec", "sis_cf"], "formato": "pct", "escala_libre": true, "fuente": "SFC, distribución de cartera por producto", "rotulo": "Evolución de la cartera de consumo vencida", "titulo": "Mora de consumo: {{ratio:cartera_vencida:cartera_consumo_dist:universo:ultimo}} en el grupo y {{ratio:cartera_vencida:cartera_consumo_dist:sis_cf:ultimo}} en las compañías de financiamiento ({{fecha:cartera_vencida}})"}
```

```grafico
{"id": "calificacion", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "comparadores": ["sis_ec"], "rotulo": "Cartera calificada por categoría de riesgo", "titulo": "Solo {{ratio:cartera_calif_total:cartera_dist_total:universo:informe}} de la cartera del grupo reporta calificación por riesgo",
 "indicadores": [{"id": "cartera_calif_a", "nombre": "A"}, {"id": "cartera_calif_b", "nombre": "B"}, {"id": "cartera_calif_c", "nombre": "C"}, {"id": "cartera_calif_d", "nombre": "D"}, {"id": "cartera_calif_e", "nombre": "E"}],
 "nota": "Solo la cartera con calificación reportada; algunas entidades no la reportan para todos sus productos."}
```

### Desembolsos, número de créditos y tasas frente al sistema
<!-- analisis:desembolsos -->
En {{anio}}, las entidades del universo desembolsaron {{anual:desembolsos:universo:informe:billones}} en {{anual:creditos:universo:informe:miles}} créditos, sin contar el uso de tarjetas de crédito.

La tasa promedio ponderada de los créditos de consumo fue {{v:tasa_consumo:universo:ultimo:tasa}} en {{fecha:tasa_consumo}}, frente a {{v:tasa_consumo:sis_ec:ultimo:tasa}} en los establecimientos de crédito. La diferencia refleja el perfil de riesgo de los clientes y el peso de los créditos de bajo monto y corto plazo.
<!-- /analisis -->

```grafico
{"id": "desembolsos", "tipo": "barras", "indicador": "desembolsos", "anual": "informe", "formato": "milm", "rotulo": "Desembolsos del año por entidad (sin tarjetas)", "titulo": "Desembolsos de crédito del grupo por entidad en {{anio}}"}
```

```grafico
{"id": "tasa_consumo", "tipo": "lineas", "indicador": "tasa_consumo", "entidades": ["universo", "sis_ec", "sis_bancos"], "formato": "tasa", "escala_libre": true, "rotulo": "Tasa de los desembolsos de consumo", "titulo": "El crédito de consumo del grupo cuesta {{v:tasa_consumo:universo:ultimo:tasa}}; el de los establecimientos de crédito, {{v:tasa_consumo:sis_ec:ultimo:tasa}}"}
```

### Tarjetas de crédito y débito
<!-- analisis:tarjetas -->
El universo tenía {{v:tarjetas_credito:universo:informe:millones}} de tarjetas de crédito vigentes a {{corte}}, {{part:tarjetas_credito:universo:sis_total:informe}} de las del sistema, y {{v:tarjetas_debito:universo:informe:millones}} de tarjetas débito.

En el mes del corte, el valor promedio de una compra con sus tarjetas de crédito fue de {{ratio:tc_compras_monto:tc_compras_n:universo:informe:entero}} pesos, frente a {{ratio:tc_compras_monto:tc_compras_n:sis_ec:informe:entero}} pesos en el sistema. Tickets más bajos indican un uso más cotidiano de la tarjeta.
<!-- /analisis -->

```grafico
{"id": "tarjetas", "tipo": "apiladas", "fecha": "informe", "formato": "millones", "rotulo": "Tarjetas vigentes", "titulo": "El grupo tiene {{v:tarjetas_credito:universo:informe:millones}} de tarjetas de crédito vigentes",
 "indicadores": [{"id": "tarjetas_credito", "nombre": "Crédito"}, {"id": "tarjetas_debito", "nombre": "Débito"}]}
```

```grafico
{"id": "ticket_tc", "tipo": "barras", "ratio": ["tc_compras_monto", "tc_compras_n"], "fecha": "informe", "formato": "miles", "unidad": "Miles de pesos por compra", "comparadores": ["sis_ec"], "rotulo": "Valor promedio de las compras con tarjeta de crédito", "titulo": "Una compra con tarjeta de crédito del grupo vale en promedio {{ratio:tc_compras_monto:tc_compras_n:universo:informe:miles}} pesos"}
```
