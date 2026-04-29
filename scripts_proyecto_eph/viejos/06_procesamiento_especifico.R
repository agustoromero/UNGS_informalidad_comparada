###############################################################################
# 06_procesamiento_especifico.R - Transformaciones por grupo
#
# Inputs:
#   - data/procesada/asalariados.rds
#   - data/procesada/cuenta_propia.rds
# Outputs:
#   - data/procesada/asalariados_proc.rds
#   - data/procesada/cuenta_propia_proc.rds
###############################################################################

# --- 1. Setup ---
source("scripts/00_setup.R")

# --- 2. Funciones de procesamiento ---

#' Procesamiento avanzado de asalariados
procesar_asalariados <- function(base) {
  message("Procesando asalariados...")
  
  base %>%
    mutate( # Variable de registro laboral completa
      registro_formal = case_when(
        PP07H == 1 ~ "Registrado",
        PP07H == 2 ~ "No registrado",
        TRUE ~ "No especificado"
      ),
      
      # Tipo de contrato detallado
      tipo_contrato = case_when(
        PP07J == 1 ~ "Temporal",
        PP07J == 2 ~ "Permanente",
        PP07J == 9 ~ "No especificado",
        TRUE ~ "No aplica"
      ),
      
      # Tamaño de empresa con categorías EPH
      tamaño_empresa = case_when(
        PP04C %in% 1:6 ~ "1-5 empleados",
        PP04C %in% 7:8 ~ "6-40 empleados",
        PP04C %in% 9:12 ~ "41-200 empleados",
        PP04C99 == 4 ~ "201+ empleados",
        TRUE ~ "No especificado"
      ),
      # Clasificación por calificación y tamaño
      perfil_ocupacional = interaction(
        case_when(
          str_sub(PP04D_COD, 5, 5) == "1" ~ "Profesional",
          str_sub(PP04D_COD, 5, 5) == "2" ~ "Técnico",
          str_sub(PP04D_COD, 5, 5) == "3" ~ "Operativo",
          str_sub(PP04D_COD, 5, 5) == "4" ~ "No calificado",
          TRUE ~ "Sin clasif."
        ),
        case_when(
          PP04C %in% 1:6 ~ "Pequeña",
          PP04C %in% 7:8 ~ "Mediana",
          PP04C %in% 9:12 ~ "Grande",
          TRUE ~ "Sin dato"
        ),
        sep = " - "
      ),
      
      # Antigüedad categorizada
      antiguedad_cat = cut(
        as.numeric(antiguedad_empleo),
        breaks = c(0, 1, 3, 5, 10, Inf),
        labels = c("<1 año", "1-3 años", "3-5 años", "5-10 años", "10+ años"),
        right = FALSE
      ),
      
      # Ingreso real (ajustado)
      ingreso_real = P21 / indice_precios * 100  # Asumiendo que existe índice
    )
}

#' Procesamiento avanzado de cuentapropistas
procesar_cuenta_propia <- function(base) {
  message("Procesando cuentapropistas...")
  
  base %>%
    mutate(
      # Nivel de calificación
      calificacion = factor(
        CALIFICACION,
        levels = 1:4,
        labels = c("Profesional", "Técnico", "Operativo", "No calificado")
      ),
      
      # Sector de actividad (simplificado)
      sector = case_when(
        str_sub(PP04B_COD, 1, 1) %in% c("A", "B") ~ "Agropecuario",
        str_sub(PP04B_COD, 1, 1) %in% c("C", "D", "E") ~ "Industrial",
        str_sub(PP04B_COD, 1, 1) %in% c("G", "H", "I") ~ "Comercio",
        str_sub(PP04B_COD, 1, 1) %in% c("J", "K", "L") ~ "Servicios",
        TRUE ~ "Otros"
      )
    )
}

# --- 3. Carga y procesamiento ---
message("Cargando subconjuntos base...")
asalariados <- readRDS("data/procesada/asalariados.rds")
cuenta_propia <- readRDS("data/procesada/cuenta_propia.rds")

# Procesar cada grupo
asalariados_proc <- procesar_asalariados(asalariados)
cuenta_propia_proc <- procesar_cuenta_propia(cuenta_propia)

# --- 4. Guardado ---
message("\nGuardando resultados procesados...")
saveRDS(asalariados_proc, "data/procesada/asalariados_proc.rds")
saveRDS(cuenta_propia_proc, "data/procesada/cuenta_propia_proc.rds")

# Limpieza
rm(list = ls())
gc()

message("\n✅ Procesamiento específico completado!")
message("📊 Resultados guardados en:")
message("- data/procesada/asalariados_proc.rds")
message("- data/procesada/cuenta_propia_proc.rds")