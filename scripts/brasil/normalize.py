from pathlib import Path
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


RAW = Path("outputs/raw_brasil/brasil_raw.parquet")
OUT = Path("data/brasil_clean")


def write_chunk(df, path):

    table = pa.Table.from_pandas(
        df,
        preserve_index=False,
    )

    pq.write_table(
        table,
        path,
        compression="snappy",
    )


def normalize():

    OUT.mkdir(
        parents=True,
        exist_ok=True,
    )

    pf = pq.ParquetFile(RAW)

    print("row groups:", pf.num_row_groups)

    for rg in range(pf.num_row_groups):

        print(f"\n[RG {rg+1}/{pf.num_row_groups}]")

        table = pf.read_row_group(rg)

        df = table.to_pandas()

        df["Ano"] = pd.to_numeric(
            df["Ano"],
            errors="coerce",
        )

        df["Trimestre"] = pd.to_numeric(
            df["Trimestre"],
            errors="coerce",
        )

        combos = (
            df[
                ["Ano", "Trimestre"]
            ]
            .dropna()
            .drop_duplicates()
            .sort_values(
                ["Ano", "Trimestre"]
            )
        )

        for row in combos.itertuples(index=False):

            year = int(row.Ano)
            tri = int(row.Trimestre)

            mask = (
                (df["Ano"] == year)
                &
                (df["Trimestre"] == tri)
            )

            piece = df.loc[mask]

            folder = OUT / str(year)

            folder.mkdir(
                parents=True,
                exist_ok=True,
            )

            path = (
                folder
                / f"T{tri}.parquet"
            )

            print(
                f"→ {year} T{tri}",
                piece.shape,
            )

            if path.exists():

                old = pq.read_table(path)

                new = pa.Table.from_pandas(
                    piece,
                    preserve_index=False,
                )

                merged = pa.concat_tables(
                    [
                        old,
                        new,
                    ],
                    promote_options="default",
                )

                pq.write_table(
                    merged,
                    path,
                    compression="snappy",
                )

            else:

                write_chunk(
                    piece,
                    path,
                )

            del piece

        del df
        del table

    print("\nDONE")


if __name__ == "__main__":
    normalize()