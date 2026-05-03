from pathlib import Path
import warnings
import pandas as pd

COUNTRY = "brasil"
YEAR = 2023
INPUT_PATH = Path("data/brasil/PNADC_012023_20250815/PNADC_012023.txt")


def load_data() -> pd.DataFrame:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(INPUT_PATH)
    try:
        df = pd.read_fwf(INPUT_PATH)
    except Exception:
        df = pd.read_csv(INPUT_PATH, sep=";", low_memory=False)
    return df


def clean_variables(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    id_cols = [c for c in ["UPA", "V1008", "V1014", "V2003"] if c in df.columns]
    if len(id_cols) < 2:
        raise ValueError("No se pudo construir id para PNAD (faltan claves)")
    df["id"] = df[id_cols].astype(str).agg("_".join, axis=1)
    return df


def build_core_variables(df: pd.DataFrame) -> pd.DataFrame:
    needed = ["V1028"]
    for c in needed:
        if c not in df.columns:
            raise ValueError(f"Falta columna crítica {c} en PNAD")
    out = pd.DataFrame()
    out["pais"] = COUNTRY
    out["anio"] = YEAR
    out["trimestre"] = 1
    out["id"] = df["id"]
    out["ponderador"] = df["V1028"]
    out["ocupado"] = (df.get("VD4002", "") == "Pessoas ocupadas").astype(int)
    out["desocupado"] = (df.get("VD4002", "") == "Pessoas desocupadas").astype(int)
    out["inactivo"] = 1 - out["ocupado"] - out["desocupado"]
    out["asalariado"] = df.get("VD4009", "").astype(str).str.contains("Empregado|Trabalhador doméstico|Militar", na=False).astype(int)
    out["cuentapropia"] = (df.get("VD4009", "") == "Conta-própria").astype(int)
    reg_no = df.get("VD4009", "").astype(str).str.contains("sem carteira", na=False)
    no_ss = (df.get("VD4012", "") == "Não contribuinte")
    tam_small = df.get("V4018", "").isin(["1 a 5 pessoas", "6 a 10 pessoas"]) if "V4018" in df.columns else pd.Series(False, index=df.index)
    out["informal"] = ((out["asalariado"].eq(1) & reg_no) | (out["cuentapropia"].eq(1) & (tam_small | no_ss))).astype(int)
    out["formal"] = 1 - out["informal"]
    out["sector"] = "Priv"
    return out


def apply_weights(df: pd.DataFrame) -> pd.DataFrame:
    if df["ponderador"].isna().any():
        raise ValueError("Hay ponderadores faltantes")
    return df


def run_checks(df: pd.DataFrame) -> None:
    if df["ocupado"].mean() < 0.2:
        warnings.warn("tasa de ocupación baja")


def export_data(df: pd.DataFrame) -> None:
    out = Path("outputs/harmonized")
    out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / f"{COUNTRY}_{YEAR}.parquet", index=False)
    df.to_csv(out / f"{COUNTRY}_{YEAR}.csv", index=False)


def main() -> None:
    df = load_data()
    df = clean_variables(df)
    df = build_core_variables(df)
    df = apply_weights(df)
    run_checks(df)
    export_data(df)


if __name__ == "__main__":
    main()
