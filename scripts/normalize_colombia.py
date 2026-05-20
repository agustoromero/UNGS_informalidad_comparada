from pathlib import Path
import shutil

BASE = Path("data/colombia")
OUT  = Path("data/colombia_clean/2018")

MONTH_TO_Q = {
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

# -------------------------------------------------------------
# helpers
# -------------------------------------------------------------

def log(msg):
    print(f"[NORMALIZE] {msg}")


def iter_month_dirs(base: Path):
    """
    Soporta:
    - Enero/
    - Enero.csv/
    """

    for p in base.iterdir():

        if not p.is_dir():
            continue

        name = p.name.replace(".csv", "")

        if name in MONTH_TO_Q:
            yield p, name


def find_area_files(month_dir: Path):

    # caso 1: Enero.csv/Enero.csv/
    nested = list(month_dir.rglob("Área*")) + list(month_dir.rglob("Area*"))

    return [f for f in nested if f.is_file() and f.suffix.lower() == ".csv"]


def safe_copy(src: Path, dst: Path):

    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


# -------------------------------------------------------------
# main
# -------------------------------------------------------------

def normalize():

    log("Colombia 2018")

    if not BASE.exists():
        raise FileNotFoundError(BASE)

    for month_dir, month_name in iter_month_dirs(BASE):

        q = MONTH_TO_Q[month_name]

        files = find_area_files(month_dir)

        if not files:
            print(f"[WARN] sin datos: {month_dir}")
            continue

        out_q = OUT / f"T{q}"

        for f in files:

            # -----------------------------------------------------
            # limpieza nombre
            # -----------------------------------------------------

            clean_name = (
                f.name
                .replace("Área - ", "")
                .replace("Area - ", "")
                .replace(".csv", "")
                .strip()
                .lower()
                .replace(" ", "_")
                .replace("(", "")
                .replace(")", "")
            )

            dst = out_q / f"{clean_name}.csv"

            safe_copy(f, dst)

        log(f"{month_name} -> T{q} OK ({len(files)} archivos)")


if __name__ == "__main__":
    normalize()