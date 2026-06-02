#!/usr/bin/env python
import pandas as pd

# Cargar solo lo necesario
print("Cargando raw Brasil...")
df = pd.read_parquet('outputs/raw_brasil/brasil_raw.parquet', 
                      columns=['Ano', 'V1022', 'V1028'])

print("\n=== TOTAL ===")
print(f"Total rows: {len(df):,}")
print(f"Total weight: {df['V1028'].sum():,.2f}")

# Por año
for year in sorted(df['Ano'].unique()):
    df_year = df[df['Ano'] == year]
    
    # V1022 == 1 (urbano)
    u1 = df_year[df_year['V1022'] == 1]
    # V1022 == 2 (rural)
    u2 = df_year[df_year['V1022'] == 2]
    
    print(f"\n=== {year} ===")
    print(f"V1022==1 rows: {len(u1):,}, weight: {u1['V1028'].sum():,.2f}")
    print(f"V1022==2 rows: {len(u2):,}, weight: {u2['V1028'].sum():,.2f}")
    print(f"Total year: {len(df_year):,}, weight: {df_year['V1028'].sum():,.2f}")
    print(f"V1022==1 % of population: {u1['V1028'].sum() / df_year['V1028'].sum() * 100:.1f}%")
