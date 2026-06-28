from pathlib import Path

import pandas as pd


BASE = Path("data/colombia")
OUT = Path("data/colombia_clean/2023")

OUT.mkdir(
    parents=True,
    exist_ok=True,
)

MONTH_TO_TRIM = {
    "Enero": 1,
    "Febrero": 1,
    "Marzo": 1,
    "Abril": 2,
    "Mayo": 2,
    "Junio": 2,
    "Julio": 3,
    "Agosto": 3,
    "Septiembre": 3,
    "Octubre": 4,
    "Noviembre": 4,
    "Diciembre": 4,
}

MERGE_KEYS = [
    "DIRECTORIO",
    "SECUENCIA_P",
    "ORDEN",
]


def read_module(path: Path) -> pd.DataFrame:
    df = pd.read_csv(
        path,
        sep=";",
        encoding="latin1",
        low_memory=False,
    )
    df.columns = [str(column).replace("\ufeff", "").strip() for column in df.columns]
    return df


def dedupe_columns(df: pd.DataFrame) -> pd.DataFrame:
    return df.loc[:, ~df.columns.duplicated()].copy()


def merge_module(base: pd.DataFrame, module: pd.DataFrame, suffix: str) -> pd.DataFrame:
    duplicate_keys = int(module.duplicated(MERGE_KEYS, keep=False).sum())
    if duplicate_keys:
        raise ValueError(f"Colombia 2023 {suffix}: claves duplicadas={duplicate_keys}")

    return base.merge(
        module,
        on=MERGE_KEYS,
        how="left",
        suffixes=("", suffix),
        validate="one_to_one",
    )


frames = {
    1: [],
    2: [],
    3: [],
    4: [],
}

for month, trim in MONTH_TO_TRIM.items():
    print(f"\n[COLOMBIA] {month}")

    possible = [
        BASE / month / month / "CSV" / "CSV",
        BASE / month / month / "CSV" / "CVS",
    ]

    folder = next((p for p in possible if p.exists()), None)
    if folder is None:
        print(f"[ERROR] no existe carpeta para {month}")
        continue

    ft = read_module(folder / "Fuerza de trabajo.CSV")
    ocupados = read_module(folder / "Ocupados.CSV")
    no_ocupados = read_module(folder / "No ocupados.CSV")
    demographics = read_module(
        folder / "Características generales, seguridad social en salud y educación.CSV"
    )

    demographic_keep = [
        *MERGE_KEYS,
        *[
            column
            for column in ["P3271", "P6040", "P3042"]
            if column in demographics.columns
        ],
    ]

    df = merge_module(ft, ocupados, "_ocu")
    df = merge_module(df, no_ocupados, "_no_ocu")
    df = merge_module(df, demographics[demographic_keep], "_dem")
    df = dedupe_columns(df)

    df["OCI"] = pd.to_numeric(df.get("OCI"), errors="coerce")
    df["DSI"] = pd.to_numeric(df.get("DSI"), errors="coerce")
    df["INI"] = df["OCI"].isna() & df["DSI"].isna()
    df["MES_NOMBRE"] = month

    activity = (
        df["OCI"].eq(1).astype(int)
        + df["DSI"].eq(1).astype(int)
        + df["INI"].astype(int)
    )
    bad_activity = int(activity.ne(1).sum())
    if bad_activity:
        raise ValueError(
            f"Colombia 2023 {month}: actividad no exclusiva en {bad_activity} filas"
        )

    frames[trim].append(df)

for trim in [1, 2, 3, 4]:
    out = pd.concat(
        frames[trim],
        ignore_index=True,
    )
    months = out["MES_NOMBRE"].nunique()
    out["FEX_C18"] = (
        pd.to_numeric(out["FEX_C18"], errors="coerce")
        / months
    )

    print(
        f"[T{trim}]",
        out.shape,
        f"meses={months}",
    )

    out.to_parquet(
        OUT / f"T{trim}.parquet",
        index=False,
    )

print("\nDONE")
