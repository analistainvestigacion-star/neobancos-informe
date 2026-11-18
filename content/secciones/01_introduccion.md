## I. Introducción y metodología

### Objetivo y alcance
<!-- analisis:intro -->
Este informe mide el tamaño, el crecimiento y el aporte a la inclusión financiera de los neobancos y las billeteras digitales vigiladas por la Superintendencia Financiera de Colombia (SFC). Se trata de entidades que nacieron digitales o que operan principalmente por canales digitales, con licencias de banco, compañía de financiamiento o sociedad especializada en depósitos y pagos electrónicos (SEDPE).

El objetivo es responder cuatro preguntas con cifras oficiales: qué tan grandes son frente al sistema financiero, a cuántas personas atienden y con qué productos, cómo se fondean y cuánto prestan, y qué tan sana es su cartera. Las cifras de esta página se recalculan cada mes con los datos abiertos de la SFC y de Fogafín; los textos de análisis se revisan con cada actualización.
<!-- /analisis -->

### Contexto
<!-- analisis:contexto -->
El segmento digital del sistema financiero colombiano se construyó por tres vías de licencia. La primera es la de banco, que permite captar todo tipo de depósitos y otorgar crédito. La segunda es la de compañía de financiamiento, por la que optaron varias de las entidades más grandes del grupo: también capta y presta, con un capital mínimo menor. La tercera es la SEDPE, creada por la Ley 1735 de 2014 para ofrecer depósitos electrónicos, pagos, giros y transferencias, sin otorgar crédito.

Esta diversidad de licencias explica buena parte de las diferencias que se ven en el informe: las SEDPE concentran clientes de depósitos electrónicos de bajo saldo, mientras que los bancos y las compañías de financiamiento concentran los saldos de ahorro, los CDT y la cartera.
<!-- /analisis -->

### Universo
El universo incluye {{n_ent:activo:informe}} entidades con información a {{corte}}: bancos digitales, compañías de financiamiento digitales y SEDPE. Las entidades que recibieron licencia en 2026 aparecen en las series más recientes, pero no en las comparaciones anuales.

```grafico
{"tipo": "tabla_entidades"}
```

### Fuentes y corte
Las comparaciones anuales usan el corte de {{corte}} frente a {{base}}. Las gráficas de evolución llegan hasta el último dato publicado por cada fuente. Las fuentes son la SFC (CUIF, captaciones por rangos, distribución de cartera, formatos 414, 441 y 444, tarjetas, solvencia e inclusión financiera) y Fogafín (saldos por producto de depósito). Los comparadores del sistema son los establecimientos de crédito (bancos, corporaciones financieras, compañías de financiamiento y cooperativas financieras), los bancos, las compañías de financiamiento y las SEDPE en conjunto.

Daviplata y Pibank operan dentro de la licencia de Davivienda y de Banco Pichincha, respectivamente, por lo que la SFC no publica sus cifras por separado y no hacen parte del universo.

### Definiciones
- **Cliente:** persona natural o jurídica titular de al menos un producto de depósito en la entidad, según el reporte de captaciones por rangos. La suma entre entidades cuenta más de una vez a quien tenga productos en varias.
- **Cuenta:** cada producto de depósito abierto; un cliente puede tener varias cuentas.
- **Cuenta activa:** producto con movimientos en el periodo definido por Fogafín; los demás se clasifican como inactivos o abandonados.
- **Depósito de bajo monto y depósito electrónico:** productos de trámite simplificado, con límites de saldo y de transacciones mensuales, pensados para personas que acceden por primera vez al sistema financiero.
- **Indicador de cartera vencida:** cartera con mora frente a la cartera total del producto.
