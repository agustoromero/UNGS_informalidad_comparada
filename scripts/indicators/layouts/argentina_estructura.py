from __future__ import annotations

from scripts.indicators.periods import quarter_columns
from scripts.indicators.schema import RowSpec, TableSpec


ARGENTINA_ESTRUCTURA_ROWS = (
    RowSpec("Sector Formal", "sector_formal", "ocupados"),
    RowSpec("Autónomos profesionales", "autonomos_profesionales", "ocupados"),
    RowSpec("Asalariados Privados", "asalariados_privados_no_micro", "ocupados"),
    RowSpec("Asalariados Públicos", "asalariados_publicos", "ocupados"),
    RowSpec("Patrones", "patrones_no_micro", "ocupados"),
    RowSpec("Sector Informal", "sector_informal", "ocupados"),
    RowSpec("Patrones (Micro)", "patrones_micro", "ocupados"),
    RowSpec("Asalariados Privados (Micro)", "asalariados_privados_micro", "ocupados"),
    RowSpec("Autónomos no profesionales", "autonomos_no_profesionales", "ocupados"),
    RowSpec("Trabajo Familiar", "trabajo_familiar", "ocupados"),
    RowSpec("Empleo doméstico", "empleo_domestico", "ocupados"),
)


ARGENTINA_ESTRUCTURA_PCT = TableSpec(
    table_id="argentina_estructura_pct",
    label="Argentina estructura - participaciones",
    rows=ARGENTINA_ESTRUCTURA_ROWS,
    columns=quarter_columns((2018, 2023)),
    default_denominator_id="ocupados",
    annual_method="sum_then_ratio",
    value_format="share",
)


ARGENTINA_ESTRUCTURA_CANT = TableSpec(
    table_id="argentina_estructura_cant",
    label="Argentina estructura - cantidades",
    rows=ARGENTINA_ESTRUCTURA_ROWS,
    columns=quarter_columns((2018, 2023)),
    default_denominator_id="ocupados",
    annual_method="sum_then_ratio",
    value_format="count",
)

