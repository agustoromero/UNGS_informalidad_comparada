###############################################################################
# 05_filtrar_grupos.R - Creación de subconjuntos clave
#
# Input: data/procesada/base_final.rds
# Outputs: 
#   - data/procesada/ocupados.rds
#   - data/procesada/asalariados.rds
#   - data/procesada/cuenta_propia.rds
###############################################################################

# --- 1. Setup ---
source("scripts/00_setup.R")

# Verificar si existe la base final
if (!file.exists("data/procesada/base_final.rds")) {
  stop("Ejecutar primero 04_consolidar_base.R")
}

# --- 2. Funciones de filtrado ---

#' Filtrar población ocupada
filtrar_ocupados <- function(base) {
  base %>%
    filter(ESTADO == "Ocupado") %>%
    mutate(
      condicion_actividad = "Ocupado",
      tipo_empleo = case_when(
        CAT_OCUP == "Asalariado" ~ "Asalariado",
        CAT_OCUP == "Cuenta propia" ~ "Cuenta propia",
        CAT_OCUP == "Patrón" ~ "Patrón",
        TRUE ~ "Otro"
      )
    )
}

#' Filtrar asalariados con limpieza
filtrar_asalariados <- function(base) {
  base %>%
    filter(CAT_OCUP == "Asalariado", !is.na(P21), P21 > 0) %>%
    mutate(
      tipo_empleo = "Asalariado",
      # Variables específicas para asalariados
      registro_laboral = ifelse(PP07H == 1, "Registrado", "No registrado"),
      tipo_contrato = ifelse(PP07J == 1, "Temporal", 
                             ifelse(PP07J == 2, "Permanente", NA))
    )
}

#' Filtrar cuentapropistas con limpieza
filtrar_cuenta_propia <- function(base) {
  base %>%
    filter(CAT_OCUP == "Cuenta propia", 
           (PP06C > 0 | PP06D > 0),  # Ingresos positivos
           !is.na(CALIFICACION)) %>%
    mutate(
      tipo_empleo = "Cuenta propia",
      ingreso_total = PP06C + PP06D
    )
}

# --- 3. Procesamiento principal ---
message("Cargando base final...")
datos_completos <- readRDS("data/procesada/base_final.rds")

message("\nCreando subconjuntos:")
message("- Ocupados...")
ocupados <- filtrar_ocupados(datos_completos)

message("- Asalariados...")
asalariados <- filtrar_asalariados(datos_completos)

message("- Cuentapropistas...")
cuenta_propia <- filtrar_cuenta_propia(datos_completos)

# --- 4. Guardado y limpieza ---
message("\nGuardando resultados...")
saveRDS(ocupados, "data/procesada/ocupados.rds")
saveRDS(asalariados, "data/procesada/asalariados.rds")
saveRDS(cuenta_propia, "data/procesada/cuenta_propia.rds")

# Limpieza
rm(list = setdiff(ls(), c("datos_completos")))
gc()

message("\n✅ Subconjuntos creados exitosamente!")
message("📊 Resumen:")
message("- Ocupados: ", format(nrow(ocupados), big.mark = ","))
message("- Asalariados: ", format(nrow(asalariados), big.mark = ","))
message("- Cuentapropistas: ", format(nrow(cuenta_propia), big.mark = ","))