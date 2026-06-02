from pathlib import Path
import warnings

import pandas as pd
import pyreadr


MERGE_KEYS_MX = [
    "cd_a",
    "ent",
    "con",
    "v_sel",
    "n_hog",
    "h_mud",
    "n_ren",
]


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


def summarize_duplicate_ids(df: pd.DataFrame, id_col, weight_col: str, label: str) -> None:

    dup_mask = df.duplicated(id_col, keep=False)
    dup_rows = int(dup_mask.sum())

    if dup_rows == 0:
        log(f"{label}: sin IDs duplicados")
        return

    dup_share = dup_rows / max(len(df), 1)
    id_cols = id_col if isinstance(id_col, list) else [id_col]
    duplicated = df.loc[dup_mask, [*id_cols, weight_col]].copy()

    weight_variation = (
        duplicated
        .groupby(id_cols, dropna=False)[weight_col]
        .nunique(dropna=True)
        .gt(1)
        .mean()
    )

    warnings.warn(
        f"{label}: {dup_rows:,} filas con ID duplicado "
        f"({dup_share:.2%} del trimestre); "
        f"{weight_variation:.2%} de IDs duplicados con V1028 variable"
    )



# =============================================================================
# PERIODS
# =============================================================================

def get_periods(country: str, year: int):

    # -------------------------------------------------------------------------
    # ARGENTINA
    # -------------------------------------------------------------------------

    if country == "argentina":

        base = Path("data/argentina")

        return {
            int(f.stem.split("_T")[1]): f
            for f in sorted(
                base.glob(f"base_{year}_T*.rds")
            )
        }

    # -------------------------------------------------------------------------
    # BRASIL
    # -------------------------------------------------------------------------

    if country == "brasil":

        urban_parquet = Path("data/intermediate/brasil_urbano.parquet")
        raw_parquet = Path("outputs/raw_brasil/brasil_raw.parquet")

        parquet = urban_parquet if urban_parquet.exists() else raw_parquet

        if not parquet.exists():
            raise FileNotFoundError(
                "No existe ninguno de los archivos de Brasil: data/intermediate/brasil_urbano.parquet o outputs/raw_brasil/brasil_raw.parquet"
            )

        return {
            1: parquet,
            2: parquet,
            3: parquet,
            4: parquet,
        }

    # -------------------------------------------------------------------------
    # MEXICO
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

                warnings.warn(
                    f"Faltan archivos ENOE en {folder}"
                )

                continue

            periods[i] = (
                coe1[0],
                coe2[0],
            )

        return periods

    # -------------------------------------------------------------------------
    # COLOMBIA
    # -------------------------------------------------------------------------

    if country == "colombia":

        base = Path("data/colombia_clean") / str(year)

        if not base.exists():
            raise FileNotFoundError(f"No existe {base}")

        periods = {
            1: base / "T1.parquet",
            2: base / "T2.parquet",
            3: base / "T3.parquet",
            4: base / "T4.parquet",
        }

        return periods

    # -------------------------------------------------------------------------

    raise ValueError(country)


# =============================================================================
# LOADERS
# =============================================================================

def load_period(country: str, src, year=None):

    # -------------------------------------------------------------------------
    # ARGENTINA
    # -------------------------------------------------------------------------

    if country == "argentina":

        log(f"Leyendo Argentina: {src.name}")

        return next(
            iter(
                pyreadr.read_r(str(src)).values()
            )
        )

    # -------------------------------------------------------------------------
    # BRASIL
    # -------------------------------------------------------------------------

    if country == "brasil":

        log("Leyendo Brasil parquet consolidado")

        needed = [
            "Ano",
            "Trimestre",
            "UF",    
            "UPA",
            "V1008",
            "V1014",
            "V2003",
            "V1022",
            "V1028",
            "VD4002",
            "VD4009",
            "VD4012",
            "V4018",
        ]

        df = pd.read_parquet(
            src,
            columns=needed,
            filters=[("Ano", "==", year)],
        )

        df["Ano"] = (
            pd.to_numeric(
                df["Ano"],
                errors="coerce",
            )
            .astype("Int64")
        )

        df["Trimestre"] = (
            pd.to_numeric(
                df["Trimestre"],
                errors="coerce",
            )
            .astype("Int64")
        )

        log(
            f"Brasil {year}: "
            f"{df.shape[0]:,} filas"
        )

        return df

    # -------------------------------------------------------------------------
    # MEXICO
    # -------------------------------------------------------------------------

    if country == "mexico":

        log(f"Leyendo México: {src[0].name}")

        a = pd.read_csv(
            src[0],
            low_memory=False,
        )

        b = pd.read_csv(
            src[1],
            low_memory=False,
        )

        dup_a = a.duplicated(
            MERGE_KEYS_MX
        ).sum()

        dup_b = b.duplicated(
            MERGE_KEYS_MX
        ).sum()

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

        # -------------------------------------------------------------
        # SDEMT
        # -------------------------------------------------------------

        folder = src[0].parent

        sdemt_files = list(
         folder.glob("*SDEMT*.csv")
        )

        if sdemt_files:

         sdemt = pd.read_csv(
          sdemt_files[0],
          low_memory=False,
          encoding="latin1",
         )

         keep = [
             c
             for c in [
                 *MERGE_KEYS_MX,
                 "clase1",
                 "clase2",
                 "pos_ocu",
                 "emp_ppal",
                 "seg_soc",
                 "tue_ppal",
                 "medicasc",
                 "t_loc",
                 "t_loc_tri",
                 "t_loc_men",
                 "fac",
             ]
             if c in sdemt.columns
         ]

         sdemt = sdemt[keep]

         merged = merged.merge(
             sdemt,
             on=MERGE_KEYS_MX,
             how="left",
         )

        else:
         warnings.warn(
         f"No se encontró SDEMT en {folder}"
         )

        log(
            f"México merged: {merged.shape}"
         )

        na_share = merged[
            ["clase2", "pos_ocu", "emp_ppal"]
         ].isna().mean()

        log(
            f"NA shares SDEMT:\n{na_share}"
         )

        return merged

    # -------------------------------------------------------------------------
    # COLOMBIA
    # -------------------------------------------------------------------------

    if country == "colombia":

        log(f"Leyendo parquet Colombia: {src.name}")

        return pd.read_parquet(src)

    # -------------------------------------------------------------------------

    raise ValueError(country)


def apply_geography_filter(country: str, year: int, df: pd.DataFrame) -> pd.DataFrame:

    if country == "argentina":
        return df

    if country == "brasil":
        if "V1022" not in df.columns:
            warnings.warn(
                "Brasil: no se encontró V1022 para filtrar urbano; se conserva el conjunto actual"
            )
            return df

        urban = df[df["V1022"].astype(str).str.strip().eq("1")].copy()

        log(
            f"Brasil {year}: urbano filtrado {len(urban):,} / {len(df):,} filas"
        )

        return urban

    if country == "mexico":
        loc_cols = [
            c
            for c in ["t_loc", "t_loc_tri", "t_loc_men"]
            if c in df.columns
        ]

        if not loc_cols:
            warnings.warn(
                "México: no se encontró t_loc/t_loc_tri/t_loc_men para filtrar urbano; se conserva el conjunto actual"
            )
            return df

        loc_col = loc_cols[0]
        urban = df[
            pd.to_numeric(df[loc_col], errors="coerce").ne(4)
        ].copy()

        log(
            f"México {year}: urbano filtrado {loc_col} != 4 -> {len(urban):,} / {len(df):,} filas"
        )

        return urban

    if country == "colombia":
        if "CLASE" in df.columns:
            urban = df[
                pd.to_numeric(df["CLASE"], errors="coerce").eq(1)
            ].copy()

            log(
                f"Colombia {year}: urbano filtrado CLASE == 1 -> {len(urban):,} / {len(df):,} filas"
            )

            return urban

        warnings.warn(
            "Colombia: no se encontró CLASE para filtrar urbano; se conserva el conjunto actual"
        )
        return df

    return df


# =============================================================================
# HARMONIZATION
# =============================================================================

def build_core(
    country: str,
    year: int,
    trimestre: int,
    df: pd.DataFrame,
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
                pd.Series(
                    False,
                    index=df.index,
                ),
            )
            .isin([1, 2, 3, 4, 5, 6])
        )

    # -------------------------------------------------------------------------
    # BRASIL
    # -------------------------------------------------------------------------
    # BRASIL (PNADC)
    #
    # ID:
    # UF + UPA + V1008 + V1014 + V2003
    #
    # Observación:
    # ~4% de IDs aparecen múltiples veces dentro del trimestre.
    # No son duplicados exactos.
    # Las diferencias se concentran en ponderadores (V1028)
    # y variables derivadas.
    # No elimino duplicados.
    elif country == "brasil":

        df["id"] = (
            df[
                [
                    "UF",    
                    "UPA",
                    "V1008",
                    "V1014",
                    "V2003",
                ]
            ]
            .astype(str)
            .agg("_".join, axis=1)
        )

        out["id"] = df["id"]  

        out["ponderador"] = df["V1028"]

        estado = pd.to_numeric(
           df["VD4002"],
           errors="coerce",
        )

        cat = pd.to_numeric(
            df["VD4009"],
            errors="coerce",
        )
        reg_no = pd.Series(
            False,
            index=df.index,
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

        out["id"] = df["id"]

        # ---------------------------------------------------------------------
        # PONDERADOR
        # ---------------------------------------------------------------------

        if "fac" in df.columns:

         out["ponderador"] = df["fac"]

        elif "FAC" in df.columns:

         out["ponderador"] = df["FAC"]

        elif "fac_tri" in df.columns:

         out["ponderador"] = df["fac_tri"]

        elif "fac_tri_x" in df.columns:

         out["ponderador"] = df["fac_tri_x"]

        elif "fac_tri_y" in df.columns:

         out["ponderador"] = df["fac_tri_y"]

        else:

         raise ValueError(
             "México sin ponderador"
          )

        # ---------------------------------------------------------------------
        # CONDICION ACTIVIDAD
        # clase2:
        # 1 ocupado
        # 2 desocupado
        # 3 disponible
        # 4 no disponible
        # ---------------------------------------------------------------------

        if "clase2" in df.columns:

            estado = pd.to_numeric(
                df["clase2"],
                errors="coerce",
            )

        else:

            warnings.warn(
                "México sin clase2; usando r_def"
            )

            estado = pd.to_numeric(
                df.get("r_def", 0),
                errors="coerce",
            )

        # ---------------------------------------------------------------------
        # POSICION OCUPACION
        # pos_ocu:
        # 1 subordinado/remunerado
        # 3 cuenta propia
        # ---------------------------------------------------------------------

        if "pos_ocu" in df.columns:

            cat = pd.to_numeric(
                df["pos_ocu"],
                errors="coerce",
            )

        else:

            warnings.warn(
                "México sin pos_ocu; usando p3"
            )

            cat = pd.to_numeric(
                df.get("p3", -1),
                errors="coerce",
            )

        # ---------------------------------------------------------------------
        # SIN CONTRATO
        # ---------------------------------------------------------------------

        if "p3j" in df.columns:

            reg_no = (
                pd.to_numeric(
                    df["p3j"],
                    errors="coerce",
                )
                .eq(2)
            )

        elif "p3j1" in df.columns:

            reg_no = (
                pd.to_numeric(
                    df["p3j1"],
                    errors="coerce",
                )
                .eq(2)
            )

        else:

            warnings.warn(
                "México sin variable p3j/p3j1"
            )

            reg_no = pd.Series(
                False,
                index=df.index,
            )

        # ---------------------------------------------------------------------
        # PEQUEÑA UNIDAD
        # ---------------------------------------------------------------------

        if "tue_ppal" in df.columns:

            small = (
                pd.to_numeric(
                    df["tue_ppal"],
                    errors="coerce",
                )
                .eq(1)
            )

        else:

            small = (
                pd.to_numeric(
                    df.get("p3k1", 99),
                    errors="coerce",
                )
                .isin([1, 2, 3])
            )


    # -------------------------------------------------------------------------
    # COLOMBIA
    # -------------------------------------------------------------------------

    elif country == "colombia":

        keys = [
            "DIRECTORIO",
            "SECUENCIA_P",
            "ORDEN",
        ]
        
        df["id"] = (
           df[keys]
           .astype(str)
           .agg("_".join, axis=1)
         )
        
        
        # ---------------------------------------------------------------------
        # PONDERADOR
        # ---------------------------------------------------------------------
        tmp = df.copy()

        candidate_weights = [
             "FEX_C18",
             "FEX_DPTO_C",
             "FEX_C",
              "FEX",
        ]

        available = [
             c
             for c in candidate_weights
             if c in tmp.columns
        ]

        if not available:
             raise ValueError(
                 f"No se encontró ponderador Colombia: {tmp.columns.tolist()}"
         )

        fex_col = available[0]

        print("[COLOMBIA] usando ponderador:", fex_col)

        tmp["ponderador"] = (
             tmp[fex_col]
             .astype(str)
             .str.replace(",", ".", regex=False)
        )

        tmp["ponderador"] = pd.to_numeric(
        tmp["ponderador"],
        errors="coerce",
        )

        print(
             "[COLOMBIA] ponderador NA:",
             tmp["ponderador"].isna().mean()
       )

        print(
            tmp["ponderador"].describe()
        )

        # ---------------------------------------------------------------------
        # CONDICION ACTIVIDAD
        #
        # OCI:
        # 1 ocupado
        # 2 desocupado
        # 3 inactivo
        # ---------------------------------------------------------------------

        estado = df.get(
             "OCI",
             pd.Series(pd.NA, index=df.index)
            )

        estado = pd.to_numeric(estado, errors="coerce")

        # ---------------------------------------------------------------------
        # POSICION OCUPACIONAL
        #
        # P6430:
        # 1 obrero/empleado particular
        # 4 cuenta propia
        # ---------------------------------------------------------------------

        cat = df.get(
              "P6430",
             pd.Series(pd.NA, index=df.index)
        )

        cat = pd.to_numeric(cat, errors="coerce")

        # ---------------------------------------------------------------------
        # INFORMALIDAD
        #
        # P6450:
        # 1 cotiza
        # 2 no cotiza
        # ---------------------------------------------------------------------

        no_ss = (
            pd.to_numeric(
                df.get("P6450"),
                errors="coerce",
            )
            .eq(2)
        )

        # ---------------------------------------------------------------------
        # SIN CONTRATO
        #
        # P6440:
        # 1 escrito
        # 2 verbal
        # ---------------------------------------------------------------------

        reg_no = (
            pd.to_numeric(
                df.get("P6440"),
                errors="coerce",
            )
            .ne(1)
        )

        # ---------------------------------------------------------------------
        # PEQUEÑA EMPRESA
        #
        # P6870:
        # tamaño empresa
        # ---------------------------------------------------------------------

        p6870 = df.get(
             "P6870",
             pd.Series(
                 99,
                 index=df.index,
            ),
        )

        small = (
            pd.to_numeric(
             p6870,
             errors="coerce",
            )
             .isin([1, 2, 3, 4])
        )    
    
    # =========================================================================
    # IDS
    # =========================================================================
        out["id"] = tmp["id"]
        out["ponderador"] = tmp["ponderador"]
        df = tmp
        
    # =========================================================================
    # CONDICION ACTIVIDAD
    # =========================================================================

    if country == "mexico":

        out["ocupado"] = (
            estado.eq(1)
        ).astype(int)

        out["desocupado"] = (
            estado.eq(2)
        ).astype(int)

        out["inactivo"] = (
            ~(out["ocupado"].astype(bool) | out["desocupado"].astype(bool))
        ).astype(int)

    elif country == "brasil":

        estado = pd.to_numeric(
            estado,
            errors="coerce",
        )

        out["ocupado"] = (
            estado.eq(1)
        ).astype(int)

        out["desocupado"] = (
            estado.eq(2)
        ).astype(int)

        out["inactivo"] = (
            estado.isna()
        ).astype(int)

    else:

        estado = pd.to_numeric(
            estado,
            errors="coerce",
        )

        valido = estado.notna()

        out["ocupado"] = (
            estado.eq(1)
        ).astype(int)

        out["desocupado"] = (
            estado.eq(2)
        ).astype(int)

        out["inactivo"] = (
            valido
            &
            ~out["ocupado"].astype(bool)
            &
            ~out["desocupado"].astype(bool)
        ).astype(int)

    # =========================================================================
    # CATEGORIA OCUPACIONAL
    # =========================================================================

    out["asalariado"] = (

        (
            cat.isin([3])
        )

        if country == "argentina"

        else (

            cat.isin([
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            ])

            if country == "brasil"

            else (

                (
                    cat == 1
                )

                if country == "mexico"

                else cat.isin(
                    [1, 2, 3, 8]
                )

            )
        )

    ).astype(int)

    out["cuentapropia"] = (

        cat.eq(2)

        if country == "argentina"

        else (

            cat.eq(9)

            if country == "brasil"

            else (

                (
                    cat == 3
                )

                if country == "mexico"

                else (
                    cat == 4
                )

            )
        )

    ).astype(int)

    # =========================================================================
    # INFORMALIDAD
    # =========================================================================

    if country == "mexico":

        # ---------------------------------------------------------------------
        # EMP_PPAL:
        # 1 informal
        # 2 formal
        # ---------------------------------------------------------------------

        if "EMP_PPAL" in df.columns:

            out["informal"] = (
                pd.to_numeric(
                    df["EMP_PPAL"],
                    errors="coerce",
                )
                .eq(1)
            ).astype(int)

            out["formal"] = (
                pd.to_numeric(
                    df["EMP_PPAL"],
                    errors="coerce",
                )
                .eq(2)
            ).astype(int)

        else:

            # fallback
            if "SEG_SOC" in df.columns:

                no_ss = (
                    pd.to_numeric(
                        df["SEG_SOC"],
                        errors="coerce",
                    )
                    .eq(2)
                )

            else:

                no_ss = (
                    pd.to_numeric(
                        df.get("p3m4", 0),
                        errors="coerce",
                    ) != 4
                )

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
                    (
                        small | no_ss
                    )
                )
            ).astype(int)

            out["formal"] = (
                1 - out["informal"]
            )

    elif country == "brasil":

        sem_carteira = cat.isin([2, 4, 6])

        no_ss = (
            pd.to_numeric(
                df.get("VD4012"),
                errors="coerce",
            )
            .eq(2)
        )

        out["informal"] = (
            (
                out["asalariado"].eq(1)
                &
                sem_carteira
            )
            |
            (
                out["cuentapropia"].eq(1)
                &
                no_ss
            )
        ).astype(int)

        out["formal"] = (
            1 - out["informal"]
        )

    else:

        no_ss = (
            (
                df.get("P6920", 0) == 2
            )
            if country == "colombia"
            else reg_no
        )

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
                (
                    small | no_ss
                )
            )
        ).astype(int)

        out["formal"] = (
            1 - out["informal"]
        )

    # =========================================================================
    # SECTOR
    # =========================================================================

    out["sector"] = "Priv"

    return out[COMMON_COLUMNS]


# =============================================================================
# RUNNER
# =============================================================================

def run_country_year(
    country: str,
    year: int,
):

    log(
        f"INICIANDO {country.upper()} {year}"
    )

    periods = get_periods(
        country,
        year,
    )

    if not periods:

        raise FileNotFoundError(
            f"Sin períodos para {country} {year}"
        )

    dfs = []

    for t, p in periods.items():

        log(
            f"Procesando trimestre {t}"
        )

        raw = load_period(
            country,
            p,
            year,
        )

        raw = apply_geography_filter(country, year, raw)

        if raw.empty:
            warnings.warn(
                f"{country.title()} {year} T{t}: datos vacíos luego de aplicar filtro de geografía urbana"
            )
            continue

        # -------------------------------------------------------------
        # BRASIL
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

            summarize_duplicate_ids(
                raw_t,
                id_col=["UF", "UPA", "V1008", "V1014", "V2003"],
                weight_col="V1028",
                label=f"Brasil {year} T{t}",
            )

            core = build_core(
                country,
                year,
                t,
                raw_t,
            )

        else:

            core = build_core(
                country,
                year,
                t,
                raw,
            )

        # -------------------------------------------------------------
        # DOWNCAST
        # -------------------------------------------------------------

        int_cols = (
            core.select_dtypes(
                include=["int64"]
            ).columns
        )

        float_cols = (
            core.select_dtypes(
                include=["float64"]
            ).columns
        )

        core[int_cols] = (
            core[int_cols]
            .apply(
                pd.to_numeric,
                downcast="integer",
            )
        )

        core[float_cols] = (
            core[float_cols]
            .apply(
                pd.to_numeric,
                downcast="float",
            )
        )

        log(
            f"Core T{t}: "
            f"{core.memory_usage(deep=True).sum() / 1024**2:.2f} MB"
        )

        # -------------------------------------------------------------
        # TMP
        # -------------------------------------------------------------

        tmp_dir = Path(
            "outputs/harmonized/tmp"
        )

        tmp_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        tmp_file = (
            tmp_dir
            / f"{country}_{year}_T{t}.parquet"
        )

        core.to_parquet(
            tmp_file,
            index=False,
        )

        log(
            f"Temporal guardado: {tmp_file}"
        )

        dfs.append(core)

    # -------------------------------------------------------------
    # VALIDACION
    # -------------------------------------------------------------

    if not dfs:

        raise ValueError(
            f"No se generaron datos para {country} {year}"
        )

    # -------------------------------------------------------------
    # CONCAT
    # -------------------------------------------------------------

    log(
        "Concatenando trimestres..."
    )

    df = pd.concat(
        dfs,
        ignore_index=True,
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

    assert (
        df["ponderador"] > 0
    ).all()

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
            "inconsistencia en condición de actividad"
        )

    # -------------------------------------------------------------
    # OUTPUT
    # -------------------------------------------------------------

    out = Path(
        "outputs/harmonized"
    )

    out.mkdir(
        parents=True,
        exist_ok=True,
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
        index=False,
    )

    log(
        f"Guardado final: {parquet_path}"
    )

    return df
