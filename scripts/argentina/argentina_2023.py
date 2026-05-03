from pathlib import Path
import warnings
import pandas as pd
import pyreadr

COUNTRY = "argentina"
YEAR = 2023
INPUT_PATH = Path("data/argentina/base_2023_T3.rds")


def _require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    miss = [c for c in cols if c not in df.columns]
    if miss:
        raise ValueError(f"Faltan columnas críticas: {miss}")


def load_data() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"No existe {INPUT_PATH}")
    result = pyreadr.read_r(str(INPUT_PATH))
    df = next(iter(result.values()))
    return df


def clean_variables(df: pd.DataFrame) -> pd.DataFrame:
    _require_columns(df, ["CODUSU", "NRO_HOGAR", "COMPONENTE", "ESTADO", "CAT_OCUP", "PONDERA", "PP07H"])
    df = df.copy()
    df["id"] = df["CODUSU"].astype(str) + "_" + df["NRO_HOGAR"].astype(str) + "_" + df["COMPONENTE"].astype(str)
    return df


def build_core_variables(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame()
    out["pais"] = COUNTRY
    out["anio"] = YEAR
    out["trimestre"] = df["TRIMESTRE"] if "TRIMESTRE" in df.columns else 3
    out["id"] = df["id"]
    out["ponderador"] = df["PONDERA"]
    out["ocupado"] = (df["ESTADO"] == 1).astype(int)
    out["desocupado"] = (df["ESTADO"] == 2).astype(int)
    out["inactivo"] = (df["ESTADO"] == 3).astype(int)
    out["asalariado"] = (df["CAT_OCUP"] == 3).astype(int)
    out["cuentapropia"] = (df["CAT_OCUP"] == 2).astype(int)
    informal_asal = (out["asalariado"].eq(1) & df["PP07H"].eq(2))
    size_small = df["PP04C"].isin([1, 2, 3, 4, 5, 6]) if "PP04C" in df.columns else pd.Series(False, index=df.index)
    informal_cp = out["cuentapropia"].eq(1) & (size_small | df["PP07H"].eq(2))
    out["informal"] = (informal_asal | informal_cp).astype(int)
    out["formal"] = 1 - out["informal"]
    out["sector"] = "Priv"
    return out


def apply_weights(df: pd.DataFrame) -> pd.DataFrame:
    if "ponderador" not in df.columns or df["ponderador"].isna().any():
        raise ValueError("Hay ponderadores faltantes")
    return df


def run_checks(df: pd.DataFrame) -> None:
    assert "ocupado" in df.columns
    assert "ponderador" in df.columns
    assert df["ponderador"].notna().all()
    if df["ocupado"].mean() < 0.2:
        warnings.warn("tasa de ocupación baja")
    if not ((df["ocupado"] + df["desocupado"] + df["inactivo"]) == 1).all():
        warnings.warn("inconsistencia en condición de actividad")


def export_data(df: pd.DataFrame) -> None:
    base = Path("outputs/harmonized")
    base.mkdir(parents=True, exist_ok=True)
    df.to_parquet(base / f"{COUNTRY}_{YEAR}.parquet", index=False)
    df.to_csv(base / f"{COUNTRY}_{YEAR}.csv", index=False)


def main() -> None:
    df = load_data()
    df = clean_variables(df)
    df = build_core_variables(df)
    df = apply_weights(df)
    run_checks(df)
    export_data(df)


if __name__ == "__main__":
    main()
