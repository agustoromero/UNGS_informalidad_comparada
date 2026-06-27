from pathlib import Path
import re
import pandas as pd

base = Path(__file__).resolve().parents[2]

SAS_INPUT_PATH = (
    base
    / "data"
    / "brasil"
    / "Dicionario_e_input_20221031"
    / "input_PNADC_trimestral.sas"
)

# =========================================================
# HELPERS
# =========================================================

def build_layout_from_input_txt(input_txt: Path) -> pd.DataFrame:

    rows = []

    pattern = re.compile(
        r"^@\s*(\d+)\s+([A-Za-z0-9_]+)\s+([^;\s]+)"
    )

    with input_txt.open(
        "r",
        encoding="latin1",
        errors="ignore"
    ) as fh:

        for line in fh:

            raw = line.strip()

            if not raw.startswith("@"):
                continue

            m = pattern.match(raw)

            if not m:
                continue

            start = int(m.group(1))
            var = m.group(2)
            fmt = m.group(3)

            width_match = re.search(
                r"(\d+)",
                fmt
            )

            if not width_match:
                continue

            width = int(width_match.group(1))

            if width <= 0:
                continue

            rows.append(
                (start, width, var)
            )

    if not rows:
        raise ValueError(
            f"No se pudo parsear {input_txt}"
        )

    layout = pd.DataFrame(
        rows,
        columns=[
            "pos_ini",
            "tam",
            "var"
        ]
    )

    layout = (
        layout
        .drop_duplicates(
            subset=["var"],
            keep="first"
        )
        .sort_values("pos_ini")
        .reset_index(drop=True)
    )

    return layout


def build_colspecs(layout):

    colspecs = [
        (
            int(r.pos_ini) - 1,
            int(r.pos_ini) - 1 + int(r.tam)
        )
        for r in layout.itertuples()
    ]

    names = (
        layout["var"]
        .astype(str)
        .tolist()
    )

    return colspecs, names


# =========================================================
# VALIDACIÓN LAYOUT
# =========================================================

if not SAS_INPUT_PATH.exists():

    raise FileNotFoundError(
        f"No existe {SAS_INPUT_PATH}"
    )

layout = build_layout_from_input_txt(
    SAS_INPUT_PATH
)

colspecs, names = build_colspecs(
    layout
)

print("=" * 80)
print("LAYOUT")
print("=" * 80)

print(
    "variables:",
    len(names)
)

print(
    "ultima posicion:",
    max(e for _, e in colspecs)
)

# =========================================================
# BUSCAR TXT
# =========================================================

txt_files = sorted(
    base.rglob("PNADC_*.txt")
)

if not txt_files:

    raise FileNotFoundError(
        "No se encontraron TXT PNADC"
    )

print("\nTXT encontrados:")

for f in txt_files:
    print(f)

# =========================================================
# PROCESAR UNO POR UNO
# =========================================================

for file in txt_files:

    print("\n" + "=" * 80)
    print(file.name)
    print("=" * 80)

    df = pd.read_fwf(
        file,
        colspecs=colspecs,
        names=names,
        encoding="latin1"
    )

    print(
        "shape:",
        df.shape
    )

    required = [
        "Ano",
        "Trimestre",
        "V1028"
    ]

    for var in required:

        if var not in df.columns:

            raise ValueError(
                f"Falta {var}"
            )

    anos = (
        df["Ano"]
        .dropna()
        .unique()
        .tolist()
    )

    trimestres = (
        df["Trimestre"]
        .dropna()
        .unique()
        .tolist()
    )

    print(
        "años:",
        anos
    )

    print(
        "trimestres:",
        trimestres
    )

    if len(anos) != 1:

        raise ValueError(
            f"{file.name} tiene múltiples años"
        )

    if len(trimestres) != 1:

        raise ValueError(
            f"{file.name} tiene múltiples trimestres"
        )

    ano = int(anos[0])
    trimestre = int(trimestres[0])

    print(
        "ponderador:",
        df["V1028"].sum()
    )

    out_dir = (
        base
        / "data"
        / "brasil_clean"
        / str(ano)
    )

    out_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    out_file = (
        out_dir
        / f"T{trimestre}.parquet"
    )

    df.to_parquet(
        out_file,
        index=False
    )

    print(
        f"guardado -> {out_file}"
    )

print("\n" + "=" * 80)
print("FINALIZADO")
print("=" * 80)