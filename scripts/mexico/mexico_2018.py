"""Pipeline mexico 2018.

Baseline conceptual: argentina_estructura.
"""

from pathlib import Path
import pandas as pd

COUNTRY = "mexico"
YEAR = 2018


def load_data() -> pd.DataFrame:
    """Leer microdatos desde data/mexico (OneDrive/local sync)."""
    raise NotImplementedError("Definir lectura específica para MEXICO 2018")


def clean_variables(df: pd.DataFrame) -> pd.DataFrame:
    return df


def build_core_variables(df: pd.DataFrame) -> pd.DataFrame:
    # TODO: construir variables armonizadas según config/variables.yaml
    return df


def apply_weights(df: pd.DataFrame) -> pd.DataFrame:
    if "ponderador" not in df.columns:
        raise ValueError("Falta ponderador: no se puede continuar")
    return df


def export_data(df: pd.DataFrame) -> None:
    out = Path("outputs/harmonized") / f"{c}_{y}.parquet"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)


def main() -> None:
    df = load_data()
    df = clean_variables(df)
    df = build_core_variables(df)
    df = apply_weights(df)
    export_data(df)


if __name__ == "__main__":
    main()
