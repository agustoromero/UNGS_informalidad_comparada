"""Chequeos automáticos de estructura, distribución y coherencia."""

from pathlib import Path
import pandas as pd


def run_checks(df: pd.DataFrame) -> list[str]:
    warnings: list[str] = []

    assert "ocupado" in df.columns
    assert df["ponderador"].notna().all()

    occ_rate = df["ocupado"].mean()
    if occ_rate < 0.3:
        warnings.append("Tasa de ocupación sospechosa (<0.3)")

    identity = df[["ocupado", "desocupado", "inactivo"]].sum(axis=1)
    assert (identity == 1).all()

    return warnings


def write_log(name: str, warnings: list[str]) -> None:
    log_path = Path("logs") / f"{name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    content = "OK" if not warnings else "\n".join(["WARNINGS:", *warnings])
    log_path.write_text(content, encoding="utf-8")




def check_conflict_markers(search_root: Path) -> list[str]:
    """Detecta residuos de conflictos de merge en archivos de texto."""
    warnings: list[str] = []
    patterns = ("<" * 7, "=" * 7, ">" * 7)
    exts = {".py", ".yaml", ".yml", ".md", ".txt"}

    for path in search_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in exts:
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        if any(token in content for token in patterns):
            warnings.append(f"Conflicto de merge detectado en {path}")

    return warnings


def main() -> None:
    marker_warnings = check_conflict_markers(Path("."))
    if marker_warnings:
        for msg in marker_warnings:
            print(msg)

    files = sorted(Path("outputs/harmonized").glob("*.parquet"))
    for file in files:
        if file.name == "harmonized.parquet":
            continue
        df = pd.read_parquet(file)
        warnings = run_checks(df) + marker_warnings
        write_log(file.stem, warnings)


if __name__ == "__main__":
    main()
