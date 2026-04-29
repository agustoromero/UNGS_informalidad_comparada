###############################################################################
# 01_definir_trimestres.R - Gestión de períodos de análisis EPH 2014-2024
#
# Este script:
# 1. Define los trimestres a incluir (2014-2024 por defecto)
# 2. Proporciona funciones para gestión flexible de períodos
# 3. Guarda configuración en /config/trimestres_seleccionados.csv
#
# Depende de: 00_setup.R
# Crea: trimestres_seleccionados (dataframe con ANO4, TRIMESTRE, anio_trim, fecha)
###############################################################################
###############################################################################
# 01_definir_trimestres.R - Versión definitiva funcionando
###############################################################################


# 1. Cargar configuración inicial ---------------------------------------------
suppressMessages({
  source("scripts/00_setup.R")
  # Resolver conflicto específico para between()
  conflict_prefer("between", "dplyr")
})

# 2. Definición básica de períodos --------------------------------------------

# Rango completo del proyecto (2014-2024)
anos_proyecto <- 2014:2024

# Trimestres base (todos los posibles en el período)
trimestres_base <- expand.grid(
  ANO4 = anos_proyecto,
  TRIMESTRE = 1:4,
  stringsAsFactors = FALSE
) %>% 
  as_tibble()

# 3. Configuración por defecto -----------------------------------------------

# Detección del último trimestre disponible (usando dplyr::between explícitamente)
ultimo_trimestre_disponible <- case_when(
  dplyr::between(lubridate::month(Sys.Date()), 1, 3) ~ 4,    # Q1 -> Q4 año anterior
  dplyr::between(lubridate::month(Sys.Date()), 4, 6) ~ 1,    # Q2 -> Q1 disponible
  dplyr::between(lubridate::month(Sys.Date()), 7, 9) ~ 2,    # Q3 -> Q2 disponible
  TRUE ~ 3                                           # Q4 -> Q3 disponible
)

# 4. Creación del dataframe con fechas ---------------------------------------

trimestres_seleccionados <- trimestres_base %>%
  filter(
    (ANO4 < lubridate::year(Sys.Date())) |       # Todos los años anteriores
      (ANO4 == lubridate::year(Sys.Date()) & TRIMESTRE <= ultimo_trimestre_disponible) # Año actual
  ) %>%
  arrange(ANO4, TRIMESTRE) %>%
  mutate(
    anio_trim = paste0(ANO4, "T", TRIMESTRE),
    # Creación robusta de fechas (asegurando formato Date)
    fecha = as.Date(
      case_when(
        TRIMESTRE == 1 ~ paste0(ANO4, "-01-01"),
        TRIMESTRE == 2 ~ paste0(ANO4, "-04-01"),
        TRIMESTRE == 3 ~ paste0(ANO4, "-07-01"),
        TRIMESTRE == 4 ~ paste0(ANO4, "-10-01"),
        TRUE ~ NA_character_
      )
    ),
    etiqueta = paste0(ANO4, "-Q", TRIMESTRE),
    periodo_num = ANO4 + (TRIMESTRE-1)/4
  ) %>%
  # Asegurar que no haya fechas NA
  filter(!is.na(fecha))

# 5. Función de visualización mejorada ---------------------------------------

visualizar_trimestres <- function() {
  # Verificar que las columnas necesarias existen
  required_cols <- c("ANO4", "TRIMESTRE", "anio_trim", "fecha")
  if (!all(required_cols %in% names(trimestres_seleccionados))) {
    stop("Faltan columnas esenciales en el dataframe")
  }
  
  cat("\nTrimestres actualmente seleccionados (primeras filas):\n")
  print(head(trimestres_seleccionados))
  
  cat("\nResumen temporal:\n")
  cat("- Año inicial:", min(trimestres_seleccionados$ANO4), "\n")
  cat("- Año final:", max(trimestres_seleccionados$ANO4), "\n")
  cat("- Total trimestres:", nrow(trimestres_seleccionados), "\n")
  cat("- Último trimestre incluido:", max(trimestres_seleccionados$anio_trim), "\n")
  
  # Mostrar fechas solo si existen
  if ("fecha" %in% names(trimestres_seleccionados)) {
    if (length(trimestres_seleccionados$fecha) > 0) {
      cat("- Fecha más temprana:", format(min(trimestres_seleccionados$fecha), "%Y-%m-%d"), "\n")
      cat("- Fecha más reciente:", format(max(trimestres_seleccionados$fecha), "%Y-%m-%d"), "\n")
    }
  }
}

# 6. Exportar configuración robusta ------------------------------------------

if (!dir.exists("config")) {
  dir.create("config", recursive = TRUE)
}

tryCatch({
  readr::write_csv(trimestres_seleccionados, "config/trimestres_seleccionados.csv")
  message("\n✅ Configuración guardada en CSV")
}, error = function(e) {
  saveRDS(trimestres_seleccionados, "config/trimestres_seleccionados.rds")
  message("\n✅ Configuración guardada en RDS (falló CSV)")
})

# 7. Verificación final -----------------------------------------------------

# Verificación de estructura
stopifnot(
  "fecha" %in% names(trimestres_seleccionados),
  class(trimestres_seleccionados$fecha) == "Date",
  !any(is.na(trimestres_seleccionados$fecha))
)

# Mostrar resultados
visualizar_trimestres()
message("\n✅ Script ejecutado correctamente. Todas las fechas creadas adecuadamente.")
# 8. Ejemplos de uso (descomentar si se necesitan) ---------------------------

# EJEMPLO 1: Analizar solo los segundos trimestres
# actualizar_trimestres(trimestres = 2)

# EJEMPLO 2: Analizar solo 2018-2020
# actualizar_trimestres(anos = 2018:2020)

# EJEMPLO 3: Excluir trimestres específicos
# exclusiones <- data.frame(ANO4 = c(2020, 2020), TRIMESTRE = c(2, 3))
# actualizar_trimestres(exclusiones = exclusiones)

# EJEMPLO 4: Forzar inclusión del último trimestre disponible (aunque no esté publicado)
# actualizar_trimestres(force_actual = TRUE)
