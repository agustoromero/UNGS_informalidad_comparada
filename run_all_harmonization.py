#!/usr/bin/env python
"""
Script maestro para ejecutar la armonización completa:
- Argentina 2018, 2023
- Brasil 2018, 2023
- México 2018, 2023
- Colombia 2018, 2023
"""

import sys
import os
from pathlib import Path
import subprocess

# Directorio base del proyecto
PROJECT_ROOT = Path(__file__).parent

def run_script(script_path: str) -> bool:
    """Ejecuta un script de Python y retorna True si es exitoso."""
    print(f"\n{'='*70}")
    print(f"Ejecutando: {script_path}")
    print(f"{'='*70}")
    
    full_path = str(PROJECT_ROOT / script_path)
    
    # Crear environment con PYTHONPATH actualizado
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    
    result = subprocess.run(
        [sys.executable, full_path],
        cwd=PROJECT_ROOT,
        env=env,
        capture_output=False
    )
    
    if result.returncode != 0:
        print(f"❌ Error en {script_path}")
        return False
    
    print(f"✅ Completado: {script_path}")
    return True


def main():
    scripts = [
        # Argentina
        "scripts/argentina/argentina_2018.py",
        "scripts/argentina/argentina_2023.py",
        # Brasil
        "scripts/brasil/brasil_2018.py",
        "scripts/brasil/brasil_2023.py",
        # México
        "scripts/mexico/mexico_2018.py",
        "scripts/mexico/mexico_2023.py",
        # Colombia
        "scripts/colombia/colombia_2018.py",
        "scripts/colombia/colombia_2023.py",
    ]
    
    print("\n" + "="*70)
    print("INICIANDO ARMONIZACIÓN COMPLETA")
    print("="*70)
    print(f"Directorio: {PROJECT_ROOT}")
    print(f"Scripts a ejecutar: {len(scripts)}")
    for i, script in enumerate(scripts, 1):
        print(f"  {i}. {script}")
    
    failed = []
    for script in scripts:
        if not run_script(str(PROJECT_ROOT / script)):
            failed.append(script)
    
    # Ejecutar armonización final
    print(f"\n{'='*70}")
    print("Ejecutando armonización final...")
    print(f"{'='*70}")
    
    if not run_script("scripts/harmonization/build_harmonized.py"):
        failed.append("scripts/harmonization/build_harmonized.py")
    
    # Resumen final
    print(f"\n{'='*70}")
    print("RESUMEN FINAL")
    print(f"{'='*70}")
    
    if not failed:
        print("✅ ARMONIZACIÓN COMPLETADA EXITOSAMENTE")
        print("\nArchivos generados en outputs/harmonized/:")
        harmonized_dir = PROJECT_ROOT / "outputs" / "harmonized"
        if harmonized_dir.exists():
            for f in sorted(harmonized_dir.glob("*")):
                if f.is_file():
                    size_mb = f.stat().st_size / (1024 * 1024)
                    print(f"  - {f.name} ({size_mb:.2f} MB)")
        return 0
    else:
        print("❌ FALLOS EN LA ARMONIZACIÓN:")
        for script in failed:
            print(f"  - {script}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
