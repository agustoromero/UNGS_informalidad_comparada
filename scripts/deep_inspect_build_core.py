"""
Deep inspection of build_core() Brasil to find data loss
"""
import pandas as pd
from pathlib import Path
import sys

print("=" * 80)
print("INSPECCIÓN PROFUNDA: build_core() Brasil")
print("=" * 80)

# ============================================================================
# CARGAR BRASIL_CLEAN T1 (INPUT A build_core)
# ============================================================================

print("\n[INPUT] brasil_clean/2018/T1.parquet")
print("-" * 80)

clean_parquet = Path("data/brasil_clean/2018/T1.parquet")
df_input = pd.read_parquet(clean_parquet)

print(f"Filas: {len(df_input):,}")
print(f"Columnas: {len(df_input.columns)}")
print(f"Población (V1028): {df_input['V1028'].sum():,.0f}")

# Filtrar por trimestre 1
df_t1 = df_input[df_input['Trimestre'] == 1].copy()
print(f"\nTrimestre 1 input: {len(df_t1):,} filas, {df_t1['V1028'].sum():,.0f} población")

# ============================================================================
# SIMULAR LO QUE HACE build_core() PARA BRASIL
# ============================================================================

print("\n[SIMULACIÓN] Pasos de build_core()")
print("-" * 80)

# Paso 1: Crear ID (como en línea 528-535)
print("\n1. Crear ID...")
df_work = df_t1.copy()

try:
    df_work["id"] = (
        df_work[
            [
                "UF",    
                "UPA",
                "V1008",
                "V1014",
                "V2003",
            ]
        ]
        .astype(str)
        .agg("_".join, axis=1)
    )
    print(f"   ✓ IDs creados: {len(df_work):,} filas")
    print(f"   Población: {df_work['V1028'].sum():,.0f}")
except Exception as e:
    print(f"   ✗ Error creando ID: {e}")
    sys.exit(1)

# Paso 2: Convertir estado de actividad (como en línea 549-552)
print("\n2. Procesar estado de actividad (VD4002)...")
df_work["estado"] = pd.to_numeric(
    df_work["VD4002"],
    errors="coerce",
)
print(f"   Estado NA: {df_work['estado'].isna().sum():,} ({df_work['estado'].isna().mean():.2%})")
print(f"   Población en estado valid: {df_work.loc[df_work['estado'].notna(), 'V1028'].sum():,.0f}")

# Paso 3: Crear variables booleanas (ocupado, desocupado, inactivo)
print("\n3. Crear variables binarias estado...")

ocupado = (df_work["estado"] == 1).astype(int)
desocupado = (df_work["estado"] == 2).astype(int)
inactivo = (df_work["estado"].isna()).astype(int)

print(f"   Ocupados: {ocupado.sum():,} filas ({ocupado.mean():.2%})")
print(f"   Desocupados: {desocupado.sum():,} filas ({desocupado.mean():.2%})")
print(f"   Inactivos: {inactivo.sum():,} filas ({inactivo.mean():.2%})")

pop_ocupados = df_work.loc[ocupado.eq(1), 'V1028'].sum()
pop_desocupados = df_work.loc[desocupado.eq(1), 'V1028'].sum()
pop_inactivos = df_work.loc[inactivo.eq(1), 'V1028'].sum()

print(f"\n   Población ocupados: {pop_ocupados:,.0f}")
print(f"   Población desocupados: {pop_desocupados:,.0f}")
print(f"   Población inactivos: {pop_inactivos:,.0f}")
print(f"   TOTAL: {pop_ocupados + pop_desocupados + pop_inactivos:,.0f}")

# Paso 4: Crear categoría ocupacional (como en línea 553-560)
print("\n4. Procesar categoría ocupacional (VD4009)...")
df_work["cat"] = pd.to_numeric(
    df_work["VD4009"],
    errors="coerce",
)
print(f"   Categoría NA: {df_work['cat'].isna().sum():,} ({df_work['cat'].isna().mean():.2%})")
print(f"   Valores únicos: {sorted(df_work['cat'].dropna().unique())}")

asalariado = cat.isin([1,2,3,4,5,6,7])
cuentapropia = cat.eq(9)

print(f"   Asalariados: {asalariado.sum():,} filas")
print(f"   Cuenta propia: {cuentapropia.sum():,} filas")

# Paso 5: Crear variable informalidad
print("\n5. Procesar informalidad...")
df_work["no_ss"] = (
    pd.to_numeric(
        df_work.get("VD4012"),
        errors="coerce",
    )
    .eq(2)
)

print(f"   Sin SS: {df_work['no_ss'].sum():,} filas ({df_work['no_ss'].mean():.2%})")

# ============================================================================
# PROBLEMA DETECTADO
# ============================================================================

print("\n" + "=" * 80)
print("[ANÁLISIS DEL PROBLEMA]")
print("=" * 80)

# Verificar que el DataFrame mantiene el índice correcto
print(f"\nÍndice original: {df_t1.index.min()}-{df_t1.index.max()}")
print(f"Índice en work: {df_work.index.min()}-{df_work.index.max()}")

# El problema probable: el out DataFrame puede estar perdiendo filas
# por indexación incorrecta

print(f"\nProblema probable:")
print(f"  El build_core() crea un 'out' DataFrame vacío con index=df.index")
print(f"  Luego asigna columnas que pueden no mantener el índice consistente")
print(f"  Esto puede causar que solo queden filas con índice válido en el resultado final")

# Simular creación de out como en build_core()
print("\n6. Simular creación de 'out' DataFrame...")
out = pd.DataFrame(index=df_work.index)
print(f"   out creado con {len(out):,} filas (índice de df)")

out["pais"] = "brasil"
out["anio"] = 2018
out["trimestre"] = 1
out["id"] = df_work["id"]
out["ponderador"] = df_work["V1028"]
out["ocupado"] = ocupado
out["desocupado"] = desocupado
out["inactivo"] = inactivo
out["asalariado"] = asalariado
out["cuentapropia"] = cuentapropia

print(f"   Después de asignaciones: {len(out):,} filas")
print(f"   Población: {out['ponderador'].sum():,.0f}")
print(f"   Filas con ponderador válido: {out['ponderador'].notna().sum():,}")

# Verificar valores nulos
print(f"\n   Nulls por columna:")
for col in out.columns:
    if out[col].isna().any():
        print(f"     {col}: {out[col].isna().sum():,}")
