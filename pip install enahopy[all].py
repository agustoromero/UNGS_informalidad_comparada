from enahopy.loader import ENAHODataDownloader
import os

# ==============================
# CONFIG
# ==============================

OUTPUT_DIR = r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada\data\peru"
os.makedirs(OUTPUT_DIR, exist_ok=True)

YEARS = ["2007", "2018", "2023"]

# módulos clave (equivalentes a EPH)
MODULES = [
    '01',  # hogar
    '02',  # persona
    '05',  # empleo
    '34'   # sumaria (ingresos agregados)
]

# ==============================
# DESCARGA
# ==============================

downloader = ENAHODataDownloader(verbose=True)

data = downloader.download(
    modules=MODULES,
    years=YEARS,
    output_dir=OUTPUT_DIR,
    decompress=True,
    load_dta=False,   # ⚠️ no cargamos en memoria (más liviano)
    parallel=True,
    max_workers=3
)

print("\n✔ Descarga finalizada")

