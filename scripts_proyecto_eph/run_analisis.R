###############################################################################
# SCRIPT CENTRAL - PROYECTO EPH
# Modos de ejecución (descomentar lo necesario):
###############################################################################

# -----------------------------------------------------------------------------
# OPCIÓN 1: EJECUCIÓN COMPLETA (descarga y procesa todo desde cero)
# -----------------------------------------------------------------------------
source("scripts/00_setup.R")
source("scripts/01_definir_trimestres.R")
source("scripts/02_descargar_datos.R")      # Descarga desde EPH
source("scripts/03_importar_procesar.R")    # Procesamiento inicial
source("scripts/04_consolidar_base.R")      # Unión y etiquetado
# source("scripts/05_filtrar_grupos.R")     # Opcional: crear subconjuntos
source("scripts/06_procesamiento_especifico.R") # Procesamiento por grupo
source("scripts/07_analisis.R")             # Análisis principales
source("scripts/08_visualizacion.R")        # Generación de gráficos
source("scripts/09_exportar.R")             # Exportación de resultados

# -----------------------------------------------------------------------------
# OPCIÓN 2: EJECUCIÓN PARCIAL (usando datos ya descargados)
# -----------------------------------------------------------------------------
# source("scripts/00_setup.R")
# source("scripts/01_definir_trimestres.R")
# source("scripts/03_importar_procesar.R")  # Usa datos locales
# source("scripts/04_consolidar_base.R")
# [resto igual...]

# -----------------------------------------------------------------------------
# OPCIÓN 3: SOLO ANÁLISIS (con base consolidada existente)
# -----------------------------------------------------------------------------
# source("scripts/00_setup.R")
# source("scripts/07_analisis.R")
# source("scripts/08_visualizacion.R")
# source("scripts/09_exportar.R")

# -----------------------------------------------------------------------------
# OPCIÓN 4: SOLO VISUALIZACIÓN (con resultados pre-generados)
# -----------------------------------------------------------------------------
# source("scripts/00_setup.R")
# source("scripts/08_visualizacion.R")
# source("scripts/09_exportar.R")