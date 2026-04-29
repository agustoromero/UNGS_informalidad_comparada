# Análisis de tasas laborales
# --------------------------

# Función para calcular tasas (versión optimizada)
calcular_tasas <- function(df) {
  df %>%
    filter(CH06 > 14) %>%
    summarise(
      across(c(ESTADO, PP03J, INTENSI), ~sum(PONDERA * (.x %in% c(1,2)), .names = "{.col}_sum"),
             Poblacion = sum(PONDERA),
             .groups = "drop"
      ) %>%
        mutate(
          PEA = ESTADO_sum %in% 1:2,
          # ... [resto de cálculos]
        )
}

# Cálculo por grupos
calcular_tasas_grupo <- function(grupo) {
  datos_completos %>%
    group_by(anio_trim, across(any_of(grupo))) %>%
    calcular_tasas()
}

# Grupos a analizar
grupos_analisis <- list(
  c("CH04", "rango_etario"),  # Sexo y edad
  c("rango_etario"),          # Solo edad
  c("CH04"),                  # Solo sexo
  character()                 # Total
)

# Calcular todas las combinaciones
tasas_resultados <- map_dfr(grupos_analisis, calcular_tasas_grupo)