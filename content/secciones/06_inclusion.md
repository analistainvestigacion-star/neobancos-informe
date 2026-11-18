## VI. Inclusión y uso

### Depósitos de bajo monto
<!-- analisis:dbm -->
Los depósitos de bajo monto y los depósitos electrónicos son la puerta de entrada al sistema financiero para buena parte de la población. Según Fogafín, las entidades del universo administraban {{v:dbm_productos:universo:informe:millones}} de depósitos de bajo monto y ordinarios al corte trimestral más cercano a {{corte}}, de los cuales {{ratio:dbm_activos:dbm_productos:universo:informe}} estaban activos. Las SEDPE, que solo pueden ofrecer este tipo de productos, explican la mayor parte de estas cuentas.

La SFC no publica en datos abiertos el desglose por sexo de los titulares de depósitos de bajo monto. Como aproximación, el informe usa las cuentas de ahorro, que sí traen esta información.
<!-- /analisis -->

```grafico
{"id": "dbm", "tipo": "barras", "indicador": "dbm_productos", "fecha": "informe", "formato": "millones", "titulo": "Depósitos de bajo monto y ordinarios por entidad", "nota": "Fogafín publica cortes trimestrales."}
```

### Titulares por sexo
<!-- analisis:sexo -->
Las mujeres son titulares de {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:universo:informe}} de las cuentas de ahorro del universo, frente a {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:sis_ec:informe}} en los establecimientos de crédito. La cifra es relevante porque la brecha de género en el acceso a productos financieros persiste en el país, y los canales digitales pueden reducirla al eliminar barreras de desplazamiento y de horario.
<!-- /analisis -->

```grafico
{"id": "ctas_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Cuentas de ahorro por sexo del titular", "comparadores": ["sis_ec"],
 "indicadores": [{"id": "ctas_ahorro_mujeres", "nombre": "Mujeres"}, {"id": "ctas_ahorro_hombres", "nombre": "Hombres"}],
 "nota": "Aproximación: la SFC no publica en datos abiertos el sexo de los titulares de depósitos de bajo monto."}
```

### Transacciones de los depósitos de bajo monto
<!-- analisis:dbm_trx -->
La SFC no publica en datos abiertos las transacciones de los depósitos de bajo monto por entidad. Esta sección se completará con los anexos del Reporte de Inclusión Financiera y con información de las entidades asociadas. Mientras tanto, la sección de operaciones por canal muestra el uso transaccional de las entidades del universo.
<!-- /analisis -->

### Crédito por sexo
<!-- analisis:credito_sexo -->
En {{anio}}, las mujeres recibieron {{anual:desembolsos_mujer:universo:informe:billones}} en desembolsos de las entidades del universo y los hombres {{anual:desembolsos_hombre:universo:informe:billones}}, sin contar el uso de tarjetas de crédito.
<!-- /analisis -->

```grafico
{"id": "cred_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "titulo": "Desembolsos a personas naturales por sexo (mes del corte)",
 "indicadores": [{"id": "desembolsos_mujer", "nombre": "Mujeres"}, {"id": "desembolsos_hombre", "nombre": "Hombres"}]}
```

### Operaciones por canal
<!-- analisis:canales -->
En {{fecha:operaciones}}, las entidades del universo registraron {{v:operaciones:universo:ultimo:millones}} de operaciones por {{v:monto_operaciones:universo:ultimo:billones}} a través de sus canales.
<!-- /analisis -->

```grafico
{"id": "canales", "tipo": "canales", "medida": "cantidad", "formato": "millones", "titulo": "Operaciones por canal (último mes disponible)"}
```
