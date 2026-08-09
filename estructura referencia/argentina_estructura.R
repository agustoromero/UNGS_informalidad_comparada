#=========================================
# ESTRUCTURA OCUPACIONAL - VERSION FINAL
# 4 trimestres + anual
# % y cantidades
#=========================================

library(dplyr)
library(tidyr)
library(purrr)
library(eph)

#-----------------------------------------
# 1. PARAMETROS
#-----------------------------------------

anios <- c(2007, 2018, 2023)
trimestres <- 1:4

grid <- expand.grid(ANO4 = anios, TRIMESTRE = trimestres)

#-----------------------------------------
# 2. DESCARGA DE DATOS
#-----------------------------------------

datos <- purrr::pmap_dfr(grid, function(ANO4, TRIMESTRE) {
  eph::get_microdata(year = ANO4, trimester = TRIMESTRE, type = "individual") %>%
    mutate(
      anio = ANO4,
      trimestre = TRIMESTRE,
      anio_trim = paste0(ANO4, "T", TRIMESTRE)
    )
})

#-----------------------------------------
# 3. VARIABLES BASE
#-----------------------------------------

datos <- datos %>%
  mutate(
    estado = ESTADO,
    cat_ocup = CAT_OCUP,
    
    asal = if_else(estado == 1 & cat_ocup == 3, 1, 0),
    cuentpro = if_else(estado == 1 & cat_ocup == 2, 1, 0),
    patron = if_else(estado == 1 & cat_ocup == 1, 1, 0),
    restocup = if_else(estado == 1 & cat_ocup == 4, 1, 0),
    
    serdom1 = if_else(estado == 1 & PP04B1 == 1, 1, 0, missing = NA_real_),
    
    sector = case_when(
      estado == 1 & PP04A == 1 ~ 1,
      estado == 1 & PP04A %in% c(2,3) ~ 0,
      TRUE ~ NA_real_
    ),
    
    tam = case_when(
      estado == 1 & (PP04C %in% 1:5 | (PP04C == 99 & PP04C99 == 1)) ~ 1,
      estado == 1 & (PP04C %in% 6:8 | (PP04C == 99 & PP04C99 == 2)) ~ 2,
      estado == 1 & (PP04C %in% 9:12 | (PP04C == 99 & PP04C99 == 3)) ~ 3,
      TRUE ~ NA_real_
    )
  )

#-----------------------------------------
# 4. EDUCACION
#-----------------------------------------

datos <- datos %>%
  mutate(
    educr = case_when(
      NIVEL_ED == 6 ~ 3,
      NIVEL_ED %in% c(4,5) ~ 2,
      NIVEL_ED %in% c(1,2,3) ~ 1,
      TRUE ~ NA_real_
    ),
    
    cuentprop_prof = if_else(cuentpro == 1 & educr == 3, 1, 0),
    cuentprop_noprof = if_else(cuentpro == 1 & educr %in% c(1,2), 1, 0)
  )

#-----------------------------------------
# 5. CATEGORIA OCUPACIONAL FINAL
#-----------------------------------------

datos <- datos %>%
  mutate(
    categoria = case_when(
      estado != 1 ~ NA_character_,
      
      serdom1 == 1 ~ "Empleo doméstico",
      
      cuentprop_prof == 1 ~ "Autónomos profesionales",
      
      asal == 1 & sector == 1 ~ "Asalariados Públicos",
      
      asal == 1 & sector == 0 & tam %in% c(2,3) ~ "Asalariados Privados",
      
      asal == 1 & sector == 0 & tam == 1 ~ "Asalariados Privados (Micro)",
      
      patron == 1 & tam %in% c(2,3) ~ "Patrones",
      
      patron == 1 & tam == 1 ~ "Patrones (Micro)",
      
      cuentprop_noprof == 1 ~ "Autónomos no profesionales",
      
      restocup == 1 ~ "Trabajo Familiar",
      
      TRUE ~ NA_character_
    )
  )

#-----------------------------------------
# 6. SECTOR AGREGADO
#-----------------------------------------

datos <- datos %>%
  mutate(
    sector_agregado = case_when(
      categoria %in% c(
        "Autónomos profesionales",
        "Asalariados Privados",
        "Asalariados Públicos",
        "Patrones"
      ) ~ "Sector Formal",
      
      categoria %in% c(
        "Patrones (Micro)",
        "Asalariados Privados (Micro)",
        "Autónomos no profesionales",
        "Trabajo Familiar",
        "Empleo doméstico"
      ) ~ "Sector Informal",
      
      TRUE ~ NA_character_
    )
  )

base <- datos %>%
  filter(estado == 1, !is.na(categoria))

#-----------------------------------------
# 7. FUNCION TABLA (% y cantidades)
#-----------------------------------------

armar_tabla <- function(data, valor){
  
  # TRIMESTRAL
  tabla_trim <- data %>%
    group_by(anio, trimestre, categoria) %>%
    summarise(valor = sum({{valor}}, na.rm = TRUE), .groups = "drop") %>%
    group_by(anio, trimestre) %>%
    mutate(valor = valor / sum(valor)) %>%
    ungroup() %>%
    mutate(periodo = paste0(anio, "_T", trimestre)) %>%
    select(periodo, categoria, valor)
  
  # ANUAL
  tabla_anual <- data %>%
    group_by(anio, categoria) %>%
    summarise(valor = sum({{valor}}, na.rm = TRUE), .groups = "drop") %>%
    group_by(anio) %>%
    mutate(valor = valor / sum(valor)) %>%
    ungroup() %>%
    mutate(periodo = paste0(anio, "_Anual")) %>%
    select(periodo, categoria, valor)
  
  # UNIR Y PIVOTEAR
  bind_rows(tabla_trim, tabla_anual) %>%
    pivot_wider(names_from = periodo, values_from = valor) %>%
    arrange(categoria)
}

#-----------------------------------------
# 8. TABLAS
#-----------------------------------------

tabla_pct <- armar_tabla(base, PONDERA)

tabla_cant <- base %>%
  group_by(anio, trimestre, categoria) %>%
  summarise(valor = sum(PONDERA), .groups = "drop") %>%
  mutate(periodo = paste0(anio, "_T", trimestre)) %>%
  select(periodo, categoria, valor) %>%
  bind_rows(
    base %>%
      group_by(anio, categoria) %>%
      summarise(valor = sum(PONDERA), .groups = "drop") %>%
      mutate(periodo = paste0(anio, "_Anual")) %>%
      select(periodo, categoria, valor)
  ) %>%
  pivot_wider(names_from = periodo, values_from = valor) %>%
  arrange(categoria)

#-----------------------------------------
# 9. AGREGAR SECTOR FORMAL / INFORMAL
#-----------------------------------------

agregar_sector <- function(){
  
  sector <- base %>%
    group_by(anio, trimestre, sector_agregado) %>%
    summarise(valor = sum(PONDERA), .groups = "drop") %>%
    group_by(anio, trimestre) %>%
    mutate(valor = valor / sum(valor)) %>%
    ungroup() %>%
    mutate(periodo = paste0(anio, "_T", trimestre)) %>%
    select(periodo, categoria = sector_agregado, valor) %>%
    bind_rows(
      base %>%
        group_by(anio, sector_agregado) %>%
        summarise(valor = sum(PONDERA), .groups = "drop") %>%
        group_by(anio) %>%
        mutate(valor = valor / sum(valor)) %>%
        ungroup() %>%
        mutate(periodo = paste0(anio, "_Anual")) %>%
        select(periodo, categoria = sector_agregado, valor)
    ) %>%
    pivot_wider(names_from = periodo, values_from = valor)
  
  return(sector)
}

tabla_pct <- bind_rows(agregar_sector(), tabla_pct)
tabla_cant <- bind_rows(agregar_sector(), tabla_cant)


#-----------------------------------------
# 10. ORDEN FINAL
#-----------------------------------------

orden <- c(
  "Sector Formal",
  "Autónomos profesionales",
  "Asalariados Privados",
  "Asalariados Públicos",
  "Patrones",
  "Sector Informal",
  "Patrones (Micro)",
  "Asalariados Privados (Micro)",
  "Autónomos no profesionales",
  "Trabajo Familiar",
  "Empleo doméstico"
)

tabla_pct <- tabla_pct %>% filter(categoria %in% orden) %>% arrange(match(categoria, orden))
tabla_cant <- tabla_cant %>% filter(categoria %in% orden) %>% arrange(match(categoria, orden))

#-----------------------------------------
# RESULTADOS
#-----------------------------------------

print(tabla_pct)
print(tabla_cant)


