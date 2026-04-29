#=========================================
# BRASIL - PNADC
# ESTRUCTURA OCUPACIONAL
# 4 trimestres + anual
# % y cantidades
#=========================================

library(PNADcIBGE)
library(dplyr)
library(tidyr)
library(purrr)

#-----------------------------------------
# 1. PARAMETROS
#-----------------------------------------

anios <- c(2012, 2018, 2023)  # PNADC empieza en 2012
trimestres <- 1:4

#-----------------------------------------
# 2. DESCARGA
#-----------------------------------------

datos <- purrr::map_dfr(anios, function(a){
  
  get_pnadc(year = a, quarter = 1:4,
            vars = c(
              "VD4002",  # posición ocupacional
              "VD4009",  # formalidad
              "VD3004",  # educación
              "VD4016",  # tamaño establecimiento
              "VD4001",  # ocupado
              "V1028"    # peso
            ),
            design = FALSE) %>%
    mutate(anio = a)
  
})

#-----------------------------------------
# 3. VARIABLES BASE
#-----------------------------------------

datos <- datos %>%
  mutate(
    ocupado = if_else(VD4001 == 1, 1, 0),
    
    # posición ocupacional
    asal = if_else(VD4002 == 1, 1, 0),
    cuentapropia = if_else(VD4002 == 2, 1, 0),
    empleador = if_else(VD4002 == 3, 1, 0),
    familiar = if_else(VD4002 == 4, 1, 0),
    
    # formalidad (clave en Brasil)
    formal = if_else(VD4009 == 1, 1, 0),
    
    # tamaño
    tam = case_when(
      VD4016 <= 5 ~ 1,
      VD4016 %in% 6:10 ~ 2,
      VD4016 > 10 ~ 3,
      TRUE ~ NA_real_
    )
  )

#-----------------------------------------
# 4. EDUCACION (proxy profesional)
#-----------------------------------------

datos <- datos %>%
  mutate(
    educ = case_when(
      VD3004 >= 5 ~ 3,   # superior
      VD3004 >= 3 ~ 2,   # medio
      TRUE ~ 1
    ),
    
    cuentaprop_prof = if_else(cuentapropia == 1 & educ == 3, 1, 0),
    cuentaprop_noprof = if_else(cuentapropia == 1 & educ != 3, 1, 0)
  )

#-----------------------------------------
# 5. CATEGORIA OCUPACIONAL
#-----------------------------------------

datos <- datos %>%
  mutate(
    categoria = case_when(
      
      ocupado != 1 ~ NA_character_,
      
      # doméstico (aprox)
      VD4002 == 5 ~ "Empleo doméstico",
      
      cuentaprop_prof == 1 ~ "Autónomos profesionales",
      
      asal == 1 & formal == 1 ~ "Asalariados Privados",
      
      asal == 1 & formal == 0 & tam == 1 ~ "Asalariados Privados (Micro)",
      
      empleador == 1 & tam %in% c(2,3) ~ "Patrones",
      
      empleador == 1 & tam == 1 ~ "Patrones (Micro)",
      
      cuentaprop_noprof == 1 ~ "Autónomos no profesionales",
      
      familiar == 1 ~ "Trabajo Familiar",
      
      TRUE ~ NA_character_
    )
  )

#-----------------------------------------
# 6. SECTOR FORMAL / INFORMAL
#-----------------------------------------

datos <- datos %>%
  mutate(
    sector_agregado = case_when(
      
      categoria %in% c(
        "Autónomos profesionales",
        "Asalariados Privados",
        "Patrones"
      ) & formal == 1 ~ "Sector Formal",
      
      TRUE ~ "Sector Informal"
    )
  )

base <- datos %>%
  filter(ocupado == 1, !is.na(categoria))

#-----------------------------------------
# 7. FUNCION TABLA (%)
#-----------------------------------------

armar_tabla <- function(data, valor){
  
  tabla_trim <- data %>%
    group_by(anio, Quarter, categoria) %>%
    summarise(valor = sum({{valor}}, na.rm = TRUE), .groups = "drop") %>%
    group_by(anio, Quarter) %>%
    mutate(valor = valor / sum(valor)) %>%
    ungroup() %>%
    mutate(periodo = paste0(anio, "_T", Quarter)) %>%
    select(periodo, categoria, valor)
  
  tabla_anual <- data %>%
    group_by(anio, categoria) %>%
    summarise(valor = sum({{valor}}, na.rm = TRUE), .groups = "drop") %>%
    group_by(anio) %>%
    mutate(valor = valor / sum(valor)) %>%
    ungroup() %>%
    mutate(periodo = paste0(anio, "_Anual")) %>%
    select(periodo, categoria, valor)
  
  bind_rows(tabla_trim, tabla_anual) %>%
    pivot_wider(names_from = periodo, values_from = valor)
}

#-----------------------------------------
# 8. TABLAS
#-----------------------------------------

tabla_pct <- armar_tabla(base, V1028)

tabla_cant <- base %>%
  group_by(anio, Quarter, categoria) %>%
  summarise(valor = sum(V1028), .groups = "drop") %>%
  mutate(periodo = paste0(anio, "_T", Quarter)) %>%
  select(periodo, categoria, valor) %>%
  bind_rows(
    base %>%
      group_by(anio, categoria) %>%
      summarise(valor = sum(V1028), .groups = "drop") %>%
      mutate(periodo = paste0(anio, "_Anual")) %>%
      select(periodo, categoria, valor)
  ) %>%
  pivot_wider(names_from = periodo, values_from = valor)

#-----------------------------------------
# RESULTADOS
#-----------------------------------------

print(tabla_pct)
print(tabla_cant)
