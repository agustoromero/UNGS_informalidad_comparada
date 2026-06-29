from __future__ import annotations

from pathlib import Path

import pandas as pd


HARMONIZED_DIR = Path("outputs/harmonized")


def read_harmonized_country(country: str, years: tuple[int, ...] | None = None) -> pd.DataFrame:
    selected_years = years or (2018, 2023)
    frames = []
    for year in selected_years:
        path = HARMONIZED_DIR / f"{country}_{year}.parquet"
        if not path.exists():
            raise FileNotFoundError(path)
        frames.append(pd.read_parquet(path))
    return pd.concat(frames, ignore_index=True)


def read_harmonized_all() -> pd.DataFrame:
    path = HARMONIZED_DIR / "harmonized_all.parquet"
    if not path.exists():
        raise FileNotFoundError(path)
    return pd.read_parquet(path)

