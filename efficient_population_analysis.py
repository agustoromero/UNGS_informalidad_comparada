"""
Efficient population loss analysis - focusing on key metrics only
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys

base_path = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")

print("=" * 80)
print("BRAZIL DATA PIPELINE - POPULATION LOSS ANALYSIS")
print("=" * 80)

# Stage 3: Harmonized Brasil 2018 (use as reference)
print("\n[STAGE 3] Harmonized Brasil 2018")
print("-" * 80)
try:
    harmonized_path = base_path / "outputs/harmonized/brasil_2018.parquet"
    df_harm = pd.read_parquet(harmonized_path)
    harm_pop = df_harm['ponderador'].sum()
    harm_rows = len(df_harm)
    print(f"Rows: {harm_rows:,}")
    print(f"Total population (ponderador): {harm_pop:,.0f}")
    print(f"Average per row: {harm_pop/harm_rows:,.2f}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Stage 2: Brasil Clean T1
print("\n[STAGE 2] Brasil Clean T1")
print("-" * 80)
try:
    clean_t1_path = base_path / "data/brasil_clean/2018/T1.parquet"
    # Read with filter to get only needed columns
    df_clean = pd.read_parquet(clean_t1_path, columns=['V1028'])
    clean_pop = df_clean['V1028'].sum()
    clean_rows = len(df_clean)
    print(f"Rows: {clean_rows:,}")
    print(f"Total population (V1028): {clean_pop:,.0f}")
    print(f"Average per row: {clean_pop/clean_rows:,.2f}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Stage 1: Raw Brasil 
print("\n[STAGE 1] Raw Brasil")
print("-" * 80)
try:
    raw_path = base_path / "outputs/raw_brasil/brasil_raw.parquet"
    # Read filtered by year to reduce memory
    df_raw = pd.read_parquet(raw_path, filters=[('Ano', '==', 2018)], columns=['Ano', 'Trimestre', 'V1028'])
    raw_pop = df_raw['V1028'].sum()
    raw_rows = len(df_raw)
    print(f"Rows: {raw_rows:,}")
    print(f"Total population (V1028): {raw_pop:,.0f}")
    print(f"Average per row: {raw_pop/raw_rows:,.2f}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 80)
print("SUMMARY: POPULATION TRACKING")
print("=" * 80)
print(f"1. Raw Brasil (2018):          {raw_pop:>20,.0f} ({raw_rows:>12,} rows)")
print(f"2. Brasil Clean T1:            {clean_pop:>20,.0f} ({clean_rows:>12,} rows)")
print(f"3. Harmonized Brasil 2018:     {harm_pop:>20,.0f} ({harm_rows:>12,} rows)")

print("\n" + "=" * 80)
print("LOSS ANALYSIS")
print("=" * 80)

# Raw to Clean
loss_pop_1 = raw_pop - clean_pop
loss_pct_1 = (loss_pop_1 / raw_pop) * 100
loss_rows_1 = raw_rows - clean_rows
loss_rows_pct_1 = (loss_rows_1 / raw_rows) * 100

print(f"\n Raw Brasil → Brasil Clean T1")
print(f"  Population loss:     {loss_pop_1:>15,.0f} ({loss_pct_1:>6.2f}%)")
print(f"  Row loss:            {loss_rows_1:>15,} ({loss_rows_pct_1:>6.2f}%)")

# Clean to Harmonized
loss_pop_2 = clean_pop - harm_pop
loss_pct_2 = (loss_pop_2 / clean_pop) * 100
loss_rows_2 = clean_rows - harm_rows
loss_rows_pct_2 = (loss_rows_2 / clean_rows) * 100

print(f"\n Brasil Clean T1 → Harmonized Brasil 2018")
print(f"  Population loss:     {loss_pop_2:>15,.0f} ({loss_pct_2:>6.2f}%)")
print(f"  Row loss:            {loss_rows_2:>15,} ({loss_rows_pct_2:>6.2f}%)")

# Total
loss_pop_total = raw_pop - harm_pop
loss_pct_total = (loss_pop_total / raw_pop) * 100

print(f"\n Raw Brasil → Harmonized Brasil 2018")
print(f"  Population loss:     {loss_pop_total:>15,.0f} ({loss_pct_total:>6.2f}%)")

print("\n" + "=" * 80)
print("KEY FINDINGS")
print("=" * 80)
print(f"Expected population: ~170 million urban per quarter")
print(f"Actual final population: {harm_pop/1_000_000:.1f} million")
print(f"Deficit: {(170 - harm_pop/1_000_000):.1f} million")
