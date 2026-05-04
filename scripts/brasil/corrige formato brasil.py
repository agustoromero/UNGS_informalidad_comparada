import pandas as pd
from pathlib import Path

# ----------------------------
# 1. rutas
# ----------------------------
base = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")

file = list(base.rglob("PNADC_012018.txt"))[0]
dict_path = list(base.rglob("Brasil*dicionario*PNADC*.xls*"))[0]

# ----------------------------
# 2. leer diccionario Excel
# ----------------------------
xls = pd.ExcelFile(dict_path)
raw = xls.parse(xls.sheet_names[0], header=None)

# ----------------------------
# 3. detectar inicio de tabla (robusto)
# ----------------------------
start_row = None

for i in range(len(raw)):
    row = raw.iloc[i].astype(str)
    if row.str.contains("Posição inicial", na=False).any():
        start_row = i
        break

if start_row is None:
    raise ValueError("No se encontró 'Posição inicial' en el diccionario")

# ----------------------------
# 4. extraer bloque útil
# ----------------------------
layout = raw.iloc[start_row + 1:].copy()
layout = layout.dropna(how="all")

# quedarnos con primeras 3 columnas útiles
layout = layout.iloc[:, :3]
layout.columns = ["pos_ini", "tam", "var"]

# ----------------------------
# 5. limpieza fuerte
# ----------------------------
layout = layout.dropna()

layout["pos_ini"] = pd.to_numeric(layout["pos_ini"], errors="coerce")
layout["tam"] = pd.to_numeric(layout["tam"], errors="coerce")

layout = layout.dropna()

# filtrar basura
layout = layout[(layout["pos_ini"] > 0) & (layout["tam"] > 0)]

# ----------------------------
# 6. colspecs
# ----------------------------
colspecs = [
    (int(r.pos_ini) - 1, int(r.pos_ini) - 1 + int(r.tam))
    for r in layout.itertuples()
]

names = layout["var"].astype(str).tolist()

# ----------------------------
# 7. leer microdato
# ----------------------------
df = pd.read_fwf(
    file,
    colspecs=colspecs,
    names=names,
    encoding="latin1"
)

# ----------------------------
# 8. sanity check
# ----------------------------
print("Shape:", df.shape)
print(df.head())

