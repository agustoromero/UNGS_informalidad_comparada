###############################################################################
# 00_setup.R - Configuración avanzada para análisis EPH 2014-2024
#
# Este script:
# 1. Carga/instala paquetes necesarios
# 2. Configura directorios y entorno
# 3. Define variables esenciales para el análisis laboral
# 4. Establece funciones auxiliares
# 5. Configura parámetros visuales
#
# Última actualización: [fecha]
###############################################################################

# 1. INSTALACIÓN Y CARGA DE PAQUETES ------------------------------------------
required_packages <- c(
  # Core
  "tidyverse",       # Incluye dplyr, ggplot2, tidyr, etc.
  "haven",           # Importación de datos SPSS/Stata
  "eph",             # Descarga y manejo de datos EPH
  "conflicted",      # Manejo de conflictos de funciones
  # Procesamiento
  "labelled",        # Manejo de variables etiquetadas
  "stringr",         # Manipulación de strings
  "lubridate",       # Manejo de fechas
  "zoo",             # Funciones para series de tiempo
  
  # Análisis
  "survey",          # Para análisis de encuestas complejas
  "srvyr",           # Versión tidy de survey
  
  # Visualización
  "ggrepel",         # Etiquetas en gráficos
  "scales",          # Formateo de escalas
  "patchwork",       # Combinación de gráficos
  "RColorBrewer",    # Paletas de colores
  
  # Exportación
  "openxlsx",        # Exportación a Excel
  "writexl",         # Alternativa ligera para Excel
  
  # Performance
  "data.table",      # Para operaciones rápidas en grandes datasets
  "pryr"             # Monitoreo de memoria
)

# Instalar faltantes
missing_packages <- setdiff(required_packages, rownames(installed.packages()))
if (length(missing_packages) > 0) {
  message("Instalando paquetes faltantes: ", paste(missing_packages, collapse = ", "))
  install.packages(missing_packages)
}

# Cargar paquetes con manejo de conflictos
suppressPackageStartupMessages({
  library(tidyverse)
  library(haven)
  library(eph)
  library(conflicted)
  
  # Resolver conflictos comunes
  conflict_prefer("filter", "dplyr")
  conflict_prefer("select", "dplyr")
  conflict_prefer("year", "lubridate")
  conflict_prefer("month", "lubridate")
})

invisible(lapply(setdiff(required_packages, c("tidyverse", "haven", "eph")), 
                 library, character.only = TRUE))
# 2. CONFIGURACIÓN DE DIRECTORIOS --------------------------------------------
dirs <- c(
  "data/raw",            # Datos descargados originales
  "data/processed",      # Datos procesados
  "output/figures",      # Gráficos
  "output/tables",       # Tablas de resultados
  "config",              # Archivos de configuración
  "scripts/functions"    # Funciones personalizadas
)

# Crear directorios si no existen
lapply(dirs, function(x) dir.create(x, showWarnings = FALSE, recursive = TRUE))

# 3. DEFINICIÓN DE VARIABLES CLAVE -------------------------------------------

# 3.1 Variables esenciales (comunes a todos los análisis)
vars_esenciales <- c(
  # Identificación
  "CODUSU", "ANO4", "TRIMESTRE", "NRO_HOGAR", "COMPONENTE",
  
  # Geográficas
  "REGION", "AGLOMERADO", "CH15_COD",
  
  # Demográficas
  "CH03", "CH04", "CH06", "CH07", "NIVEL_ED",
  
  # Condición de actividad
  "ESTADO", "CAT_OCUP", "CAT_INAC", "IMPUTA", "INTENSI",
  
  # Ponderadores
  "PONDERA", "PONDII", "PONDIH", "PONDIIO"
)

# 3.2 Variables específicas para análisis laboral
vars_laborales <- c(
  # Características del puesto
  "PP04A", "PP04B_COD", "PP04C", "PP04C99", "PP04G",
  "PP07A", "PP07C", "PP07D", "PP07E", "PP07G1", "PP07G2", "PP07G3", "PP07G4",
  
  # Ingresos
  "P21", "TOT_P12", "P47T", "ITF", "IPCF",
  # otras Relacionadas a ingresos
  "PP3E_TOT", "PP3F_TOT", "DECOCUR", "IDECOCUR", "RDECOCUR", "GDECOCUR",
  "PDECOCUR", "ADECOCUR", "DECINDR", "IDECINDR",
  "RDECINDR", "GDECINDR", "PDECINDR", "ADECINDR", "V2_M", "V3_M", "V4_M", "V5_M",
  "V8_M", "V9_M", "V10_M", "V11_M", "V12_M", "V18_M", "V19_AM", "V21_M", "T_VI",
  "DECIFR", "IDECIFR", "RDECIFR", "GDECIFR", "PDECIFR", "ADECIFR", "DECCFR", "IDECCFR", "RDECCFR", "GDECCFR", "PDECCFR", "ADECCFR",
  
  # Antigüedad
  "PP05B2_ANO", "PP05B2_MES", "PP05B2_DIA", "PP05H",
  
  # Nuevas variables de informalidad (INDEC 2024+)
  "PP05I", "PP05J", "PP05K", "PP06E1", "PP07I2", "PP07I3", "PP07I4", 
  "PP05B3", "PP07L", "PP07M", 
  #informalidad del puesto y de la unidad productiva
  "Empleo", "Sector"
)

# 3.3 Variables por tipo de ocupación
vars_asalariados <- c(
  "PP07H", "PP07I", "PP07J", "PP07F1", "PP07F2", "PP07F3", "PP07F4", "PP07F5"
)

vars_cuentapropistas <- c(
  "PP06A", "PP06C", "PP06D", "PP06E", "PP06H", "PP05C_1", "PP05C_2", "PP05C_3"
)

# 3.4 Combinación final (ajustar según necesidad)
vars_necesarias <- unique(c(vars_esenciales, vars_laborales))

# Lista de variables que NO queremos importar (según tu especificación)
vars_excluir <- c(
  "H15", "MAS_500", "CH05", "CH09", "CH10", "CH11", "CH12", "CH13", "CH14", 
  "CH15", "CH16", "CH16_COD", "PP02C1", "PP02C2", "PP02C3", "PP02C4", "PP02C5", 
  "PP02C6", "PP02C7", "PP02C8", "PP02E", "PP02H", "PP02I", "PP03C", "PP03D", 
  "PP03G", "PP03H", "PP03I", "PP03J", "PP07J", "PP07K", "PP08D1", "PP08D4", 
  "PP08F1", "PP08F2", "PP08J1", "PP08J2", "PP08J3", "PP09A", "PP09A_ESP", 
  "PP09B", "PP09C", "PP09C_ESP", "PP10A", "PP10C", "PP10D", "PP10E", "PP11A", 
  "PP11B_COD", "PP11B1", "PP11B2_MES", "PP11B2_ANO", "PP11B2_DIA", "PP11C", 
  "PP11C99", "PP11D_COD", "PP11G_ANO", "PP11G_MES", "PP11G_DIA", "PP11L", 
  "PP11L1", "PP11M", "PP11N", "PP11O", "PP11P", "PP11Q", "PP11R", "PP11S", 
  "PP11T",
  # otras Puesto de trabajo, cobertura médica, servicio doméstico
  "CH08", "PP04A", "PP04B_COD", "PP04B1", "PP04B2", "PP04B3_MES", "PP04B3_ANO",
  "PP04B3_DIA", "PP04C", "PP04C99", "PP04G", "PP05C_1", "PP05C_2", "PP05C_3",
  "PP05E", "PP05F", "PP06A", "PP06C", "PP06D", "PP06E", "PP06H", "PP07C", "PP07D",
  "PP07E", "PP07F1", "PP07F2", "PP07F3", "PP07F4", "PP07F5", "PP07G1", "PP07G2",
  "PP07G3", "PP07G4", "PP07G_59"
)

# 4. FUNCIONES AUXILIARES MEJORADAS -----------------------------------------
actualizar_variables <- function(agregar = NULL, quitar = NULL) {
  vars_necesarias <<- union(setdiff(vars_necesarias, quitar), agregar)
  message("Variables actualizadas. Total: ", length(vars_necesarias), " variables")
}

filtrar_variables <- function(df) {
  # Filtrar variables excluidas y mantener solo las necesarias
  vars_mantener <- setdiff(names(df), vars_excluir)
  vars_final <- intersect(vars_mantener, vars_necesarias)
  df %>% select(all_of(vars_final))
}

limpiar_memoria <- function() {
  invisible(gc(verbose = FALSE, full = TRUE))
  if ("disk.frame" %in% installed.packages()) {
    disk.frame::delete_all_disk_frames()
  }
}

# 5. CONFIGURACIÓN VISUAL Y DE REPORTES --------------------------------------
theme_custom <- theme_minimal(base_size = 12) +
  theme(
    panel.grid.minor = element_blank(),
    legend.position = "bottom",
    plot.title = element_text(face = "bold", hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5)
  )

theme_set(theme_custom)

options(
  scipen = 999,
  dplyr.summarise.inform = FALSE,
  stringsAsFactors = FALSE
)

# 6. MENSAJE INICIAL --------------------------------------------------------
message("\n✅ Configuración lista para análisis EPH 2014-2024")
message("📌 Variables esenciales: ", length(vars_esenciales))
message("📌 Variables laborales: ", length(vars_laborales))
message("📌 Variables excluidas: ", length(vars_excluir))
message("📌 Variables necesarias: ", length(vars_necesarias))
message("📌 Directorios configurados: ", paste(dirs, collapse = ", "))
message("📌 Paquetes cargados: ", length(required_packages), "\n")
message("📌 Directorios verificados:")
message("- Datos originales: data/raw")
message("- Datos procesados: data/processed")
message("- Resultados: output/")
message("\nPaquetes cargados correctamente. Conflictos de funciones resueltos.")
# 7. EJEMPLOS DE USO (descomentar si es necesario) ---------------------------

# Ejemplo 1: Agregar variables de salud
# actualizar_variables(agregar = c("CH08", "CH09"))

# Ejemplo 2: Quitar variables de ingresos detallados
# actualizar_variables(quitar = c("V2_M", "V3_M", "V4_M"))

# Ejemplo 3: Configurar para análisis de asalariados
# vars_necesarias <- unique(c(vars_esenciales, vars_laborales, vars_asalariados))