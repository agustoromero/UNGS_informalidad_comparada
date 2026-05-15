from pathlib import Path
import warnings
import pandas as pd
import pyreadr

MERGE_KEYS_MX = ["cd_a", "ent", "con", "v_sel", "n_hog", "h_mud", "n_ren"]

COMMON_COLUMNS = [
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
    "informal",
    "formal",
    "sector",
]


# =============================================================================
# HELPERS
# =============================================================================

def log(msg):
    print(f"[PIPELINE] {msg}")


# =============================================================================
# PERIODS
# =============================================================================

def get_periods(country: str, year: int):

    if country == "brasil":

     parquet = Path(
        "outputs/raw_brasil/brasil_raw.parquet"
     )

     if not parquet.exists():
        raise FileNotFoundError(
            "No existe brasil_raw.parquet"
        )

     return {
        1: parquet,
        2: parquet,
        3: parquet,
        4: parquet,
    }

   

    # -------------------------------------------------------------------------

    if country == "brasil":

        parquet = Path("outputs/raw_brasil/brasil_raw.parquet")

        if not parquet.exists():
            raise FileNotFoundError(
                "No existe outputs/raw_brasil/brasil_raw.parquet"
            )

        return {1: parquet}

    # -------------------------------------------------------------------------

    if country == "mexico":

        base = Path("data/mexico")

        folders = sorted(
            base.glob(
                "2018trim*_csv"
                if year == 2018
                else "enoe_2023_trim*_csv"
            )
        )

        periods = {}

        for i, folder in enumerate(folders, start=1):

            coe1 = list(folder.glob("*COE1*.csv"))
            coe2 = list(folder.glob("*COE2*.csv"))

            if not coe1 or not coe2:
                warnings.warn(f"Faltan archivos ENOE en {folder}")
                continue

            periods[i] = (coe1[0], coe2[0])

        return periods

    # -------------------------------------------------------------------------

    if country == "colombia":

        base = Path("data/colombia")

        months = sorted(
            [p for p in base.glob("*") if p.is_dir()]
        )

        if not months:
            raise FileNotFoundError(
                "No se encontraron carpetas GEIH"
            )

        periods = {}

        q = 1

        for i in range(0, len(months), 3):

            block = months[i:i + 3]

            if len(block) < 3:
                warnings.warn(
                    f"Trimestre incompleto Colombia: {block}"
                )
                continue

            periods[q] = block
            q += 1

        return periods

    # -------------------------------------------------------------------------

    raise ValueError(country)


# =============================================================================
# LOADERS
# =============================================================================

def load_period(country: str, src, year=None):

    # -------------------------------------------------------------------------

    if country == "argentina":

        log(f"Leyendo Argentina: {src.name}")

        return next(
            iter(
                pyreadr.read_r(str(src)).values()
            )
        )

     # -------------------------------------------------------------------------

    if country == "brasil":

     log("Leyendo Brasil parquet consolidado")

    needed = [
        "Ano",
        "Trimestre",
        "UPA",
        "V1008",
        "V1014",
        "V2003",
        "V1028",
        "VD4002",
        "VD4009",
        "VD4012",
        "V4018",
    ]

    df = pd.read_parquet(
        src,
        columns=needed
    )

    df["Ano"] = df["Ano"].astype(int)
    df["Trimestre"] = df["Trimestre"].astype(int)

    df = df[df["Ano"] == year].copy()

    log(
        f"Brasil {year}: "
        f"{df.shape[0]:,} filas"
    )

    return df
    # -------------------------------------------------------------------------

    if country == "mexico":

        log(f"Leyendo México: {src[0].name}")

        a = pd.read_csv(src[0], low_memory=False)
        b = pd.read_csv(src[1], low_memory=False)

        dup_a = a.duplicated(MERGE_KEYS_MX).sum()
        dup_b = b.duplicated(MERGE_KEYS_MX).sum()

        if dup_a > 0:
            warnings.warn(
                f"Duplicados COE1: {dup_a}"
            )

        if dup_b > 0:
            warnings.warn(
                f"Duplicados COE2: {dup_b}"
            )

        merged = a.merge(
            b,
            on=MERGE_KEYS_MX,
            how="inner",
            validate="many_to_many",
        )

        log(f"México merged: {merged.shape}")

        return merged

    # -------------------------------------------------------------------------

    if country == "colombia":

        parts = []

        for m in src:

            log(f"Leyendo Colombia: {m.name}")

            car = list(m.rglob("*Caracter*csv"))
            ft = list(m.rglob("*Fuerza*csv"))
            ocu = list(m.rglob("*Ocup*csv"))

            if not car or not ft or not ocu:
                warnings.warn(
                    f"Archivos faltantes en {m}"
                )
                continue

            cdf = pd.read_csv(car[0], low_memory=False)
            fdf = pd.read_csv(ft[0], low_memory=False)
            odf = pd.read_csv(ocu[0], low_memory=False)

            keys = [
                "DIRECTORIO",
                "SECUENCIA_P",
                "ORDEN",
                "HOGAR",
            ]

            tmp = (
                cdf
                .merge(fdf, on=keys, how="inner")
                .merge(odf, on=keys, how="left")
            )

            parts.append(tmp)

        if not parts:
            raise ValueError(
                "No se pudieron cargar meses Colombia"
            )

        return pd.concat(parts, ignore_index=True)

    # -------------------------------------------------------------------------

    raise ValueError(country)


# =============================================================================
# HARMONIZATION
# =============================================================================

def build_core(
    country: str,
    year: int,
    trimestre: int,
    df: pd.DataFrame
) -> pd.DataFrame:

    out = pd.DataFrame(index=df.index)

    out["pais"] = country
    out["anio"] = year
    out["trimestre"] = trimestre

    # -------------------------------------------------------------------------
    # ARGENTINA
    # -------------------------------------------------------------------------

    if country == "argentina":

        df["id"] = (
            df["CODUSU"].astype(str)
            + "_"
            + df["NRO_HOGAR"].astype(str)
            + "_"
            + df["COMPONENTE"].astype(str)
        )

        out["ponderador"] = df["PONDERA"]

        estado = df["ESTADO"]

        cat = df["CAT_OCUP"]

        reg_no = df["PP07H"].eq(2)

        small = (
            df.get(
                "PP04C",
                pd.Series(False, index=df.index)
            )
            .isin([1, 2, 3, 4, 5, 6])
        )

    # -------------------------------------------------------------------------
    # BRASIL
    # -------------------------------------------------------------------------

    elif country == "brasil":

        df["id"] = (
            df[
                ["UPA", "V1008", "V1014", "V2003"]
            ]
            .astype(str)
            .agg("_".join, axis=1)
        )

        out["ponderador"] = df["V1028"]

        estado = df["VD4002"]

        cat = df["VD4009"].astype(str)

        reg_no = cat.str.contains(
            "sem carteira",
            case=False,
            na=False
        )

        small = (
            df.get("V4018", 99)
            .isin([1, 2])
        )

    # -------------------------------------------------------------------------
    # MEXICO
    # -------------------------------------------------------------------------

    elif country == "mexico":

        df["id"] = (
            df[MERGE_KEYS_MX]
            .astype(str)
            .agg("_".join, axis=1)
        )

        w = "fac" if "fac" in df.columns else "FAC"

        out["ponderador"] = df[w]

        estado = df.get("clase2", 0)

        cat = df.get("pos_ocu", -1)

        reg_no = df.get("p3j", 0).eq(2)

        small = (
            df.get("emple7c", 99)
            .isin([1, 2, 3])
        )

    # -------------------------------------------------------------------------
    # COLOMBIA
    # -------------------------------------------------------------------------

    else:

        keys = [
            "DIRECTORIO",
            "SECUENCIA_P",
            "ORDEN",
            "HOGAR",
        ]

        df["id"] = (
            df[keys]
            .astype(str)
            .agg("_".join, axis=1)
        )

        w = next(
            c
            for c in [
                "fex_c_2011",
                "FEX_C_2011",
                "fexp",
                "FEXP",
            ]
            if c in df.columns
        )

        out["ponderador"] = df[w]

        estado = df.get("OCI", 1)

        cat = df.get("P6430", -1)

        reg_no = ~(
            (df.get("P6440", 0) == 1)
            &
            (df.get("P6450", 0) == 2)
        )

        small = (
            df.get("P6870", 99)
            .isin([1, 2, 3, 4])
        )

    # =========================================================================

    out["id"] = df["id"]

    # -------------------------------------------------------------------------

    if country == "brasil":

        out["ocupado"] = (
            estado.eq("Pessoas ocupadas")
        ).astype(int)

        out["desocupado"] = (
            estado.eq("Pessoas desocupadas")
        ).astype(int)

    else:

        out["ocupado"] = (
            estado.eq(1)
            if hasattr(estado, "eq")
            else (estado == 1)
        ).astype(int)

        out["desocupado"] = (
            estado.eq(2)
            if hasattr(estado, "eq")
            else (estado == 2)
        ).astype(int)

    # -------------------------------------------------------------------------

    out["inactivo"] = (
        1
        - out["ocupado"]
        - out["desocupado"]
    )

    # -------------------------------------------------------------------------

    out["asalariado"] = (

        (
            cat.isin([3])
        )

        if country == "argentina"

        else (

            cat.str.contains(
                "Empregado|Trabalhador doméstico|Militar",
                case=False,
                na=False
            )

            if country == "brasil"

            else (

                (cat == 1)

                if country == "mexico"

                else cat.isin([1, 2, 3, 8])

            )
        )

    ).astype(int)

    # -------------------------------------------------------------------------

    out["cuentapropia"] = (

        cat.eq(2)

        if country == "argentina"

        else (

            cat.str.contains(
                "Conta",
                case=False,
                na=False
            )

            if country == "brasil"

            else (

                cat == 3

                if country == "mexico"

                else cat == 4

            )
        )

    ).astype(int)

    # -------------------------------------------------------------------------

    no_ss = (

        (df.get("VD4012", "") == "Não contribuinte")

        if country == "brasil"

        else (

            (df.get("p3m4", 0) != 4)

            if country == "mexico"

            else (

                (df.get("P6920", 0) == 2)

                if country == "colombia"

                else reg_no

            )
        )

    )

    # -------------------------------------------------------------------------

    out["informal"] = (
        (
            out["asalariado"].eq(1)
            &
            reg_no
        )
        |
        (
            out["cuentapropia"].eq(1)
            &
            (small | no_ss)
        )
    ).astype(int)

    out["formal"] = 1 - out["informal"]

    out["sector"] = "Priv"

    return out[COMMON_COLUMNS]


# =============================================================================
# RUNNER
# =============================================================================

def run_country_year(country: str, year: int):

    log(f"INICIANDO {country.upper()} {year}")

    periods = get_periods(country, year)

    if not periods:
        raise FileNotFoundError(
            f"Sin períodos para {country} {year}"
        )

    dfs = []

    for t, p in periods.items():

        log(f"Procesando trimestre {t}")

        raw = load_period(country, p, year)

        # -------------------------------------------------------------
        # Brasil: filtrar trimestre desde parquet consolidado
        # -------------------------------------------------------------

        if country == "brasil":

            raw_t = raw[
                raw["Trimestre"] == t
            ].copy()

            if raw_t.empty:
                warnings.warn(
                    f"Brasil {year} T{t} vacío"
                )
                continue

            core = build_core(
                country,
                year,
                t,
                raw_t
            )

        else:

            core = build_core(
                country,
                year,
                t,
                raw
            )

        # -------------------------------------------------------------
        # DOWNCAST PARA AHORRAR MEMORIA
        # -------------------------------------------------------------

        int_cols = core.select_dtypes(
            include=["int64"]
        ).columns

        float_cols = core.select_dtypes(
            include=["float64"]
        ).columns

        core[int_cols] = core[int_cols].apply(
            pd.to_numeric,
            downcast="integer"
        )

        core[float_cols] = core[float_cols].apply(
            pd.to_numeric,
            downcast="float"
        )

        log(
            f"Core T{t}: "
            f"{core.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
        )

        # -------------------------------------------------------------
        # GUARDADO INTERMEDIO POR TRIMESTRE
        # -------------------------------------------------------------

        tmp_dir = Path(
            "outputs/harmonized/tmp"
        )

        tmp_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        tmp_file = (
            tmp_dir
            / f"{country}_{year}_T{t}.parquet"
        )

        core.to_parquet(
            tmp_file,
            index=False
        )

        log(
            f"Temporal guardado: {tmp_file}"
        )

        dfs.append(core)

    # -------------------------------------------------------------
    # VALIDACIÓN
    # -------------------------------------------------------------

    if not dfs:
        raise ValueError(
            f"No se generaron datos para "
            f"{country} {year}"
        )

    # -------------------------------------------------------------
    # CONCAT FINAL
    # -------------------------------------------------------------

    log("Concatenando trimestres...")

    df = pd.concat(
        dfs,
        ignore_index=True
    )

    log(
        f"Shape final: {df.shape}"
    )

    log(
        f"Memoria final: "
        f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
    )

    # -------------------------------------------------------------
    # CHECKS
    # -------------------------------------------------------------

    assert df["ponderador"].notna().all()

    assert (df["ponderador"] > 0).all()

    if df["ocupado"].mean() < 0.2:

        warnings.warn(
            "tasa de ocupación baja"
        )

    if not (
        (
            df["ocupado"]
            + df["desocupado"]
            + df["inactivo"]
        ) == 1
    ).all():

        warnings.warn(
            "inconsistencia en condición "
            "de actividad"
        )

    # -------------------------------------------------------------
    # OUTPUT FINAL
    # -------------------------------------------------------------

    out = Path(
        "outputs/harmonized"
    )

    out.mkdir(
        parents=True,
        exist_ok=True
    )

    parquet_path = (
        out
        / f"{country}_{year}.parquet"
    )

    log(
        "Guardando parquet final..."
    )

    df.to_parquet(
        parquet_path,
        index=False
    )

    log(
        f"Guardado final: {parquet_path}"
    )

    return df