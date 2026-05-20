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

    folder = None

    for p in possible:
        if p.exists():
           folder = p
           break

    if folder is None:
        print(f"[ERROR] no existe carpeta para {month}")
        continue

    ocupados_path = folder / "Ocupados.CSV"
    ft_path = folder / "Fuerza de trabajo.CSV"

    ocu = pd.read_csv(
        ocupados_path,
        sep=";",
        encoding="latin1",
        low_memory=False,
    )

    ft = pd.read_csv(
        ft_path,
        sep=";",
        encoding="latin1",
        low_memory=False,
    )

    ft_keep = (
        MERGE_KEYS
        + [
            "FEX_C18",
            "PET",
            "FFT",
        ]
    )

    ft = ft[ft_keep].copy()

    df = ocu.merge(
        ft,
        on=MERGE_KEYS,
        how="left",
    )

    df["MES_NOMBRE"] = month

    frames[trim].append(df)

for trim in [1, 2, 3, 4]:

    out = pd.concat(
        frames[trim],
        ignore_index=True,
    )

    print(
        f"[T{trim}]",
        out.shape,
    )

    out.to_parquet(
        OUT / f"T{trim}.parquet",
        index=False,
    )

print("\nDONE")