###############################################################################
# 02_descargar_datos.R - Descarga de microdatos EPH (2014-2024)
#
# Este script:
# 1. Carga la configuración de trimestres
# 2. Descarga archivos faltantes usando el paquete `eph`
# 3. Maneja errores y reinicios automáticos
# 4. Guarda metadatos del proceso
#
# Depende de: 01_definir_trimestres.R
# Output: Archivos RDS en data/original/
###############################################################################

# 1. Setup -------------------------------------------------------------------
source("scripts/00_setup.R")
source("scripts/01_definir_trimestres.R")

# 2. Configuración avanzada --------------------------------------------------

# Umbral para reintentos de descarga
MAX_INTENTOS <- 3
PAUSA_ENTRE_INTENTOS <- 5 # segundos

# 3. Función mejorada de descarga --------------------------------------------

#' Descarga segura de microdatos EPH
#'
#' @param ano Año a descargar
#' @param trimestre Trimestre (1-4)
#' @param force Redescargar incluso si existe (FALSE por defecto)
#' @return TRUE si fue exitoso, FALSE si falló
descargar_trimestre <- function(ano, trimestre, force = FALSE) {
  archivo <- sprintf("data/original/individual_%dT%d.rds", ano, trimestre)
  
  # Verificar si ya existe
  if (file.exists(archivo) && !force) {
    message(sprintf("✓ [%d-T%d] Ya existe en %s", ano, trimestre, archivo))
    return(TRUE)
  }
  
  # Intentar descarga
  intento <- 1
  while (intento <= MAX_INTENTOS) {
    tryCatch({
      message(sprintf("\n⌛ [%d-T%d] Descargando (Intento %d/%d)...", 
                      ano, trimestre, intento, MAX_INTENTOS))
      
      # Usar el paquete eph con selección de variables
      microdata <- eph::get_microdata(
        year = ano,
        trimester = trimestre,
        type = "individual",
        vars = vars_necesarias,
        .quiet = FALSE
      )
      
      # Verificar estructura básica
      if (!inherits(microdata, "data.frame")) stop("Datos no son dataframe")
      if (nrow(microdata) == 0) stop("Dataframe vacío")
      
      # Guardar con compresión eficiente
      saveRDS(microdata, file = archivo, compress = "xz")
      message(sprintf("✓ [%d-T%d] Guardado en %s", ano, trimestre, archivo))
      return(TRUE)
      
    }, error = function(e) {
      message(sprintf("❌ Error en intento %d: %s", intento, e$message))
      intento <<- intento + 1
      Sys.sleep(PAUSA_ENTRE_INTENTOS) # Pausa entre intentos
      return(FALSE)
    })
  }
  
  warning(sprintf("Falló descarga de %d-T%d después de %d intentos", 
                  ano, trimestre, MAX_INTENTOS))
  return(FALSE)
}

# 4. Proceso principal -------------------------------------------------------

# Verificar configuración
if (!exists("trimestres_seleccionados")) {
  stop("No se encontró trimestres_seleccionados. Ejecutar primero 01_definir_trimestres.R")
}

# Crear directorio si no existe
dir.create("data/original", showWarnings = FALSE, recursive = TRUE)

# Descargar solo trimestres faltantes
resultados <- trimestres_seleccionados %>%
  mutate(
    descargado = purrr::pmap_int(
      list(ANO4, TRIMESTRE),
      ~ as.integer(descargar_trimestre(..1, ..2))
    )
  )

# 5. Verificación y reportes ------------------------------------------------

# Generar resumen estadístico
resumen_descarga <- resultados %>%
  summarise(
    total = n(),
    exitosas = sum(descargado, na.rm = TRUE),
    existentes = sum(file.exists(
      sprintf("data/original/individual_%dT%d.rds", ANO4, TRIMESTRE))),
    fallidas = sum(descargado == 0, na.rm = TRUE)
  )

# Mostrar resumen en consola
cat("\n🔍 Resumen de descarga:\n")
cat("-----------------------\n")
cat(sprintf("Trimestres totales:   %3d\n", resumen_descarga$total))
cat(sprintf("Descargas exitosas:   %3d\n", resumen_descarga$exitosas))
cat(sprintf("Archivos existentes:  %3d\n", resumen_descarga$existentes))
cat(sprintf("Fallidas/omitidas:    %3d\n", resumen_descarga$fallidas))

# Guardar log detallado
if (!dir.exists("config")) dir.create("config", recursive = TRUE)

log_descarga <- resultados %>%
  mutate(
    ruta = sprintf("data/original/individual_%dT%d.rds", ANO4, TRIMESTRE),
    tamano_MB = ifelse(file.exists(ruta), round(file.size(ruta)/1024/1024, 2), NA)
  )

write_csv(log_descarga, "config/log_descarga_eph.csv")

message("\n✅ Script 02_descargar_datos.R ejecutado correctamente")
message("📋 Detalles guardados en: config/log_descarga_eph.csv")