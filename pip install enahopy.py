import os
import requests

# ==============================
# CONFIG
# ==============================

OUTPUT_DIR = r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada\data\peru"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ⚠️ IDs reales del catálogo (ejemplo funcional)
SURVEYS = {
    "2007": "https://anda.inec.gob.ec/anda/index.php/catalog/195/get_microdata",
    "2018": "https://anda.inec.gob.ec/anda/index.php/catalog/735/get_microdata",
    "2023": "https://anda.inec.gob.ec/anda/index.php/catalog/877/get_microdata"
}

# ==============================
# DESCARGA
# ==============================

session = requests.Session()
session.verify = False  # 🔥 necesario por SSL roto

requests.packages.urllib3.disable_warnings()

for year, url in SURVEYS.items():
    print(f"\nDescargando ENEMDU {year}...")

    try:
        response = session.get(url, stream=True, timeout=60)

        if response.status_code != 200:
            print(f"Error {response.status_code}")
            continue

        filename = os.path.join(OUTPUT_DIR, f"enemdu_{year}.zip")

        with open(filename, "wb") as f:
            for chunk in response.iter_content(8192):
                f.write(chunk)

        print(f"✔ Guardado en: {filename}")

    except Exception as e:
        print(f"Error en {year}: {e}")
