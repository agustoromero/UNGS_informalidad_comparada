from pathlib import Path
import pandas as pd
import numpy as np

base = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")

# =========================
# 1. ENCONTRAR ARCHIVOS
# =========================

def find_file(pattern):
    return list(base.rglob(pattern))[0]

def load_brasil_txt():
    return find_file("PNADC_*.txt")

def load_brasil_dict():
    return find_file("Brasil*dicionario*PNADC*.xls*")


file = load_brasil_txt()
dict_path = load_brasil_dict()

print("TXT:", file)
print("DICT:", dict_path)

# =========================
# 2. LEER DICCIONARIO
# =========================

xls = pd.ExcelFile(dict_path)
df_raw = xls.parse(xls.sheet_names[0], header=None)

# buscar inicio real del layout
mask = df_raw.apply(
    lambda col: col.astype(str).str.contains("Posição inicial", na=False)
)

start_row = mask.any(axis=1).idxmax()

layout = df_raw.iloc[start_row + 1:].copy()
layout = layout.dropna(how="all")

# quedarnos con columnas relevantes
layout = layout.iloc[:, :3]
layout.columns = ["pos_ini", "tam", "var"]

layout = layout.dropna()
layout["pos_ini"] = pd.to_numeric(layout["pos_ini"], errors="coerce")
layout["tam"] = pd.to_numeric(layout["tam"], errors="coerce")
layout = layout.dropna()

# =========================
# 3. CONSTRUIR COLSPEC
# =========================

colspecs = [
    (int(r.pos_ini) - 1, int(r.pos_ini) - 1 + int(r.tam))
    for r in layout.itertuples()
]

names = layout["var"].astype(str).tolist()

print("Variables:", len(names))
print("Ejemplo:", names[:10])

# =========================
# 4. LEER FIXED WIDTH
# =========================

df = pd.read_fwf(
    file,
    colspecs=colspecs,
    names=names,
    encoding="latin1"
)

# =========================
# 5. VALIDACIÓN BÁSICA
# =========================

print("\nSHAPE:", df.shape)

required = ["V1028", "VD4002", "VD4009"]

for r in required:
    print(r, r in df.columns)

# chequeo estructura mínima
assert df.shape[1] > 200, "No se cargaron suficientes variables"
assert "V1028" in df.columns, "Falta ponderador V1028"

# =========================
# 6. GUARDAR LIMPIO
# =========================

out = base / "outputs" / "raw_brasil"
out.mkdir(parents=True, exist_ok=True)

df.to_parquet(out / "brasil_raw.parquet", index=False)
df.to_csv(out / "brasil_raw.csv", index=False)

print("\n✔ Guardado en:", out)
