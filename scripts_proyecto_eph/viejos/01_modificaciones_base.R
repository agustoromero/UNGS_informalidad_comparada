##1
# Crear carpeta si no existe
ruta_datos <- "data/original/"
if (!dir.exists(ruta_datos)) dir.create(ruta_datos)

# Armar tabla de trimestres deseados
trimestres_seleccionados <- expand.grid(
  ANO4 = 2016:2024,
  TRIMESTRE = 1:4
)
# Podés descomentar esta línea si querés limitar
# trimestres_seleccionados <- trimestres_seleccionados %>% filter(!(ANO4 == 2024 & TRIMESTRE > 2))

# Función para descargar y guardar archivos
descargar_datos <- function(ano, trimestre) {
  archivo <- paste0(ruta_datos, "base_", ano, "_T", trimestre, ".rds")
  if (!file.exists(archivo)) {
    tryCatch({
      datos <- get_microdata(year = ano, period = trimestre, type = "individual")
      saveRDS(datos, file = archivo)
      message("Descargado y guardado: ", archivo)
    }, error = function(e) {
      message("Error al descargar ", ano, " T", trimestre)
    })
  } else {
    message("Ya existe: ", archivo)
  }
}

# Descargar todos
mapply(descargar_datos, trimestres_seleccionados$ANO4, trimestres_seleccionados$TRIMESTRE)

# Función para importar y etiquetar
importar_datos <- function(ano, trimestre) {
  archivo <- paste0(ruta_datos, "base_", ano, "_T", trimestre, ".rds")
  if (file.exists(archivo)) {
    datos <- readRDS(archivo) %>%
      haven::zap_labels() %>%
      mutate(anio_trim = paste0(ano, "T", trimestre))
    return(datos)
  } else {
    message("No se encontró: ", archivo)
    return(NULL)
  }
}

# Leer todas las bases
lista_datos <- lapply(1:nrow(trimestres_seleccionados), function(i) {
  importar_datos(trimestres_seleccionados$ANO4[i], trimestres_seleccionados$TRIMESTRE[i])
})

# Unir
datos_completos <- bind_rows(lista_datos)

# Etiquetar y variables clave
datos_completos <- datos_completos %>%
  organize_labels(type = "individual") %>%
  organize_caes() %>%
  organize_cno() %>%
  mutate(
    rango_etario = case_when(
      CH06 < 19  ~ "Menor a 19",
      CH06 >= 19 & CH06 <= 30 ~ "Jovenes (de 19 a 30 años)",
      CH06 >= 31 & CH06 <= 45 ~ "Adultos (de 31 a 45)",
      CH06 >= 46 & CH06 <= 60 ~ "Adultos 2 (de 46 a 60)",
      CH06 >= 61  ~ "Mayores de 60",
      TRUE ~ NA_character_
    ),
    nivel.ed1 = factor(case_when(
      NIVEL_ED %in% c(7,1,2,3) ~ "Menor a Secundaria",
      NIVEL_ED == 4 ~ "Secundaria Completa",
      NIVEL_ED == 5 ~ "Superior Incompleto",
      NIVEL_ED == 6 ~ "Superior Completo",
      TRUE ~ "Ns/Nr"
    ), levels = c("Menor a Secundaria","Secundaria Completa","Superior Incompleto","Superior Completo"))
  )

# Guardar base consolidada
saveRDS(datos_completos, "data/original/base_eph_2016_2024.rds")

# Limpieza
rm(ruta_datos, trimestres_seleccionados, lista_datos, importar_datos, descargar_datos)



##2 crear Subconjuntos
ocupados        <- datos_completos %>% filter(ESTADO == 1)
desocupados     <- datos_completos %>% filter(ESTADO == 2)
inactivos       <- datos_completos %>% filter(ESTADO == 3)

asalariados     <- ocupados %>% filter(CAT_OCUP == 3)
cuenta_propia   <- ocupados %>% filter(CAT_OCUP == 2)
patron          <- ocupados %>% filter(CAT_OCUP == 1)

# Guardado
saveRDS(ocupados,        "data/procesada/ocupados.rds")
saveRDS(desocupados,     "data/procesada/desocupados.rds")
saveRDS(inactivos,       "data/procesada/inactivos.rds")
saveRDS(asalariados,     "data/procesada/asalariados.rds")
saveRDS(cuenta_propia,   "data/procesada/cuenta_propia.rds")
saveRDS(patron,          "data/procesada/patron.rds")

# Limpieza
rm(ocupados, desocupados, inactivos, cuenta_propia, patron)




##3
# Leer asalariados procesamiento asalariados
asalariados <- readRDS("data/procesada/asalariados.rds")

# Procesar
asalariados_proc <- asalariados %>%
  mutate(
    PP04D_COD = str_pad(PP04D_COD, 5, "left", "0"),
    digito.calificacion = str_sub(PP04D_COD, 5, 5),
    calificacion = factor(case_when(
      digito.calificacion == "1" ~ "Profesionales",
      digito.calificacion == "2" ~ "Técnicos",
      digito.calificacion == "3" ~ "Operativos",
      digito.calificacion == "4" ~ "No calificados",
      TRUE ~ NA_character_
    ), levels = c("Profesionales", "Técnicos", "Operativos", "No calificados")),
    grupos.calif = factor(case_when(
      calificacion %in% c("Profesionales", "Técnicos") ~ "Alta",
      calificacion == "Operativos" ~ "Media",
      calificacion == "No calificados" ~ "Baja",
      TRUE ~ NA_character_
    ), levels = c("Baja", "Media", "Alta")),
    registrado = case_when(P21 == 1 ~ TRUE, P21 == 2 ~ FALSE, TRUE ~ NA),
    aporta_ss = case_when(PP07H == 1 ~ TRUE, PP07H == 2 ~ FALSE, TRUE ~ NA),
    tam_estab = case_when(
      PP04C %in% 1:6 | (PP04C == 99 & PP04C99 == 1) ~ "1-5 personas",
      PP04C %in% 7:8 | (PP04C == 99 & PP04C99 == 2) ~ "6-40 personas",
      PP04C %in% 9:12 | (PP04C == 99 & PP04C99 == 3) ~ "41-200 personas",
      PP04C == 99 & PP04C99 == 4 ~ "201 o más",
      TRUE ~ NA_character_
    ),
    antiguedad_empleo = factor(case_when(
      as_factor(PP07A) %in% c("1", "2", "3", "4", "5", "6") ~ as_factor(PP07A)
    ), levels = c("1", "2", "3", "4", "5", "6"),
    labels = c("menor a 1 mes", "1 a 3 meses", "más de 3 a 6 meses",
               "más de 6 a 12 meses", "más de 1 año a 5 años", "más de 5 años"))
  )

# Guardar
saveRDS(asalariados_proc, "data/procesada/asalariados_proc.rds")
rm(asalariados)
