from pathlib import Path
import warnings
import pandas as pd
import pyreadr

MERGE_KEYS_MX = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ren"]


def get_periods(country: str, year: int):
    if country == "argentina":
        base = Path("data/argentina")
        return {int(f.stem.split("_T")[1]): f for f in sorted(base.glob(f"base_{year}_T*.rds"))}
    if country == "brasil":
        base = Path("data/brasil")
        periods = {}
        for i, folder in enumerate(sorted(base.glob(f"PNADC_*{year}*")), start=1):
            txts = list(folder.glob("*.txt"))
            if txts:
                periods[i] = txts[0]
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


def build_core(country: str, year: int, trimestre: int, df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["pais"] = country
    out["anio"] = year
    out["trimestre"] = trimestre
    if country == "argentina":
        id_series = df["CODUSU"].astype(str)+"_"+df["NRO_HOGAR"].astype(str)+"_"+df["COMPONENTE"].astype(str)
        out["ponderador"] = df["PONDERA"]
        estado = df["ESTADO"]
        cat = df["CAT_OCUP"]
        reg_no = df["PP07H"].eq(2)
        small = df.get("PP04C", pd.Series(False,index=df.index)).isin([1,2,3,4,5,6])
    elif country == "brasil":
        id_series = df[[c for c in ["UPA","V1008","V1014","V2003"] if c in df.columns]].astype(str).agg("_".join, axis=1)
        out["ponderador"] = df["V1028"]
        estado = df.get("VD4002","")
        cat = df.get("VD4009","")
        reg_no = cat.astype(str).str.contains("sem carteira",na=False)
        small = df.get("V4018","").isin(["1 a 5 pessoas","6 a 10 pessoas"])
    elif country == "mexico":
        id_series = df[MERGE_KEYS_MX].astype(str).agg("_".join, axis=1)
        w = "fac" if "fac" in df.columns else "FAC"
        out["ponderador"] = df[w]
        estado = df.get("clase2",0)
        cat = df.get("pos_ocu",-1)
        reg_no = df.get("p3j",0).eq(2)
        small = df.get("emple7c",99).isin([1,2,3])
    else:
        keys=["DIRECTORIO","SECUENCIA_P","ORDEN","HOGAR"]
        id_series = df[keys].astype(str).agg("_".join, axis=1)
        w = next(c for c in ["fex_c_2011","FEX_C_2011","fexp","FEXP"] if c in df.columns)
        out["ponderador"] = df[w]
        estado = df.get("OCI",1)
        cat = df.get("P6430",-1)
        reg_no = ~((df.get("P6440",0)==1)&(df.get("P6450",0)==2))
        small = df.get("P6870",99).isin([1,2,3,4])

    out["id"] = id_series
    out["ocupado"] = (estado.eq(1) if hasattr(estado,'eq') else (estado=="Pessoas ocupadas")).astype(int)
    out["desocupado"] = (estado.eq(2) if hasattr(estado,'eq') else (estado=="Pessoas desocupadas")).astype(int)
    out["inactivo"] = 1 - out["ocupado"] - out["desocupado"]
    out["asalariado"] = (cat.isin([3]) if country=="argentina" else (cat.astype(str).str.contains("Empregado|Trabalhador doméstico|Militar",na=False) if country=="brasil" else (cat==1 if country=="mexico" else cat.isin([1,2,3,8])))).astype(int)
    out["cuentapropia"] = (cat.eq(2) if country=="argentina" else (cat.eq("Conta-própria") if country=="brasil" else (cat==3 if country=="mexico" else cat==4))).astype(int)
    no_ss = (df.get("VD4012","")=="Não contribuinte") if country=="brasil" else (df.get("p3m4",0)!=4 if country=="mexico" else (df.get("P6920",0)==2 if country=="colombia" else reg_no))
    out["informal"] = ((out["asalariado"].eq(1) & reg_no) | (out["cuentapropia"].eq(1) & (small | no_ss))).astype(int)
    out["formal"] = 1 - out["informal"]
    out["sector"] = "Priv"
    return out


def run_country_year(country: str, year: int):
    periods = get_periods(country, year)
    if not periods:
        raise FileNotFoundError(f"Sin períodos para {country} {year}")
    dfs = [build_core(country, year, t, load_period(country, periods[t])) for t in sorted(periods)]
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
