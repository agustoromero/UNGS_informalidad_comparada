#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "[AUDIT] Repo: $ROOT"
echo "[AUDIT] Fecha UTC: $(date -u +%Y-%m-%dT%H:%M:%SZ)"

python - <<'PY'
import importlib, sys
mods=['pandas','pyarrow']
missing=[]
for m in mods:
    try:
        importlib.import_module(m)
    except Exception:
        missing.append(m)
if missing:
    print('[AUDIT] Faltan dependencias:', ', '.join(missing))
    sys.exit(2)
print('[AUDIT] Dependencias OK')
PY

python scripts/brasil/diagnose_pnadc_types.py
