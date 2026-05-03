from pathlib import Path
import warnings
import pandas as pd

COUNTRY = "colombia"
YEAR = 2018
MONTHS_T1 = ["Enero", "Febrero", "Marzo"]
ID_KEYS = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "HOGAR"]


def _find_module_files(month: str, pattern: str) -> list[Path]:
    root = Path("data/colombia") / month
    return list(root.rglob(pattern))


def _load_month(month: str) -> pd.DataFrame:
    car = _find_module_files(month, "*Caracter*csv")
    ft = _find_module_files(month, "*Fuerza*csv")
    ocu = _find_module_files(month, "*Ocup*csv")
    if not (car and ft and ocu):
        raise FileNotFoundError(f"No se encontraron módulos GEIH completos para {month}")
    car_df = pd.read_csv(car[0])
    ft_df = pd.read_csv(ft[0])
    ocu_df = pd.read_csv(ocu[0])
    for k in ID_KEYS:
        if k not in car_df.columns or k not in ft_df.columns or k not in ocu_df.columns:
            raise ValueError(f"Falta clave {k} en módulos de {month}")
    base = car_df.merge(ft_df, on=ID_KEYS, how="inner", validate="one_to_one")
    base = base.merge(ocu_df, on=ID_KEYS, how="left", validate="one_to_one")
    if base.empty:
        raise ValueError(f"Merge vacío en {month}")
    base["mes"] = month
    return base


def load_data() -> pd.DataFrame:
    dfs = [_load_month(m) for m in MONTHS_T1]
    df = pd.concat(dfs, ignore_index=True)
    df["trimestre"] = 1
    return df


def clean_variables(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["id"] = df[ID_KEYS].astype(str).agg("_".join, axis=1)
    return df


def _weight_column(df: pd.DataFrame) -> str:
    for c in ["fex_c_2011", "FEX_C_2011", "fexp", "FEXP"]:
        if c in df.columns:
            return c
    raise ValueError("No se encontró ponderador GEIH")


def build_core_variables(df: pd.DataFrame) -> pd.DataFrame:
    w = _weight_column(df)
    out = pd.DataFrame()
    out["pais"] = COUNTRY
    out["anio"] = YEAR
    out["trimestre"] = df["trimestre"]
    out["id"] = df["id"]
    out["ponderador"] = df[w]
    out["ocupado"] = (df.get("OCI", 0) == 1).astype(int) if "OCI" in df.columns else (df.get("P6430", 0).notna()).astype(int)
    out["desocupado"] = (df.get("DES", 0) == 1).astype(int) if "DES" in df.columns else 0
    out["inactivo"] = 1 - out["ocupado"] - out["desocupado"]
    out["asalariado"] = df.get("P6430", -1).isin([1, 2, 3, 8]).astype(int)
    out["cuentapropia"] = (df.get("P6430", -1) == 4).astype(int)
    reg_no = ~((df.get("P6440", 0) == 1) & (df.get("P6450", 0) == 2))
    no_ss = (df.get("P6920", 0) == 2)
    tam_small = df.get("P6870", 99).isin([1, 2, 3, 4]) if "P6870" in df.columns else pd.Series(False, index=df.index)
    out["informal"] = ((out["asalariado"].eq(1) & reg_no) | (out["cuentapropia"].eq(1) & (tam_small | no_ss))).astype(int)
    out["formal"] = 1 - out["informal"]
    out["sector"] = "Priv"
    return out


def apply_weights(df: pd.DataFrame) -> pd.DataFrame:
    if df["ponderador"].isna().any():
        raise ValueError("Hay ponderadores faltantes")
    return df


def run_checks(df: pd.DataFrame) -> None:
    assert df["ponderador"].notna().all()
    if not ((df["ocupado"] + df["desocupado"] + df["inactivo"]) == 1).all():
        warnings.warn("inconsistencia en condición de actividad")


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
