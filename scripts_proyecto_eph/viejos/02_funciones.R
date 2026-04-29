# ===============================================
# 02_funciones_utiles.R
# Funciones auxiliares reutilizables
# ===============================================

library(dplyr)
library(stringr)
library(ggplot2)
library(glue)

# 📊 Calcular tasas básicas
calcular_tasas <- function(df) {
  df %>%
    filter(CH06 > 14, is.na(CAT_INAC)) %>%  # Excluir jubilados/pensionados
    summarise(
      PEA         = sum((ESTADO %in% c(1, 2)) * PONDERA, na.rm = TRUE),
      Ocupados    = sum((ESTADO == 1) * PONDERA, na.rm = TRUE),
      Desocupados = sum((ESTADO == 2) * PONDERA, na.rm = TRUE),
      Inactivos   = sum((ESTADO == 3) * PONDERA, na.rm = TRUE),
      Total       = sum(PONDERA, na.rm = TRUE)
    ) %>%
    mutate(
      Tasa_actividad    = 100 * PEA / Total,
      Tasa_empleo       = 100 * Ocupados / Total,
      Tasa_desocupacion = 100 * Desocupados / PEA,
      Tasa_inactividad  = 100 * Inactivos / Total
    )
}

# 🧮 Cuadro resumen asalariados
cuadro_perfiles_asalariados <- function(df) {
  df %>%
    group_by(anio_trim, grupos.calif, registrado) %>%
    summarise(
      ingreso_medio = weighted.mean(P21, PONDERA, na.rm = TRUE),
      n             = sum(PONDERA, na.rm = TRUE),
      .groups = "drop"
    )
}

# 💰 Calcular IPC trimestral base 100
calcular_ipc_trimestral <- function(ipc_mensual, base = "2016T1") {
  ipc_mensual <- ipc_mensual %>%
    mutate(fecha = as.Date(paste0(anio, "-", mes, "-01"))) %>%
    arrange(fecha) %>%
    mutate(indice_base = valor / valor[glue("{anio[1]}T{mes[1]}") == base] * 100)
  
  ipc_mensual %>%
    mutate(anio_trim = paste0(anio, "T", ceiling(mes / 3))) %>%
    group_by(anio_trim) %>%
    summarise(ipc_trim = mean(indice_base, na.rm = TRUE), .groups = "drop")
}

# 🧹 Filtro etario personalizado
crear_rango_etario <- function(edad) {
  case_when(
    edad < 19 ~ "Menor a 19",
    eda
    