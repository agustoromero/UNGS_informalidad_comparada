from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

# ==============================
# CONFIG
# ==============================

DOWNLOAD_DIR = r"C:\Users\agusr\OneDrive\repos\UNGS_informalidad_comparada\data\chile"

chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "directory_upgrade": True
})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

# ==============================
# ABRIR PORTAL
# ==============================

driver.get("https://bancodatosene.ine.cl/")
time.sleep(10)

# ==============================
# SELECCIONAR AÑO (AJUSTABLE)
# ==============================

try:
    selects = driver.find_elements(By.TAG_NAME, "select")

    for s in selects:
        options = s.find_elements(By.TAG_NAME, "option")
        for op in options:
            if "2023" in op.text:
                op.click()
                print("✔ Año 2023 seleccionado")
                break

    time.sleep(5)

except Exception as e:
    print("Error seleccionando año:", e)

# ==============================
# CLICK EN TABLA / GENERAR
# ==============================

try:
    botones = driver.find_elements(By.TAG_NAME, "button")

    for b in botones:
        if "generar" in b.text.lower() or "consultar" in b.text.lower():
            b.click()
            print("✔ Tabla generada")
            break

    time.sleep(10)

except Exception as e:
    print("Error generando tabla:", e)

# ==============================
# EXPORTAR
# ==============================

try:
    botones = driver.find_elements(By.TAG_NAME, "button")

    for b in botones:
        if "export" in b.text.lower():
            b.click()
            print("✔ Exportando archivo")
            break

except Exception as e:
    print("Error exportando:", e)

# ==============================
# ESPERAR DESCARGA
# ==============================

time.sleep(30)

driver.quit()

