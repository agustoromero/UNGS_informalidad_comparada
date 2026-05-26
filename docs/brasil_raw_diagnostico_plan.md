# Brasil PNADC — Plan integral para diagnosticar, probar y corregir `brasil_raw`

## Objetivo
Diagnosticar y corregir **exclusivamente** la construcción de `outputs/raw_brasil/brasil_raw.parquet`.

> Alcance: no tocar harmonization (`scripts/common_pipeline.py` / `build_core`) hasta cerrar la integridad del RAW.

---

## Hipótesis de trabajo
Las anomalías de tasas laborales se originan por **desalineación del layout FWF** (colspecs corridas), no por reglas de clasificación.

Indicadores críticos observados:
- `V2007` fuera de `{1,2}`.
- `V2009` con patrones imposibles (`101`, `202`, `304`, ...).
- `VD4002` fuera de `{1,2,NA}`.
- `VD4009` fuera de `{1..10,NA}`.

---

## Pregunta técnica clave (resolver primero)
**¿El layout para `read_fwf()` debe salir del `input_txt` oficial o del XLS?**

### Respuesta propuesta (según evidencia en `PNADcIBGE-master`)
- `read_pnadc()` construye posiciones y anchos a partir del **`input_txt` SAS**.
- El XLS se usa para **etiquetas y categorías** (`pnadc_labeller`), no para colspecs primarias.

**Implicación práctica:** si `corrije_brasil.py` arma colspecs desde XLS como fuente principal, hay alto riesgo de corrimiento.

---

## Secuencia de diagnóstico y validación (gates)

### Gate A — Congelamiento downstream
- No modificar harmonization / `build_core`.
- No interpretar tasas finales todavía.

### Gate B — Sanidad de insumos
- Confirmar disponibilidad de:
  - `PNADC_*.txt`.
  - `input_*.txt` oficial.
  - XLS diccionario.
- Eliminar raw previo:
  - `outputs/raw_brasil/brasil_raw.parquet`
  - opcional `outputs/raw_brasil/brasil_raw.csv`

### Gate C — Auditoría del parser de layout
1. Verificar detección de `start_row` si se usa XLS.
2. Validar columnas reales de layout (`pos_ini`, `tam`, `var`) por contenido, no por índice fijo.
3. Limpiar encabezados repetidos/notas.
4. Verificar colspecs:
   - `pos_ini > 0`, `tam > 0`, enteros.
   - `end = pos_ini + tam - 1`.
   - monotonía razonable.
   - sin overlaps no esperados.

### Gate D — Lectura mínima (`nrows=1000`, primer TXT)
- Leer muestra pequeña y reportar:
  - shape
  - dtypes
  - primeras 30 variables
  - muestras de centinelas
- Validaciones must-pass:
  - `V2007 ∈ {1,2,NA}`
  - `V2009 ∈ [0,130]`
  - `VD4002 ∈ {1,2,NA}`
  - `VD4008 ∈ {1..6,NA}`
  - `VD4009 ∈ {1..10,NA}`
  - `VD4012 ∈ {1,2,NA}`
  - `Ano` y `Trimestre` coherentes.

### Gate E — Reconstrucción full RAW
- Solo si Gate D pasó.
- Regenerar parquet completo.
- Repetir validaciones de dominio en full dataset.
- Confirmar ausencia de mezcla masiva código/texto.

### Gate F — Auditoría de IDs (sin deduplicar)
- ID: `UF_UPA_V1008_V1014_V2003`.
- Medir repetidos, confirmar no clones exactos.
- Documentar variables que cambian (`V1028`, `VD*`, ...).
- Decisión explícita: **NO `drop_duplicates()`**.

---

## Propuesta mínima de corrección (`scripts/brasil/corrije_brasil.py`)

1. Priorizar `input_txt` como fuente de layout FWF.
2. Mantener XLS solo para metadatos/categorías (opcional en esta etapa).
3. Agregar validaciones de gate dentro del script:
   - chequeos centinela con `assert`/errores explícitos.
   - abortar si dominios imposibles.
4. Ejecutar en dos etapas:
   - `--sample-rows 1000` (modo diagnóstico)
   - corrida completa solo si diagnóstico pasa.

---

## Criterio de aceptación (Definition of Done)
- RAW consistente con dominios centinela.
- IDs repetidos documentados y preservados.
- Evidencia reproducible de comandos y resultados.
- Recién después: revisar `build_core` si todavía hay anomalías.

---

## Evidencia mínima a adjuntar en PR
- Tabla de dominios de centinelas (sample + full).
- Extracto de colspecs para variables clave (`V2007`, `V2009`, `VD4002`, `VD4008`, `VD4009`, `VD4012`).
- % IDs repetidos y explicación de no deduplicación.
- Hash/fecha de `brasil_raw.parquet` reconstruido.
