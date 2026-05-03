from pathlib import Path
import warnings
import pandas as pd

COUNTRY = "mexico"
YEAR = 2023
COE1 = Path("data/mexico/enoe_2023_trim1_csv/ENOE_COE1T123.csv")
COE2 = Path("data/mexico/enoe_2023_trim1_csv/ENOE_COE2T123.csv")
MERGE_KEYS = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ren"]


def load_data() -> pd.DataFrame:
    for p in [COE1, COE2]:
        if not p.exists():
            raise FileNotFoundError(p)
    a = pd.read_csv(COE1)
    b = pd.read_csv(COE2)
    if any(k not in a.columns or k not in b.columns for k in MERGE_KEYS):
        raise ValueError("Faltan claves de merge en COE1/COE2")
    df = a.merge(b, on=MERGE_KEYS, how="inner", validate="one_to_one")
    if df.empty:
        raise ValueError("Merge vacío de COE1 y COE2")
    return df


def clean_variables(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["id"] = df[MERGE_KEYS].astype(str).agg("_".join, axis=1)
    return df


def _pick_weight(df: pd.DataFrame) -> str:
    for c in ["fac", "FAC", "factor"]:
        if c in df.columns:
            return c
    raise ValueError("No se encontró ponderador fac")


def build_core_variables(df: pd.DataFrame) -> pd.DataFrame:
    w = _pick_weight(df)
    out = pd.DataFrame()
    out["pais"] = COUNTRY
    out["anio"] = YEAR
    out["trimestre"] = 1
    out["id"] = df["id"]
    out["ponderador"] = df[w]
    out["ocupado"] = (df.get("clase2", 0) == 1).astype(int)
    out["desocupado"] = (df.get("clase2", 0) == 2).astype(int)
    out["inactivo"] = 1 - out["ocupado"] - out["desocupado"]
    out["asalariado"] = (df.get("pos_ocu", -1) == 1).astype(int)
    out["cuentapropia"] = (df.get("pos_ocu", -1) == 3).astype(int)
    reg_no = (df.get("p3j", 0) == 2)
    no_ss = (df.get("p3m4", 0) != 4)
    tam_small = df.get("emple7c", 99).isin([1, 2, 3]) if "emple7c" in df.columns else pd.Series(False, index=df.index)
    out["informal"] = ((out["asalariado"].eq(1) & reg_no) | (out["cuentapropia"].eq(1) & (tam_small | no_ss))).astype(int)
    out["formal"] = 1 - out["informal"]
    out["sector"] = "Priv"
    out["metodologia"] = "ENOE_nueva"
    return out


def apply_weights(df: pd.DataFrame) -> pd.DataFrame:
    if df["ponderador"].isna().any():
        raise ValueError("Hay ponderadores faltantes")
    return df


def run_checks(df: pd.DataFrame) -> None:
    assert "ocupado" in df.columns
    assert df["ponderador"].notna().all()
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
