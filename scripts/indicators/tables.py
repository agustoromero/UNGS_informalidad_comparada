from __future__ import annotations

import pandas as pd

from scripts.indicators.aggregations import grouped
from scripts.indicators.measures import safe_divide
from scripts.indicators.periods import period_frame, validate_complete_year
from scripts.indicators.registry import get_indicator, indicator_count
from scripts.indicators.schema import ColumnSpec, RowSpec, TableSpec


def _row_value(df: pd.DataFrame, row: RowSpec, spec: TableSpec):
    numerator = indicator_count(df, row.indicator_id)
    if spec.value_format == "count":
        return numerator

    denominator_id = (
        row.denominator_id
        or get_indicator(row.indicator_id).denominator_id
        or spec.default_denominator_id
    )
    if denominator_id is None:
        raise ValueError(f"La fila {row.label} no define denominador.")

    denominator = indicator_count(df, denominator_id)
    return safe_divide(numerator, denominator)


def _period_value(
    df: pd.DataFrame,
    column: ColumnSpec,
    row: RowSpec,
    spec: TableSpec,
):
    if column.quarter is not None or spec.annual_method == "sum_then_ratio":
        return _row_value(period_frame(df, column), row, spec)

    validate_complete_year(df, column.year)
    values = [
        _row_value(period_frame(df, ColumnSpec("", column.year, quarter)), row, spec)
        for quarter in (1, 2, 3, 4)
    ]
    valid_values = [value for value in values if not pd.isna(value)]
    if len(valid_values) != 4:
        return pd.NA
    return float(pd.Series(valid_values, dtype="float64").mean())


def build_table(df: pd.DataFrame, spec: TableSpec) -> pd.DataFrame:
    """Build a table from a declarative spec. No export side effects."""

    rows = []
    for group_values, group_df in grouped(df, spec.group.dimensions):
        for row in spec.rows:
            out_row = {**group_values, "categoria": row.label}
            for column in spec.columns:
                out_row[column.label] = _period_value(group_df, column, row, spec)
            rows.append(out_row)

    result = pd.DataFrame(rows)
    order = {row.label: position for position, row in enumerate(spec.rows)}
    result["_orden"] = result["categoria"].map(order)
    result = result.sort_values([*spec.group.dimensions, "_orden"]).drop(columns="_orden")
    return result.reset_index(drop=True)
