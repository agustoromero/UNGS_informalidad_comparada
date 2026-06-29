from __future__ import annotations

import pandas as pd


def require_columns(df: pd.DataFrame, columns: tuple[str, ...] | list[str]) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise KeyError(f"Faltan columnas requeridas: {missing}")


def safe_divide(numerator: float | int | pd.NA, denominator: float | int | pd.NA):
    if pd.isna(numerator) or pd.isna(denominator) or denominator == 0:
        return pd.NA
    return float(numerator) / float(denominator)


def weighted_total(df: pd.DataFrame, weight_col: str = "ponderador") -> float:
    require_columns(df, [weight_col])
    return float(pd.to_numeric(df[weight_col], errors="coerce").sum())


def weighted_count(
    df: pd.DataFrame,
    mask: pd.Series,
    weight_col: str = "ponderador",
) -> float:
    require_columns(df, [weight_col])
    aligned_mask = mask.reindex(df.index).fillna(False).astype(bool)
    weights = pd.to_numeric(df.loc[aligned_mask, weight_col], errors="coerce")
    return float(weights.sum())


def weighted_share(
    df: pd.DataFrame,
    numerator_mask: pd.Series,
    denominator_mask: pd.Series,
    weight_col: str = "ponderador",
):
    numerator = weighted_count(df, numerator_mask, weight_col)
    denominator = weighted_count(df, denominator_mask, weight_col)
    return safe_divide(numerator, denominator)

