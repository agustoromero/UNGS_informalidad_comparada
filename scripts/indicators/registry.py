from __future__ import annotations

import pandas as pd

from scripts.indicators.measures import require_columns, weighted_count
from scripts.indicators.schema import IndicatorSpec


def _one(df: pd.DataFrame, column: str) -> pd.Series:
    require_columns(df, [column])
    return pd.to_numeric(df[column], errors="coerce").eq(1)


def _not_one(df: pd.DataFrame, column: str) -> pd.Series:
    require_columns(df, [column])
    return ~pd.to_numeric(df[column], errors="coerce").eq(1)


def _all(df: pd.DataFrame) -> pd.Series:
    return pd.Series(True, index=df.index)


def _any_registered(df: pd.DataFrame, indicator_ids: tuple[str, ...]) -> pd.Series:
    mask = pd.Series(False, index=df.index)
    for indicator_id in indicator_ids:
        mask = mask | get_indicator(indicator_id).mask(df)
    return mask


INDICATORS: dict[str, IndicatorSpec] = {
    "poblacion": IndicatorSpec(
        "poblacion",
        "Poblacion",
        _all,
        ("ponderador",),
        description="Total ponderado del archivo armonizado.",
    ),
    "pea": IndicatorSpec(
        "pea",
        "PEA",
        lambda df: _one(df, "ocupado") | _one(df, "desocupado"),
        ("ocupado", "desocupado", "ponderador"),
        description="Ocupados + desocupados.",
    ),
    "ocupados": IndicatorSpec(
        "ocupados",
        "Ocupados",
        lambda df: _one(df, "ocupado"),
        ("ocupado", "ponderador"),
    ),
    "desocupados": IndicatorSpec(
        "desocupados",
        "Desocupados",
        lambda df: _one(df, "desocupado"),
        ("desocupado", "ponderador"),
    ),
    "inactivos": IndicatorSpec(
        "inactivos",
        "Inactivos",
        lambda df: _one(df, "inactivo"),
        ("inactivo", "ponderador"),
    ),
    "asalariados": IndicatorSpec(
        "asalariados",
        "Asalariados",
        lambda df: _one(df, "asalariado"),
        ("asalariado", "ponderador"),
        denominator_id="ocupados",
    ),
    "asalariados_publicos": IndicatorSpec(
        "asalariados_publicos",
        "Asalariados publicos",
        lambda df: _one(df, "asalariado_publico"),
        ("asalariado_publico", "ponderador"),
        denominator_id="ocupados",
    ),
    "asalariados_privados": IndicatorSpec(
        "asalariados_privados",
        "Asalariados privados",
        lambda df: _one(df, "asalariado_privado"),
        ("asalariado_privado", "ponderador"),
        denominator_id="ocupados",
    ),
    "asalariados_privados_no_micro": IndicatorSpec(
        "asalariados_privados_no_micro",
        "Asalariados Privados",
        lambda df: _one(df, "asalariado_privado")
        & _not_one(df, "asalariado_privado_micro"),
        ("asalariado_privado", "asalariado_privado_micro", "ponderador"),
        denominator_id="ocupados",
        description="Asalariados privados excluyendo el flag armonizado asalariado_privado_micro.",
    ),
    "cuenta_propia": IndicatorSpec(
        "cuenta_propia",
        "Cuenta propia",
        lambda df: _one(df, "cuentapropia"),
        ("cuentapropia", "ponderador"),
        denominator_id="ocupados",
    ),
    "autonomos_profesionales": IndicatorSpec(
        "autonomos_profesionales",
        "Autonomos profesionales",
        lambda df: _one(df, "cuentapropia") & _one(df, "educacion_superior"),
        ("cuentapropia", "educacion_superior", "ponderador"),
        denominator_id="ocupados",
        description="Cuenta propia con educacion_superior armonizada.",
    ),
    "autonomos_no_profesionales": IndicatorSpec(
        "autonomos_no_profesionales",
        "Autonomos no profesionales",
        lambda df: _one(df, "cuentapropia") & _not_one(df, "educacion_superior"),
        ("cuentapropia", "educacion_superior", "ponderador"),
        denominator_id="ocupados",
        description="Cuenta propia sin educacion_superior armonizada.",
    ),
    "patrones": IndicatorSpec(
        "patrones",
        "Patrones",
        lambda df: _one(df, "patron"),
        ("patron", "ponderador"),
        denominator_id="ocupados",
    ),
    "patrones_no_micro": IndicatorSpec(
        "patrones_no_micro",
        "Patrones",
        lambda df: _one(df, "patron") & _not_one(df, "patron_micro"),
        ("patron", "patron_micro", "ponderador"),
        denominator_id="ocupados",
        description="Patrones excluyendo el flag armonizado patron_micro.",
    ),
    "patrones_micro": IndicatorSpec(
        "patrones_micro",
        "Patrones (Micro)",
        lambda df: _one(df, "patron_micro"),
        ("patron_micro", "ponderador"),
        denominator_id="ocupados",
    ),
    "empleo_domestico": IndicatorSpec(
        "empleo_domestico",
        "Empleo domestico",
        lambda df: _one(df, "empleo_domestico"),
        ("empleo_domestico", "ponderador"),
        denominator_id="ocupados",
    ),
    "trabajo_familiar": IndicatorSpec(
        "trabajo_familiar",
        "Trabajo familiar",
        lambda df: _one(df, "trab_familiar"),
        ("trab_familiar", "ponderador"),
        denominator_id="ocupados",
    ),
    "formales": IndicatorSpec(
        "formales",
        "Formales",
        lambda df: _one(df, "formal"),
        ("formal", "ponderador"),
        denominator_id="ocupados",
    ),
    "informales": IndicatorSpec(
        "informales",
        "Informales",
        lambda df: _one(df, "informal"),
        ("informal", "ponderador"),
        denominator_id="ocupados",
    ),
    "asalariados_privados_micro": IndicatorSpec(
        "asalariados_privados_micro",
        "Asalariados Privados (Micro)",
        lambda df: _one(df, "asalariado_privado_micro"),
        ("asalariado_privado_micro", "ponderador"),
        denominator_id="ocupados",
    ),
    "sector_formal": IndicatorSpec(
        "sector_formal",
        "Sector Formal",
        lambda df: _any_registered(
            df,
            (
                "autonomos_profesionales",
                "asalariados_privados_no_micro",
                "asalariados_publicos",
                "patrones_no_micro",
            ),
        ),
        (
            "cuentapropia",
            "educacion_superior",
            "asalariado_privado",
            "asalariado_privado_micro",
            "asalariado_publico",
            "patron",
            "patron_micro",
            "ponderador",
        ),
        denominator_id="ocupados",
        description="Agregado formal de argentina_estructura sobre variables armonizadas.",
    ),
    "sector_informal": IndicatorSpec(
        "sector_informal",
        "Sector Informal",
        lambda df: _any_registered(
            df,
            (
                "patrones_micro",
                "asalariados_privados_micro",
                "autonomos_no_profesionales",
                "trabajo_familiar",
                "empleo_domestico",
            ),
        ),
        (
            "patron_micro",
            "asalariado_privado_micro",
            "cuentapropia",
            "educacion_superior",
            "trab_familiar",
            "empleo_domestico",
            "ponderador",
        ),
        denominator_id="ocupados",
        description="Agregado informal de argentina_estructura sobre variables armonizadas.",
    ),
    "ocupados_demandantes": IndicatorSpec(
        "ocupados_demandantes",
        "Ocupados demandantes",
        lambda df: pd.Series(pd.NA, index=df.index),
        ("ocupado_demandante", "ponderador"),
        denominator_id="pea",
        pending=True,
        description="Pendiente hasta incorporar ocupado_demandante en harmonized.",
    ),
    "subocupados": IndicatorSpec(
        "subocupados",
        "Subocupados",
        lambda df: pd.Series(pd.NA, index=df.index),
        ("subocupado", "ponderador"),
        denominator_id="pea",
        pending=True,
        description="Pendiente hasta incorporar subocupado en harmonized.",
    ),
}


def get_indicator(indicator_id: str) -> IndicatorSpec:
    try:
        return INDICATORS[indicator_id]
    except KeyError as exc:
        raise KeyError(f"Indicador no registrado: {indicator_id}") from exc


def indicator_count(df: pd.DataFrame, indicator_id: str) -> float:
    spec = get_indicator(indicator_id)
    require_columns(df, spec.required_columns)
    return weighted_count(df, spec.mask(df))

