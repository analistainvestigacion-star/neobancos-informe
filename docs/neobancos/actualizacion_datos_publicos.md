# Actualización automática de los datos públicos del informe de Neobancos

Este documento explica de dónde salen las cifras del informe Fintech Snapshot de Neobancos y
billeteras, cómo se descargan y transforman, y cómo se actualizan solas cada mes en
colombiafintech.co. Está escrito para quien mantenga la automatización: el equipo de
investigaciones o quien administre el repositorio y la página web.

El informe usa solo datos públicos de la Superintendencia Financiera (SFC) y de Fogafín,
publicados en el portal de datos abiertos del Estado (datos.gov.co). No hay encuesta.

## Guía rápida: qué hay que descargar

Todas las descargas son de `https://www.datos.gov.co/resource/<dataset>.json`, filtradas a las
19 entidades de `scripts/neobancos/entidades.csv`. Los tiempos son los observados en noviembre de
2026 sin token de datos.gov.co.

| # | Fuente | Dataset | Periodo | Qué se pide | Tiempo | Estado del paquete del 18-nov-2026 |
|---|---|---|---|---|---|---|
| 1 | Entidades vigiladas | `sr9n-792w` | Actual | Directorio de las 19 entidades | Segundos | Incluida |
| 2 | CUIF (estados financieros) | `mxk5-ce6w` | 2016 en adelante, mensual | Cuentas 100000, 200000, 300000, 590000 y todas las que empiezan por 14 y 21, moneda 0 | ~30 s | Incluida (hasta sep-2026) |
| 3 | Captaciones por rangos | `p22c-4r9c` | 2015 en adelante, mensual | Todas las filas | ~30 s | Incluida (hasta sep-2026) |
| 4 | Fogafín, saldos por producto | `frdr-biuv` | 2018 en adelante, trimestral | Todas las filas | Segundos | Incluida (hasta jul-2026) |
| 5 | Fogafín, depositantes | `uhdk-a4i6` | 2018 en adelante, trimestral | Todas las filas | Segundos | Incluida (hasta jul-2026) |
| 6 | Inclusión financiera | `kx2f-xjdq` | 2021 en adelante, trimestral | Unidades de captura 34 a 45 (nacionales) | ~1 min | Incluida (hasta jun-2026) |
| 7 | Distribución de cartera | `rvii-eis8` | 2015 en adelante, mensual | Todas las filas | ~10 s | Incluida (hasta sep-2026) |
| 8 | Tasas de captación (441) | `axk9-g2nh` | Histórico, diario agregado por mes | Suma de montos y de tasa × monto por mes | ~10 s | Incluida (hasta nov-2026) |
| 9 | Tarjetas | `h2jg-r3zg` | 2015 en adelante, mensual | Todas las filas | ~10 s | Incluida (hasta sep-2026) |
| 10 | Operaciones por canal | `bzdm-fkaz` | 2023 en adelante, mensual | Agregado por canal y servicio | ~10 s | Incluida (hasta jun-2026) |
| 11 | Quejas | `xyy7-rn7p` | Histórico, mensual | Agregado por producto y motivo | ~10 s | Incluida (hasta sep-2026) |
| 12 | Tasas de colocación (414), recientes | `qzsc-9esp` | Últimas ~19 semanas | Agregado por semana, tipo y producto de crédito | ~6 min | Incluida (jul a nov-2026) |
| 13 | Tasas de colocación (414), histórico | `w9zh-vetq` | Jul-2022 a ~sep-2026, semanal (≈218 semanas) | Igual que la 12, una semana por consulta | 1 a 3 min por semana; varias horas en total | **Pendiente** |

**Cómo bajar el histórico del 414 (fuente 13).** Es la única descarga larga. El servidor de
datos.gov.co corta la conexión de vez en cuando (en la primera prueba se cayó en la semana 150
de 218), así que el extractor guarda cada semana en `data/neobancos/raw/_cortes/tasas_colocacion/`
apenas llega y, si se vuelve a correr, solo pide las que faltan. Se corre así, cuantas veces haga
falta hasta que termine sin semanas fallidas:

```bash
NEOBANCOS_HILOS=4 uv run python -m scripts.neobancos.extraer tasas_colocacion
uv run python -m scripts.neobancos.consolidar
```

Conviene hacerlo con un token de datos.gov.co (`SOCRATA_APP_TOKEN`) y en un horario de poco uso
(noche o fin de semana). Una vez descargado, cada actualización mensual solo agrega las semanas
nuevas (`--desde`), que toman pocos minutos.

## 1. Arquitectura

```
datos.gov.co (SFC y Fogafín)
      │  API Socrata (SoQL)
      ▼
scripts/neobancos/extraer.py      → data/neobancos/raw/<fuente>.csv  (copia cruda filtrada)
      ▼
scripts/neobancos/consolidar.py   → Excel + data/neobancos/web/*.json (indicadores, resumen, metadatos)
      ▼
scripts/neobancos/publicar_wp.py  → Biblioteca de medios de colombiafintech.co
      ▼
Página del informe en WordPress   → lee los JSON y dibuja tablas y gráficas
```

Todo corre en GitHub Actions (`.github/workflows/neobancos.yml`) una vez al mes. Cada paso
también se puede correr a mano desde un computador con el repositorio:

```bash
uv sync
uv run python -m scripts.neobancos.extraer            # todas las fuentes
uv run python -m scripts.neobancos.consolidar         # Excel y JSON
uv run python -m scripts.neobancos.publicar_wp --prueba
```

| Archivo | Qué hace |
|---|---|
| `scripts/neobancos/entidades.csv` | Universo: una fila por entidad con su tipo y código SFC. Es lo único que se edita cuando entra o sale una asociada. |
| `scripts/neobancos/fuentes.py` | Definición de cada fuente: dataset, campos, filtros, agregación y notas. |
| `scripts/neobancos/extraer.py` | Descarga con paginación, reintentos y modo incremental. |
| `scripts/neobancos/consolidar.py` | Limpia, convierte unidades, arma indicadores, escribe el Excel y los JSON y valida. |
| `scripts/neobancos/publicar_wp.py` | Sube los JSON a WordPress por la API REST. |
| `.github/workflows/neobancos.yml` | Programación mensual y ejecución manual. |

## 2. Universo y cómo se identifica cada entidad

El universo son las asociadas de Colombia Fintech vigiladas por la SFC. Daviplata, Nequi,
Cobre, Kapital y Tpaga quedan fuera: Daviplata y Nequi no son entidades aparte o no son
asociadas, y las otras tres no son vigiladas.

En todas las fuentes de la SFC una entidad se identifica con dos números: el **tipo de
entidad** (1 = establecimiento bancario, 4 = compañía de financiamiento, 128 = SEDPE) y el
**código de entidad** dentro de ese tipo. Fogafín usa los mismos códigos
(`codigo_tipo_entidad_sfc`, `codigo_entidad_sfc`). El par tipo + código es la llave; el
nombre no sirve porque cambia entre fuentes y en el tiempo.

| Tipo | Entidades (código) |
|---|---|
| 1 Bancos | Lulo Bank 65, Revolut 69 |
| 4 Compañías de financiamiento | Tuya 26, Iris 108, Crezcamos 118, RappiPay 124, Mercado Pago 126, Bold 127, Nu 128, Koa 129, Addi 131, Plata 132 |
| 128 SEDPE | Movii 1, Powwi (Pagos GDE) 2, Dale! 3, Ding (Tecnipagos) 4, Coink 5, Global66 6, StoneX 7 |

La correspondencia entre la marca y el código se hizo por NIT contra el listado de entidades
vigiladas (`sr9n-792w`). Ojo: en HubSpot varias asociadas están registradas con el NIT de la
sociedad matriz (Addi, Bold, Mercado Pago), no con el de la compañía de financiamiento; el
NIT que cuenta aquí es el de la entidad vigilada.

**Cuando entra una asociada nueva o una entidad obtiene licencia:** buscarla en
`https://www.datos.gov.co/resource/sr9n-792w.json?numeroidentificacion=<NIT>` para obtener
tipo y código, y agregar una fila en `entidades.csv` con `incluir=si`. Si sale, se cambia a
`incluir=no` (no se borra, para conservar el rastro). Las entidades que empezaron a operar en
2026 (Revolut, Addi, Plata) ya están; sus series empiezan cuando empiezan a reportar.

**Fusiones y cambios de código:** si la SFC asigna un código nuevo (por ejemplo, una escisión
como la de Nequi de Bancolombia), se agrega una fila nueva y se anota en `nota` desde cuándo
aplica. El código anterior se deja con su fecha para no perder historia.

## 3. Fuentes

Todas se consultan en `https://www.datos.gov.co/resource/<dataset>.json` (API SODA de
Socrata). La ficha de cada una está en `https://www.datos.gov.co/d/<dataset>`.

| Clave | Dataset | Publica | Qué trae | Frecuencia | Notas |
|---|---|---|---|---|---|
| `cuif` | `mxk5-ce6w` | SFC | Estados financieros por cuenta PUC: activo, pasivo, patrimonio, cartera (14) y captaciones (21) | Mensual | En pesos. `moneda`: 0 total, 1 legal, 2 extranjera; se usa 0. Cuentas de 4 dígitos = terminadas en `00`. |
| `captaciones` | `p22c-4r9c` | SFC | Clientes, cuentas y saldo por producto de depósito, por rango de saldo, fuente y tipo de cliente | Mensual | Saldos en **miles de pesos**. `subcuenta` 999 = total de la unidad de captura. |
| `fogafin_productos` | `frdr-biuv` | Fogafín | Número y saldo de productos de depósito por estado (activo, inactivo, abandonado) | Trimestral | Cortes de enero, abril, julio y octubre; **no hay diciembre**. Saldos en miles. |
| `fogafin_depositantes` | `uhdk-a4i6` | Fogafín | Depositantes y saldo por tipo de persona | Trimestral | Mismos cortes; la fecha viene como texto `dd/mm/aaaa`. |
| `inclusion` | `kx2f-xjdq` | SFC | Cuentas de ahorro y depósitos de bajo monto (número, activos, por sexo), créditos por sexo, corresponsales | Trimestral | Solo se traen las unidades nacionales (34 en adelante). Las 1-33 son departamentos y no se suman con ellas. |
| `cartera` | `rvii-eis8` | SFC | Saldo de cartera por producto, vencida por tramos, clientes en mora y calificación A-E | Mensual | Solo entidades que otorgan crédito. |
| `tasas_colocacion` | `w9zh-vetq` | SFC | Formato 414: montos y número de desembolsos y tasa por tipo y producto de crédito | Semanal | Histórico; llega hasta dos meses antes del último corte. Muy pesado. |
| `tasas_colocacion_recientes` | `qzsc-9esp` | SFC | Formato 414, últimos dos meses | Semanal | Completa las semanas que aún no están en el histórico. |
| `tasas_captacion` | `axk9-g2nh` | SFC | Formato 441: tasas y montos de CDT y CDAT y saldos de captación | Diaria | Se agrega por mes. |
| `tarjetas` | `h2jg-r3zg` | SFC | Tarjetas de crédito y débito vigentes, activas y canceladas | Mensual | |
| `canales` | `bzdm-fkaz` | SFC | Número y monto de operaciones por canal y servicio transaccional | Mensual | Campos en códigos; se interpretan con la guía de reporte de la SFC. Publicación irregular. |
| `quejas` | `xyy7-rn7p` | SFC | Quejas por producto y motivo | Mensual | El último mes publicado viene incompleto y se descarta. |
| `entidades_sfc` | `sr9n-792w` | SFC | Directorio de entidades vigiladas | Continua | Para conciliar NIT, tipo y código. |

Fuentes que ya no sirven y no se deben usar: `7jfv-7spn` (montos por cosechas, descontinuada
en 2025), `bn4c-kptq` (formato 444, reemplazado por `bzdm-fkaz` en 2023), formato 088
(reemplazado por el 414 desde julio de 2022) y `ptgf-ywrb` (inclusión financiera hasta 2020).

## 4. Cómo se consulta (SoQL)

Cada consulta filtra el universo con una condición por tipo de entidad:

```
$where=((tipo_entidad='1' AND codigo_entidad in ('65','69'))
     OR (tipo_entidad='128' AND codigo_entidad in ('1','2','3','4','5','6','7'))
     OR (tipo_entidad='4' AND codigo_entidad in ('26','108',...)))
```

Hay tres modos, definidos en `fuentes.py`:

- **filas**: trae las filas tal cual, ordenadas, en páginas de 50.000 (`$limit` y `$offset`)
  hasta que una página llega incompleta.
- **agregado**: la API suma antes de entregar (`$select` con `sum(...)` y `$group`). Se usa en
  canales, quejas y tasas de captación, que traen detalle municipal o diario que el informe
  no necesita. Ejemplo de tasas de captación por mes:

  ```
  $select=tipoentidad,codigoentidad,date_trunc_ym(fechacorte) as mes,uca,subcuenta,
          sum(monto) as monto_total,sum(tasa * monto) as tasa_por_monto
  $group=tipoentidad,codigoentidad,date_trunc_ym(fechacorte),uca,subcuenta
  ```

  Un alias no puede tener el mismo nombre que una columna (`sum(monto) as monto` da error 400).
- **por_fecha**: para el formato 414, que tiene millones de filas y no responde a consultas
  amplias. Primero se listan las fechas de corte (`$select=distinct fecha_corte`) y luego se
  pide cada semana agregada, varias en paralelo (`NEOBANCOS_HILOS`, 6 por defecto). Cada
  semana tarda de 1 a 3 minutos y se guarda en `data/neobancos/raw/_cortes/<fuente>/<fecha>.csv`
  apenas llega; una corrida interrumpida se retoma donde quedó. Si alguna semana falla, la fuente
  queda marcada con error en `_extraccion.json` y basta con volver a correr.

**Límites y token.** Sin token, datos.gov.co limita las consultas por dirección IP. Para la
automatización conviene crear un token de aplicación gratuito en datos.gov.co
(Perfil > Developer settings) y guardarlo como `SOCRATA_APP_TOKEN`. Los reintentos esperan
10, 20 y 30 segundos; un error 400 no se reintenta porque significa que la consulta está mal.

**Modo incremental.** `extraer.py --desde AAAA-MM-DD <fuente>` descarga solo desde esa fecha y
conserva lo que ya estaba en el CSV antes de ella. El workflow lo usa para el formato 414
(últimos tres meses) y guarda el histórico en el repositorio, así que no hay que bajar todo
el 414 cada mes. Las demás fuentes se descargan completas porque tardan poco y la SFC a veces
corrige meses anteriores.

## 5. Transformaciones (consolidar.py)

- **Entidad**: a cada fila se le agrega la marca y el tipo según `entidades.csv`.
- **Fechas**: todas se normalizan a `AAAA-MM-DD` en la columna `corte`. El 414 semanal se
  agrega por mes (`corte` = último día del mes).
- **Unidades**: captaciones y Fogafín publican saldos en miles de pesos; se multiplican por
  1.000 para que todo quede en pesos. El CUIF ya viene en pesos.
- **Valores no numéricos**: `N/A` y vacíos se tratan como dato faltante, no como cero.
- **Indicadores clave** (hoja y archivo `indicadores`), en formato largo
  (entidad, tipo, corte, indicador, valor, unidad, fuente, dataset):
  - CUIF: activo, pasivo, patrimonio, resultado del ejercicio, cartera neta (140000) y cada
    producto de captación (210500 cuenta corriente, 210700 CDT, 210800 ahorro, 211600
    especiales, 212000 electrónicos), más "Depósitos totales (CUIF)" = suma de esas cinco.
  - Captaciones: clientes, cuentas y saldo por producto desde la unidad 2 (fuente de
    captación), subcuenta 999; si falta, unidad 1 o 5. "Clientes de depósito (suma por
    producto)" suma clientes de cada producto y por eso puede contar dos veces a la misma
    persona.
  - Fogafín: depositantes y productos activos.
  - 414: desembolsos, número de créditos y tasa ponderada por tipo de crédito y mes
    (tasa ponderada = suma de tasa × monto / suma de monto).
- **Quejas**: si el último mes tiene menos de la mitad de las filas de los meses anteriores
  se descarta, porque la SFC lo publica incompleto.

Salidas:

| Archivo | Uso |
|---|---|
| `data/neobancos/Datos públicos Neobancos – SFC y Fogafín.xlsx` | Trabajo del equipo. Hojas: Léeme, Resumen (fórmulas SUMIFS sobre Indicadores), Entidades, Indicadores, una por fuente y Fuentes. |
| `data/neobancos/web/indicadores.json` / `.csv` | Serie completa para la página. |
| `data/neobancos/web/resumen.json` | Por entidad e indicador: último corte y valor de cada diciembre. |
| `data/neobancos/web/metadatos.json` | Fuentes, último corte, fecha de generación y universo. |
| `data/neobancos/web/validacion.json` | Entidades esperadas frente a encontradas en cada fuente. |

## 6. Validaciones

`consolidar.py` escribe `validacion.json` e imprime, por fuente, cuántas entidades del
universo trajo y cuáles faltan. Antes de publicar conviene revisar:

1. **Entidades faltantes que antes estaban.** Es normal que falten las que no reportan esa
   fuente (las SEDPE no tienen cartera ni 414; StoneX solo aparece en el CUIF; Revolut, Addi y
   Plata no tienen datos antes de 2026). Si desaparece una entidad que el mes anterior estaba,
   puede ser un cambio de código.
2. **Último corte.** En `metadatos.json` el `ultimo_corte` de las fuentes mensuales debe
   haber avanzado un mes respecto a la corrida anterior. Si no avanzó, la SFC no ha publicado
   y no hace falta publicar.
3. **Saltos atípicos.** Un indicador que cambia más de 50 % frente al mes anterior merece una
   mirada (suele ser una corrección o un cambio de metodología, no un error).
4. **Valores de control** (verificados en noviembre de 2026, corte dic-2025): Nu, depósitos de
   ahorro ≈ COP 6,02 billones y CDT ≈ COP 3,46 billones; Movii, depósitos electrónicos ≈
   COP 94.200 millones.

## 7. Cuándo actualizar

**Día recomendado: el 20 de cada mes (el 22 en febrero).**

La SFC publica las cifras mensuales según un calendario oficial ("Calendario de publicación"
del Informe de actualidad del sistema financiero colombiano):
https://www.superfinanciera.gov.co/publicaciones/10086637/

- Las entidades transmiten el CUIF durante los primeros 20 días comunes del mes siguiente al
  de reporte; el cierre de diciembre tiene 10 días adicionales.
- La SFC publica el corte del mes M hacia el **día 15 a 19 del mes M+2**. Los datasets
  mensuales de datos.gov.co (CUIF, cartera, captaciones, tarjetas y quejas) se cargan el mismo
  día. Ejemplo verificado: el corte de septiembre de 2026 se publicó el 17 de noviembre de
  2026 y ese día se actualizaron los cinco datasets.
- El corte de diciembre sale más tarde, hacia el 19 o 20 de febrero.

Calendario 2026 (mes de corte → fecha de publicación): enero → 16-mar, febrero → 17-abr,
marzo → 19-may, abril → 17-jun, mayo → 17-jul, junio → 18-ago, julio → 17-sep,
agosto → 16-oct, septiembre → 17-nov, octubre → 17-dic, noviembre → 18-ene-2027,
diciembre → 19-feb-2027. En 2025 las fechas estuvieron entre el 14 y el 20.

Por eso el workflow corre el día 20 (el 22 en febrero), a las 06:00 de Bogotá: deja uno o dos
días de margen sobre la fecha más tardía del calendario. Conviene revisar el calendario cada
enero, cuando la SFC publica el del año.

Fuentes que no siguen ese calendario:

| Fuente | Cuándo aparece el dato nuevo | Implicación |
|---|---|---|
| Formato 414 (`qzsc-9esp`) | Corte del viernes, publicado el viernes siguiente | La corrida mensual trae las semanas hasta unos 7 días antes. Si se quiere semanal, agregar un `cron` los sábados solo para el 414. |
| Formato 441 (`axk9-g2nh`) | 1 o 2 días hábiles después | El mes en curso queda parcial; usar solo meses completos. |
| Inclusión financiera (`kx2f-xjdq`) | Trimestre que cierra en M, hacia el día 10 de M+3 | Se toma en la corrida del mes en que aparezca. |
| Fogafín (`frdr-biuv`, `uhdk-a4i6`) | Unos 3 meses después del corte; cortes de enero, abril, julio y octubre | Para "diciembre" usar octubre o enero y decirlo en la metodología. |
| Canales (`bzdm-fkaz`) | Irregular: en noviembre de 2026 el último corte era junio | No bloquear la publicación por esta fuente. |

Una alternativa más robusta que la fecha fija es correr el workflow todos los días entre el 14
y el 23 y publicar solo cuando el `ultimo_corte` del CUIF cambie respecto a la corrida
anterior (se lee de `data/neobancos/raw/_extraccion.json`, que queda en el repositorio).

## 8. Automatización con GitHub Actions

El archivo `.github/workflows/neobancos.yml` hace, en orden:

1. Instala Python 3.12 y las dependencias con uv.
2. Extrae las fuentes livianas (todas menos el 414).
3. Extrae el 414 histórico de forma incremental (últimos tres meses) y las semanas recientes.
4. Consolida y valida.
5. Guarda el Excel y los JSON como *artifact* de la corrida (se descargan desde la pestaña
   Actions durante 90 días).
6. Hace commit del histórico del 414 y del registro de extracción en el repositorio.
7. Publica en WordPress.

También se puede correr a mano (Actions > neobancos-datos-publicos > Run workflow), indicando
una fecha `desde` para el 414 (vacío = últimos tres meses) y si se publica o no.

**Para activarlo:**

1. Subir el repositorio `cf-mcp` a GitHub (hoy es una carpeta local sin git). Mientras tanto,
   el workflow es una plantilla lista.
2. La primera vez, descargar el 414 completo en local
   (`uv run python -m scripts.neobancos.extraer tasas_colocacion`, toma horas) y hacer commit de
   `data/neobancos/raw/tasas_colocacion.csv`. Desde ahí cada corrida solo agrega meses.
3. Crear los secretos en Settings > Secrets and variables > Actions:

| Secreto | Para qué |
|---|---|
| `SOCRATA_APP_TOKEN` | Token de datos.gov.co (opcional pero recomendado) |
| `WP_URL` | `https://colombiafintech.co` |
| `WP_USER` | Usuario de WordPress con permiso para subir medios |
| `WP_APP_PASSWORD` | Contraseña de aplicación de ese usuario (no la contraseña normal) |

4. Dar permiso de escritura al workflow (Settings > Actions > General > Workflow
   permissions > Read and write), necesario para el commit del paso 6.

## 9. Publicación en colombiafintech.co

`publicar_wp.py` sube `indicadores.json`, `resumen.json` y `metadatos.json` a la biblioteca de
medios con los nombres `neobancos-indicadores.json`, `neobancos-resumen.json` y
`neobancos-metadatos.json`. Antes de subir borra la versión anterior para que el nombre no
cambie (WordPress agregaría `-1`, `-2`). Las URL quedan del tipo
`https://colombiafintech.co/wp-content/uploads/<año>/<mes>/neobancos-resumen.json`; como la
carpeta de año y mes cambia, la página debe buscar la URL vigente por nombre:

```js
// En la página del informe (bloque HTML personalizado o plugin de gráficas)
const r = await fetch('/wp-json/wp/v2/media?search=neobancos-resumen&per_page=1');
const [medio] = await r.json();
const datos = await (await fetch(medio.source_url)).json();
// datos[entidad][indicador] = {ultimo: {corte, valor}, diciembres: {"2024": v, "2025": v}, unidad}
```

Requisitos en WordPress:

- Permitir la carga de archivos `.json` en Medios (por defecto WordPress los bloquea; se
  habilita con un plugin de tipos MIME o con el filtro `upload_mimes` en el tema hijo).
- Un usuario de servicio (no personal) con rol Autor o Editor y una contraseña de aplicación.
- La página del informe con un bloque que lea los JSON. La fecha de actualización se toma de
  `metadatos.json` (`generado` y `ultimo_corte` de cada fuente) y debe mostrarse en la página.

**Alternativa sin JavaScript**: un endpoint propio en el tema o un plugin
(`register_rest_route`) que reciba el JSON y lo guarde como opción de WordPress; la página lo
muestra con un shortcode. Es más trabajo de desarrollo pero no depende de la biblioteca de
medios.

**Respaldo manual**: si la automatización falla, descargar el *artifact* de la última corrida
en GitHub (o correr los tres comandos de la sección 1 en local) y subir los tres JSON a Medios
a mano con los mismos nombres.

## 10. Mantenimiento

- **Cambio de columnas en una fuente**: `extraer.py` falla con un error 400 que cita la
  columna. Revisar la ficha del dataset (`/api/views/<id>.json` lista los campos) y ajustar
  `fuentes.py`.
- **Dataset reemplazado**: la SFC a veces crea un dataset nuevo y deja de actualizar el
  anterior (pasó con formato 444 → `bzdm-fkaz` y con inclusión financiera 2020 → 2021). Si el
  `ultimo_corte` de una fuente no avanza en tres meses, buscar en datos.gov.co si hay uno
  nuevo.
- **Cambios de PUC**: si la SFC cambia el catálogo de cuentas, revisar `CUENTAS_CLAVE` y
  `DEPOSITOS` en `consolidar.py`.
- **Nueva fuente**: agregar una entrada en `FUENTES` (`fuentes.py`); `extraer.py` la descarga
  sin más cambios y `consolidar.py` la escribe como hoja si se agrega a la lista `simples`.

**Lo que no se puede obtener de fuentes públicas** (y por eso no está en el informe):
Daviplata y Nequi como entidades separadas en 2025; usuarios activos al mes con definición
propia (solo hay cuentas activas según la SFC); clientes únicos entre entidades; Bre-B por
entidad (el Banco de la República publica solo totales del sistema); transacciones por flujo
(P2P, pagos a comercios, recargas); y fraude por entidad. Bre-B por entidad, flujos e
inclusión de usuarios de pagos se piden en el bloque de vigiladas del formulario de Pagos.
