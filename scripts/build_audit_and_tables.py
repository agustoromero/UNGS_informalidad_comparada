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

    mask = df[columns].sum(axis=1).gt(0)

    return float(df.loc[mask, "ponderador"].sum())


def audit_file(path: Path) -> tuple[pd.DataFrame, pd.DataFrame]:

    df = pd.read_parquet(path)
    country, year = path.stem.rsplit("_", 1)

    summary = {
        "archivo": str(path),
        "pais": country,
        "anio": int(year),
        "registros": int(len(df)),
        "columnas": int(df.shape[1]),
        "ponderador_suma": float(df["ponderador"].sum()) if "ponderador" in df else pd.NA,
        "ponderador_missing": int(df["ponderador"].isna().sum()) if "ponderador" in df else pd.NA,
        "id_duplicados_trimestre": (
            int(df.duplicated(["anio", "trimestre", "id"], keep=False).sum())
            if {"anio", "trimestre", "id"}.issubset(df.columns)
            else pd.NA
        ),
    }

    rows = []
    for column in df.columns:
        series = df[column]
        non_null = int(series.notna().sum())
        unique = int(series.nunique(dropna=True))
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

        for variable in ["sexo", "nivel_educativo"]:
            if variable not in group.columns:
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

    return pd.DataFrame(rows)


def quarterly_indicators(df: pd.DataFrame) -> pd.DataFrame:

    rows = []
    group_cols = ["pais", "anio", "trimestre"]

    for keys, group in df.groupby(group_cols, dropna=False):
        base = dict(zip(group_cols, keys))

        for indicator, columns in INDICATORS.items():
            rows.append(
                {
                    **base,
                    "indicador": indicator,
                    "valor_ponderado": weighted_sum(group, columns),
                    "casos_sin_ponderar": (
                        int(len(group))
                        if columns is None
                        else int(group[columns].sum(axis=1).gt(0).sum())
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

    annual = (
        quarterly
        .groupby(["pais", "anio", *keys], dropna=False)[value_cols]
        .mean()
        .reset_index()
    )

    annual["periodos_promediados"] = 4

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

    for name, table in outputs.items():
        table.to_csv(out_dir / name, index=False, encoding="utf-8-sig")

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
