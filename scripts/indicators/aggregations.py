from __future__ import annotations

from collections.abc import Iterator

import pandas as pd

from scripts.indicators.measures import require_columns


def grouped(df: pd.DataFrame, dimensions: tuple[str, ...]) -> Iterator[tuple[dict, pd.DataFrame]]:
    if not dimensions:
        yield {}, df
        return

    require_columns(df, dimensions)
    for keys, group in df.groupby(list(dimensions), dropna=False):
        if not isinstance(keys, tuple):
            keys = (keys,)
        yield dict(zip(dimensions, keys)), group

