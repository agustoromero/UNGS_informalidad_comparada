from pathlib import Path
import pandas as pd


def main():

    base = Path(
        "outputs/harmonized"
    )

    files = sorted(
        base.glob(
            "*.parquet"
        )
    )

    files = [
        f
        for f in files
        if f.name
        not in {
            "harmonized.parquet",
            "harmonized_all.parquet",
        }
    ]

    if not files:

        print(
            "[HARMONIZATION] No hay archivos"
        )

        return

    print(
        "\n[HARMONIZATION] Archivos:"
    )

    dfs = []

    for f in files:

        print(
            f"→ {f.name}"
        )

        dfs.append(
            pd.read_parquet(f)
        )

    out = pd.concat(
        dfs,
        ignore_index=True,
    )

    target = (
        base
        / "harmonized_all.parquet"
    )

    out.to_parquet(
        target,
        index=False,
    )

    print(
        "\n[HARMONIZATION] OK"
    )

    print(
        target
    )

    print(
        out.shape
    )


if __name__ == "__main__":

    main()
