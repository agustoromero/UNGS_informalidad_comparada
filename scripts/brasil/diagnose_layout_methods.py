from pathlib import Path
import re


def parse_layout_input_txt(input_txt: Path):
    import pandas as pd

    pattern = re.compile(r"^@\s*(\d+)\s+([A-Za-z0-9_]+)\s+([^;\s]+)")
    rows = []

    with input_txt.open("r", encoding="latin1", errors="ignore") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith("@"):
                continue
            m = pattern.match(line)
            if not m:
                continue
            start = int(m.group(1))
            var = m.group(2)
            fmt = m.group(3)
            w = re.search(r"(\d+)", fmt)
            if not w:
                continue
            width = int(w.group(1))
            rows.append((start, width, var))

    layout = pd.DataFrame(rows, columns=["pos_ini", "tam", "var"])
    layout = layout.drop_duplicates(subset=["var"], keep="first")
    layout = layout.sort_values(["pos_ini", "var"]).reset_index(drop=True)
    return layout


def parse_layout_xls(dict_xls: Path):
    import pandas as pd

    xls = pd.ExcelFile(dict_xls)
    df_raw = xls.parse(xls.sheet_names[0], header=None)
    mask = df_raw.apply(lambda col: col.astype(str).str.contains("Posição inicial", na=False))
    start_row = mask.any(axis=1).idxmax()
    layout = df_raw.iloc[start_row + 1 :].copy().dropna(how="all")
    layout = layout.iloc[:, :3]
    layout.columns = ["pos_ini", "tam", "var"]
    layout = layout.dropna()
    layout["pos_ini"] = pd.to_numeric(layout["pos_ini"], errors="coerce")
    layout["tam"] = pd.to_numeric(layout["tam"], errors="coerce")
    layout = layout.dropna()
    layout["var"] = layout["var"].astype(str)
    layout = layout.sort_values(["pos_ini", "var"]).reset_index(drop=True)
    return layout


def read_sample(txt, layout, nrows=1000):
    import pandas as pd

    colspecs = [(int(r.pos_ini) - 1, int(r.pos_ini) - 1 + int(r.tam)) for r in layout.itertuples()]
    names = layout["var"].tolist()
    return pd.read_fwf(txt, colspecs=colspecs, names=names, encoding="latin1", nrows=nrows)


def print_domain_report(df, label):
    cols = ["V2007", "V2009", "VD4002", "VD4008", "VD4009", "V1028"]
    print(f"\n=== {label} ===")
    print("shape:", df.shape)
    for c in cols:
        if c not in df.columns:
            print(c, "MISSING")
            continue
        s = df[c]
        print(f"{c}: dtype={s.dtype}, na={s.isna().mean():.4f}, top={s.astype(str).value_counts(dropna=False).head(8).to_dict()}")


def main():
    try:
        import pandas as pd  # noqa
    except Exception as e:
        raise SystemExit(f"Falta pandas: {e}")

    base = Path(__file__).resolve().parents[2]
    txt_files = sorted(base.rglob("PNADC_*.txt"))
    input_files = sorted(base.rglob("input_PNADC*.txt"))
    xls_files = sorted(base.rglob("Brasil*dicionario*PNADC*.xls*"))

    if not txt_files:
        raise SystemExit("No hay PNADC_*.txt")
    if not input_files:
        raise SystemExit("No hay input_PNADC*.txt")
    if not xls_files:
        raise SystemExit("No hay diccionario XLS")

    txt = txt_files[0]
    input_txt = input_files[0]
    xls = xls_files[0]

    print("TXT:", txt)
    print("INPUT:", input_txt)
    print("XLS:", xls)

    lay_input = parse_layout_input_txt(input_txt)
    lay_xls = parse_layout_xls(xls)

    sentinel = ["V2007", "V2009", "VD4002", "VD4008", "VD4009", "V1028"]
    merged = lay_input.merge(lay_xls, on="var", how="outer", suffixes=("_input", "_xls"))
    print("\nComparación layout (centinelas):")
    print(merged[merged["var"].isin(sentinel)].to_string(index=False))

    df_input = read_sample(txt, lay_input, nrows=1000)
    df_xls = read_sample(txt, lay_xls, nrows=1000)

    print_domain_report(df_input, "LECTURA DESDE INPUT_TXT")
    print_domain_report(df_xls, "LECTURA DESDE XLS")


if __name__ == "__main__":
    main()
