## VI. Inclusión y uso

### Depósitos de bajo monto: cuentas, cuentas activas y titulares por sexo
<!-- analisis:dbm -->
Los depósitos de bajo monto son la puerta de entrada al sistema financiero para buena parte de la población. A {{corte}}, las entidades del universo administraban {{v:bm_cuentas:universo:informe:millones}} de estos depósitos, {{part:bm_cuentas:universo:sis_total:informe}} de los del sistema. Las SEDPE concentran {{part:bm_cuentas:grupo_sedpe:universo:informe}} de ellos.

Lo que más distingue al grupo es el uso. {{ratio:bm_activos:bm_cuentas:universo:informe}} de sus depósitos de bajo monto estaban activos, frente a {{ratio:bm_activos:bm_cuentas:sis_ec:informe}} en los establecimientos de crédito. Son cuentas que se usan, no cuentas abiertas y olvidadas.

El saldo promedio fue de {{ratio:bm_cuentas_monto:bm_cuentas:universo:informe:entero}} pesos por depósito, coherente con un producto pensado para pagos y transferencias más que para ahorrar.
<!-- /analisis -->

```grafico
{"id": "bm_cuentas", "tipo": "barras", "indicador": "bm_cuentas", "fecha": "informe", "formato": "millones", "rotulo": "Depósitos de bajo monto por entidad", "titulo": "El grupo administra {{v:bm_cuentas:universo:informe:millones}} de depósitos de bajo monto", "nota": "Incluye los depósitos de bajo monto inclusivos. Información trimestral."}
```

```grafico
{"id": "bm_activos", "tipo": "barras", "ratio": ["bm_activos", "bm_cuentas"], "fecha": "informe", "formato": "pct", "comparadores": ["sis_ec"], "rotulo": "Depósitos de bajo monto activos", "titulo": "{{ratio:bm_activos:bm_cuentas:universo:informe}} de los depósitos de bajo monto del grupo están activos; en los establecimientos de crédito, {{ratio:bm_activos:bm_cuentas:sis_ec:informe}}"}
```

### Titulares por sexo
<!-- analisis:sexo -->
Las mujeres son titulares de {{ratio:bm_mujeres:bm_titulares_sexo:universo:informe}} de los depósitos de bajo monto del universo. En las cuentas de ahorro del grupo la proporción es {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:universo:informe}}, frente a {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:sis_ec:informe}} en los establecimientos de crédito.

La cifra importa porque la brecha de género en el acceso a productos financieros persiste. Los canales digitales pueden reducirla al quitar barreras de desplazamiento y de horario.

La proporción se calcula sobre los titulares con sexo reportado. No se presenta la comparación con el sistema: en el agregado de los establecimientos de crédito, los titulares por sexo no son consistentes con el total de cuentas.
<!-- /analisis -->

```grafico
{"id": "bm_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "rotulo": "Depósitos de bajo monto por sexo del titular", "titulo": "Las mujeres son titulares de {{ratio:bm_mujeres:bm_titulares_sexo:universo:informe}} de los depósitos de bajo monto del grupo",
 "indicadores": [{"id": "bm_mujeres", "nombre": "Mujeres"}, {"id": "bm_hombres", "nombre": "Hombres"}]}
```

```grafico
{"id": "ctas_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "comparadores": ["sis_ec"], "rotulo": "Cuentas de ahorro por sexo del titular", "titulo": "En ahorro, las mujeres tienen {{ratio:ctas_ahorro_mujeres:ctas_ahorro_total:universo:informe}} de las cuentas del grupo",
 "indicadores": [{"id": "ctas_ahorro_mujeres", "nombre": "Mujeres"}, {"id": "ctas_ahorro_hombres", "nombre": "Hombres"}]}
```

### Transacciones de los depósitos de bajo monto
<!-- analisis:dbm_trx -->
En el trimestre que cerró en {{corte}}, los depósitos de bajo monto del universo registraron {{v:bm_trx_total:universo:informe:millones}} de transacciones por {{v:bm_trx_total_monto:universo:informe:billones}}. El valor promedio fue de {{ratio:bm_trx_total_monto:bm_trx_total:universo:informe:entero}} pesos por transacción.

Las transferencias dominan: las recibidas fueron {{ratio:bm_trx_recibo:bm_trx_total:universo:informe}} de las operaciones y las enviadas, {{ratio:bm_trx_envio:bm_trx_total:universo:informe}}. Los pagos sumaron {{ratio:bm_trx_pago:bm_trx_total:universo:informe}} y los retiros apenas {{ratio:bm_trx_retiro:bm_trx_total:universo:informe}}. El dinero circula dentro del sistema digital en lugar de salir a efectivo.
<!-- /analisis -->

```grafico
{"id": "bm_trx", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "comparadores": ["sis_ec"], "rotulo": "Transacciones de los depósitos de bajo monto por tipo", "titulo": "Los retiros son apenas {{ratio:bm_trx_retiro:bm_trx_total:universo:informe}} de las transacciones de bajo monto del grupo",
 "entidades": ["universo", "grupo_sedpe", "grupo_cf"],
 "indicadores": [{"id": "bm_trx_recibo", "nombre": "Transferencias recibidas"}, {"id": "bm_trx_envio", "nombre": "Transferencias enviadas"}, {"id": "bm_trx_pago", "nombre": "Pagos"}, {"id": "bm_trx_deposito", "nombre": "Depósitos"}, {"id": "bm_trx_retiro", "nombre": "Retiros"}],
 "nota": "Número de transacciones reportadas en el trimestre."}
```

### Crédito por sexo
<!-- analisis:credito_sexo -->
En {{anio}}, las mujeres recibieron {{anual:desembolsos_mujer:universo:informe:billones}} en desembolsos de las entidades del universo y los hombres {{anual:desembolsos_hombre:universo:informe:billones}}, sin contar el uso de tarjetas de crédito.
<!-- /analisis -->

```grafico
{"id": "cred_sexo", "tipo": "apiladas", "proporcion": true, "fecha": "informe", "rotulo": "Desembolsos a personas naturales por sexo", "titulo": "Distribución de los desembolsos del mes del corte por sexo",
 "indicadores": [{"id": "desembolsos_mujer", "nombre": "Mujeres"}, {"id": "desembolsos_hombre", "nombre": "Hombres"}]}
```

### Operaciones por canal
<!-- analisis:canales -->
En {{fecha:operaciones}}, las entidades del universo registraron {{v:operaciones:universo:ultimo:millones}} de operaciones por {{v:monto_operaciones:universo:ultimo:billones}} en todos sus canales. La SFC publica los canales con códigos; sus nombres se completarán con el instructivo del formato 444.
<!-- /analisis -->

```grafico
{"id": "canales", "tipo": "canales", "medida": "cantidad", "formato": "millones", "rotulo": "Operaciones por canal", "titulo": "Operaciones del grupo por canal en el último mes disponible"}
```
