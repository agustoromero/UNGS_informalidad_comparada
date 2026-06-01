from pathlib import Path
import warnings
import pandas as pd
import pyreadr

MERGE_KEYS_MX = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ren"]
CORE_COLUMNS = [
    "pais",
    "anio",
    "trimestre",
    "id",
    "ponderador",
    "ocupado",
    "desocupado",
    "inactivo",
    "asalariado",
    "cuentapropia",
    "formal",
    "informal",
    "sector",
    "categoria_ocupacional",
    "sexo",
    "edad",
]


def get_periods(country: str, year: int):
    if country == "argentina":
        base = Path("data/argentina")
        return {int(f.stem.split("_T")[1]): f for f in sorted(base.glob(f"base_{year}_T*.rds"))}
    if country == "brasil":
        base = Path("data/brasil")
        periods = {}
        for i, folder in enumerate(sorted(base.glob(f"PNADC_*{year}*")), start=1):
            txts = sorted(folder.glob("PNADC_*.txt")) or sorted(folder.glob("input_PNADC*.txt")) or sorted(folder.glob("*.txt"))
            if txts:
                periods[i] = txts[0]
        if not periods:
            raise FileNotFoundError(
                f"No se encontraron archivos PNADC para {year}. "
                "Ruta esperada: data/brasil/PNADC_<trimestre><anio>_*/PNADC_<trimestre><anio>.txt "
                "(también se acepta input_PNADC*.txt dentro de cada carpeta trimestral)."
            )
        return periods
    if country == "mexico":
        base = Path("data/mexico")
        folders = sorted(base.glob("2018trim*_csv" if year == 2018 else "enoe_2023_trim*_csv"))
        periods = {}
        for i, folder in enumerate(folders, start=1):
            periods[i] = (list(folder.glob("*COE1*.csv"))[0], list(folder.glob("*COE2*.csv"))[0])
        return periods
    if country == "colombia":
        months = sorted([p for p in Path("data/colombia").glob("*") if p.is_dir()])
        return {i // 3 + 1: months[i:i+3] for i in range(0, len(months), 3)}
    raise ValueError(country)


def load_period(country: str, src):
    if country == "argentina":
        return next(iter(pyreadr.read_r(str(src)).values()))
    if country == "brasil":
        return pd.read_fwf(src)
    if country == "mexico":
        a, b = pd.read_csv(src[0]), pd.read_csv(src[1])
        return a.merge(b, on=MERGE_KEYS_MX, how="inner", validate="one_to_one")
    if country == "colombia":
        parts = []
        for m in src:
            car = list(m.rglob("*Caracter*csv"))[0]
            ft = list(m.rglob("*Fuerza*csv"))[0]
            ocu = list(m.rglob("*Ocup*csv"))[0]
            cdf, fdf, odf = pd.read_csv(car), pd.read_csv(ft), pd.read_csv(ocu)
            keys = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "HOGAR"]
            parts.append(cdf.merge(fdf, on=keys, how="inner").merge(odf, on=keys, how="left"))
        return pd.concat(parts, ignore_index=True)
    raise ValueError(country)


def require_columns(df: pd.DataFrame, columns: list[str], context: str) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas críticas en {context}: {missing}")


def find_column(df: pd.DataFrame, candidates: list[str], context: str) -> str:
    for col in candidates:
        if col in df.columns:
            return col
    raise ValueError(f"No se encontró columna para {context}. Candidatas: {candidates}")


def apply_geographic_filter(country: str, df: pd.DataFrame) -> pd.DataFrame:
    """Aplica cobertura urbano/rural comparable antes de construir variables core."""
    if country == "argentina":
        return df
    if country == "brasil":
        require_columns(df, ["V1022"], "filtro urbano Brasil")
        return df[df["V1022"] == 1].copy()
    if country == "mexico":
        require_columns(df, ["t_loc"], "filtro urbano México")
        return df[df["t_loc"] != 4].copy()
    if country == "colombia":
        require_columns(df, ["CLASE"], "filtro urbano Colombia")
        return df[df["CLASE"] == 1].copy()
    raise ValueError(country)


def category_from_flags(asalariado: pd.Series, cuentapropia: pd.Series) -> pd.Series:
    return pd.Series(
        pd.NA,
        index=asalariado.index,
        dtype="object",
    ).mask(asalariado.eq(1), "Asalariado").mask(cuentapropia.eq(1), "Cuenta propia").fillna("Resto")


def age_group(edad: pd.Series) -> pd.Series:
    numeric_age = pd.to_numeric(edad, errors="coerce")
    return pd.cut(
        numeric_age,
        bins=[-1, 24, 34, 44, 54, 64, 200],
        labels=["0-24", "25-34", "35-44", "45-54", "55-64", "65+"],
    ).astype("object").fillna("Sin dato")



def flag_equals_or_contains(series: pd.Series, numeric_value: int, text: str) -> pd.Series:
    return series.eq(numeric_value) | series.astype(str).str.contains(text, case=False, na=False)


def flag_in_or_contains(series: pd.Series, numeric_values: list[int], pattern: str) -> pd.Series:
    return series.isin(numeric_values) | series.astype(str).str.contains(pattern, case=False, na=False)

def build_core(country: str, year: int, trimestre: int, df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["pais"] = country
    out["anio"] = year
    out["trimestre"] = trimestre
    if country == "argentina":
        require_columns(df, ["CODUSU", "NRO_HOGAR", "COMPONENTE", "PONDERA", "ESTADO", "CAT_OCUP", "PP07H"], "Argentina")
        id_series = df["CODUSU"].astype(str)+"_"+df["NRO_HOGAR"].astype(str)+"_"+df["COMPONENTE"].astype(str)
        out["ponderador"] = df["PONDERA"]
        estado = df["ESTADO"]
        cat = df["CAT_OCUP"]
        reg_no = df["PP07H"].eq(2)
        small = df.get("PP04C", pd.Series(False,index=df.index)).isin([1,2,3,4,5,6])
        out["sexo"] = df.get("CH04", pd.Series(pd.NA, index=df.index)).map({1: "Varon", 2: "Mujer"})
        out["edad"] = df.get("CH06", pd.Series(pd.NA, index=df.index))
        out["sector"] = "Priv"
        if "PP04B_COD" in df.columns:
            out.loc[df["PP04B_COD"].isin([75, *range(7500, 7600)]), "sector"] = "Pub"
            out.loc[df["PP04B_COD"].isin([95, *range(9500, 9600)]), "sector"] = "SD"
    elif country == "brasil":
        require_columns(df, ["UPA", "V1008", "V1014", "V2003", "V1028", "VD4002", "VD4009"], "Brasil")
        id_series = df[["UPA","V1008","V1014","V2003"]].astype(str).agg("_".join, axis=1)
        out["ponderador"] = df["V1028"]
        estado = df["VD4002"]
        cat = df["VD4009"]
        reg_no = cat.isin([2, 4, 6]) | cat.astype(str).str.contains("sem carteira", case=False, na=False)
        small = df.get("V4018", pd.Series("", index=df.index)).isin(["1 a 5 pessoas", "6 a 10 pessoas"])
        out["sexo"] = df.get("V2007", pd.Series(pd.NA, index=df.index)).replace({1: "Varon", 2: "Mujer", "Homem": "Varon", "Mulher": "Mujer"})
        out["edad"] = df.get("V2009", pd.Series(pd.NA, index=df.index))
        out["sector"] = "Priv"
        cat_str = cat.astype(str)
        out.loc[cat.isin([5, 6, 7]) | cat_str.str.contains("setor público|Militar|servidor estatutário", case=False, na=False), "sector"] = "Pub"
        out.loc[cat.isin([3, 4]) | cat_str.str.contains("Trabalhador doméstico", case=False, na=False), "sector"] = "SD"
    elif country == "mexico":
        require_columns(df, [*MERGE_KEYS_MX, "clase2", "pos_ocu"], "México")
        id_series = df[MERGE_KEYS_MX].astype(str).agg("_".join, axis=1)
        weight_col = find_column(df, ["fac", "FAC"], "ponderador México")
        out["ponderador"] = df[weight_col]
        estado = df["clase2"]
        cat = df["pos_ocu"]
        reg_no = df.get("p3j", pd.Series(0, index=df.index)).eq(2)
        small = df.get("emple7c", pd.Series(99, index=df.index)).isin([1,2,3])
        out["sexo"] = df.get("sex", pd.Series(pd.NA, index=df.index)).map({1: "Varon", 2: "Mujer"})
        out["edad"] = df.get("eda", pd.Series(pd.NA, index=df.index))
        out["sector"] = "Resto"
        if "tue2" in df.columns:
            out.loc[df["tue2"].isin([1, 2, 3, 5, 7]), "sector"] = "Priv"
            out.loc[df["tue2"].eq(4), "sector"] = "Pub"
            out.loc[df["tue2"].eq(6), "sector"] = "SD"
    else:
        keys = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "HOGAR"]
        require_columns(df, [*keys, "P6430"], "Colombia")
        id_series = df[keys].astype(str).agg("_".join, axis=1)
        weight_col = find_column(df, ["fex_c", "FEX_C", "fex_c_2011", "FEX_C_2011", "fexp", "FEXP"], "ponderador Colombia")
        out["ponderador"] = df[weight_col]
        estado = df.get("OCI", pd.Series(1, index=df.index))
        cat = df["P6430"]
        reg_no = ~((df.get("P6440", pd.Series(0, index=df.index)) == 1) & (df.get("P6450", pd.Series(0, index=df.index)) == 2))
        small = df.get("P6870", pd.Series(99, index=df.index)).isin([1,2,3,4])
        out["sexo"] = df.get("P6020", pd.Series(pd.NA, index=df.index)).map({1: "Varon", 2: "Mujer"})
        out["edad"] = df.get("P6040", pd.Series(pd.NA, index=df.index))
        out["sector"] = "Resto"
        out.loc[cat.isin([1, 4, 5, 7]), "sector"] = "Priv"
        out.loc[cat.eq(2), "sector"] = "Pub"
        out.loc[cat.eq(3), "sector"] = "SD"

    out["id"] = id_series
    if country == "brasil":
        out["ocupado"] = flag_equals_or_contains(estado, 1, "Pessoas ocupadas").astype(int)
        out["desocupado"] = flag_equals_or_contains(estado, 2, "Pessoas desocupadas").astype(int)
        out["asalariado"] = flag_in_or_contains(cat, [1, 2, 3, 4, 5, 6, 7], "Empregado|Trabalhador doméstico|Militar").astype(int)
        out["cuentapropia"] = flag_in_or_contains(cat, [9], "Conta-própria").astype(int)
    else:
        out["ocupado"] = estado.eq(1).astype(int)
        out["desocupado"] = estado.eq(2).astype(int)
        out["asalariado"] = (cat.isin([3]) if country=="argentina" else (cat==1 if country=="mexico" else cat.isin([1,2,3,8]))).astype(int)
        out["cuentapropia"] = (cat.eq(2) if country=="argentina" else (cat==3 if country=="mexico" else cat==4)).astype(int)
    out["inactivo"] = 1 - out["ocupado"] - out["desocupado"]
    out["categoria_ocupacional"] = category_from_flags(out["asalariado"], out["cuentapropia"])
    no_ss = (df.get("VD4012", pd.Series("", index=df.index)).isin([2]) | df.get("VD4012", pd.Series("", index=df.index)).astype(str).str.contains("Não contribuinte", case=False, na=False)) if country=="brasil" else (df.get("p3m4", pd.Series(0, index=df.index))!=4 if country=="mexico" else (df.get("P6920", pd.Series(0, index=df.index))==2 if country=="colombia" else reg_no))
    out["informal"] = ((out["asalariado"].eq(1) & reg_no) | (out["cuentapropia"].eq(1) & (small | no_ss))).astype(int)
    out["formal"] = 1 - out["informal"]
    return out[CORE_COLUMNS]


def weighted_sum(df: pd.DataFrame, flag: str) -> float:
    return (df[flag].fillna(0) * df["ponderador"]).sum()


def summary_row(df: pd.DataFrame, label: str = "total") -> dict:
    ocupados = weighted_sum(df, "ocupado")
    total_weight = df["ponderador"].sum()
    informal_weight = (df["informal"].fillna(0) * df["ocupado"].fillna(0) * df["ponderador"]).sum()
    return {
        "grupo": label,
        "poblacion_ponderada": total_weight,
        "ocupados": ocupados,
        "asalariados": weighted_sum(df, "asalariado"),
        "informales": informal_weight,
        "tasa_ocupacion": ocupados / total_weight if total_weight else pd.NA,
        "tasa_informalidad": informal_weight / ocupados if ocupados else pd.NA,
    }


def grouped_summary(df: pd.DataFrame, column: str) -> pd.DataFrame:
    rows = []
    for value, group in df.groupby(column, dropna=False):
        rows.append(summary_row(group, "Sin dato" if pd.isna(value) else str(value)))
    return pd.DataFrame(rows)


def export_summary_tables(df: pd.DataFrame, country: str, year: int) -> None:
    out = Path("outputs/tablas")
    out.mkdir(parents=True, exist_ok=True)
    occupied = df[df["ocupado"] == 1].copy()
    occupied["grupo_edad"] = age_group(occupied["edad"])
    with pd.ExcelWriter(out / f"{country}_{year}.xlsx") as writer:
        pd.DataFrame([summary_row(df)]).to_excel(writer, sheet_name="resumen", index=False)
        grouped_summary(occupied, "categoria_ocupacional").to_excel(writer, sheet_name="categoria_ocupacional", index=False)
        grouped_summary(occupied, "sector").to_excel(writer, sheet_name="sector", index=False)
        grouped_summary(occupied, "sexo").to_excel(writer, sheet_name="sexo", index=False)
        grouped_summary(occupied, "grupo_edad").to_excel(writer, sheet_name="edad", index=False)


def run_country_year(country: str, year: int):
    periods = get_periods(country, year)
    if not periods:
        raise FileNotFoundError(f"Sin períodos para {country} {year}")
    dfs = []
    for trimestre in sorted(periods):
        raw = load_period(country, periods[trimestre])
        filtered = apply_geographic_filter(country, raw)
        dfs.append(build_core(country, year, trimestre, filtered))
    df = pd.concat(dfs, ignore_index=True)
    assert df["ponderador"].notna().all()
    if df["ocupado"].mean() < 0.2:
        warnings.warn("tasa de ocupación baja")
    if not ((df["ocupado"] + df["desocupado"] + df["inactivo"]) == 1).all():
        warnings.warn("inconsistencia en condición de actividad")
    assert df["trimestre"].nunique() >= 4
    out = Path("outputs/harmonized"); out.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out / f"{country}_{year}.parquet", index=False)
    df.to_csv(out / f"{country}_{year}.csv", index=False)
    export_summary_tables(df, country, year)
