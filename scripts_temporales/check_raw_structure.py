#!/usr/bin/env python
import pyarrow.parquet as pq
from pathlib import Path

path = Path('outputs/raw_brasil/brasil_raw.parquet')
pf = pq.ParquetFile(path)

print(f"Total rows: {pf.metadata.num_rows:,}")

# Leer solo Ano y Trimestre
df = pf.read_row_group(0, columns=['Ano', 'Trimestre']).to_pandas()

print(f"\nAño-Trimestre combinations:")
combinations = df[['Ano','Trimestre']].drop_duplicates().sort_values(['Ano','Trimestre'])
print(combinations.to_string(index=False))

print(f"\nRows per Ano-Trimestre:")
print(df.groupby(['Ano','Trimestre']).size())

print(f"\nRows per Ano:")
print(df.groupby('Ano').size())
