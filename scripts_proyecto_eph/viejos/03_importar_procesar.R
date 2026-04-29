###############################################################################
# 03_importar_procesar.R - Importación y procesamiento inicial de datos EPH
#
# Este script:
# 1. Importa los archivos RDS descargados
# 2. Aplica filtros y selección de variables
# 3. Realiza transformaciones iniciales
# 4. Guarda datos procesados
#
# Modos de uso:
# - Ejecución normal: Procesa todos los trimestres
# - Procesamiento por lotes: Para evitar sobrecarga de memoria
###############################################################################

# 1. Cargar configuración ----------------------------------------------------
source("scripts/00_setup.R")

# Validacion de variables:
vars_faltantes <- setdiff(vars_esenciales, names(datos))
if (length(vars_faltantes) > 0) {
  warning("Variables faltantes: ", paste(vars_faltantes, collapse = ", "))
}
# 1. Definición de tipos de variables -----------------------------------------
tipos_variables <- list(
  # Variables críticas que han causado problemas
  CH05 = "character",       # Parentesco
  PP04D_COD = "character",  # Código ocupación
  CODUSU = "character",     # ID del hogar
  AGLOMERADO = "integer",   # Código de aglomerado
  
  # Variables numéricas
  P21 = "numeric",          # Ingreso principal
  PP06C = "numeric",        # Ingreso cuenta propia
  PP06D = "numeric",        # Ingreso otras actividades
  
  # Variables categóricas
  ESTADO = "integer",       # Condición de actividad
  CAT_OCUP = "integer",     # Categoría ocupacional
  NIVEL_ED = "integer"      # Nivel educativo
)

# 2. Función mejorada de importación -----------------------------------------
importar_archivo <- function(archivo) {
  tryCatch({
    message("Procesando: ", basename(archivo))
    
    # Leer archivo
    datos <- readRDS(archivo)
    
    # Verificar variables disponibles
    vars_disponibles <- intersect(names(datos), c(vars_necesarias, names(tipos_variables)))
    
    # Seleccionar y convertir variables
    datos_procesados <- datos %>%
      select(all_of(vars_disponibles)) %>%
      mutate(
        across(
          .cols = any_of(names(tipos_variables)),
          .fns = ~ {
            tipo_deseado <- tipos_variables[[cur_column()]]
            switch(tipo_deseado,
                   "character" = as.character(.x),
                   "numeric" = as.numeric(.x),
                   "integer" = as.integer(.x),
                   .x) # Mantener original si no está en la lista
          },
          .names = "{.col}"
        ),
        anio_trim = str_extract(basename(archivo), "(?<=base_)\\d+_T\\d+"),
        .before = 1
      )
    
    # Verificación post-conversión
    problemas <- map_lgl(names(tipos_variables), ~ {
      if (.x %in% names(datos_procesados)) {
        !inherits(datos_procesados[[.x]], tipos_variables[[.x]])
      } else {
        FALSE
      }
    })
    
    if (any(problemas)) {
      vars_problema <- names(tipos_variables)[problemas]
      warning("Problemas de tipo en: ", paste(vars_problema, collapse = ", "))
    }
    
    datos_procesados
    
  }, error = function(e) {
    warning("Error procesando ", basename(archivo), ": ", e$message)
    return(NULL)
  })
}

# 3. Procesamiento por lotes seguro ------------------------------------------

archivos_descargados <- list.files(
  path = "data/original",
  pattern = "^base_\\d+_T\\d+\\.rds$",
  full.names = TRUE
)

# Procesar en lotes pequeños con verificación
lotes <- split(archivos_descargados, ceiling(seq_along(archivos_descargados)/3))

resultados <- map(lotes, function(lote) {
  message("\nProcesando lote de ", length(lote), " archivos...")
  
  # Procesar cada archivo individualmente
  datos_lote <- map(lote, function(archivo) {
    datos <- importar_archivo(archivo)
    
    # Guardar temporalmente para liberar memoria
    if (!is.null(datos)) {
      temp_file <- tempfile(fileext = ".rds")
      saveRDS(datos, temp_file)
      return(temp_file)
    }
    return(NULL)
  })
  
  # Filtrar archivos válidos
  datos_lote[!sapply(datos_lote, is.null)]
})

# 4. Combinación final con verificación --------------------------------------

# Combinar solo archivos válidos
archivos_validos <- unlist(resultados)
datos_completos <- map_dfr(archivos_validos, ~ {
  datos <- readRDS(.x)
  
  # Verificación final de tipos
  map(names(tipos_variables), ~ {
    if (.x %in% names(datos) && !inherits(datos[[.x]], tipos_variables[[.x]])) {
      datos[[.x]] <<- do.call(paste0("as.", tipos_variables[[.x]]), list(datos[[.x]]))
    }
  })
  
  datos
})

# 5. Guardado de resultados --------------------------------------------------

dir.create("data/procesada", showWarnings = FALSE, recursive = TRUE)
saveRDS(datos_completos, "data/procesada/base_completa.rds", compress = "xz")

# Limpieza de archivos temporales
map(archivos_validos, unlink)

# Resumen final
message("\nProceso completado exitosamente!")
message("Total archivos procesados: ", length(archivos_descargados))
message("Total registros finales: ", format(nrow(datos_completos), big.mark = ","))
message("Variables en dataset final: ", paste(names(datos_completos), collapse = ", "))