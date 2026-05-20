#!/usr/bin/env python
"""Test script para verificar el pipeline de Colombia"""

import scripts.common_pipeline as cp

print('[TEST] Ejecutando pipeline Colombia 2018...')
df = cp.run_country_year('colombia', 2018)

print(f'\nResultado:')
print(f'  Shape: {df.shape}')
trims = df['trimestre'].value_counts().sort_index().to_dict()
print(f'  Trimestres: {trims}')
mean_pond = df['ponderador'].mean()
min_pond = df['ponderador'].min()
max_pond = df['ponderador'].max()
print(f'  Ponderador: mean={mean_pond:.2f}, min={min_pond:.2f}, max={max_pond:.2f}')
print(f'  Ocupado: {df["ocupado"].sum():,} / {df.shape[0]:,}')
print(f'  Formal: {df["formal"].sum():,}')
print(f'  Informal: {df["informal"].sum():,}')

print('\n✓ Pipeline ejecutado exitosamente')
