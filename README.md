# Informe vivo: Neobancos y Billeteras Digitales

Este repositorio genera el informe web *Fintech Snapshot 2025: Neobancos y Billeteras Digitales* a partir de los datos abiertos de la Superintendencia Financiera de Colombia (SFC) y de Fogafín en datos.gov.co. Cuando las fuentes publican datos nuevos, las cifras, las gráficas y los números dentro de los párrafos se actualizan solos. Los párrafos de análisis se revisan desde Claude Code (sin API de pago) y salen a la web solo cuando alguien del equipo los aprueba.

## Cómo funciona

```
datos.gov.co ──► etl/extract.py ──► data/raw/<fuente>/<AAAA-MM>.parquet   (incremental)
                 etl/transform.py ─► data/processed/indicadores.parquet   (entidad, fecha, indicador, valor)
                 etl/validate.py ──► data/processed/alertas.json          (errores bloquean la publicación)
                 etl/publish.py ───► site/data/informe.json + indicadores.csv
                 etl/textos.py ────► cifras para redactar y validación de los párrafos
site/embed.js ──► se inserta en WordPress y dibuja el informe con los datos de site/data/
```

- **`.github/workflows/actualizar.yml`** corre el día 20 de cada mes a las 7:00 a. m. (la SFC publica la información mensual a mediados de mes) (también se puede correr a mano desde la pestaña Actions). Revisa la fecha de actualización de cada dataset y solo descarga si algo cambió. Si la validación falla, no publica y abre un issue. Si hubo datos nuevos, abre un issue recordando revisar los textos.
- **`.github/workflows/publicar.yml`** publica `site/` en GitHub Pages. Corre después de cada actualización y cuando se aprueba un PR de textos.

## Fuentes (datos.gov.co)

| Fuente | Dataset | Frecuencia | Uso en el informe |
|---|---|---|---|
| CUIF por moneda | `mxk5-ce6w` | mensual | Activos, patrimonio, depósitos y cartera por modalidad |
| Captaciones por rangos | `p22c-4r9c` | mensual | Clientes, cuentas, personas naturales y jurídicas, rangos de saldo |
| Fogafín, saldos por producto | `frdr-biuv` | trimestral (ene, abr, jul, oct) | Cuentas activas e inactivas, depósitos de bajo monto |
| Distribución de cartera | `rvii-eis8` | mensual | Cartera vencida de consumo |
| Formato 414 | `w9zh-vetq` y `qzsc-9esp` | semanal | Desembolsos, número de créditos, tasas, crédito por sexo |
| Formato 441 | `axk9-g2nh` | diaria | Tasas y montos de CDT |
| Tarjetas | `h2jg-r3zg` | mensual | Tarjetas de crédito y débito vigentes |
| Inclusión financiera | `kx2f-xjdq` | trimestral | Cuentas de ahorro por sexo del titular |
| Operaciones por canal (444) | `bzdm-fkaz` | mensual | Operaciones por canal |

Particularidades de las fuentes, ya resueltas en el código:
- El CUIF repite filas idénticas en algunos meses (feb-2024, feb-2026). Se depuran antes de sumar.
- Captaciones por rangos reporta los saldos en miles de pesos. Se convierten a pesos.
- En la distribución de cartera, el renglón 5 es el total de cada producto. Los demás renglones lo desagregan.
- En inclusión financiera, `unicap = 34` es el total nacional. Los demás son departamentos y municipios.
- Fogafín no tiene corte de diciembre. El informe usa el corte trimestral anterior más cercano.
- El 414 tarda unos 6 minutos por mes. Por eso se descarga mes a mes y queda guardado.

## Editar el informe

- **Universo:** `config/entidades.yaml`. Para agregar una entidad, se añade su tipo y código SFC. Las fechas de autorización se diligencian a mano.
- **Textos y gráficas:** `content/secciones/*.md`. Las cifras van como marcadores, por ejemplo `{{v:depositos_total:universo:informe:billones}}`. Las gráficas son bloques de código ` ```grafico ` con un JSON. La lista completa de marcadores está al inicio de `etl/textos.py`.
- **Párrafos de análisis:** son los que están entre `<!-- analisis:id -->` y `<!-- /analisis -->`. Sus cifras se actualizan solas; el análisis se revisa en Claude Code con `/actualizar-textos-neobancos` (abriendo Claude Code en la carpeta CF), que redacta, valida con `python -m etl.textos validar` y propone un PR. No usa la API de pago.
- **Nombres de canales del formato 444:** `config/canales_444.yaml`. Está pendiente de completar con el instructivo de la SFC.

## Correr localmente

```bash
python -m venv .venv && .venv/Scripts/pip install -r requirements.txt
.venv/Scripts/python -m etl.cli todo          # descargar + transformar + validar + publicar
.venv/Scripts/python -m http.server 8765 --directory site   # vista previa en http://localhost:8765
```

## Puesta en marcha en GitHub

1. Crear el repositorio en la cuenta del gremio y subir este código.
2. En *Settings → Pages*, elegir **GitHub Actions** como origen.
3. Opcional: en *Settings → Secrets and variables → Actions*, agregar `SOCRATA_APP_TOKEN` para tener más cupo en datos.gov.co.
4. Correr *Actualizar datos* a mano una vez (con "forzar").

## Insertar en WordPress

En la página del informe, agregar un bloque **HTML personalizado** con:

```html
<div id="cf-neobancos"></div>
<script src="https://analistainvestigacion-star.github.io/neobancos-informe/embed.js" defer></script>
```

Si el tema o un plugin de seguridad elimina las etiquetas `<script>`, se puede usar un iframe:

```html
<iframe src="https://analistainvestigacion-star.github.io/neobancos-informe/" style="width:100%;height:9000px;border:0" loading="lazy"></iframe>
```
