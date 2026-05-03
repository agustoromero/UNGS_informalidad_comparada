"""Plantilla operativa país-año para comparabilidad estricta."""

from pathlib import Path
import pandas as pd


def load_data() -> pd.DataFrame:
    """Leer microdatos del país-año desde /data/<pais>."""
    raise NotImplementedError


def clean_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Limpiar variables fuente y tipos."""
    return df


def build_core_variables(df: pd.DataFrame) -> pd.DataFrame:
    """Construir variables core según config/variables.yaml."""
    return df


def apply_weights(df: pd.DataFrame) -> pd.DataFrame:
    """Aplicar ponderadores sin modificación de magnitud."""
    if "ponderador" not in df.columns:
        raise ValueError("Falta columna ponderador")
    return df


def export_data(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(output_path, index=False)


def main() -> None:
    df = load_data()
    df = clean_variables(df)
    df = build_core_variables(df)
    df = apply_weights(df)
    export_data(df, Path("outputs/harmonized/template.parquet"))


if __name__ == "__main__":
    main()
