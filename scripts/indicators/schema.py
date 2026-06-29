from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Literal

import pandas as pd


MaskFunc = Callable[[pd.DataFrame], pd.Series]
AnnualMethod = Literal["sum_then_ratio", "quarter_mean"]


@dataclass(frozen=True)
class IndicatorSpec:
    """Single methodological definition for a weighted indicator."""

    indicator_id: str
    label: str
    mask: MaskFunc
    required_columns: tuple[str, ...]
    denominator_id: str | None = None
    description: str = ""
    pending: bool = False


@dataclass(frozen=True)
class RowSpec:
    """A table row that points to one registered indicator."""

    label: str
    indicator_id: str
    denominator_id: str | None = None


@dataclass(frozen=True)
class ColumnSpec:
    """A time column in a table."""

    label: str
    year: int
    quarter: int | None = None


@dataclass(frozen=True)
class GroupSpec:
    """Reusable group-by dimensions."""

    dimensions: tuple[str, ...] = ()


@dataclass(frozen=True)
class TableSpec:
    """Declarative table layout. It contains no calculation logic."""

    table_id: str
    label: str
    rows: tuple[RowSpec, ...]
    columns: tuple[ColumnSpec, ...]
    group: GroupSpec = field(default_factory=GroupSpec)
    default_denominator_id: str | None = None
    annual_method: AnnualMethod = "sum_then_ratio"
    value_format: Literal["share", "count"] = "share"

