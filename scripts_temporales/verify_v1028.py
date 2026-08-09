#!/usr/bin/env python
"""
Verificar que V1028 se está leyendo correctamente desde el TXT de Brasil.
"""
from pathlib import Path
import re

# Ruta al SAS
sas_path = Path('data/brasil/Dicionario_e_input_20221031/input_PNADC_trimestral.sas')

# Buscar V1028
print("=== VERIFICAR V1028 EN SAS ===")
with sas_path.open('r', encoding='latin1', errors='ignore') as fh:
    for line in fh:
        if 'V1028' in line and '@' in line and 'REPLICADO' not in line:
            print(line.strip())
            # Extraer posición
            m = re.search(r'@(\d+)\s+V1028\s+(\S+)', line)
            if m:
                pos = int(m.group(1))
                fmt = m.group(2)
                width_match = re.search(r'(\d+)', fmt)
                width = int(width_match.group(1)) if width_match else None
                print(f"  -> Posición (1-indexed): {pos}, Ancho: {width}")
                print(f"  -> En 0-indexed: [{pos-1}:{pos-1+width}]")

# Leer primer registro del TXT
print("\n=== PRIMER REGISTRO DEL TXT ===")
txt_path = Path('data/brasil/PNADC_012018_20250815/PNADC_012018.txt')
with txt_path.open('r', encoding='latin1', errors='ignore') as fh:
    first_line = fh.readline().rstrip('\n')

print(f"Longitud total: {len(first_line)}")

# Extraer V1028
# SAS dice: @0050 V1028 15.
# En 0-indexed: [49:64]
v1028_0indexed = first_line[49:64]
print(f"V1028 [49:64]: '{v1028_0indexed}'")
print(f"V1028 stripped: '{v1028_0indexed.strip()}'")
print(f"V1028 as float: {float(v1028_0indexed.strip())}")

# Extraer otros para referencia
print("\nOtras variables:")
print(f"V2007 [94:95]: '{first_line[94:95]}'")
print(f"V2009 [103:106]: '{first_line[103:106]}'")
