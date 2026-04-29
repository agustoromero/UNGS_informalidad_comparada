# ============================================
# Preparación de bases EPH (2014T1–2025T1)
# ============================================

# Librerías necesarias
library(tidyverse)
library(eph)
library(haven)
library(dplyr)
library(readr)
library(openxlsx)
library(stringr)
library(purrr)

# Rutas del proyecto
ruta_datos <- "data/"
ruta_scripts <- "scripts/"

# Definir trimestres de interés: 2014T1 a 2025T1
trimestres_seleccionados <- expand.grid(
  ANO4 = 2014:2025,
  TRIMESTRE = 1:4
) %>%
  filter(!(ANO4 == 2025 & TRIMESTRE > 1)) %>%   # hasta 2025T1
  arrange(ANO4, TRIMESTRE)

# Función para descargar y guardar en RDS si no existe
descargar_datos <- function(ano, trimestre) {
  archivo <- paste0(ruta_datos, "base_", ano, "_T", trimestre, ".rds")
  if (!file.exists(archivo)) {
    datos <- get_microdata(year = ano, period = trimestre, type = "individual")
    saveRDS(datos, archivo)
    message("Descargado y guardado: ", archivo)
  } else {
    message("Ya existe: ", archivo)
  }
}

# Descargar todos los trimestres

#mapply(descargar_datos, trimestres_seleccionados$ANO4, trimestres_seleccionados$TRIMESTRE)

# Importar datos y agregar identificador
importar_datos <- function(ano, trimestre) {
  archivo <- paste0(ruta_datos, "base_", ano, "_T", trimestre, ".rds")
  if (file.exists(archivo)) {
    datos <- readRDS(archivo) %>%
      mutate(
        ANO4 = ano,
        TRIMESTRE = trimestre,
        anio_trim = paste0(ano, "T", trimestre)
      )
    return(datos)
  } else {
    return(NULL)
  }
}


# Unificar todos los trimestres
base_completa <- map2_dfr(trimestres_seleccionados$ANO4,
                        trimestres_seleccionados$TRIMESTRE,
                        importar_datos)

# ===============================
# Selección de variables núcleo
# ===============================
# (ajustar este vector con las 91 variables que quieras conservar)
vars_nucleo <- c(# Identificación y contexto
  "CODUSU","NRO_HOGAR","COMPONENTE","CH03","CH04","CH06","CH07","CH15_COD",
  "ANO4","TRIMESTRE","REGION","AGLOMERADO", "anio_trim",
  "ESTADO","CAT_OCUP","CAT_INAC","NIVEL_ED","IMPUTA","INTENSI",
  
  # Horas trabajadas
  "PP3E_TOT","PP3F_TOT",
  
  #ocupado demandante
  "PP03J",
  
  # Ingreso ocupación principal
  "P21","DECOCUR","IDECOCUR","RDECOCUR","GDECOCUR","PDECOCUR","ADECOCUR","PONDIIO",
  
  # Ingreso otras ocupaciones y total individual
  "TOT_P12","P47T","DECINDR","IDECINDR","RDECINDR","GDECINDR","PDECINDR","ADECINDR",
  
  # Ingresos no laborales
  "V2_M","V3_M","V4_M","V5_M","V8_M","V9_M","V10_M","V11_M","V12_M","V18_M","V19_AM","V21_M",
  "T_VI",
  # Ingresos familiares
  "ITF","DECIFR","IDECIFR","RDECIFR","GDECIFR","PDECIFR","ADECIFR",
  "IPCF","DECCFR","IDECCFR","RDECCFR","GDECCFR","PDECCFR","ADECCFR",
  # Ponderadores
  "PONDERA","PONDII","PONDIH",
  #aporta o le descuentan
  "PP07H", "PP07I",
  # Sector Institucional
  "PP04A",
  #Tamaño establecimiento y rescate
  "PP04C", "PP04C99",
  #CAES
  "PP04B_COD","PP04D_COD",
  #antiguedad
  "PP05H","PP05B2_MES","PP05B2_ANO","PP05B2_DIA", "PP07A",
  #tiempo de finalización
  "PP07C","PP07D",
  #part-time involuntario
  "PP03G",
  #vacaciones aguinaldo pago por enfermedad obra social G4 
  "PP07G1","PP07G2","PP07G3","PP07G4"
  # #nuevo cuestionario
  # "PP05I","PP05J","PP05K","PP07I2","PP07I3","PP07I4", "PP05B3","PP06E1",
  # #Proporción en negro
  # "PP07L","PP07M"
  # #Informalidad en el empleo y la unidad
  # "Empleo", "Sector"
)


base_nucleo <- base_completa %>%
  select(any_of(vars_nucleo)) %>%
  mutate(
    # Crear variable de rango etario
    rango_etario = case_when(
      CH06 < 19 ~ "Menor a 19",
      between(CH06, 19, 30) ~ "19 a 30",
      between(CH06, 31, 45) ~ "31 a 45",
      between(CH06, 46, 60) ~ "46 a 60",
      between(CH06, 61, 65) ~ "61 a 65",
      between(CH06, 66, 70) ~ "66 a 70",
      CH06 > 70 ~ "Mayor a 70",
      TRUE ~ NA_character_
    ),
    # Nivel educativo
    nivel_ed = case_when(
      NIVEL_ED %in% c(1, 2, 3, 7) ~ "Menor a Secundaria",
      NIVEL_ED == 4 ~ "Secundaria Completa",
      NIVEL_ED == 5 ~ "Superior Incompleto",
      NIVEL_ED == 6 ~ "Superior Completo",
      TRUE ~ "Ns/Nr"
    ) %>% factor(
      levels = c("Menor a Secundaria",
                 "Secundaria Completa",
                 "Superior Incompleto",
                 "Superior Completo",
                 "Ns/Nr"),
      ordered = TRUE
    )
  ) %>%
  # Filtrar exclusiones
  filter(
    ESTADO != 0,           # entrevista no realizada
    ESTADO != 4,           # menor de 10
    CAT_OCUP != 0,         # categoría ignorada
    CAT_OCUP != 9,         # Ns/Nr 
  )

#diccionario etiquetas generales
base_nucleo <-  base_nucleo %>%
  organize_labels(type = "individual")

saveRDS(base_nucleo, paste0(ruta_datos, "base_nucleo.rds"))
message("Base núcleo guardada en: data/base_nucleo.rds")

# ===============================
# Generar base de ocupados
# ===============================
base_ocupados <- base_nucleo %>%
  filter(ESTADO == 1)   # solo ocupados
  
saveRDS(base_ocupados, paste0(ruta_datos, "base_ocupados.rds"))
message("Base de ocupados guardada en: data/base_ocupados.rds")

#C1
#C2
#C3
#C4
################################################################################################

# Cargar base de ocupados
base_ocupados <- readRDS("data/base_ocupados.rds")

# Transformaciones a ocupados  
base_ocupados <- base_ocupados %>%
  filter(ESTADO== 1) %>%
  mutate(
    cat_ocupado = case_when(
      CAT_OCUP == 3 & PP07H == 1 ~ "Asalariado registrado",
      CAT_OCUP == 3 & PP07H == 2 ~ "Asalariado no registrado",
      CAT_OCUP == 2 & PP07I == 1 ~ "Cuenta propia registrado",
      CAT_OCUP == 2 & PP07I == 2 ~ "Cuenta propia no registrado",
      TRUE ~ NA_character_
    ),
    tam_estab = case_when(
      !is.na(PP04C99) ~ case_when(
        PP04C99 == 1 ~ "peque",
        PP04C99 == 2 ~ "mediano",
        PP04C99 == 3 ~ "grande",
        PP04C99 == 9 ~ "NS/NR"
      ),
      PP04C == 1 ~ "uni",
      PP04C %in% c(2, 3, 4, 5) ~ "peque",
      PP04C %in% c(6, 7, 8) ~ "mediano",
      PP04C %in% c(9, 10, 11, 12) ~ "grande",
      TRUE ~ NA_character_
    ),
    antiguedad_empleo = case_when(
      as_factor(PP07A) %in% c("1", "2", "3", "4", "5", "6") ~ as_factor(PP07A),#asalariados
      as_factor(PP05H) %in% c("1", "2", "3", "4", "5", "6") ~ as_factor(PP05H) #no asalariados (independientes/cuentapropia)
    ), 
    antiguedad_empleo = factor(
      antiguedad_empleo, 
      levels = c("1", "2", "3", "4", "5", "6"),
      labels = c("menor a 1 mes", "1 a 3 meses", "más de 3 a 6 meses", 
                 "más de 6 a 12 meses", "más de 1 año a 5 años", "más de 5 años")
    )
  )
#diccionario CAES y CNO
base_ocupados<- organize_caes(base_ocupados) 
base_ocupados<- organize_cno(base_ocupados)
# Guardar base asalariados
saveRDS(base_ocupados, "data/base_ocupados.rds")