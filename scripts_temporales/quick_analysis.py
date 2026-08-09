"""
Quick analysis of population - read just V1028 column
"""
import pandas as pd
from pathlib import Path

base_path = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")

print("=" * 80)
print("BRAZIL POPULATION LOSS ANALYSIS - EFFICIENT")
print("=" * 80)

# Stage 1: Raw Brasil (filtered by year, read V1028 only)
print("\n[1] Raw Brasil 2018 All Quarters")
try:
    raw_path = base_path / "outputs/raw_brasil/brasil_raw.parquet"
    # Only read V1028 and Ano/Trimestre
    df_raw = pd.read_parquet(raw_path, filters=[('Ano', '==', 2018)], columns=['Ano', 'Trimestre', 'V1028'])
    raw_2018_total = df_raw['V1028'].sum()
    raw_2018_rows = len(df_raw)
    print(f"   Rows: {raw_2018_rows:,}")
    print(f"   Population: {raw_2018_total:,.0f}")
    print(f"   Per row: {raw_2018_total/raw_2018_rows:,.2f}")
    
    # Just T1
    df_raw_t1 = df_raw[df_raw['Trimestre'] == 1]
    raw_t1_total = df_raw_t1['V1028'].sum()
    raw_t1_rows = len(df_raw_t1)
    print(f"\n   T1 only:")
    print(f"     Rows: {raw_t1_rows:,}")
    print(f"     Population: {raw_t1_total:,.0f}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Stage 2: Clean Brasil T1
print("\n[2] Brasil Clean T1 2018")
try:
    clean_path = base_path / "data/brasil_clean/2018/T1.parquet"
    df_clean = pd.read_parquet(clean_path, columns=['V1028'])
    clean_pop = df_clean['V1028'].sum()
    clean_rows = len(df_clean)
    print(f"   Rows: {clean_rows:,}")
    print(f"   Population: {clean_pop:,.0f}")
    print(f"   Per row: {clean_pop/clean_rows:,.2f}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

# Stage 3: Harmonized Brasil 2018
print("\n[3] Harmonized Brasil 2018")
try:
    harm_path = base_path / "outputs/harmonized/brasil_2018.parquet"
    df_harm = pd.read_parquet(harm_path, columns=['ponderador'])
    harm_pop = df_harm['ponderador'].sum()
    harm_rows = len(df_harm)
    print(f"   Rows: {harm_rows:,}")
    print(f"   Population: {harm_pop:,.0f}")
    print(f"   Per row: {harm_pop/harm_rows:,.2f}")
except Exception as e:
    print(f"   Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("LOSS TRACKING")
print("=" * 80)

if 'raw_t1_total' in locals() and 'clean_pop' in locals():
    loss_raw_to_clean = raw_t1_total - clean_pop
    pct_1 = (loss_raw_to_clean / raw_t1_total) * 100
    print(f"\nRaw T1 → Clean T1:")
    print(f"  Loss: {loss_raw_to_clean:>15,.0f} ({pct_1:>6.2f}%)")
    print(f"  Raw rows: {raw_t1_rows:,} → Clean rows: {clean_rows:,}")

if 'clean_pop' in locals() and 'harm_pop' in locals():
    loss_clean_to_harm = clean_pop - harm_pop
    pct_2 = (loss_clean_to_harm / clean_pop) * 100
    print(f"\nClean T1 → Harmonized:")
    print(f"  Loss: {loss_clean_to_harm:>15,.0f} ({pct_2:>6.2f}%)")
    print(f"  Clean rows: {clean_rows:,} → Harm rows: {harm_rows:,}")

if 'raw_t1_total' in locals() and 'harm_pop' in locals():
    loss_total = raw_t1_total - harm_pop
    pct_total = (loss_total / raw_t1_total) * 100
    print(f"\nRaw T1 → Harmonized:")
    print(f"  Loss: {loss_total:>15,.0f} ({pct_total:>6.2f}%)")
    print(f"  Expected: ~170M, Actual: {harm_pop/1_000_000:.1f}M")
