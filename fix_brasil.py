import pandas as pd

df = pd.read_parquet("outputs/raw_brasil/brasil_raw.parquet")

print("=" * 80)
print("COLUMNAS")
print("=" * 80)
print(df.columns.tolist())

print("\n" + "=" * 80)
print("AÑOS")
print("=" * 80)

print(df["Ano"].value_counts(dropna=False).sort_index())

print("\n" + "=" * 80)
print("VARIABLES CLAVE")
print("=" * 80)

needed = [
    "Ano",
    "Trimestre",
    "V1028",
    "VD4001",
    "VD4002",
]

for v in needed:
    print(f"{v}: {'OK' if v in df.columns else 'FALTA'}")