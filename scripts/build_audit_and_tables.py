from pathlib import Path

import pandas as pd


COUNTRIES = [
    "argentina",
    "brasil",
    "mexico",
    "colombia",
]

YEARS = [
    2018,
    2023,
]

BINARY_VARS = [
    "ocupado",
    "desocupado",
    "inactivo",
    "asalariado",
    "asalariado_publico",
    "asalariado_privado",
    "cuentapropia",
    "patron",
    "trab_familiar",
    "empleo_domestico",
    "formal",
    "informal",
    "small",
    "patron_micro",
    "asalariado_privado_micro",
    "educacion_superior",
]

INDICATORS = {
    "poblacion": None,
    "pea": ["ocupado", "desocupado"],
    "ocupados": ["ocupado"],
    "desocupados": ["desocupado"],
    "inactivos": ["inactivo"],
    "asalariados": ["asalariado"],
    "asalariados_publicos": ["asalariado_publico"],
    "asalariados_privados": ["asalariado_privado"],
    "cuenta_propia": ["cuentapropia"],
    "patrones": ["patron"],
    "trabajo_familiar": ["trab_familiar"],
    "empleo_domestico": ["empleo_domestico"],
    "informales": ["informal"],
    "formales": ["formal"],
    "patrones_micro": ["patron_micro"],
    "asalariados_privados_micro": ["asalariado_privado_micro"],
}

DISTRIBUTIONS = [
    "sexo",
    "edad",
    "nivel_educativo",
    "educacion_superior",
]


def weighted_sum(df: pd.DataFrame, columns: list[str] | None) -> float:

    if columns is None:
        return float(df["ponderador"].sum())

    if not set(columns).issubset(df.columns):
        return pd.NA

    mask = df[columns].sum(axis=1).gt(0)

    return float(df.loc[mask, "ponderador"].sum())


def audit_file(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:

    df = pd.read_parquet(path)
    country, year = path.stem.rsplit("_", 1)
    activity_cols = ["ocupado", "desocupado", "inactivo"]
    has_activity = set(activity_cols).issubset(df.columns)
    identity = df[activity_cols].sum(axis=1) if has_activity else pd.Series(pd.NA, index=df.index)
    has_weight = "ponderador" in df.columns
    has_id = {"anio", "trimestre", "id"}.issubset(df.columns)

    summary = {
        "archivo": str(path),
        "pais": country,
        "anio": int(year),
        "registros": int(len(df)),
        "columnas": int(df.shape[1]),
        "id_unicos_trimestre": (
            int(df[["anio", "trimestre", "id"]].drop_duplicates().shape[0])
            if has_id
            else pd.NA
        ),
        "id_duplicados_trimestre": (
            int(df.duplicated(["anio", "trimestre", "id"], keep=False).sum())
            if has_id
            else pd.NA
        ),
        "ponderador_suma": float(df["ponderador"].sum()) if has_weight else pd.NA,
        "ponderador_media": float(df["ponderador"].mean()) if has_weight else pd.NA,
        "ponderador_min": float(df["ponderador"].min()) if has_weight else pd.NA,
        "ponderador_max": float(df["ponderador"].max()) if has_weight else pd.NA,
        "ponderador_missing": int(df["ponderador"].isna().sum()) if has_weight else pd.NA,
        "ponderador_no_positivo": int(df["ponderador"].le(0).sum()) if has_weight else pd.NA,
        "ocupados": int(df["ocupado"].sum()) if "ocupado" in df else pd.NA,
        "desocupados": int(df["desocupado"].sum()) if "desocupado" in df else pd.NA,
        "inactivos": int(df["inactivo"].sum()) if "inactivo" in df else pd.NA,
        "identidad_actividad_ok": bool(identity.eq(1).all()) if has_activity else pd.NA,
        "identidad_actividad_fallas": int(identity.ne(1).sum()) if has_activity else pd.NA,
    }

    rows = []
    for column in df.columns:
        series = df[column]
        non_null = int(series.notna().sum())
        unique = int(series.nunique(dropna=True))
        numeric = pd.to_numeric(series, errors="coerce")
        numeric_non_null = numeric.notna().sum()
        is_numeric = numeric_non_null > 0 and numeric_non_null >= non_null * 0.95
        is_binary_var = column in BINARY_VARS
        anomalous_binary = (
            bool(~series.dropna().isin([0, 1]).all())
            if is_binary_var
            else False
        )
        rows.append(
            {
                "archivo": path.name,
                "pais": country,
                "anio": int(year),
                "variable": column,
                "tipo": str(series.dtype),
                "no_missing": non_null,
                "missing": int(series.isna().sum()),
                "missing_pct": float(series.isna().mean()),
                "n_unicos": unique,
                "vacia": non_null == 0,
                "constante": unique <= 1,
                "media": float(numeric.mean()) if is_numeric else pd.NA,
                "min": float(numeric.min()) if is_numeric else pd.NA,
                "max": float(numeric.max()) if is_numeric else pd.NA,
                "binaria_anomala": anomalous_binary,
                "categorias": (
                    "|".join(map(str, sorted(series.dropna().unique().tolist(), key=str)[:30]))
                    if unique <= 30
                    else "MAS_DE_30"
                ),
            }
        )

    return pd.DataFrame([summary]), pd.DataFrame(rows)


def audit_distributions(df: pd.DataFrame) -> pd.DataFrame:

    rows = []

    for keys, group in df.groupby(["pais", "anio", "trimestre"], dropna=False):
        pais, anio, trimestre = keys

        for variable in BINARY_VARS:
            if variable not in group.columns:
                rows.append(
                    {
                        "pais": pais,
                        "anio": anio,
                        "trimestre": trimestre,
                        "variable": variable,
                        "categoria": "MISSING_COLUMN",
                        "casos": 0,
                        "ponderado": 0.0,
                        "pct": pd.NA,
                    }
                )
                continue

            for category, subset in group.groupby(variable, dropna=False):
                rows.append(
                    {
                        "pais": pais,
                        "anio": anio,
                        "trimestre": trimestre,
                        "variable": variable,
                        "categoria": category,
                        "casos": int(len(subset)),
                        "ponderado": float(subset["ponderador"].sum()),
                        "pct": float(subset["ponderador"].sum() / group["ponderador"].sum()),
                    }
                )

        for variable in DISTRIBUTIONS:
            if variable not in group.columns:
                continue

            tmp = group.copy()
            tmp[variable] = tmp[variable].astype("string").fillna("Sin dato")

            for category, subset in tmp.groupby(variable, dropna=False):
                rows.append(
                    {
                        "pais": pais,
                        "anio": anio,
                        "trimestre": trimestre,
                        "variable": variable,
                        "categoria": category,
                        "casos": int(len(subset)),
                        "ponderado": float(subset["ponderador"].sum()),
                        "pct": float(subset["ponderador"].sum() / group["ponderador"].sum()),
                    }
                )

    return pd.DataFrame(rows)


def quarterly_indicators(df: pd.DataFrame) -> pd.DataFrame:

    rows = []
    group_cols = ["pais", "anio", "trimestre"]

    for keys, group in df.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, keys))

        for indicator, columns in INDICATORS.items():
            available = columns is None or set(columns).issubset(group.columns)
            rows.append(
                {
                    **base,
                    "indicador": indicator,
                    "valor_ponderado": weighted_sum(group, columns),
                    "casos_sin_ponderar": (
                        int(len(group))
                        if columns is None
                        else (
                            int(group[columns].sum(axis=1).gt(0).sum())
                            if available
                            else pd.NA
                        )
                    ),
                    "estado_dato": "ok" if available else "variable_ausente",
                    "observacion": (
                        pd.NA
                        if available
                        else "La variable no posee informacion para ese trimestre."
                    ),
                }
            )

    return pd.DataFrame(rows)


def quarterly_distributions(df: pd.DataFrame) -> pd.DataFrame:

    rows = []
    group_cols = ["pais", "anio", "trimestre"]

    for keys, group in df.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, keys))

        for variable in DISTRIBUTIONS:
            if variable not in group.columns:
                rows.append(
                    {
                        **base,
                        "dimension": variable,
                        "categoria": pd.NA,
                        "valor_ponderado": pd.NA,
                        "casos_sin_ponderar": pd.NA,
                        "pct": pd.NA,
                        "estado_dato": "variable_ausente",
                        "observacion": "La variable no posee informacion para ese trimestre.",
                    }
                )
                continue

            tmp = group.copy()
            tmp[variable] = tmp[variable].astype("string").fillna("Sin dato")
            total = tmp["ponderador"].sum()

            for category, subset in tmp.groupby(variable, dropna=False):
                value = float(subset["ponderador"].sum())
                rows.append(
                    {
                        **base,
                        "dimension": variable,
                        "categoria": category,
                        "valor_ponderado": value,
                        "casos_sin_ponderar": int(len(subset)),
                        "pct": value / total if total else pd.NA,
                        "estado_dato": "ok",
                        "observacion": pd.NA,
                    }
                )

    return pd.DataFrame(rows)


def annual_from_quarters(quarterly: pd.DataFrame, keys: list[str]) -> pd.DataFrame:

    value_cols = [
        "valor_ponderado",
        "casos_sin_ponderar",
    ]

    if "pct" in quarterly.columns:
        value_cols.append("pct")

    metadata_cols = [
        column
        for column in ["estado_dato", "observacion"]
        if column in quarterly.columns
    ]

    base_period_counts = (
        quarterly
        .groupby(["pais", "anio"], dropna=False)["trimestre"]
        .nunique()
        .reset_index(name="periodos_promediados")
    )

    incomplete = base_period_counts[
        base_period_counts["periodos_promediados"].ne(4)
    ]

    if not incomplete.empty:
        raise ValueError(
            "No se pueden calcular cuadros anuales con trimestres incompletos: "
            f"{incomplete.to_dict(orient='records')}"
        )

    group_cols = ["pais", "anio", *keys]
    complete_periods = quarterly[
        ["pais", "anio", "trimestre"]
    ].drop_duplicates()
    complete_groups = quarterly[group_cols].drop_duplicates()

    complete_quarterly = (
        complete_groups
        .merge(
            complete_periods,
            on=["pais", "anio"],
            how="left",
            validate="many_to_many",
        )
        .merge(
            quarterly,
            on=[*group_cols, "trimestre"],
            how="left",
            validate="one_to_one",
        )
    )

    missing_row = complete_quarterly["valor_ponderado"].isna()
    missing_variable = (
        complete_quarterly["estado_dato"].eq("variable_ausente")
        if "estado_dato" in complete_quarterly.columns
        else pd.Series(False, index=complete_quarterly.index)
    )
    absent_category = missing_row & ~missing_variable

    complete_quarterly.loc[absent_category, value_cols] = (
        complete_quarterly.loc[absent_category, value_cols].fillna(0)
    )
    if "estado_dato" in complete_quarterly.columns:
        complete_quarterly.loc[absent_category, "estado_dato"] = "categoria_ausente"
    if "observacion" in complete_quarterly.columns:
        complete_quarterly.loc[absent_category, "observacion"] = (
            "Categoria con frecuencia cero en el trimestre."
        )

    annual = (
        complete_quarterly
        .groupby(group_cols, dropna=False)[value_cols]
        .mean()
        .reset_index()
    )

    period_counts = (
        complete_quarterly
        .groupby(group_cols, dropna=False)["trimestre"]
        .nunique()
        .reset_index(name="periodos_promediados")
    )

    annual = annual.merge(
        period_counts,
        on=group_cols,
        how="left",
        validate="one_to_one",
    )

    if metadata_cols:
        annual_status = (
            complete_quarterly
            .groupby(group_cols, dropna=False)
            .agg(
                trimestres_con_dato=("valor_ponderado", lambda s: int(s.notna().sum())),
                trimestres_variable_ausente=(
                    "estado_dato",
                    lambda s: int(s.eq("variable_ausente").sum()),
                ),
                observacion=(
                    "observacion",
                    lambda s: " | ".join(
                        sorted({str(value) for value in s.dropna() if str(value)})
                    )
                    or pd.NA,
                ),
            )
            .reset_index()
        )
        annual = annual.merge(
            annual_status,
            on=group_cols,
            how="left",
            validate="one_to_one",
        )

    return annual


def annual_variation(annual: pd.DataFrame, keys: list[str]) -> pd.DataFrame:

    wide = annual.pivot_table(
        index=["pais", *keys],
        columns="anio",
        values="valor_ponderado",
        aggfunc="first",
    ).reset_index()

    for year in YEARS:
        if year not in wide.columns:
            wide[year] = pd.NA

    wide["variacion_absoluta"] = wide[2023] - wide[2018]
    wide["variacion_relativa"] = wide["variacion_absoluta"] / wide[2018]

    return wide


def subset_dimension(table: pd.DataFrame, dimension: str) -> pd.DataFrame:

    if "dimension" not in table.columns:
        return table.iloc[0:0].copy()

    return table[table["dimension"].eq(dimension)].copy()


def write_documentation(
    out_dir: Path,
    audit_summary: pd.DataFrame,
    audit_variables: pd.DataFrame,
) -> None:

    limitations = []

    if "identidad_actividad_fallas" in audit_summary:
        failures = int(audit_summary["identidad_actividad_fallas"].fillna(0).sum())
        limitations.append(
            f"- Identidad ocupado + desocupado + inactivo: {failures} fallas."
        )

    limitations.append(
        "- Colombia 2018: los parquets limpios no contienen CLASE; el filtro urbano no se aplica y se conserva el conjunto disponible."
    )
    limitations.append(
        "- Colombia 2023: sexo, edad y educacion se enriquecen desde el modulo Caracteristicas generales; P3069 se usa como reemplazo de P6870 para tamano de establecimiento cuando P6870 no esta disponible."
    )
    limitations.append(
        "- Los promedios anuales se calculan como promedio simple de los cuatro trimestres. Categorias ausentes en un trimestre se imputan como cero antes de promediar."
    )

    demographic_missing = audit_variables[
        audit_variables["variable"].isin(DISTRIBUTIONS)
        & audit_variables["missing"].gt(0)
    ]

    for _, row in demographic_missing.iterrows():
        limitations.append(
            "- Faltantes demograficos: "
            f"{row['pais']} {int(row['anio'])} {row['variable']} "
            f"{int(row['missing'])} casos ({row['missing_pct']:.4%})."
        )

    text = "\n".join(
        [
            "# Documentacion breve - ETAPA 2",
            "",
            "Equivalencias y criterios metodologicos:",
            *limitations,
            "",
        ]
    )

    (out_dir / "documentacion_metodologica_breve.md").write_text(
        text,
        encoding="utf-8",
    )


def write_outputs(
    audit_summary: pd.DataFrame,
    audit_variables: pd.DataFrame,
    audit_categories: pd.DataFrame,
    q_indicators: pd.DataFrame,
    q_distributions: pd.DataFrame,
    annual_indicators: pd.DataFrame,
    annual_distributions: pd.DataFrame,
    annual_indicator_variation: pd.DataFrame,
    annual_distribution_variation: pd.DataFrame,
    out_dir: Path,
) -> None:

    out_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "auditoria_nacional_resumen.csv": audit_summary,
        "auditoria_nacional_variables.csv": audit_variables,
        "auditoria_comparada_distribuciones.csv": audit_categories,
        "cuadros_trimestrales_indicadores.csv": q_indicators,
        "cuadros_trimestrales_distribuciones.csv": q_distributions,
        "cuadros_anuales_indicadores.csv": annual_indicators,
        "cuadros_anuales_distribuciones.csv": annual_distributions,
        "cuadros_anuales_indicadores_variacion.csv": annual_indicator_variation,
        "cuadros_anuales_distribuciones_variacion.csv": annual_distribution_variation,
    }

    for dimension in DISTRIBUTIONS:
        outputs[f"cuadros_trimestrales_{dimension}.csv"] = subset_dimension(
            q_distributions,
            dimension,
        )
        outputs[f"cuadros_anuales_{dimension}.csv"] = subset_dimension(
            annual_distributions,
            dimension,
        )
        outputs[f"cuadros_anuales_{dimension}_variacion.csv"] = subset_dimension(
            annual_distribution_variation,
            dimension,
        )

    for name, table in outputs.items():
        table.to_csv(out_dir / name, index=False, encoding="utf-8-sig")

    write_documentation(out_dir, audit_summary, audit_variables)

    with pd.ExcelWriter(out_dir / "auditoria_y_cuadros.xlsx", engine="openpyxl") as writer:
        for name, table in outputs.items():
            sheet = name.replace(".csv", "")[:31]
            table.to_excel(writer, sheet_name=sheet, index=False)


def main() -> None:

    harmonized_dir = Path("outputs/harmonized")
    out_dir = Path("outputs/diagnostics")

    national_paths = [
        harmonized_dir / f"{country}_{year}.parquet"
        for country in COUNTRIES
        for year in YEARS
    ]

    missing = [
        path
        for path in national_paths
        if not path.exists()
    ]

    if missing:
        raise FileNotFoundError(f"Faltan parquets nacionales: {missing}")

    audit_summaries = []
    audit_variables = []
    frames = []

    for path in national_paths:
        summary, variables = audit_file(path)
        audit_summaries.append(summary)
        audit_variables.append(variables)
        frames.append(pd.read_parquet(path))

    df = pd.concat(frames, ignore_index=True)

    audit_summary = pd.concat(audit_summaries, ignore_index=True)
    audit_vars = pd.concat(audit_variables, ignore_index=True)
    audit_categories = audit_distributions(df)

    q_indicators = quarterly_indicators(df)
    q_distributions = quarterly_distributions(df)

    annual_indicators = annual_from_quarters(
        q_indicators,
        ["indicador"],
    )
    annual_distributions = annual_from_quarters(
        q_distributions,
        ["dimension", "categoria"],
    )

    annual_indicator_variation = annual_variation(
        annual_indicators,
        ["indicador"],
    )
    annual_distribution_variation = annual_variation(
        annual_distributions,
        ["dimension", "categoria"],
    )

    write_outputs(
        audit_summary,
        audit_vars,
        audit_categories,
        q_indicators,
        q_distributions,
        annual_indicators,
        annual_distributions,
        annual_indicator_variation,
        annual_distribution_variation,
        out_dir,
    )

    print(f"Auditorias y cuadros generados en {out_dir}")


if __name__ == "__main__":
    main()
