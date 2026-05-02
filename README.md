# UNGS_informalidad_comparada

## Principio rector

Este proyecto construye una base homogénea de empleo a nivel individuo-empleo, con definición híbrida de informalidad consistente con `argentina_estructura`, usando comparabilidad estricta entre países y años, a partir de microdatos nacionales.

## Estructura del repositorio

```text
/data/
    argentina/
    brasil/
    mexico/
    colombia/

/scripts/
    argentina/
    brasil/
    mexico/
    colombia/
    harmonization/
    checks/

/config/
/outputs/
    harmonized/
    tablas/
/logs/
```

## Flujo de trabajo

1. Procesar país-año en `scripts/<pais>/<pais>_<anio>.py`.
2. Armonizar en `scripts/harmonization/build_harmonized.py`.
3. Validar en `scripts/checks/run_checks.py`.
4. Exportar outputs homogéneos en `outputs/harmonized` y `outputs/tablas`.

## Nota de datos pesados

Las bases pesadas pueden mantenerse fuera de GitHub (por ejemplo OneDrive local) y sincronizarse en `data/` para la ejecución local.


## Referencias operativas verificadas

Este pipeline toma como referencia directa la lógica ya implementada en:

- `precariedad.mundial/scripts/Argentina.R`
- `precariedad.mundial/scripts/Brasil.R`
- `precariedad.mundial/scripts/Mexico.R`
- `precariedad.mundial/scripts/Colombia.R`
- `precariedad.mundial/genera_base_homogenea.R`

Las equivalencias de variables y reglas extraídas de esos scripts están documentadas en `config/country_mappings.yaml`.

## Ruta sugerida para datos pesados (OneDrive)

Para ejecución local en Windows, usar sincronización de datos en:
`C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada\data\...`

