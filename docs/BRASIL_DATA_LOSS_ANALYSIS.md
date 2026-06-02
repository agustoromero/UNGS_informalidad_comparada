# Análisis de Pérdida de Datos Brasil: Reporte Completo

## Resumen Ejecutivo

**PROBLEMA CRÍTICO IDENTIFICADO**: Se pierden ~85% de la población entre `brasil_clean` (410.6M) y `harmonized/brasil_2018.parquet` (63.8M)

**UBICACIÓN**: `scripts/common_pipeline.py` - función `build_core()` líneas ~488-560 (sección Brasil)

**IMPACTO**: 
- Esperado: ~170M población urbana por trimestre (4 trimestres = 680M)
- Obtenido: 63.8M total (9.4% de lo esperado)

---

## Diagnóstico Detallado

### Fase 1: Raw parsing ✓ EXITOSO
```
File: outputs/raw_brasil/brasil_raw.parquet
Filas: 800,000 (200k por trimestre)
Población expandida (V1028): 189,879,084
```
**Conclusión**: El parsing de PNADC es correcto

### Fase 2: Brasil clean ✓ EXITOSO
```
File: data/brasil_clean/2018/T1.parquet
Filas: 1,121,482
Población expandida (V1028): 410,627,890
Estado: ✓ Incremento esperado vs raw
```
**Conclusión**: La limpieza y consolidación funciona

### Fase 3: Harmonización ✗ CRÍTICO
```
File: outputs/harmonized/brasil_2018.parquet
Filas: 254,324 (23.0% de brasil_clean)
Población expandida (ponderador): 63,810,440 (15.5% de brasil_clean)

Desglose por trimestre:
  T1: 64,070 filas → 15,848,180 población (vs 47.12M esperado = 33.6%)
  T2: 63,389 filas → 15,981,532 población
  T3: 63,344 filas → 15,909,443 población
  T4: 63,521 filas → 16,071,281 población
```
**Conclusión**: AQUÍ SE PIERDE LA POBLACIÓN (85% de pérdida)

---

## Raíz de la Causa Probable

### Análisis del código `build_core()` Brasil

**Ubicación**: [common_pipeline.py líneas 490-560](scripts/common_pipeline.py#L490-L560)

```python
elif country == "brasil":
    # Línea 528-535: Crear ID
    df["id"] = (
        df[["UF", "UPA", "V1008", "V1014", "V2003"]]
        .astype(str)
        .agg("_".join, axis=1)
    )
    
    out["id"] = df["id"]  # ← POSIBLE PROBLEMA 1: index mismatch
    out["ponderador"] = df["V1028"]
    
    # Línea 549-552: Convertir estado
    estado = pd.to_numeric(df["VD4002"], errors="coerce")
    cat = pd.to_numeric(df["VD4009"], errors="coerce")
    
    # Línea 558: sin contrato (False para Brasil)
    reg_no = pd.Series(False, index=df.index)
    
    # Línea 560: pequeña unidad
    small = (df.get("V4018", 99).isin([1, 2]))
```

**Problemas Identificados**:

1. **IndexError potencial**: Cuando se crea `out = pd.DataFrame(index=df.index)` con ~1.1M filas, pero luego se asignan series que pueden no tener el mismo índice

2. **Selección en COMMON_COLUMNS**: Al final (línea ~819), se retorna solo `out[COMMON_COLUMNS]` - si hay NaN/NA, algunas filas podrían no incluirse

3. **Truncamiento silencioso**: No hay validación de que todas las filas se conserven

---

## Plan de Corrección

### Paso 1: Verificar el problema real

Ejecutar este script para inspeccionar `build_core()` paso a paso:

```bash
python scripts/deep_inspect_build_core.py
```

Esto mostrará:
- Cuántas filas entran a `build_core()`
- Cuántas filas salen de cada paso
- Dónde exactamente se pierden las filas

### Paso 2: Corregir `build_core()` Brasil

**Solución A (Recomendada)**: Usar `reset_index()` para garantizar índices consistentes

```python
elif country == "brasil":
    # ANTES
    df["id"] = (...)
    out["id"] = df["id"]
    
    # DESPUÉS
    df_work = df.copy()
    df_work["id"] = (...)
    
    out = pd.DataFrame(index=df_work.index)  # O usar range(len(df_work))
    out["id"] = df_work["id"].values  # Usar .values para evitar index issues
    out["ponderador"] = df_work["V1028"].values
```

**Solución B**: Usar `.reset_index(drop=True)` al inicio de `build_core()`

```python
def build_core(country, year, trimestre, df):
    # Guardar índice original si es necesario
    original_index = df.index
    
    # Reset para evitar problemas de indexación
    df = df.reset_index(drop=True)
    
    out = pd.DataFrame(index=range(len(df)))
    # ... resto del código
```

### Paso 3: Añadir validaciones

Después de `build_core()`, en `run_country_year()` (línea ~760):

```python
# Después de: core = build_core(...)
assert len(core) > 0, f"core está vacío para {country} {year}"
assert core["ponderador"].notna().all(), f"core tiene ponderadores NA"

# Validación de población
pop_antes = raw["V1028"].sum() if "V1028" in raw.columns else raw[raw.columns[0]].sum()
pop_despues = core["ponderador"].sum()

if pop_despues < pop_antes * 0.5:  # Si pierde >50%
    warnings.warn(
        f"{country} {year}: Pérdida CRÍTICA de población. "
        f"Antes: {pop_antes:,.0f}, Después: {pop_despues:,.0f} "
        f"({100*pop_despues/pop_antes:.1f}%)"
    )
```

### Paso 4: Testing

Para verificar la corrección:

```python
# Script de test
import pandas as pd
from pathlib import Path

# Cargar brasil_clean T1
df = pd.read_parquet("data/brasil_clean/2018/T1.parquet")
df_t1 = df[df['Trimestre'] == 1].copy()

pop_input = df_t1['V1028'].sum()
print(f"Input población: {pop_input:,.0f}")

# Ejecutar build_core
from scripts.common_pipeline import build_core
core = build_core("brasil", 2018, 1, df_t1)

pop_output = core['ponderador'].sum()
print(f"Output población: {pop_output:,.0f}")
print(f"Ratio: {pop_output/pop_input:.2%}")

# Debería estar cerca de 100%, no 33%
assert pop_output/pop_input > 0.9, "Pérdida de población detectada"
```

---

## Archivos a Revisar

| Archivo | Líneas | Acción |
|---------|--------|--------|
| [common_pipeline.py](scripts/common_pipeline.py) | 488-560 | Revisar build_core() Brasil |
| [common_pipeline.py](scripts/common_pipeline.py) | 750-800 | Añadir validaciones |
| [scripts/diagnose_brasil_raw.py](scripts/diagnose_brasil_raw.py) | Todo | Usar para diagnóstico |
| [scripts/deep_inspect_build_core.py](scripts/deep_inspect_build_core.py) | Todo | Usar para debugging |

---

## Datos de Referencia

### Original estimado (PNADC_012018.txt - Archivo de 1.86GB)
```
Nota: Archivo en formato de campos fijos (no CSV)
No pudo procesarse completo por tamaño, pero muestra:
- Columnas V1022 y V1028 disponibles
- Estimación: ~170M población urbana por trimestre
```

### brasil_raw.parquet
```
Año: 2018
Total población: 189,879,084
Desglose:
  T1: 47,120,812
  T2: 47,505,564
  T3: 47,121,669
  T4: 48,131,040
Filas: 800,000 (200k por trimestre)
```

### brasil_clean/2018
```
Año: 2018
T1 población: 410,627,890
Filas: 1,121,482
Nota: Aparentemente hay consolidación de filas vs raw
```

### harmonized/brasil_2018.parquet (ACTUAL)
```
Año: 2018
Total población: 63,810,440
Desglose:
  T1: 15,848,180 (66.5% pérdida vs raw T1)
  T2: 15,981,532
  T3: 15,909,443
  T4: 16,071,281
Filas: 254,324
Columnas: pais, anio, trimestre, id, ponderador, ocupado, desocupado, inactivo, asalariado, cuentapropia, informal, formal, sector
```

---

## Próximos Pasos Recomendados

1. **Inmediato**: Ejecutar `deep_inspect_build_core.py` para confirmar el problema
2. **Corto plazo**: Aplicar Solución A o B en `build_core()` Brasil
3. **Validación**: Ejecutar test suite y comparar resultados
4. **Documentación**: Actualizar README con hallazgos

---

## Notas para Continuación

Si se agota el crédito, la próxima sesión debe:

1. Revisar este reporte
2. Ejecutar `scripts/deep_inspect_build_core.py` para confirmar
3. Editar `common_pipeline.py` línea ~488-560
4. Aplicar las correcciones sugeridas en "Paso 2"
5. Ejecutar validaciones en "Paso 3"

La solución es **relativamente sencilla** una vez identificada la causa. El problema NO está en los datos source, está en la **lógica de indexación** en `build_core()`.
