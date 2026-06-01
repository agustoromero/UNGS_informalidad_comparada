"""Auditoría de duplicados de persona en PNAD Contínua Brasil.

La auditoría responde dos preguntas antes de tomar decisiones de limpieza:
1. si los duplicados de ``UPA + V1008 + V1014 + V2003`` ya están en el bruto;
2. si aparecen recién después de la construcción core del pipeline.

No modifica microdatos ni outputs del pipeline. Por defecto imprime tablas en consola.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import pandas as pd

from scripts.common_pipeline import build_core, get_periods, load_period

ID_COLUMNS = ["UPA", "V1008", "V1014", "V2003"]
SEX_COLUMN = "V2007"
AGE_COLUMN = "V2009"
BIRTH_COLUMNS = ["V2008", "V20081", "V20082"]
URBAN_COLUMN = "V1022"


def make_person_id(df: pd.DataFrame) -> pd.Series:
    """Construye id_persona oficial usado para auditar duplicados PNADC."""
    if "id_persona" in df.columns:
        return df["id_persona"].astype(str)
    missing = [col for col in ID_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas para id_persona: {missing}")
    return df[ID_COLUMNS].astype(str).agg("_".join, axis=1)


def available_columns(df: pd.DataFrame, candidates: Iterable[str]) -> list[str]:
    return [col for col in candidates if col in df.columns]


def count_unique_tuples(frame: pd.DataFrame, columns: list[str]) -> int:
    if not columns:
        return 0
    return frame[columns].drop_duplicates().shape[0]


def classify_duplicate_group(group: pd.DataFrame, birth_columns: list[str]) -> pd.Series:
    """Clasifica un grupo de id_persona repetido en Tipo A/B/C."""
    n_sexos = group[SEX_COLUMN].nunique(dropna=False) if SEX_COLUMN in group.columns else 0
    n_edades = group[AGE_COLUMN].nunique(dropna=False) if AGE_COLUMN in group.columns else 0
    n_fechas_nacimiento = count_unique_tuples(group, birth_columns)
    all_rows_equal = group.drop(columns=["id_persona"], errors="ignore").drop_duplicates().shape[0] == 1

    if n_sexos > 1 or n_edades > 1 or n_fechas_nacimiento > 1:
        duplicate_type = "C_conflicto_identidad"
    elif all_rows_equal:
        duplicate_type = "A_duplicado_perfecto"
    else:
        duplicate_type = "B_misma_persona_difiere_laboral"

    hogares_cols = [col for col in ["UPA", "V1008", "V1014"] if col in group.columns]

    return pd.Series(
        {
            "n_filas": len(group),
            "n_hogares": count_unique_tuples(group, hogares_cols),
            "n_edades": n_edades,
            "n_sexos": n_sexos,
            "n_fechas_nacimiento": n_fechas_nacimiento,
            "tipo_duplicado": duplicate_type,
        }
    )


def duplicate_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Devuelve una fila por id_persona repetido con métricas de identidad."""
    df = df.copy()
    df["id_persona"] = make_person_id(df)
    duplicated = df[df["id_persona"].duplicated(keep=False)].copy()
    if duplicated.empty:
        return pd.DataFrame(
            columns=[
                "id_persona",
                "n_filas",
                "n_hogares",
                "n_edades",
                "n_sexos",
                "n_fechas_nacimiento",
                "tipo_duplicado",
            ]
        )

    birth_columns = available_columns(duplicated, BIRTH_COLUMNS)
    rows = []
    for id_persona, group in duplicated.groupby("id_persona", dropna=False):
        row = classify_duplicate_group(group, birth_columns=birth_columns)
        row["id_persona"] = id_persona
        rows.append(row)
    return pd.DataFrame(rows)[
        [
            "id_persona",
            "n_filas",
            "n_hogares",
            "n_edades",
            "n_sexos",
            "n_fechas_nacimiento",
            "tipo_duplicado",
        ]
    ]


def summarize_duplicates(groups: pd.DataFrame, total_rows: int) -> pd.DataFrame:
    """Calcula magnitud de duplicados por tipo y porcentaje del universo."""
    if groups.empty:
        return pd.DataFrame(
            [
                {
                    "tipo_duplicado": "total",
                    "ids_duplicados": 0,
                    "filas_en_ids_duplicados": 0,
                    "filas_excedentes": 0,
                    "pct_filas_universo": 0.0,
                }
            ]
        )

    by_type = (
        groups.groupby("tipo_duplicado", dropna=False)
        .agg(
            ids_duplicados=("id_persona", "nunique"),
            filas_en_ids_duplicados=("n_filas", "sum"),
            filas_excedentes=("n_filas", lambda values: int((values - 1).sum())),
        )
        .reset_index()
    )
    by_type["pct_filas_universo"] = by_type["filas_en_ids_duplicados"] / total_rows * 100

    total = pd.DataFrame(
        [
            {
                "tipo_duplicado": "total",
                "ids_duplicados": groups["id_persona"].nunique(),
                "filas_en_ids_duplicados": groups["n_filas"].sum(),
                "filas_excedentes": int((groups["n_filas"] - 1).sum()),
                "pct_filas_universo": groups["n_filas"].sum() / total_rows * 100,
            }
        ]
    )
    return pd.concat([total, by_type], ignore_index=True)


def audit_by_period(df: pd.DataFrame) -> pd.DataFrame:
    """Cruza año/trimestre contra cantidad de duplicados."""
    period_cols = [col for col in ["Ano", "Trimestre", "_pipeline_trimestre"] if col in df.columns]
    if not period_cols:
        raise ValueError("No hay columnas de período para cruzar duplicados")

    rows = []
    for period_values, period_df in df.groupby(period_cols, dropna=False):
        period_values = period_values if isinstance(period_values, tuple) else (period_values,)
        groups = duplicate_groups(period_df)
        summary = summarize_duplicates(groups, len(period_df))
        for _, row in summary.iterrows():
            rows.append(dict(zip(period_cols, period_values)) | row.to_dict())
    return pd.DataFrame(rows)


def load_raw_year(year: int, urban_only: bool) -> pd.DataFrame:
    periods = get_periods("brasil", year)
    frames = []
    for trimestre in sorted(periods):
        path = periods[trimestre]
        df = load_period("brasil", path).copy()
        df["_pipeline_trimestre"] = trimestre
        df["_source_path"] = str(path)
        if urban_only:
            if URBAN_COLUMN not in df.columns:
                raise ValueError(f"No se puede filtrar urbano: falta {URBAN_COLUMN}")
            df = df[df[URBAN_COLUMN] == 1].copy()
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def build_core_year(raw_df: pd.DataFrame, year: int) -> pd.DataFrame:
    frames = []
    for trimestre, period_df in raw_df.groupby("_pipeline_trimestre", dropna=False):
        frames.append(build_core("brasil", year, int(trimestre), period_df.copy()))
    return pd.concat(frames, ignore_index=True)


def print_table(title: str, df: pd.DataFrame) -> None:
    print(f"\n===== {title} =====")
    if df.empty:
        print("(sin filas)")
    else:
        print(df.to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description="Audita duplicados PNADC Brasil en bruto y pipeline core")
    parser.add_argument("--year", type=int, required=True, choices=[2018, 2023])
    parser.add_argument("--urban-only", action="store_true", help="Aplica V1022 == 1 antes de auditar")
    parser.add_argument("--top", type=int, default=20, help="Cantidad de grupos duplicados a mostrar")
    args = parser.parse_args()

    raw = load_raw_year(args.year, args.urban_only)
    raw_groups = duplicate_groups(raw)
    raw_summary = summarize_duplicates(raw_groups, len(raw))
    raw_by_period = audit_by_period(raw)

    core = build_core_year(raw, args.year)
    core_groups = duplicate_groups(core.rename(columns={"id": "id_persona"}))
    core_summary = summarize_duplicates(core_groups, len(core))

    print_table("Resumen duplicados bruto", raw_summary)
    print_table("Duplicados bruto por período", raw_by_period)
    print_table("Top grupos duplicados bruto", raw_groups.sort_values("n_filas", ascending=False).head(args.top))
    print_table("Resumen duplicados luego de build_core", core_summary)

    print("\n===== Control bruto vs pipeline =====")
    print(f"filas_bruto={len(raw)}")
    print(f"filas_core={len(core)}")
    print(f"mismas_filas={len(raw) == len(core)}")
    print(f"duplicados_bruto_filas={int(raw_summary.loc[raw_summary['tipo_duplicado'].eq('total'), 'filas_en_ids_duplicados'].iloc[0])}")
    print(f"duplicados_core_filas={int(core_summary.loc[core_summary['tipo_duplicado'].eq('total'), 'filas_en_ids_duplicados'].iloc[0])}")


if __name__ == "__main__":
    main()
