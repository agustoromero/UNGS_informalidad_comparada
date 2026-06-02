from pathlib import Path

import pandas as pd


def summarize_df(df: pd.DataFrame) -> dict:
    total_weight = float(df["ponderador"].sum())
    result = {
        "rows": int(len(df)),
        "total_weight": total_weight,
        "ocupado_weight": float((df["ponderador"] * df["ocupado"]).sum()),
        "desocupado_weight": float((df["ponderador"] * df["desocupado"]).sum()),
        "inactivo_weight": float((df["ponderador"] * df["inactivo"]).sum()),
        "asalariado_weight": float((df["ponderador"] * df["asalariado"]).sum()),
        "cuentapropia_weight": float((df["ponderador"] * df["cuentapropia"]).sum()),
        "informal_weight": float((df["ponderador"] * df["informal"]).sum()),
        "formal_weight": float((df["ponderador"] * df["formal"]).sum()),
    }
    if total_weight > 0:
        result.update(
            {
                "ocupado_pct": result["ocupado_weight"] / total_weight,
                "desocupado_pct": result["desocupado_weight"] / total_weight,
                "inactivo_pct": result["inactivo_weight"] / total_weight,
                "asalariado_pct": result["asalariado_weight"] / total_weight,
                "cuentapropia_pct": result["cuentapropia_weight"] / total_weight,
                "informal_pct": result["informal_weight"] / total_weight,
                "formal_pct": result["formal_weight"] / total_weight,
            }
        )
    return result


def build_country_workbook(country: str, rows: list[dict], target_dir: Path) -> Path:
    workbook_path = target_dir / f"{country}.xlsx"

    with pd.ExcelWriter(workbook_path, engine="openpyxl") as writer:
        summary = pd.DataFrame(rows)
        summary = summary.set_index("year")
        summary = summary[
            [
                "rows",
                "total_weight",
                "ocupado_weight",
                "desocupado_weight",
                "inactivo_weight",
                "asalariado_weight",
                "cuentapropia_weight",
                "informal_weight",
                "formal_weight",
                "ocupado_pct",
                "desocupado_pct",
                "inactivo_pct",
                "asalariado_pct",
                "cuentapropia_pct",
                "informal_pct",
                "formal_pct",
            ]
        ]
        summary.to_excel(writer, sheet_name="summary")

        for row in rows:
            year = row["year"]
            df = pd.read_parquet(row["path"])
            activity = [
                ("ocupado", "ocupado"),
                ("desocupado", "desocupado"),
                ("inactivo", "inactivo"),
            ]
            category = [
                ("asalariado", "asalariado"),
                ("cuentapropia", "cuentapropia"),
            ]
            formality = [
                ("informal", "informal"),
                ("formal", "formal"),
            ]

            detail_rows = []
            for label, col in activity + category + formality:
                detail_rows.append(
                    {
                        "group": label,
                        "weight": float((df["ponderador"] * df[col]).sum()),
                        "unweighted_count": int(df[col].sum()),
                    }
                )
            details = pd.DataFrame(detail_rows)
            details.to_excel(writer, sheet_name=f"{year}_breakdown", index=False)

    return workbook_path


def main() -> None:
    harmonized_dir = Path("outputs/harmonized")
    target_dir = Path("outputs/harmonized_excels")
    target_dir.mkdir(parents=True, exist_ok=True)

    parquet_files = sorted(harmonized_dir.glob("*.parquet"))
    country_rows: dict[str, list[dict]] = {}

    for parquet_path in parquet_files:
        stem = parquet_path.stem
        parts = stem.split("_")
        if len(parts) < 2:
            continue
        country = "_".join(parts[:-1])
        try:
            year = int(parts[-1])
        except ValueError:
            continue

        df = pd.read_parquet(parquet_path)
        summary = summarize_df(df)
        summary["year"] = year
        summary["path"] = parquet_path

        country_rows.setdefault(country, []).append(summary)

    for country, rows in country_rows.items():
        rows = sorted(rows, key=lambda x: x["year"])
        workbook_path = build_country_workbook(country, rows, target_dir)
        print(f"Generado: {workbook_path}")


if __name__ == "__main__":
    main()
