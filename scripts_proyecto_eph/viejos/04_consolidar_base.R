###############################################################################
# 04_consolidar_base.R - Consolidación y etiquetado de datos EPH
# 
# Inputs:
# - Archivos trimestrales en data/procesada/base_completa.rds (generado por 03_importar_procesar.R)
# 
# Outputs:
# - Base consolidada con etiquetas en data/procesada/base_final.rds
# - Registro de variables generadas en config/log_variables.csv
###############################################################################

source("scripts/00_setup.R")

# --- 1. Función de etiquetado mejorada ---
etiquetar_base <- function(base) {
  tryCatch({
    message("Aplicando etiquetas EPH...")
    base %>%
      eph::organize_labels(type = "individual") %>%
      eph::organize_caes() %>%
      eph::organize_cno()
  }, error = function(e) {
    message("Error en etiquetado automático: ", e$message)
    message("Aplicando etiquetado básico...")
    
    base %>%
      mutate(
        ESTADO = factor(ESTADO, 
                        levels = c(1, 2, 3),
                        labels = c("Ocupado", "Desocupado", "Inactivo")),
        CAT_OCUP = factor(CAT_OCUP,
                          levels = c(1, 2, 3, 4),
                          labels = c("Patrón", "Cuenta propia", "Asalariado", "Otro"))
      )
  })
}

# --- 2. Generación de variables ---
generar_variables <- function(base) {
  message("Creando variables derivadas...")
  
  base %>%
    mutate(
      rango_etario = cut(
        CH06,
        breaks = c(0, 18, 30, 45, 60, Inf),
        labels = c("<19", "19-30", "31-45", "46-60", "60+"),
        right = FALSE
      ),
      nivel_ed = factor(
        case_when(
          NIVEL_ED %in% c(1, 2, 3, 7) ~ "Menor a Secundaria",
          NIVEL_ED == 4 ~ "Secundaria Completa",
          NIVEL_ED == 5 ~ "Superior Incompleto",
          NIVEL_ED == 6 ~ "Superior Completo",
          TRUE ~ "Ns/Nr"
        ),
        levels = c("Menor a Secundaria", "Secundaria Completa", 
                   "Superior Incompleto", "Superior Completo", "Ns/Nr")
      ),
      periodo = zoo::as.yearqtr(anio_trim, format = "%YT%q")  # Usando zoo::
    )
}

# --- 3. Proceso principal ---
message("\n[1/3] Cargando datos procesados...")
datos_completos <- readRDS("data/procesada/base_completa.rds")

message("[2/3] Aplicando etiquetas...")
datos_completos <- etiquetar_base(datos_completos)

message("[3/3] Generando variables...")
datos_completos <- generar_variables(datos_completos)

# --- 4. Guardado y limpieza ---
saveRDS(datos_completos, "data/procesada/base_final.rds")



message("\n✅ Proceso completado exitosamente!")
message("📊 Resumen final:")