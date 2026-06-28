from pathlib import Path
import shutil

import pandas as pd


BASE = Path("data/colombia")
OUT = Path("data/colombia_clean/2018")

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

KEYS = [
    "DIRECTORIO",
    "SECUENCIA_P",
    "ORDEN",
]

REQUIRED_MODULES = {
    "caracteristicas_generales_personas",
    "fuerza_de_trabajo",
    "ocupados",
    "desocupados",
    "inactivos",
}


def log(msg):
    print(f"[NORMALIZE] {msg}")


def iter_month_dirs(base: Path):
    for path in base.iterdir():
        if not path.is_dir():
            continue

        name = path.name.replace(".csv", "")
        if name in MONTH_TO_Q:
            yield path, name


def find_area_files(month_dir: Path):
    files = list(month_dir.rglob("Area*")) + list(month_dir.rglob("*rea*"))
    return [path for path in files if path.is_file() and path.suffix.lower() == ".csv"]


def clean_name(path: Path) -> str:
    name = (
        path.name.replace(".csv", "")
        .replace(" - ", "_")
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("(", "")
        .replace(")", "")
    )
    if name.startswith("area_") or name.startswith("area_-_"):
        name = name.split("_", 1)[1]
    if "caracter" in name and "generales" in name:
        return "caracteristicas_generales_personas"
    if "fuerza_de_trabajo" in name:
        return "fuerza_de_trabajo"
    if "ocupados" == name or name.endswith("_ocupados"):
        return "ocupados"
    if "desocupados" in name:
        return "desocupados"
    if "inactivos" in name:
        return "inactivos"
    return name


def safe_copy(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)


def read_module(path: Path) -> pd.DataFrame:
    for encoding in ["utf-8-sig", "latin1"]:
        try:
            df = pd.read_csv(path, sep=";", encoding=encoding, low_memory=False)
            df.columns = [str(column).replace("\ufeff", "").strip() for column in df.columns]
            return df
        except UnicodeDecodeError:
            continue
    raise UnicodeDecodeError("csv", b"", 0, 1, f"No se pudo leer {path}")


def merge_module(base: pd.DataFrame, module: pd.DataFrame, label: str) -> pd.DataFrame:
    duplicate_keys = int(module.duplicated(KEYS, keep=False).sum())
    if duplicate_keys:
        raise ValueError(f"Colombia 2018 {label}: claves duplicadas={duplicate_keys}")

    return base.merge(
        module,
        on=KEYS,
        how="left",
        suffixes=("", f"_{label}"),
        validate="one_to_one",
    )


def build_month_frame(month_dir: Path, month_name: str) -> pd.DataFrame:
    modules = {
        clean_name(path): read_module(path)
        for path in find_area_files(month_dir)
    }

    missing = REQUIRED_MODULES.difference(modules)
    if missing:
        raise FileNotFoundError(f"Faltan modulos Colombia 2018 {month_name}: {sorted(missing)}")

    base = modules["fuerza_de_trabajo"]
    base = merge_module(base, modules["ocupados"], "ocu")
    base = merge_module(base, modules["desocupados"], "des")
    base = merge_module(base, modules["inactivos"], "ina")
    base = merge_module(base, modules["caracteristicas_generales_personas"], "dem")

    base["OCI"] = pd.to_numeric(base.get("OCI"), errors="coerce")
    base["DSI"] = pd.to_numeric(base.get("DSI"), errors="coerce")
    base["INI"] = pd.to_numeric(base.get("INI"), errors="coerce")

    activity = base[["OCI", "DSI", "INI"]].notna().sum(axis=1)
    bad_activity = int(activity.ne(1).sum())
    if bad_activity:
        raise ValueError(
            f"Colombia 2018 {month_name}: actividad no exclusiva en {bad_activity} filas"
        )

    base["MES_NOMBRE"] = month_name
    base["trimestre_origen"] = MONTH_TO_Q[month_name]
    return base


def normalize():
    log("Colombia 2018")

    if not BASE.exists():
        raise FileNotFoundError(BASE)

    quarter_frames = {1: [], 2: [], 3: [], 4: []}

    for month_dir, month_name in iter_month_dirs(BASE):
        quarter = MONTH_TO_Q[month_name]
        files = find_area_files(month_dir)
        if not files:
            print(f"[WARN] sin datos: {month_dir}")
            continue

        out_q = OUT / f"T{quarter}"
        for source in files:
            safe_copy(source, out_q / f"{clean_name(source)}.csv")

        frame = build_month_frame(month_dir, month_name)
        quarter_frames[quarter].append(frame)
        log(f"{month_name} -> T{quarter} OK ({len(files)} archivos)")

    for quarter in [1, 2, 3, 4]:
        if not quarter_frames[quarter]:
            raise FileNotFoundError(f"Sin meses para Colombia 2018 T{quarter}")

        df = pd.concat(quarter_frames[quarter], ignore_index=True)
        months = df["MES_NOMBRE"].nunique()
        df["FEX_DPTO_C"] = (
            pd.to_numeric(
                df["fex_c_2011"].astype(str).str.replace(",", ".", regex=False),
                errors="coerce",
            )
            / months
        )
        df.to_parquet(OUT / f"T{quarter}.parquet", index=False)
        log(f"T{quarter} parquet OK: {df.shape}; meses={months}")


if __name__ == "__main__":
    normalize()
