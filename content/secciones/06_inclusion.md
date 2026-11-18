## VI. Inclusión y uso

### Depósitos de bajo monto
<!-- analisis:dbm -->
Según Fogafín, las entidades del universo administraban {{v:dbm_productos:universo:informe:millones}} de depósitos de bajo monto y ordinarios al corte trimestral más cercano a {{corte}}, de los cuales {{ratio:dbm_activos:dbm_productos:universo:informe}} estaban activos.
<!-- /analisis -->

```grafico
{"id": "dbm", "tipo": "barras", "indicador": "dbm_productos", "fecha": "informe", "formato": "millones", "titulo": "Depósitos de bajo monto y ordinarios por entidad", "nota": "Fogafín publica cortes trimestrales."}
```

### Titulares de cuentas de ahorro por sexo
<!-- analisis:sexo -->
Las mujeres son titulares de {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:universo:informe}} de las cuentas de ahorro del universo, frente a {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:sis_ec:informe}} en los establecimientos de crédito.
<!-- /analisis -->

```grafico
{"id": "ctas_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Cuentas de ahorro por sexo del titular",
 "indicadores": [{"id": "ctas_ahorro_mujeres", "nombre": "Mujeres"}, {"id": "ctas_ahorro_hombres", "nombre": "Hombres"}]}
```

### Crédito por sexo
<!-- analisis:credito_sexo -->
En {{anio}}, las mujeres recibieron {{anual:desembolsos_mujer:universo:informe:billones}} en desembolsos de las entidades del universo y los hombres {{anual:desembolsos_hombre:universo:informe:billones}}, sin contar tarjetas de crédito.
<!-- /analisis -->

```grafico
{"id": "cred_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Desembolsos a personas naturales por sexo (mes del corte)",
 "indicadores": [{"id": "desembolsos_mujer", "nombre": "Mujeres"}, {"id": "desembolsos_hombre", "nombre": "Hombres"}]}
```

### Operaciones por canal
```grafico
{"id": "canales", "tipo": "canales", "medida": "cantidad", "formato": "millones", "titulo": "Operaciones por canal (último mes disponible)"}
```
