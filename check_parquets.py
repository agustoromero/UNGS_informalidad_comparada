import pandas as pd
from pathlib import Path

for q in [1, 2, 3, 4]:
    path = Path('data/colombia_clean/2018') / f'T{q}.parquet'
    df = pd.read_parquet(path)
    print(f'T{q}: shape={df.shape}')
    print(f'  columns: {df.columns.tolist()[:10]}')
    if 'ponderador' in df.columns:
        na_count = df['ponderador'].isna().sum()
        dtype = df['ponderador'].dtype
        print(f'  ponderador: NA={na_count}, dtype={dtype}')
        if df['ponderador'].notna().any():
            print(f'    values: min={df["ponderador"].min():.2f}, max={df["ponderador"].max():.2f}')
    else:
        print('  ponderador: COLUMNA NO EXISTE')
