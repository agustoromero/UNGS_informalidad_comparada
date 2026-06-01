"""Construye y valida la base urbana intermedia de Brasil PNADC.

Esta rutina es deliberadamente previa a la armonización: solo carga PNADC, aplica
``V1022 == 1`` y exporta diagnósticos de cobertura y pesos. No modifica la
lógica de duplicados ni ejecuta ``build_core``.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts.common_pipeline import get_periods, load_period

REQUIRED_COLUMNS = ["V1022", "V1028", "V2007", "V2009", "VD4001", "VD4002", "VD4009", "VD4012"]
DEFAULT_YEARS = [2018, 2023]
INTERMEDIATE_DIR = Path("data/intermediate")
OUTPUT_DIR = Path("outputs/brasil")
RAW_OUTPUT = INTERMEDIATE_DIR / "brasil_raw.parquet"
URBAN_OUTPUT = INTERMEDIATE_DIR / "brasil_urbano.parquet"
AUDIT_OUTPUT = OUTPUT_DIR / "auditoria_urbano_rural.csv"
WEIGHTS_OUTPUT = OUTPUT_DIR / "validacion_pesos.xlsx"


def require_columns(df: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas críticas para validar Brasil PNADC: {missing}")


def is_urban(series: pd.Series) -> pd.Series:
    """Identifica registros urbanos con la definición oficial V1022 == 1."""
    return series.eq(1) | series.astype(str).str.strip().eq("1")


def load_brasil_raw(years: list[int]) -> pd.DataFrame:
    frames = []
    for year in years:
        periods = get_periods("brasil", year)
        for trimestre in sorted(periods):
            df = load_period("brasil", periods[trimestre]).copy()
            df["anio"] = year
            df["trimestre"] = trimestre
            df["source_path"] = str(periods[trimestre])
            require_columns(df, REQUIRED_COLUMNS)
            frames.append(df)
    if not frames:
        raise FileNotFoundError(f"No se encontraron archivos PNADC para años {years}")
    return pd.concat(frames, ignore_index=True)


def build_urban_audit(raw: pd.DataFrame, urban: pd.DataFrame) -> pd.DataFrame:
    before = raw.groupby(["anio", "trimestre"], dropna=False).size().rename("filas_antes")
    after = urban.groupby(["anio", "trimestre"], dropna=False).size().rename("filas_despues")
    audit = pd.concat([before, after], axis=1).fillna(0).reset_index()
    audit["filas_antes"] = audit["filas_antes"].astype(int)
    audit["filas_despues"] = audit["filas_despues"].astype(int)
    audit["filas_eliminadas"] = audit["filas_antes"] - audit["filas_despues"]
    audit["porcentaje_eliminado"] = audit["filas_eliminadas"] / audit["filas_antes"] * 100

    total_before = len(raw)
    total_after = len(urban)
    total = pd.DataFrame(
        [
            {
                "anio": "total",
                "trimestre": "total",
                "filas_antes": total_before,
                "filas_despues": total_after,
                "filas_eliminadas": total_before - total_after,
                "porcentaje_eliminado": (total_before - total_after) / total_before * 100 if total_before else 0,
            }
        ]
    )
    return pd.concat([audit, total], ignore_index=True)


def weighted_counts(df: pd.DataFrame, variable: str) -> pd.DataFrame:
    return (
        df.groupby(["anio", "trimestre", variable], dropna=False)
        .agg(casos=(variable, "size"), ponderados=("V1028", "sum"))
        .reset_index()
        .rename(columns={variable: "valor"})
        .assign(variable=variable)
        [["anio", "trimestre", "variable", "valor", "casos", "ponderados"]]
    )


def weight_universe(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["anio", "trimestre"], dropna=False)
        .agg(casos=("V1028", "size"), ponderados=("V1028", "sum"))
        .reset_index()
    )


def value_counts_by_year(df: pd.DataFrame, variables: list[str]) -> pd.DataFrame:
    rows = []
    for year, year_df in df.groupby("anio", dropna=False):
        for variable in variables:
            counts = year_df[variable].value_counts(dropna=False).rename_axis("valor").reset_index(name="casos")
            counts["anio"] = year
            counts["variable"] = variable
            counts["porcentaje"] = counts["casos"] / len(year_df) * 100 if len(year_df) else 0
            rows.append(counts[["anio", "variable", "valor", "casos", "porcentaje"]])
    return pd.concat(rows, ignore_index=True)


def export_outputs(raw: pd.DataFrame, urban: pd.DataFrame, audit: pd.DataFrame) -> None:
    INTERMEDIATE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    raw.to_parquet(RAW_OUTPUT, index=False)
    urban.to_parquet(URBAN_OUTPUT, index=False)
    audit.to_csv(AUDIT_OUTPUT, index=False)

    with pd.ExcelWriter(WEIGHTS_OUTPUT) as writer:
        audit.to_excel(writer, sheet_name="auditoria_urbano_rural", index=False)
        weight_universe(urban).to_excel(writer, sheet_name="universo_total", index=False)
        weighted_counts(urban, "V2007").to_excel(writer, sheet_name="sexo_V2007", index=False)
        weighted_counts(urban, "VD4001").to_excel(writer, sheet_name="actividad_VD4001", index=False)
        weighted_counts(urban, "VD4002").to_excel(writer, sheet_name="ocupacion_VD4002", index=False)
        value_counts_by_year(urban, REQUIRED_COLUMNS).to_excel(writer, sheet_name="distribuciones_minimas", index=False)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Construye Brasil urbano PNADC y valida pesos antes de armonizar")
    parser.add_argument("--years", nargs="+", type=int, default=DEFAULT_YEARS, help="Años PNADC a procesar")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw = load_brasil_raw(args.years)
    urban = raw[is_urban(raw["V1022"])].copy()
    audit = build_urban_audit(raw, urban)
    export_outputs(raw, urban, audit)

    print("===== Brasil urbano PNADC =====")
    print(audit.to_string(index=False))
    print(f"Raw parquet: {RAW_OUTPUT}")
    print(f"Urban parquet: {URBAN_OUTPUT}")
    print(f"Auditoría CSV: {AUDIT_OUTPUT}")
    print(f"Validación pesos Excel: {WEIGHTS_OUTPUT}")


if __name__ == "__main__":
    main()
