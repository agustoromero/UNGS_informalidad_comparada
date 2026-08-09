"""
Analyze population loss across Brazil data processing pipeline
"""
import pandas as pd
import numpy as np
from pathlib import Path

# Define paths
base_path = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")
raw_path = base_path / "outputs/raw_brasil/brasil_raw.parquet"
clean_t1_path = base_path / "data/brasil_clean/2018/T1.parquet"
harmonized_path = base_path / "outputs/harmonized/brasil_2018.parquet"

print("=" * 80)
print("BRAZIL DATA PIPELINE - POPULATION LOSS ANALYSIS")
print("=" * 80)

stages = []

# Stage 1: Raw Brasil
print("\n[STAGE 1] Raw Brasil (brasil_raw.parquet)")
print("-" * 80)
try:
    df_raw = pd.read_parquet(raw_path)
    print(f"Rows: {len(df_raw):,}")
    print(f"Columns: {sorted(df_raw.columns.tolist())}")
    
    # Try to find weight column
    weight_cols = [col for col in df_raw.columns if 'weight' in col.lower() or 'peso' in col.lower() or 'ponderador' in col.lower()]
    print(f"Weight columns detected: {weight_cols}")
    
    if weight_cols:
        weight_col = weight_cols[0]
        total_pop_raw = df_raw[weight_col].sum()
        print(f"\nUsing column: {weight_col}")
        print(f"Total expanded population: {total_pop_raw:,.0f}")
        stages.append({"stage": "Raw Brasil", "population": total_pop_raw, "rows": len(df_raw)})
    else:
        # Try default column names
        for col in ['weight', 'weights', 'WEIGHT', 'WEIGHTS', 'V1032', 'V1033']:
            if col in df_raw.columns:
                total_pop_raw = df_raw[col].sum()
                print(f"\nUsing column: {col}")
                print(f"Total expanded population: {total_pop_raw:,.0f}")
                stages.append({"stage": "Raw Brasil", "population": total_pop_raw, "rows": len(df_raw)})
                weight_col = col
                break
        else:
            print("\nWarning: No obvious weight column found")
            print("First few columns:", df_raw.columns[:10].tolist())
            
except Exception as e:
    print(f"Error reading raw parquet: {e}")

# Stage 2: Brasil Clean T1
print("\n[STAGE 2] Brasil Clean T1 (data/brasil_clean/2018/T1.parquet)")
print("-" * 80)
try:
    df_clean = pd.read_parquet(clean_t1_path)
    print(f"Rows: {len(df_clean):,}")
    print(f"Columns: {sorted(df_clean.columns.tolist())}")
    
    # Try to find weight column
    weight_cols = [col for col in df_clean.columns if 'weight' in col.lower() or 'peso' in col.lower() or 'ponderador' in col.lower()]
    print(f"Weight columns detected: {weight_cols}")
    
    if weight_cols:
        weight_col_clean = weight_cols[0]
        total_pop_clean = df_clean[weight_col_clean].sum()
        print(f"\nUsing column: {weight_col_clean}")
        print(f"Total expanded population: {total_pop_clean:,.0f}")
        stages.append({"stage": "Brasil Clean T1", "population": total_pop_clean, "rows": len(df_clean)})
    else:
        # Try default column names
        for col in ['weight', 'weights', 'WEIGHT', 'WEIGHTS', 'V1032', 'V1033']:
            if col in df_clean.columns:
                total_pop_clean = df_clean[col].sum()
                print(f"\nUsing column: {col}")
                print(f"Total expanded population: {total_pop_clean:,.0f}")
                stages.append({"stage": "Brasil Clean T1", "population": total_pop_clean, "rows": len(df_clean)})
                weight_col_clean = col
                break
        else:
            print("\nWarning: No obvious weight column found")
            print("First few columns:", df_clean.columns[:10].tolist())
            
except Exception as e:
    print(f"Error reading clean parquet: {e}")

# Stage 3: Harmonized Brasil 2018
print("\n[STAGE 3] Harmonized Brasil 2018 (outputs/harmonized/brasil_2018.parquet)")
print("-" * 80)
try:
    df_harmonized = pd.read_parquet(harmonized_path)
    print(f"Rows: {len(df_harmonized):,}")
    print(f"Columns: {sorted(df_harmonized.columns.tolist())}")
    
    # Try to find weight column
    weight_cols = [col for col in df_harmonized.columns if 'weight' in col.lower() or 'peso' in col.lower() or 'ponderador' in col.lower()]
    print(f"Weight columns detected: {weight_cols}")
    
    if weight_cols:
        weight_col_harm = weight_cols[0]
        total_pop_harm = df_harmonized[weight_col_harm].sum()
        print(f"\nUsing column: {weight_col_harm}")
        print(f"Total expanded population: {total_pop_harm:,.0f}")
        stages.append({"stage": "Harmonized Brasil 2018", "population": total_pop_harm, "rows": len(df_harmonized)})
    else:
        # Try default column names
        for col in ['weight', 'weights', 'WEIGHT', 'WEIGHTS', 'V1032', 'V1033']:
            if col in df_harmonized.columns:
                total_pop_harm = df_harmonized[col].sum()
                print(f"\nUsing column: {col}")
                print(f"Total expanded population: {total_pop_harm:,.0f}")
                stages.append({"stage": "Harmonized Brasil 2018", "population": total_pop_harm, "rows": len(df_harmonized)})
                weight_col_harm = col
                break
        else:
            print("\nWarning: No obvious weight column found")
            print("First few columns:", df_harmonized.columns[:10].tolist())
            
except Exception as e:
    print(f"Error reading harmonized parquet: {e}")

# Summary and Loss Analysis
if len(stages) > 0:
    print("\n" + "=" * 80)
    print("SUMMARY: POPULATION TRACKING")
    print("=" * 80)
    
    for i, stage in enumerate(stages):
        print(f"{i+1}. {stage['stage']}: {stage['population']:>20,.0f} ({stage['rows']:>12,} rows)")
    
    print("\n" + "=" * 80)
    print("LOSS ANALYSIS")
    print("=" * 80)
    
    for i in range(len(stages) - 1):
        current = stages[i]
        next_stage = stages[i + 1]
        loss_pop = current['population'] - next_stage['population']
        loss_pct = (loss_pop / current['population']) * 100
        loss_rows = current['rows'] - next_stage['rows']
        loss_rows_pct = (loss_rows / current['rows']) * 100
        
        print(f"\n{current['stage']} → {next_stage['stage']}")
        print(f"  Population loss:     {loss_pop:>15,.0f} ({loss_pct:>6.2f}%)")
        print(f"  Row loss:            {loss_rows:>15,} ({loss_rows_pct:>6.2f}%)")
        print(f"  Avg pop/row change:  {next_stage['population']/next_stage['rows']:>15,.2f}  (was {current['population']/current['rows']:,.2f})")

else:
    print("\nNo valid stages to analyze - check file paths and weight columns")
