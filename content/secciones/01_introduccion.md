## I. Introducción y metodología

### En síntesis
<!-- analisis:sintesis -->
Los neobancos y las billeteras digitales vigiladas por la Superintendencia Financiera de Colombia (SFC) siguen siendo un segmento pequeño frente al sistema, pero crecen varias veces más rápido. Atienden a millones de personas, en buena parte con depósitos de bajo monto, y captan mucho más de lo que prestan.
<!-- /analisis -->

```cifras
[{"valor": "{{v:activo:universo:informe:billones}}", "texto": "activos a {{corte}} ({{n_ent:activo:informe}} entidades)"},
 {"valor": "{{crec:activo:universo}}", "texto": "crecimiento anual de los activos (establecimientos de crédito: {{crec:activo:sis_ec}})"},
 {"valor": "{{v:depositos_total:universo:informe:billones}}", "texto": "depósitos a {{corte}} ({{part:depositos_total:universo:sis_total:informe}} del sistema)"},
 {"valor": "{{v:bm_cuentas:universo:informe:millones}}", "texto": "depósitos de bajo monto a {{corte}} ({{ratio:bm_activos:bm_cuentas:universo:informe}} activos)"},
 {"valor": "{{ratio:cartera_bruta:depositos_total:universo:informe}}", "texto": "de los depósitos se presta (establecimientos de crédito: {{ratio:cartera_bruta:depositos_total:sis_ec:informe}})"}]
```

### Objetivo y alcance
<!-- analisis:intro -->
Este informe mide el tamaño, el crecimiento y el aporte a la inclusión financiera de los neobancos y las billeteras digitales vigiladas por la SFC. Responde cuatro preguntas con cifras oficiales: qué tan grandes son frente al sistema, a cuántas personas atienden, cómo se fondean y cuánto prestan, y qué tan sana es su cartera.

Las cifras se recalculan cada mes con los datos abiertos de la SFC y de Fogafín. Los textos de análisis se revisan con cada actualización.
<!-- /analisis -->

### Contexto
<!-- analisis:contexto -->
El segmento digital se construyó por tres vías de licencia. La de banco permite captar todo tipo de depósitos y prestar. La de compañía de financiamiento también capta y presta, con un capital mínimo menor, y es la que eligieron varias de las entidades más grandes del grupo.

La tercera es la sociedad especializada en depósitos y pagos electrónicos (SEDPE), creada por la Ley 1735 de 2014 del Congreso de la República. Puede ofrecer depósitos electrónicos, pagos, giros y transferencias, pero no otorgar crédito. Esta diferencia de licencias explica buena parte de los contrastes que muestra el informe.
<!-- /analisis -->

### Universo
El universo incluye {{n_ent:activo:informe}} entidades con información a {{corte}}: bancos digitales, compañías de financiamiento digitales y SEDPE. Las entidades con licencia de 2026 aparecen en las series recientes, no en las comparaciones anuales.

```grafico
{"tipo": "tabla_entidades"}
```

### Fuentes, corte y comparabilidad
<!-- analisis:metodologia -->
Las comparaciones anuales usan el corte de {{corte}} frente a {{base}}; las series llegan hasta el último dato publicado. Las fuentes son la SFC (CUIF, captaciones por rangos, distribución de cartera, formatos 414, 441 y 444, tarjetas, solvencia e inclusión financiera) y Fogafín (productos y depositantes).

El sistema de referencia son los establecimientos de crédito: bancos, corporaciones financieras, compañías de financiamiento y cooperativas financieras. Las participaciones se calculan además sobre el sistema con las SEDPE incluidas.

Tres advertencias de comparabilidad. Fogafín publica cortes trimestrales sin diciembre, por lo que se usa el más cercano anterior. Inclusión financiera es trimestral. La calificación por riesgo no se reporta para toda la cartera. Daviplata y Pibank operan dentro de Davivienda y Banco Pichincha y no se publican por separado.
<!-- /analisis -->

### Definiciones
- **Cliente:** titular de al menos un producto de depósito en la entidad, según captaciones por rangos. La suma entre entidades cuenta más de una vez a quien tenga productos en varias.
- **Depositante:** persona con al menos un depósito en la entidad, según Fogafín; no se repite entre productos de la misma entidad.
- **Cuenta activa:** producto con movimientos en el periodo definido por cada fuente (Fogafín o SFC).
- **Depósito de bajo monto:** producto de trámite simplificado, con límites de saldo y de transacciones mensuales.
- **Indicador de cartera vencida:** cartera con mora frente a la cartera total del producto.
