# Etapa 2 - ampliacion del pipeline, auditoria y cuadros comparados

## Alcance

Esta etapa mantiene la arquitectura existente: la armonizacion de microdatos queda centralizada en `scripts/common_pipeline.py`. Los scripts por pais siguen llamando a `run_country_year()`, y `scripts/harmonization/build_harmonized.py` reconstruye `outputs/harmonized/harmonized_all.parquet` a partir de los parquets nacionales.

El objetivo de la ampliacion es que los parquets armonizados nacionales y el consolidado ya contengan las variables necesarias para auditoria y cuadros comparados, sin reconstruir variables sustantivas en scripts analiticos posteriores.

## Entramado de scripts y outputs

1. `scripts/<pais>/<pais>_<anio>.py`
   - Ejecuta `run_country_year(pais, anio)`.
   - No contiene logica sustantiva propia.

2. `scripts/common_pipeline.py`
   - Define periodos disponibles por pais.
   - Lee microdatos trimestrales.
   - Aplica filtros geograficos urbanos cuando corresponde.
   - Construye variables armonizadas comunes.
   - Guarda temporales trimestrales en `outputs/harmonized/tmp/`.
   - Concatena los cuatro trimestres y guarda `outputs/harmonized/<pais>_<anio>.parquet`.

3. `scripts/harmonization/build_harmonized.py`
   - Lee los parquets nacionales.
   - Concatena paises y anos.
   - Guarda `outputs/harmonized/harmonized_all.parquet`.

4. `scripts/build_audit_and_tables.py`
   - Lee los parquets nacionales ya armonizados.
   - Genera auditorias nacionales y comparadas.
   - Genera cuadros trimestrales y anuales.
   - Guarda CSV y un Excel consolidado en `outputs/diagnostics/`.

## Variables nuevas

Se agregan a la base armonizada:

- `sexo`
- `edad`
- `nivel_educativo`
- `educacion_superior`
- `asalariado_publico`
- `asalariado_privado`
- `patron`
- `trab_familiar`
- `empleo_domestico`
- `small`
- `patron_micro`
- `asalariado_privado_micro`

No se construye `autonomo_profesional`. Para ejercicios posteriores se puede aproximar como `cuentapropia == 1` y `educacion_superior == 1`.

## Equivalencias ocupacionales

Argentina:

- `asalariado`: `CAT_OCUP == 3`
- `cuentapropia`: `CAT_OCUP == 2`
- `patron`: `CAT_OCUP == 1`
- `trab_familiar`: `CAT_OCUP == 4`
- `empleo_domestico`: `PP04B1 == 1`
- `asalariado_publico`: asalariado con `PP04A == 1`, excluyendo servicio domestico
- `asalariado_privado`: asalariado con `PP04A in (2, 3)`, excluyendo servicio domestico

Brasil:

- `asalariado_privado`: `VD4009 in (1, 2)`
- `empleo_domestico`: `VD4009 in (3, 4)`
- `asalariado_publico`: `VD4009 in (5, 6, 7)`
- `patron`: `VD4009 == 8`
- `cuentapropia`: `VD4009 == 9`
- `trab_familiar`: `VD4009 == 10`

Mexico:

- `asalariado`: `pos_ocu == 1`
- `patron`: `pos_ocu == 2`
- `cuentapropia`: `pos_ocu == 3`
- `trab_familiar`: `pos_ocu == 4`
- `asalariado_publico`: asalariado con `tue2 == 4`
- `empleo_domestico`: `tue2 == 6` o `domestico == 1`
- `asalariado_privado`: asalariado con `tue2 in (1, 2, 3, 5, 7)`, excluyendo servicio domestico

Colombia:

- `asalariado_privado`: `P6430 in (1, 8)`
- `asalariado_publico`: `P6430 == 2`
- `empleo_domestico`: `P6430 == 3`
- `cuentapropia`: `P6430 == 4`
- `patron`: `P6430 == 5`
- `trab_familiar`: `P6430 in (6, 7)`

## Variables micro

- `patron_micro`: `patron == 1` y `small == 1`
- `asalariado_privado_micro`: `asalariado_privado == 1` y `small == 1`

La definicion de `small` conserva los criterios ya usados en el pipeline para no alterar la logica general de armonizacion.

## Educacion

La variable `nivel_educativo` usa categorias textuales comparables. La comparabilidad fina esta limitada porque las encuestas no siempre distinguen terciario, universitario y posgrado con el mismo detalle.

`educacion_superior` se define como educacion superior completa o su aproximacion mas comparable disponible:

- Argentina: `NIVEL_ED == 6`
- Brasil: `VD3004 == 7`
- Mexico: `niv_ins >= 4`
- Colombia: `P6210 == 6`

## Cuadros

Los cuadros trimestrales usan siempre ponderadores oficiales. Los cuadros anuales se construyen como promedio simple de los cuatro trimestres del mismo ano para cada indicador o categoria.

Los outputs principales son:

- `outputs/diagnostics/auditoria_nacional_resumen.csv`
- `outputs/diagnostics/auditoria_nacional_variables.csv`
- `outputs/diagnostics/auditoria_comparada_distribuciones.csv`
- `outputs/diagnostics/cuadros_trimestrales_indicadores.csv`
- `outputs/diagnostics/cuadros_trimestrales_distribuciones.csv`
- `outputs/diagnostics/cuadros_anuales_indicadores.csv`
- `outputs/diagnostics/cuadros_anuales_distribuciones.csv`
- `outputs/diagnostics/cuadros_anuales_indicadores_variacion.csv`
- `outputs/diagnostics/cuadros_anuales_distribuciones_variacion.csv`
- `outputs/diagnostics/auditoria_y_cuadros.xlsx`
