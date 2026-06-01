"""Construcción de base armonizada multi-país."""

from pathlib import Path
import pandas as pd

CORE_COLUMNS = [
    "pais", "anio", "trimestre", "id", "ponderador",
    "ocupado", "desocupado", "inactivo",
    "asalariado", "cuentapropia", "formal", "informal", "sector",
    "categoria_ocupacional", "sexo", "edad",
]


def load_all_countries() -> pd.DataFrame:
    files = sorted(Path("outputs/harmonized").glob("*.parquet"))
    dfs = [pd.read_parquet(f) for f in files if f.name != "harmonized.parquet"]
    if not dfs:
        return pd.DataFrame(columns=CORE_COLUMNS)
    return pd.concat(dfs, ignore_index=True)


def standardize_variables(df: pd.DataFrame) -> pd.DataFrame:
    for col in CORE_COLUMNS:
        if col not in df.columns:
            df[col] = pd.NA
    return df[CORE_COLUMNS]


def enforce_comparability(df: pd.DataFrame) -> pd.DataFrame:
    """Aplicar reglas mínimas de comparabilidad observadas en genera_base_homogenea.R."""
    if "CATOCUP" in df.columns:
        df["CATOCUP"] = df["CATOCUP"].replace({
            "Asalariados": "Asalariado",
            "Cuenta Propia": "Cuenta propia",
        })

    if "SECTOR" in df.columns and "CATOCUP" in df.columns:
        df.loc[df["CATOCUP"].isin(["Cuenta propia", "Patron"]), "SECTOR"] = "Priv"
        df.loc[df["SECTOR"].eq("SD"), "CATOCUP"] = "Asalariado"

    return df


def export_harmonized(df: pd.DataFrame) -> None:
    out = Path("outputs/harmonized/harmonized.parquet")
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)


def main() -> None:
    df = load_all_countries()
    df = standardize_variables(df)
    df = enforce_comparability(df)
    export_harmonized(df)


if __name__ == "__main__":
    main()
