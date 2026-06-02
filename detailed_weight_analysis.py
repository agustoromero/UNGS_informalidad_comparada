"""
Detailed analysis of population loss - examining weight columns
"""
import pandas as pd
import numpy as np
from pathlib import Path

base_path = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")
raw_path = base_path / "outputs/raw_brasil/brasil_raw.parquet"
clean_t1_path = base_path / "data/brasil_clean/2018/T1.parquet"
harmonized_path = base_path / "outputs/harmonized/brasil_2018.parquet"

print("=" * 80)
print("DETAILED WEIGHT COLUMN ANALYSIS")
print("=" * 80)

# Stage 1: Raw Brasil - look for V1032, V1033 or other potential weight columns
print("\n[STAGE 1] Raw Brasil - Checking for weight columns")
print("-" * 80)
try:
    df_raw = pd.read_parquet(raw_path)
    print(f"Shape: {df_raw.shape}")
    
    # Check for common PNADC weight columns
    potential_weights = ['V1032', 'V1033', 'V1028', 'posest', 'Peso', 'peso', 'PESO']
    found_weights = []
    for col in potential_weights:
        if col in df_raw.columns:
            found_weights.append(col)
            total = df_raw[col].sum()
            print(f"  {col}: {total:,.0f} (sum)")
    
    if not found_weights:
        print("  No V1032/V1033 columns found. Numeric columns:")
        numeric_cols = df_raw.select_dtypes(include=[np.number]).columns.tolist()
        print(f"  Numeric columns: {numeric_cols[:20]}")
    
    # Show sample rows
    print("\n  Sample data (first 5 rows):")
    print(df_raw.head())
    
except Exception as e:
    print(f"Error: {e}")

# Stage 2: Brasil Clean T1
print("\n[STAGE 2] Brasil Clean T1 - Checking for weight columns")
print("-" * 80)
try:
    df_clean = pd.read_parquet(clean_t1_path)
    print(f"Shape: {df_clean.shape}")
    
    potential_weights = ['V1032', 'V1033', 'V1028', 'posest', 'Peso', 'peso', 'PESO', 'weight', 'ponderador']
    found_weights = []
    for col in potential_weights:
        if col in df_clean.columns:
            found_weights.append(col)
            total = df_clean[col].sum()
            print(f"  {col}: {total:,.0f} (sum)")
    
    if not found_weights:
        print("  No common weight columns found. Numeric columns:")
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns.tolist()
        print(f"  Numeric columns: {numeric_cols[:20]}")
    
    print("\n  Sample data (first 5 rows):")
    print(df_clean.head())
    
except Exception as e:
    print(f"Error: {e}")

# Stage 3: Harmonized
print("\n[STAGE 3] Harmonized Brasil 2018")
print("-" * 80)
try:
    df_harm = pd.read_parquet(harmonized_path)
    print(f"Shape: {df_harm.shape}")
    print(f"Columns: {df_harm.columns.tolist()}")
    
    # Check ponderador
    if 'ponderador' in df_harm.columns:
        total_pond = df_harm['ponderador'].sum()
        print(f"\n  ponderador sum: {total_pond:,.0f}")
        print(f"  ponderador stats:")
        print(f"    Min: {df_harm['ponderador'].min():,.2f}")
        print(f"    Max: {df_harm['ponderador'].max():,.2f}")
        print(f"    Mean: {df_harm['ponderador'].mean():,.2f}")
        print(f"    Median: {df_harm['ponderador'].median():,.2f}")
    
    print("\n  Sample data (first 5 rows):")
    print(df_harm.head())
    
except Exception as e:
    print(f"Error: {e}")
