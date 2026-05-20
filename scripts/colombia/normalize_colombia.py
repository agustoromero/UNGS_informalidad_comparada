"""
NORMALIZADOR COLOMBIA
=====================

Etapa 1 del pipeline: tolerancia + consolidación

INPUT:  data/colombia_clean/2018/T{1-4}/*.csv (desordenados, con duplicados)
OUTPUT: data/colombia_clean/2018/*.parquet   (limpio, indexado, listo para load_period)

✔ Este script se corre UNA SOLA VEZ por año
✔ Después, common_pipeline.py simplemente lee los .parquet
"""

from pathlib import Path
import warnings
import pandas as pd
import numpy as np


def log(msg):
    print(f"[NORMALIZE_COLOMBIA] {msg}")


def normalize_year(year: int):
    """
    Normaliza un año completo: T1-T4
    
    Para cada trimestre:
    - Lee CSVs crudos (características, fuerza, ocupados)
    - Merge en DIRECTORIO + SECUENCIA_P + ORDEN + HOGAR
    - Agrega FEX
    - Guarda como parquet
    """

    base = Path("data/colombia_clean") / str(year)

    if not base.exists():
        raise FileNotFoundError(f"No existe {base}")

    output_dir = base

    log(f"Normalizando Colombia {year}")
    log(f"Input: {base}")
    log(f"Output: {output_dir}")

    for q in [1, 2, 3, 4]:

        trim_dir = base / f"T{q}"

        if not trim_dir.exists():
            warnings.warn(f"T{q} no existe en {base}")
            continue

        log(f"\n{'='*60}")
        log(f"TRIMESTRE {q}")
        log(f"{'='*60}")

        # =====================================================================
        # CARGAR MODULOS
        # =====================================================================

        # 1. Características (eliminar duplicados: hay dos versiones en algunos trimestres)
        all_char = list(trim_dir.glob("*generales_personas.csv"))
        
        if not all_char:
            warnings.warn(f"T{q}: sin características")
            continue
        
        # 2. Fuerza (cargar una vez)
        fuerza_files = list(trim_dir.glob("*fuerza*.csv"))
        if not fuerza_files:
            warnings.warn(f"T{q}: sin fuerza de trabajo")
            continue

        fuerza_file = fuerza_files[0]

        fdf = pd.read_csv(
            fuerza_file,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
        )

        fdf.columns = fdf.columns.str.strip()
        log(f"Leyendo fuerza: {fuerza_file.name}")

        # 3. Ocupados (específico, no desocupados)
        ocu_files = [
            f for f in trim_dir.glob("*.csv")
            if "ocupados" in f.name.lower()
            and "desocupados" not in f.name.lower()
        ]

        if not ocu_files:
            warnings.warn(f"T{q}: sin ocupados")
            continue

        ocu_file = ocu_files[0]
        log(f"Leyendo ocupados: {ocu_file.name}")

        odf = pd.read_csv(
            ocu_file,
            sep=None,
            engine="python",
            encoding="utf-8-sig",
        )

        odf.columns = odf.columns.str.strip()

        # 4. Probar cada versión de características y usar la que funciona
        cdf = None
        keys = ["DIRECTORIO", "SECUENCIA_P", "ORDEN", "HOGAR"]
        
        for candidate_char_file in sorted(all_char):
            
            candidate_cdf = pd.read_csv(
                candidate_char_file,
                sep=None,
                engine="python",
                encoding="utf-8-sig",
            )
            
            candidate_cdf.columns = candidate_cdf.columns.str.strip()
            
            log(f"Leyendo características: {candidate_char_file.name}")
            
            # Intentar merge de prueba
            test_merge = candidate_cdf.merge(fdf, on=keys, how="inner")
            
            if test_merge.shape[0] > 0:
                # Este archivo funciona!
                cdf = candidate_cdf
                log(f"  -> OK ({test_merge.shape[0]} filas)")
                break
            else:
                log(f"  -> Da 0 filas, saltando")
        
        if cdf is None:
            raise ValueError(f"T{q}: ningún archivo de características funcionó")

        # =====================================================================
        # VALIDAR ESTRUCTURA
        # =====================================================================

        for name, dfx in [
            ("características", cdf),
            ("fuerza", fdf),
            ("ocupados", odf),
        ]:

            missing = [c for c in keys if c not in dfx.columns]

            if missing:
                raise ValueError(
                    f"T{q} {name}: faltan keys {missing}"
                )

        log(f"  [OK] Estructura valida")

        # =====================================================================
        # DUPLICADOS
        # =====================================================================

        dup_c = cdf.duplicated(keys).sum()
        dup_f = fdf.duplicated(keys).sum()
        dup_o = odf.duplicated(keys).sum()

        if dup_c > 0:
            warnings.warn(
                f"T{q} características: {dup_c} duplicados"
            )

        if dup_f > 0:
            warnings.warn(f"T{q} fuerza: {dup_f} duplicados")

        if dup_o > 0:
            warnings.warn(f"T{q} ocupados: {dup_o} duplicados")

        # =====================================================================
        # MERGE
        # =====================================================================

        log("Merging características + fuerza + ocupados...")
        log(f"  cdf shape: {cdf.shape}")
        log(f"  fdf shape: {fdf.shape}")
        log(f"  odf shape: {odf.shape}")

        tmp = (
            cdf.merge(
                fdf,
                on=keys,
                how="inner",
                validate="one_to_one",
            )
            .merge(
                odf,
                on=keys,
                how="left",
                validate="many_to_one",
            )
        )

        log(f"  Shape merged: {tmp.shape}")

        # =====================================================================
        # FEX (FACTOR DE EXPANSION)
        # =====================================================================

        fex_col = None

        # Buscar archivos de expansion
        fex_files = list(
            Path("data/colombia/Total_Fact_expansion").rglob("*[Ff]act*[Ee]xpans*.csv")
        )

        if fex_files:

            log(f"Encontrado FEX: {fex_files[0].name}")

            fex = pd.read_csv(
                fex_files[0],
                sep=None,
                engine="python",
                encoding="utf-8-sig",
            )

            fex.columns = fex.columns.str.strip()

            # Validar que tiene las keys
            required_fex = ["DIRECTORIO", "SECUENCIA_P", "ORDEN"]

            missing = [c for c in required_fex if c not in fex.columns]

            if missing:
                raise ValueError(f"FEX sin keys: {missing}")

            # Detectar ponderador
            weight_candidates = [c for c in fex.columns if "FEX" in c.upper()]

            if not weight_candidates:
                raise ValueError("FEX sin columna de ponderación")

            fex_col = weight_candidates[0]

            log(f"  Usando FEX column: {fex_col}")

            fex = fex[["DIRECTORIO", "SECUENCIA_P", "ORDEN", fex_col]]

            # Merge con FEX (solo 3 keys, sin HOGAR)
            tmp = tmp.merge(
                fex,
                on=["DIRECTORIO", "SECUENCIA_P", "ORDEN"],
                how="left",
                validate="many_to_one",
            )

            log(f"  Shape after FEX merge: {tmp.shape}")

        else:

            warnings.warn("No se encontró archivo FEX")

        # =====================================================================
        # PONDERADOR FINAL
        # =====================================================================

        if fex_col is not None:
            # Limpiar y convertir: usar coma como separador decimal
            tmp["ponderador"] = (
                tmp[fex_col]
                .astype(str)
                .str.replace(",", ".")
                .apply(pd.to_numeric, errors="coerce")
            )
        else:
            # Fallback: usar fex_c_2011 si existe
            if "fex_c_2011" in tmp.columns:
                tmp["ponderador"] = (
                    tmp["fex_c_2011"]
                    .astype(str)
                    .str.replace(",", ".")
                    .apply(pd.to_numeric, errors="coerce")
                )
            else:
                warnings.warn(f"T{q}: asignando ponderador = 1")
                tmp["ponderador"] = 1.0

        # =====================================================================
        # VALIDACIONES
        # =====================================================================

        log("Validando ponderador...")

        na_ponderador = tmp["ponderador"].isna().sum()

        if na_ponderador > 0:
            log(f"  ⚠ {na_ponderador} NA en ponderador")

            # Si tenemos fallback, usar
            if "fex_c_2011" in tmp.columns:
                mask = tmp["ponderador"].isna()
                tmp.loc[mask, "ponderador"] = tmp.loc[mask, "fex_c_2011"]
                log(f"    Reemplazados con fex_c_2011")

        # Check final
        if tmp["ponderador"].isna().any():
            raise ValueError(f"T{q}: ponderador aún con NA después de fallback")

        if (tmp["ponderador"] <= 0).any():
            raise ValueError(f"T{q}: ponderador <= 0")

            log(f"  [OK] Ponderador valido: mean={tmp['ponderador'].mean():.2f}")

        # =====================================================================
        # GUARDAR PARQUET
        # =====================================================================

        output_file = output_dir / f"T{q}.parquet"

        log(f"Guardando: {output_file}")

        tmp.to_parquet(
            output_file,
            index=False,
            compression="snappy",
        )

        log(f"  [OK] {output_file.name} guardado ({tmp.shape[0]:,} filas)")

        print(f"\n[DONE] Normalizacion completa para {year}")


if __name__ == "__main__":

    # Normalizar 2018 y 2023 si existen

    for year in [2018, 2023]:

        base = Path("data/colombia_clean") / str(year)

        if base.exists():

            try:
                normalize_year(year)
            except Exception as e:
                print(f"\n[ERROR] en {year}:")
                print(f"   {e}\n")

        else:

            print(f"[SKIP] {base} no existe")
