from pathlib import Path
import pandas as pd

base = Path(r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada")

# =========================================================
# 1. ENCONTRAR TODOS LOS TXT PNADC
# =========================================================

txt_files = sorted(base.rglob("PNADC_*.txt"))

if not txt_files:
    raise FileNotFoundError("No se encontraron archivos PNADC_*.txt")

print("=" * 80)
print("TXT ENCONTRADOS")
print("=" * 80)

for i, f in enumerate(txt_files, 1):
    print(f"{i}. {f}")

print("\nTOTAL TXT:", len(txt_files))

# =========================================================
# 2. ENCONTRAR DICCIONARIO
# =========================================================

dict_files = sorted(base.rglob("Brasil*dicionario*PNADC*.xls*"))

if not dict_files:
    raise FileNotFoundError("No se encontró diccionario PNADC")

dict_path = dict_files[0]

print("\n" + "=" * 80)
print("DICCIONARIO")
print("=" * 80)
print(dict_path)

# =========================================================
# 3. LEER DICCIONARIO Y CONSTRUIR COLSPECS
# =========================================================

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

layout["pos_ini"] = pd.to_numeric(
    layout["pos_ini"],
    errors="coerce"
)

layout["tam"] = pd.to_numeric(
    layout["tam"],
    errors="coerce"
)

layout = layout.dropna()

# construir colspecs
colspecs = [
    (
        int(r.pos_ini) - 1,
        int(r.pos_ini) - 1 + int(r.tam)
    )
    for r in layout.itertuples()
]

names = layout["var"].astype(str).tolist()

print("\n" + "=" * 80)
print("LAYOUT")
print("=" * 80)

print("Variables:", len(names))
print("Ejemplo:", names[:10])

# =========================================================
# 4. LEER TODOS LOS TXT
# =========================================================

dfs = []

for file in txt_files:

    print("\n" + "=" * 80)
    print("PROCESANDO")
    print("=" * 80)
    print(file.name)

    try:

        df = pd.read_fwf(
            file,
            colspecs=colspecs,
            names=names,
            encoding="latin1"
        )

        # -----------------------------
        # VALIDACIÓN BÁSICA
        # -----------------------------

        required = ["Ano", "Trimestre", "V1028", "VD4002"]

        for r in required:
            assert r in df.columns, f"Falta variable {r}"

        assert df.shape[1] > 200, (
            "No se cargaron suficientes variables"
        )

        print("SHAPE:", df.shape)

        print(
            "Años:",
            sorted(df["Ano"].dropna().unique().tolist())
        )

        print(
            "Trimestres:",
            sorted(df["Trimestre"].dropna().unique().tolist())
        )

        dfs.append(df)

    except Exception as e:

        print(f"\nERROR EN {file.name}")
        print(e)

# =========================================================
# 5. CONCATENAR
# =========================================================

if not dfs:
    raise ValueError("No se pudo cargar ningún dataframe")

print("\n" + "=" * 80)
print("CONCATENANDO")
print("=" * 80)

df_final = pd.concat(
    dfs,
    ignore_index=True
)

# =========================================================
# 6. VALIDACIÓN FINAL
# =========================================================

print("\nSHAPE FINAL:", df_final.shape)

print("\nAÑOS FINALES")
print(df_final["Ano"].value_counts().sort_index())

print("\nTRIMESTRES FINALES")
print(df_final["Trimestre"].value_counts().sort_index())

print("\nCOMBINACIONES AÑO-TRIMESTRE")
print(
    df_final[
        ["Ano", "Trimestre"]
    ]
    .drop_duplicates()
    .sort_values(["Ano", "Trimestre"])
)

# =========================================================
# 7. GUARDAR
# =========================================================

out = base / "outputs" / "raw_brasil"
out.mkdir(parents=True, exist_ok=True)

parquet_path = out / "brasil_raw.parquet"
csv_path = out / "brasil_raw.csv"

print("\n" + "=" * 80)
print("GUARDANDO")
print("=" * 80)

df_final.to_parquet(
    parquet_path,
    index=False
)

df_final.to_csv(
    csv_path,
    index=False
)

print("\n✔ PARQUET:", parquet_path)
print("✔ CSV:", csv_path)

print("\n" + "=" * 80)
print("FINALIZADO")
print("=" * 80)