from pathlib import Path
import re
import pandas as pd

base = Path(__file__).resolve().parents[2]


# =========================================================
# HELPERS
# =========================================================

def build_layout_from_input_txt(input_txt: Path) -> pd.DataFrame:
    """
    Construye layout FWF desde input SAS oficial (fuente canónica).
    Formato esperado por línea: @<start> <var> <fmt>
    donde <fmt> puede incluir $ (carácter) y ancho numérico.
    """
    rows = []

    pattern = re.compile(r"^@\s*(\d+)\s+([A-Za-z0-9_]+)\s+([^;\s]+)")

    with input_txt.open("r", encoding="latin1", errors="ignore") as fh:
        for line in fh:
            raw = line.strip()
            if not raw.startswith("@"):
                continue

            m = pattern.match(raw)
            if not m:
                continue

            start = int(m.group(1))
            var = m.group(2)
            fmt = m.group(3)

            width_match = re.search(r"(\d+)", fmt)
            if not width_match:
                continue

            width = int(width_match.group(1))
            if width <= 0:
                continue

            rows.append((start, width, var))

    if not rows:
        raise ValueError(f"No se pudo parsear layout desde {input_txt}")

    layout = pd.DataFrame(rows, columns=["pos_ini", "tam", "var"])
    layout = layout.drop_duplicates(subset=["var"], keep="first")
    layout = layout.sort_values(["pos_ini", "var"]).reset_index(drop=True)
    return layout


def build_colspecs(layout: pd.DataFrame):
    colspecs = [
        (int(r.pos_ini) - 1, int(r.pos_ini) - 1 + int(r.tam))
        for r in layout.itertuples()
    ]
    names = layout["var"].astype(str).tolist()
    return colspecs, names


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
# 2. ENCONTRAR INPUT_TXT (SAS) Y DICCIONARIO
# =========================================================

input_files = sorted(base.rglob("input_PNADC*.txt"))
if not input_files:
    raise FileNotFoundError("No se encontró input_PNADC*.txt (layout SAS)")

input_path = input_files[0]

print("\n" + "=" * 80)
print("INPUT TXT (LAYOUT CANÓNICO)")
print("=" * 80)
print(input_path)

dict_files = sorted(base.rglob("Brasil*dicionario*PNADC*.xls*"))
if dict_files:
    print("\nDICCIONARIO detectado (solo referencia de etiquetas):")
    print(dict_files[0])

# =========================================================
# 3. CONSTRUIR COLSPECS DESDE INPUT_TXT
# =========================================================

layout = build_layout_from_input_txt(input_path)
colspecs, names = build_colspecs(layout)

print("\n" + "=" * 80)
print("LAYOUT DESDE INPUT_TXT")
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
            encoding="latin1",
        )

        required = ["Ano", "Trimestre", "V1028", "VD4002", "V2007", "V2009", "VD4009"]
        for r in required:
            assert r in df.columns, f"Falta variable {r}"

        assert df.shape[1] > 200, "No se cargaron suficientes variables"

        print("SHAPE:", df.shape)
        print("Años:", sorted(df["Ano"].dropna().unique().tolist()))
        print("Trimestres:", sorted(df["Trimestre"].dropna().unique().tolist()))

        dfs.append(df)

    except Exception as e:
        print(f"\nERROR EN {file.name}")
        print(e)

if not dfs:
    raise ValueError("No se pudo cargar ningún dataframe")

# =========================================================
# 5. CONCATENAR
# =========================================================

print("\n" + "=" * 80)
print("CONCATENANDO")
print("=" * 80)

df_final = pd.concat(dfs, ignore_index=True)

# =========================================================
# 6. VALIDACIÓN FINAL
# =========================================================

print("\nSHAPE FINAL:", df_final.shape)
print("\nAÑOS FINALES")
print(df_final["Ano"].value_counts().sort_index())
print("\nTRIMESTRES FINALES")
print(df_final["Trimestre"].value_counts().sort_index())
print("\nCOMBINACIONES AÑO-TRIMESTRE")
print(df_final[["Ano", "Trimestre"]].drop_duplicates().sort_values(["Ano", "Trimestre"]))

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

df_final.to_parquet(parquet_path, index=False)
df_final.to_csv(csv_path, index=False)

print("\n✔ PARQUET:", parquet_path)
print("✔ CSV:", csv_path)
print("\n" + "=" * 80)
print("FINALIZADO")
print("=" * 80)
