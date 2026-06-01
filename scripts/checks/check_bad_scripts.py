from pathlib import Path

base = Path("scripts")

print("\n=== CHEQUEO DE SCRIPTS ===\n")

for f in base.rglob("*.py"):
    if "common_pipeline" in str(f):
        continue

    txt = f.read_text(encoding="utf-8", errors="ignore")

    if "NotImplementedError" in txt or "load_data" in txt:
        print(f"❌ PROBLEMATICO: {f}")
    else:
        print(f"✔ OK: {f}")
