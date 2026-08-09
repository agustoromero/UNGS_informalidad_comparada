import os
import requests

# ==============================
# CONFIG
# ==============================

BASE_URL = "https://www.indec.gob.ar/ftp/cuadros/menusuperior/eph"

OUTPUT_DIR = r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada\data\argentina"
os.makedirs(OUTPUT_DIR, exist_ok=True)

YEARS = ["2007", "2018", "2023"]
TRIMESTRES = ["1", "2", "3", "4"]

# ==============================
# DESCARGA
# ==============================

session = requests.Session()

for year in YEARS:
    for t in TRIMESTRES:

        # formato INDEC
        file_name = f"usu_individual_t{t}{year}.zip"
        url = f"{BASE_URL}/{year}/{file_name}"

        output_path = os.path.join(
            OUTPUT_DIR,
            f"{year}_T{t}.zip"
        )

        print(f"\nDescargando {year} T{t}...")

        try:
            r = session.get(url, stream=True, timeout=60)

            if r.status_code != 200:
                print(f"❌ No disponible ({r.status_code})")
                continue

            with open(output_path, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)

            print(f"✔ Guardado en: {output_path}")

        except Exception as e:
            print(f"Error: {e}")
