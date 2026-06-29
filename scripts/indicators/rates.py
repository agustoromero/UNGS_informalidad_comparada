from __future__ import annotations

import pandas as pd

from scripts.indicators.measures import safe_divide
from scripts.indicators.registry import indicator_count


def tasa_actividad(df: pd.DataFrame):
    return safe_divide(indicator_count(df, "pea"), indicator_count(df, "poblacion"))


def tasa_empleo(df: pd.DataFrame):
    return safe_divide(indicator_count(df, "ocupados"), indicator_count(df, "poblacion"))


def tasa_desocupacion(df: pd.DataFrame):
    return safe_divide(indicator_count(df, "desocupados"), indicator_count(df, "pea"))


def tasa_inactividad(df: pd.DataFrame):
    return safe_divide(indicator_count(df, "inactivos"), indicator_count(df, "poblacion"))

