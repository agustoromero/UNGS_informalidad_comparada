##tablas generales
# ===============================
# 1. Filtrar dos trimestres clave
# ===============================
base_comp <- base_nucleo %>%
  filter(anio_trim %in% c("2014T3", "2024T3"))

# Función de cantidades + tasas generales
calcular_tasas <- function(df) {
  df %>%
    filter(CH06 > 14) %>%  # mayores de 14
    summarise(
      Poblacion         = sum(PONDERA, na.rm = TRUE),
      Ocupados          = sum(PONDERA[ESTADO == 1], na.rm = TRUE),
      Desocupados       = sum(PONDERA[ESTADO == 2], na.rm = TRUE),
      PEA               = Ocupados + Desocupados,
      Ocupados_demand   = sum(PONDERA[ESTADO == 1 & PP03J == 1], na.rm = TRUE),
      Suboc_demandante  = sum(PONDERA[ESTADO == 1 & INTENSI == 1 & PP03J == 1], na.rm = TRUE),
      Suboc_no_demand   = sum(PONDERA[ESTADO == 1 & INTENSI == 1 & PP03J %in% c(2,9)], na.rm = TRUE),
      Subocupados       = Suboc_demandante + Suboc_no_demand,
      .groups = "drop"
    ) %>%
    mutate(
      Tasa_Actividad                = PEA / Poblacion,
      Tasa_Empleo                   = Ocupados / Poblacion,
      Tasa_Desocupacion             = Desocupados / PEA,
      Tasa_Ocupados_Demandantes     = Ocupados_demand / PEA,
      Tasa_Subocupacion             = Subocupados / PEA,
      Tasa_Subocupacion_Demandante  = Suboc_demandante / PEA,
      Tasa_Subocupacion_NoDemand    = Suboc_no_demand / PEA
    )
}

# ===============================
# Totales generales 
# ===============================
tasas_generales <- base_comp %>%
  group_by(anio_trim) %>%
  group_modify(~ calcular_tasas(.x)) %>%
  ungroup()

tasas_generales


# ===============================
# Tres tablas de 12 columnas (2 trimestres × 6 categorías) 
# ===============================

base_comp_cat <- base_comp %>%
  mutate(
    categoria6 = case_when(
      ESTADO == 1 & CAT_OCUP == 3 & PP07H == 1 ~ "Asalariado registrado",
      ESTADO == 1 & CAT_OCUP == 3 & PP07H == 2 ~ "Asalariado no registrado",
      ESTADO == 1 & CAT_OCUP == 2 & PP07I == 1 ~ "Cuenta propia registrado",
      ESTADO == 1 & CAT_OCUP == 2 & PP07I == 2 ~ "Cuenta propia no registrado",
      ESTADO == 2 ~ "Desocupado",
      ESTADO == 3 ~ "Inactivo",
      TRUE ~ NA_character_
    )
  ) %>%
  filter(!is.na(categoria6))


# ===============================
#  tabla de cantidades
# ===============================

tabla_proporciones <- base_comp_cat %>%
  group_by(anio_trim) %>%
  mutate(personas = PONDERA / sum(PONDERA, na.rm = TRUE)) %>%
  group_by(anio_trim, categoria6) %>%
  summarise(prop = sum(personas, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(names_from = c(anio_trim, categoria6),
              values_from = prop)

# ===============================
#  tabla de proporciones (por fila=100)
# ===============================

tabla_proporciones <- base_comp_cat %>%
  group_by(anio_trim) %>%
  mutate(personas = PONDERA / sum(PONDERA, na.rm = TRUE)) %>%
  group_by(anio_trim, categoria6) %>%
  summarise(prop = sum(personas, na.rm = TRUE), .groups = "drop") %>%
  pivot_wider(names_from = c(anio_trim, categoria6),
              values_from = prop)

# ===============================
#  tabla de tasas específicas (estilo INDEC)
# ===============================

tabla_tasas_especificas <- base_comp_cat %>%
  group_by(anio_trim, categoria6) %>%
  summarise(
    Poblacion   = sum(PONDERA, na.rm = TRUE),
    Ocupados    = sum(PONDERA[ESTADO == 1], na.rm = TRUE),
    Desocupados = sum(PONDERA[ESTADO == 2], na.rm = TRUE),
    PEA         = Ocupados + Desocupados,
    .groups = "drop"
  ) %>%
  mutate(
    Tasa_Actividad    = PEA / Poblacion,
    Tasa_Empleo       = Ocupados / Poblacion,
    Tasa_Desocupacion = Desocupados / PEA
  ) %>%
  pivot_wider(names_from = c(anio_trim, categoria6),
              values_from = c(Tasa_Actividad, Tasa_Empleo, Tasa_Desocupacion))
