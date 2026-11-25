# Neobancos y Billeteras Digitales: datos públicos e informe web

Este repositorio tiene dos partes:

1. **La automatización oficial de datos públicos** (`scripts/neobancos/`), entregada por la dirección de investigaciones en el paquete del 18-nov-2026. Descarga de datos.gov.co las cifras de la SFC y Fogafín para el universo de **asociadas de Colombia Fintech vigiladas por la SFC** (`scripts/neobancos/entidades.csv`), arma el Excel del equipo y los JSON, y los publica en la biblioteca de medios de WordPress. Su documentación completa está en [docs/neobancos/actualizacion_datos_publicos.md](docs/neobancos/actualizacion_datos_publicos.md).
2. **El informe web** (`etl/`, `content/`, `site/`): toma esos datos, calcula los indicadores del informe *Fintech Snapshot 2025: Neobancos y Billeteras Digitales* y los publica como una página que se inserta en WordPress.

## Cómo fluye

```
datos.gov.co ──► scripts/neobancos/extraer.py ──► data/neobancos/raw/<fuente>.csv
                 scripts/neobancos/consolidar.py ─► Excel del equipo + data/neobancos/web/*.json
                 scripts/neobancos/publicar_wp.py ► Medios de colombiafintech.co (si hay secretos de WordPress)
                 etl/ (transformar, validar, publicar) ► site/data/informe.json ──► GitHub Pages ──► página de WordPress
```

Todo corre en un solo flujo de GitHub Actions, `.github/workflows/neobancos.yml`, el día 20 de cada mes (22 en febrero). Al final abre un issue para revisar los textos. `.github/workflows/publicar.yml` vuelve a publicar la página cuando cambian los textos.

## Ampliación de la automatización para el informe web

El paquete original descarga solo las 19 asociadas. El informe web compara al grupo con el sistema financiero, así que se agregaron a `scripts/neobancos/fuentes.py`, sin cambiar las fuentes existentes:

- Dos campos opcionales en `Fuente`: `alcance` ("universo" o "sistema") y `desde` (fecha mínima fija de la fuente). `extraer.py` los respeta.
- Fuentes nuevas con sufijo `_sistema`, que traen todas las entidades de los tipos 1, 2, 4, 32 y 128 desde 2022: CUIF, captaciones, Fogafín (productos y depositantes), inclusión financiera, cartera, tarjetas, formato 441 y formato 414 (desde 2024).
- La fuente `solvencia` (dataset `x586-r5d2`), para el universo y para el sistema.

`etl/fuentes_jefe.py` es el puente: lee esos CSV y los entrega al cálculo del informe.

## Editar el informe

- **Universo:** `scripts/neobancos/entidades.csv` (el mismo de la automatización). Grupos y comparadores del sistema: `config/entidades.yaml`.
- **Textos y gráficas:** `content/secciones/*.md`. Las cifras van como marcadores, por ejemplo `{{v:depositos_total:universo:informe:billones}}`; la lista completa está al inicio de `etl/textos.py`. Las gráficas son bloques ` ```grafico ` con un JSON.
- **Revisión mensual de los textos:** en Claude Code, desde la carpeta CF, `/actualizar-textos-neobancos`. `python -m etl.textos validar` verifica las reglas de la guía de estilo.
- **Nombres de canales del formato 444:** `config/canales_444.yaml` (pendiente).

## Correr localmente

```bash
uv sync
uv run python -m scripts.neobancos.extraer          # todas las fuentes (el 414 tarda horas la primera vez)
uv run python -m scripts.neobancos.consolidar       # Excel y JSON de la automatización
uv run python -m etl.cli todo                       # informe web
uv run python -m http.server 8765 --directory site  # vista previa en http://localhost:8765
```

## Insertar en WordPress

En la página del informe, un bloque **HTML personalizado** con:

```html
<div id="cf-neobancos"></div>
<script src="https://analistainvestigacion-star.github.io/neobancos-informe/embed.js" defer></script>
```
