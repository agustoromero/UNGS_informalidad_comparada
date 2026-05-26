#!/usr/bin/env python
"""
Script maestro para ejecutar la armonización completa (ejecución directa).
"""

import sys
from pathlib import Path

# Añadir directorio al path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.common_pipeline import run_country_year
from scripts.harmonization.build_harmonized import main as harmonize_all


def main():
    configs = [
        ("argentina", 2018),
        ("argentina", 2023),
        ("brasil", 2018),
        ("brasil", 2023),
        ("mexico", 2018),
        ("mexico", 2023),
        ("colombia", 2018),
        ("colombia", 2023),
    ]
    
    print("\n" + "="*70)
    print("INICIANDO ARMONIZACIÓN COMPLETA")
    print("="*70)
    
    failed = []
    for country, year in configs:
        print(f"\n{'='*70}")
        print(f"Procesando: {country.upper()} {year}")
        print(f"{'='*70}")
        
        try:
            run_country_year(country, year)
            print(f"✅ Completado: {country} {year}")
        except Exception as e:
            print(f"❌ Error en {country} {year}: {e}")
            failed.append(f"{country}_{year}")
    
    # Ejecutar armonización final
    print(f"\n{'='*70}")
    print("Ejecutando armonización final...")
    print(f"{'='*70}")
    
    try:
        harmonize_all()
        print("✅ Armonización final completada")
    except Exception as e:
        print(f"❌ Error en armonización final: {e}")
        failed.append("harmonization")
    
    # Resumen final
    print(f"\n{'='*70}")
    print("RESUMEN FINAL")
    print(f"{'='*70}")
    
    if not failed:
        print("✅ ARMONIZACIÓN COMPLETADA EXITOSAMENTE")
        print("\nArchivos generados en outputs/harmonized/:")
        harmonized_dir = Path("outputs/harmonized")
        if harmonized_dir.exists():
            for f in sorted(harmonized_dir.glob("*")):
                if f.is_file():
                    size_mb = f.stat().st_size / (1024 * 1024)
                    print(f"  - {f.name} ({size_mb:.2f} MB)")
        return 0
    else:
        print("❌ FALLOS EN LA ARMONIZACIÓN:")
        for item in failed:
            print(f"  - {item}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
