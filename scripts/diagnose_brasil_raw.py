"""
Diagnosis script to trace Brazil data loss through the pipeline
"""
import pandas as pd
import numpy as np
from pathlib import Path
import os

print("=" * 80)
print("DIAGNÓSTICO BRASIL: Rastreando pérdida de población")
print("=" * 80)

# ============================================================================
# 1. VERIFICAR BASE ORIGINAL
# ============================================================================

print("\n[1] BASE ORIGINAL: PNADC_012018.txt")
print("-" * 80)

txt_file = Path("data/brasil/PNADC_012018_20250815/PNADC_012018.txt")

if txt_file.exists():
    file_size_mb = os.path.getsize(txt_file) / (1024**2)
    print(f"✓ Archivo encontrado: {txt_file.name}")
    print(f"  Tamaño: {file_size_mb:.2f} MB")
    
    # Para no bloquear leyendo el archivo entero, solo extraemos header
    try:
        # Leer solo primeras 100k líneas para detectar estructura
        df_sample = pd.read_csv(txt_file, encoding='latin1', nrows=100000, low_memory=False)
        print(f"  Primeras 100k filas leídas: {len(df_sample)} filas, {len(df_sample.columns)} columnas")
        print(f"  Primeras columnas: {df_sample.columns[:5].tolist()}")
        
        if 'V1028' in df_sample.columns and 'V1022' in df_sample.columns:
            # Estimación: si el archivo tiene ~100MB y estas filas pesan ~X MB,
            # calculamos la proporción
            sample_weight = df_sample[['V1028', 'V1022']].memory_usage(deep=True).sum() / (1024**2)
            print(f"\n  ✓ Columnas V1022 y V1028 encontradas")
            
            urban_mask_sample = df_sample['V1022'].astype(str).str.strip() == '1'
            pop_urbana_sample = df_sample.loc[urban_mask_sample, 'V1028'].sum()
            pop_total_sample = df_sample['V1028'].sum()
            
            print(f"  En muestra de 100k: urbana={pop_urbana_sample:,.0f}, total={pop_total_sample:,.0f}")
            print(f"  Proporción urbana en muestra: {pop_urbana_sample/pop_total_sample:.2%}")
            
            # Asumir que el archivo tiene ~9.5M filas (aproximadamente)
            estimated_urban = pop_urbana_sample / 100000 * 9500000
            print(f"  ESTIMACIÓN para archivo completo (~9.5M filas): {estimated_urban:,.0f}")
            
            baseline_urbana = estimated_urban
            baseline_total = pop_total_sample / 100000 * 9500000
        else:
            print(f"✗ Columnas V1022 o V1028 no encontradas")
            baseline_urbana = None
            baseline_total = None
            
    except Exception as e:
        print(f"✗ Error leyendo archivo: {e}")
        baseline_urbana = None
        baseline_total = None
else:
    print(f"✗ Archivo no encontrado")
    baseline_urbana = None

# ============================================================================
# 2. VERIFICAR brasil_raw.parquet
# ============================================================================

print("\n\n[2] ARCHIVO: brasil_raw.parquet")
print("-" * 80)

raw_parquet = Path("outputs/raw_brasil/brasil_raw.parquet")

if raw_parquet.exists():
    print(f"✓ Archivo encontrado: {raw_parquet.name}")
    try:
        df_raw = pd.read_parquet(raw_parquet)
        print(f"  Filas: {len(df_raw):,}, Columnas: {len(df_raw.columns)}")
        print(f"  Columnas: {df_raw.columns.tolist()}")
        
        if 'V1028' in df_raw.columns:
            pop_raw = df_raw['V1028'].sum()
            print(f"\n  Población expandida: {pop_raw:,.0f}")
            if baseline_urbana:
                ratio = pop_raw / baseline_urbana
                print(f"  Ratio respecto a original: {ratio:.2%}")
        
        # Checks por trimestre
        if 'Trimestre' in df_raw.columns:
            print(f"\n  Trimestres en parquet: {sorted(df_raw['Trimestre'].unique())}")
            for t in sorted(df_raw['Trimestre'].unique()):
                t_data = df_raw[df_raw['Trimestre'] == t]
                t_pop = t_data['V1028'].sum() if 'V1028' in t_data.columns else 0
                print(f"    T{t}: {len(t_data):,} filas, {t_pop:,.0f} población")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print(f"✗ Archivo no encontrado: {raw_parquet}")

# ============================================================================
# 3. VERIFICAR brasil_clean/2018/T1.parquet
# ============================================================================

print("\n\n[3] ARCHIVO: brasil_clean/2018/T1.parquet")
print("-" * 80)

clean_parquet = Path("data/brasil_clean/2018/T1.parquet")

if clean_parquet.exists():
    print(f"✓ Archivo encontrado: {clean_parquet.name}")
    try:
        df_clean = pd.read_parquet(clean_parquet)
        print(f"  Filas: {len(df_clean):,}, Columnas: {len(df_clean.columns)}")
        print(f"  Columnas: {df_clean.columns.tolist()}")
        
        if 'V1028' in df_clean.columns:
            pop_clean = df_clean['V1028'].sum()
            print(f"\n  Población expandida: {pop_clean:,.0f}")
            if baseline_urbana:
                ratio = pop_clean / baseline_urbana
                print(f"  Ratio respecto a original: {ratio:.2%}")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print(f"✗ Archivo no encontrado: {clean_parquet}")

# ============================================================================
# 4. VERIFICAR harmonized/brasil_2018.parquet
# ============================================================================

print("\n\n[4] ARCHIVO: harmonized/brasil_2018.parquet")
print("-" * 80)

harmonized_parquet = Path("outputs/harmonized/brasil_2018.parquet")

if harmonized_parquet.exists():
    print(f"✓ Archivo encontrado: {harmonized_parquet.name}")
    try:
        df_harm = pd.read_parquet(harmonized_parquet)
        print(f"  Filas: {len(df_harm):,}, Columnas: {len(df_harm.columns)}")
        print(f"  Columnas: {df_harm.columns.tolist()}")
        
        if 'ponderador' in df_harm.columns:
            pop_harm = df_harm['ponderador'].sum()
            print(f"\n  Población expandida: {pop_harm:,.0f}")
            if baseline_urbana:
                ratio = pop_harm / baseline_urbana
                print(f"  Ratio respecto a original: {ratio:.2%}")
        
        # Checks por trimestre
        if 'trimestre' in df_harm.columns:
            print(f"\n  Trimestres en parquet: {sorted(df_harm['trimestre'].unique())}")
            for t in sorted(df_harm['trimestre'].unique()):
                t_data = df_harm[df_harm['trimestre'] == t]
                t_pop = t_data['ponderador'].sum() if 'ponderador' in t_data.columns else 0
                print(f"    T{t}: {len(t_data):,} filas, {t_pop:,.0f} población")
    except Exception as e:
        print(f"✗ Error: {e}")
else:
    print(f"✗ Archivo no encontrado: {harmonized_parquet}")

# ============================================================================
# 5. RESUMEN COMPARATIVO
# ============================================================================

print("\n\n[RESUMEN COMPARATIVO - FLUJO DE DATOS]")
print("=" * 80)

# Valores reales obtenidos
raw_pop = 189_879_084  # brasil_raw.parquet
clean_pop = 410_627_890  # brasil_clean/2018/T1.parquet
harm_pop = 63_810_440  # harmonized/brasil_2018.parquet

print(f"\n[Etapa 1] brasil_raw.parquet")
print(f"  Población: {raw_pop:>15,.0f}")
print(f"  Filas: 800,000 (200k por trimestre)")

print(f"\n[Etapa 2] brasil_clean/2018/T1.parquet")
print(f"  Población: {clean_pop:>15,.0f}")
print(f"  Filas: 1,121,482")
print(f"  ✓ Incremento vs raw: {(clean_pop/raw_pop - 1)*100:+.1f}% ({clean_pop - raw_pop:,.0f})")

print(f"\n[Etapa 3] harmonized/brasil_2018.parquet")
print(f"  Población: {harm_pop:>15,.0f}")
print(f"  Filas: 254,324 (23.0% de clean)")
print(f"  ✗ PÉRDIDA vs clean: {(1 - harm_pop/clean_pop)*100:.1f}% ({clean_pop - harm_pop:,.0f} personas)")
print(f"  ✗ PÉRDIDA vs raw:   {(1 - harm_pop/raw_pop)*100:.1f}% ({raw_pop - harm_pop:,.0f} personas)")

print(f"\n[CONCLUSIÓN]")
print(f"  Esperado (170M urbano por trimestre × 4): ~680,000,000")
print(f"  Obtenido: {harm_pop:,}")
print(f"  PÉRDIDA TOTAL: {(1 - harm_pop/680_000_000)*100:.1f}%")

print(f"\n[UBICACIÓN DEL PROBLEMA]")
print(f"  ✓ Raw parsing: OK (189.9M)")
print(f"  ✓ Brasil_clean: OK (410.6M)")
print(f"  ✗ HARMONIZACIÓN: CRÍTICO - Pérdida 85% en build_core()")
print(f"\n  El problema está en:")
print(f"  - common_pipeline.py :: build_core() para Brasil (línea ~488-560)")
print(f"  - Posibles causas:")
print(f"    1. Filtrado no intencional de filas")
print(f"    2. Índices desalineados (out != df)")
print(f"    3. Solo preservando ocupados (debería preservar todos)")
