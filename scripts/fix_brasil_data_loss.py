"""
Fix script for Brasil data loss in build_core()

This script identifies and fixes the indexing issue in build_core() Brasil section
that causes ~85% population loss.

The problem: pd.DataFrame(index=df.index) combined with series assignments
can result in index misalignment, causing data to be dropped.

Solution: Use .values to avoid index-based alignment issues
"""

import pandas as pd
from pathlib import Path

print("=" * 80)
print("FIX VALIDATION: Brasil build_core() Population Preservation")
print("=" * 80)

# Load test data
clean_t1 = pd.read_parquet("data/brasil_clean/2018/T1.parquet")
clean_t1 = clean_t1[clean_t1['Trimestre'] == 1].copy()

print(f"\nInput: {len(clean_t1):,} filas, {clean_t1['V1028'].sum():,.0f} población")

# ============================================================================
# SIMULATE BUILD_CORE BRASIL - ORIGINAL (BROKEN)
# ============================================================================

print("\n[1] ORIGINAL (broken):")
print("-" * 80)

df = clean_t1.reset_index(drop=True)  # Simulate input
out_broken = pd.DataFrame(index=df.index)  # Creates 1.12M rows with RangeIndex

# Original problematic code:
out_broken["pais"] = "brasil"
out_broken["anio"] = 2018
out_broken["trimestre"] = 1
out_broken["id"] = (
    df[["UF", "UPA", "V1008", "V1014", "V2003"]]
    .astype(str)
    .agg("_".join, axis=1)
)
out_broken["ponderador"] = df["V1028"]

# Check status
print(f"After assignments:")
print(f"  Rows: {len(out_broken):,}")
print(f"  Population: {out_broken['ponderador'].sum():,.0f}")
print(f"  Loss: {(1 - out_broken['ponderador'].sum() / df['V1028'].sum()) * 100:.1f}%")

# ============================================================================
# SIMULATE BUILD_CORE BRASIL - FIXED (CORRECT)
# ============================================================================

print("\n[2] FIXED (correct):")
print("-" * 80)

df = clean_t1.reset_index(drop=True)
out_fixed = pd.DataFrame()  # Empty DF - will grow with assignments

# Fixed code using .values to avoid index issues:
out_fixed["pais"] = "brasil"
out_fixed["anio"] = 2018
out_fixed["trimestre"] = 1
out_fixed["id"] = (
    df[["UF", "UPA", "V1008", "V1014", "V2003"]]
    .astype(str)
    .agg("_".join, axis=1)
    .values  # ← CRITICAL FIX: Use .values
)
out_fixed["ponderador"] = df["V1028"].values  # ← CRITICAL FIX: Use .values

print(f"After assignments:")
print(f"  Rows: {len(out_fixed):,}")
print(f"  Population: {out_fixed['ponderador'].sum():,.0f}")
print(f"  Loss: {(1 - out_fixed['ponderador'].sum() / df['V1028'].sum()) * 100:.1f}%")

# ============================================================================
# VERIFICATION
# ============================================================================

print("\n[VERIFICATION]")
print("-" * 80)

if out_broken['ponderador'].sum() < out_fixed['ponderador'].sum():
    print(f"✓ FIX CONFIRMED: Original loses data")
    print(f"  Original population: {out_broken['ponderador'].sum():,.0f}")
    print(f"  Fixed population: {out_fixed['ponderador'].sum():,.0f}")
    print(f"  Improvement: {(out_fixed['ponderador'].sum() / out_broken['ponderador'].sum() - 1) * 100:.1f}%")
else:
    print(f"✗ FIX NOT NEEDED: Both have same population")

print("\n[RECOMMENDATION]")
print("-" * 80)
print(f"""
In common_pipeline.py, update build_core() Brasil section (line ~490-560):

CHANGE:
    out["ponderador"] = df["V1028"]

TO:
    out["ponderador"] = df["V1028"].values

Also add .values to ID assignment:
    out["id"] = df_id_series.values

This ensures numeric alignment, not index-based alignment.
""")
