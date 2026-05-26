from pathlib import Path


def main():
    try:
        import pandas as pd
    except Exception as exc:
        raise SystemExit(
            "Se requiere pandas para este diagnóstico. "
            f"Error de importación: {exc}"
        )

    path = Path("outputs/raw_brasil/brasil_raw.parquet")
    if not path.exists():
        raise SystemExit(f"No existe {path}")

    cols = ["Ano", "Trimestre", "UF", "UPA", "V1008", "V1014", "V2003", "V1028", "VD4002", "VD4009", "VD4012"]
    df = pd.read_parquet(path, columns=cols)

    print("=== SHAPE ===")
    print(df.shape)
    print("\n=== DTYPES ===")
    print(df.dtypes)

    for c in ["VD4002", "VD4009", "VD4012"]:
        s = df[c]
        print(f"\n=== {c} ===")
        print("NA share:", float(s.isna().mean()))
        print("Top 15 valores:")
        print(s.astype(str).value_counts(dropna=False).head(15))

    id_cols = ["UF", "UPA", "V1008", "V1014", "V2003"]
    dup = df.duplicated(id_cols, keep=False)
    print("\n=== DUPLICADOS ID ===")
    print("Filas duplicadas:", int(dup.sum()))
    print("Share duplicados:", float(dup.mean()))


if __name__ == "__main__":
    main()
