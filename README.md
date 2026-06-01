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


## Orden de ejecución recomendado

1. Ejecutar cada script país-año (por ejemplo `python scripts/argentina/argentina_2018.py`).
2. Ejecutar armonización consolidada: `python scripts/harmonization/build_harmonized.py`.
3. Ejecutar validaciones: `python scripts/checks/run_checks.py`.

Nota: cada script país-año exporta `outputs/harmonized/<COUNTRY>_<YEAR>.parquet`.

## Insumos Brasil / PNAD Contínua

El pipeline **no descarga automáticamente** microdatos de IBGE y **no espera** que los `.txt` estén dentro de `PNADcIBGE-master`. Ese paquete/proyecto sirve como referencia para descarga/lectura en R, pero los datos crudos deben estar sincronizados localmente bajo `data/brasil/`.

La ruta esperada por `scripts/common_pipeline.py` es una carpeta por trimestre con este patrón:

```text
data/brasil/
    PNADC_012018_*/
        PNADC_012018.txt
    PNADC_022018_*/
        PNADC_022018.txt
    PNADC_032018_*/
        PNADC_032018.txt
    PNADC_042018_*/
        PNADC_042018.txt
```

Para 2023 se usa el mismo criterio, por ejemplo `data/brasil/PNADC_012023_*/PNADC_012023.txt`.

Por compatibilidad, si dentro de una carpeta trimestral existe `input_PNADC*.txt` en lugar de `PNADC_*.txt`, el pipeline también lo acepta. En todos los casos, cada carpeta detectada equivale a un trimestre y el ponderador esperado es `V1028`.
