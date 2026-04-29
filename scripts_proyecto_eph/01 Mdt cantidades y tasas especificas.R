# Seleccionar solo 2 trimestres
sub_base <- base_nucleo %>%
  filter(anio_trim %in% c("2014T4", "2024T4"))
library(skimr)
skim(sub_base)
library(funModeling)

df_status(sub_base)   # resumen de variables (tipos, %NAs, cardinalidad)
df_summary(sub_base)  # estadísticas descriptivas rápidas

library(summarytools)
dfSummary(sub_base)



calcular_tasas <- function(df) {
  df %>% 
    summarise(
      Poblacion         = sum(PONDERA, na.rm = TRUE),
      Ocupados          = sum(PONDERA[ESTADO == 1], na.rm = TRUE),
      Desocupados       = sum(PONDERA[ESTADO == 2], na.rm = TRUE),
      PEA               = Ocupados + Desocupados,
      Ocupados_demand   = sum(PONDERA[ESTADO == 1 & PP03J == 1], na.rm = TRUE),
      Suboc_demandante  = sum(PONDERA[ESTADO == 1 & INTENSI == 1 & PP03J == 1], na.rm = TRUE),
      Suboc_no_demand   = sum(PONDERA[ESTADO == 1 & INTENSI == 1 & PP03J %in% c(2,9)], na.rm = TRUE),
      Subocupados       = Suboc_demandante + Suboc_no_demand,
      Informales        = sum(PONDERA[(CAT_OCUP==3 & PP07H==2) | (CAT_OCUP==2 & PP07I==2)], na.rm=TRUE),
      .groups = "drop"
    ) %>%
    mutate(
      Tasa_Actividad                = PEA / Poblacion,
      Tasa_Empleo                   = Ocupados / Poblacion,
      Tasa_Desocupacion             = Desocupados / PEA,
      Tasa_Ocupados_Demandantes     = Ocupados_demand / PEA,
      Tasa_Subocupacion             = Subocupados / PEA,
      Tasa_Subocupacion_Demandante  = Suboc_demandante / PEA,
      Tasa_Subocupacion_NoDemand    = Suboc_no_demand / PEA,
      Tasa_Informalidad             = Informales / Ocupados
    )
}

# GRAN TOTAL
tasas_mdt <- datos_completos %>%
  filter(!is.na(anio_trim)) %>%
  mutate(CH04 = "Total", rango_etario = "Total edades") %>%
  group_by(anio_trim, CH04, rango_etario) %>%
  group_modify(~ calcular_tasas(.x)) %>%
  ungroup()

# TASAS POR SEXO Y RANGO ETARIO
tasas_sexo_edad <- datos_completos %>%
  filter(!is.na(anio_trim), !is.na(rango_etario), !is.na(CH04)) %>%
  mutate(CH04 = as.character(CH04)) %>%
  group_by(anio_trim, CH04, rango_etario) %>%
  group_modify(~ calcular_tasas(.x)) %>%
  ungroup()

# TASAS POR SEXO TOTAL EDADES
tasas_sexo <- datos_completos %>%
  filter(!is.na(anio_trim), !is.na(CH04)) %>%
  mutate(CH04 = as.character(CH04)) %>%
  group_by(anio_trim, CH04) %>%
  group_modify(~ calcular_tasas(.x)) %>%
  mutate(rango_etario = "Total edades") %>%
  ungroup()

# TASAS POR RANGO ETARIO (SIN SEXO)
tasas_edad <- datos_completos %>%
  filter(!is.na(anio_trim), !is.na(rango_etario)) %>%
  mutate(CH04 = "Total") %>%
  group_by(anio_trim, CH04, rango_etario) %>%
  group_modify(~ calcular_tasas(.x)) %>%
  ungroup()

