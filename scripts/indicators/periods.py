from __future__ import annotations

import pandas as pd

from scripts.indicators.measures import require_columns
from scripts.indicators.schema import ColumnSpec


def quarter_columns(years: tuple[int, ...]) -> tuple[ColumnSpec, ...]:
    columns: list[ColumnSpec] = []
    for year in years:
        for quarter in (1, 2, 3, 4):
            columns.append(ColumnSpec(f"{year}_T{quarter}", year, quarter))
        columns.append(ColumnSpec(f"{year}_Anual", year, None))
    return tuple(columns)


def validate_complete_year(df: pd.DataFrame, year: int) -> None:
    require_columns(df, ["anio", "trimestre"])
    quarters = set(
        pd.to_numeric(
            df.loc[df["anio"].eq(year), "trimestre"],
            errors="coerce",
        ).dropna().astype(int)
    )
    expected = {1, 2, 3, 4}
    if quarters != expected:
        raise ValueError(
            f"Anio {year} incompleto. Esperados={sorted(expected)}; "
            f"observados={sorted(quarters)}"
        )


def period_frame(df: pd.DataFrame, column: ColumnSpec) -> pd.DataFrame:
    require_columns(df, ["anio", "trimestre"])
    if column.quarter is None:
        validate_complete_year(df, column.year)
        return df.loc[df["anio"].eq(column.year)].copy()

    return df.loc[
        df["anio"].eq(column.year) & df["trimestre"].eq(column.quarter)
    ].copy()

