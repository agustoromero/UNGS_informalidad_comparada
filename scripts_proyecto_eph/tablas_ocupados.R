
# Cargar base de ocupados
base_ocupados <- readRDS("data/base_ocupados.rds")
# ===============================
# Función genérica para estructurar cuadros
# ===============================
tabla_ocupados <- function(df, dimension) {
  base_cant <- df %>%
    group_by(anio_trim, !!sym(dimension), CAT_OCUP) %>%
    summarise(personas = sum(PONDERA, na.rm = TRUE), .groups = "drop")
  
  base_prop <- base_cant %>%
    group_by(anio_trim, !!sym(dimension)) %>%
    mutate(prop = 100 * personas / sum(personas, na.rm = TRUE)) %>%
    ungroup()
  
  tabla_prop <- base_prop %>%
    select(anio_trim, !!sym(dimension), CAT_OCUP, prop) %>%
    pivot_wider(names_from = anio_trim, values_from = prop) %>%
    mutate(tipo = "Proporción (%)")
  
  tabla_cant <- base_prop %>%
    select(anio_trim, !!sym(dimension), CAT_OCUP, personas) %>%
    pivot_wider(names_from = anio_trim, values_from = personas) %>%
    mutate(tipo = "Cantidad (personas)")
  
  bind_rows(tabla_prop, tabla_cant)
}

# ===============================
# 3. Dimensiones simples
# ===============================
tab_sector <- tabla_ocupados(base_ocupados, "PP04A")       # Público / Privado / Otro
tab_calif  <- tabla_ocupados(base_ocupados, "CALIFICACION")  # Profesionales, Técnicos, etc.
tab_rama   <- tabla_ocupados(base_ocupados, "caes_seccion_label.x")   # Rama (22 sectores)
tab_tamest <- tabla_ocupados(base_ocupados, "tam_estab")     # Tamaño del establecimiento

# ===============================
# 4. Dimensiones especiales
# ===============================

# --- Insuficiencia horaria
tab_intensi <- base_ocupados %>%
  group_by(anio_trim, INTENSI) %>%
  summarise(personas = sum(PONDERA, na.rm = TRUE), .groups = "drop") %>%
  group_by(anio_trim) %>%
  mutate(prop = 100 * personas / sum(personas)) %>%
  ungroup()

# --- Tiempo parcial involuntario/ tiempo determinado
tab_tiempo <- base_ocupados %>%
  mutate(
    part_time = if_else(PP3E_TOT + PP3F_TOT < 35 & PP03G == 1, 1, 0),
    tiempo_determ = if_else(PP07C == 2, 1, 0)
  ) %>%
  summarise(
    part_time = sum(part_time * PONDERA, na.rm = TRUE),
    tiempo_determ = sum(tiempo_determ * PONDERA, na.rm = TRUE),
    .by = anio_trim
  )

# --- Sobreocupados
tab_sobre <- base_ocupados %>%
  mutate(sobreocupado = if_else(PP3E_TOT + PP3F_TOT > 45, 1, 0)) %>%
  summarise(
    sobreocupados = sum(sobreocupado * PONDERA, na.rm = TRUE),
    total = sum(PONDERA, na.rm = TRUE),
    .by = anio_trim
  ) %>%
  mutate(prop = 100 * sobreocupados / total)

# --- Antigüedad
tab_antig <- base_ocupados %>%
  mutate(antiguedad_empleo = case_when(
    PP05H <= 3 ~ "<=3 meses",
    PP05H > 3 & PP05H <= 6 ~ "3–6 meses",
    PP05H > 6 & PP05H <= 24 ~ "6m–2 años",
    PP05H > 24 & PP05H <= 60 ~ "2–5 años",
    PP05H > 60 & PP05H <= 120 ~ "5–10 años",
    PP05H > 120 ~ ">10 años",
    TRUE ~ "Ns/Nr"
  )) %>%
  group_by(anio_trim, antiguedad_empleo) %>%
  summarise(personas = sum(PONDERA, na.rm = TRUE), .groups = "drop") %>%
  group_by(anio_trim) %>%
  mutate(prop = 100 * personas / sum(personas))

# ===============================
# 5. Exportar a Excel
# ===============================
wb <- createWorkbook()
addWorksheet(wb, "Sector");       writeData(wb, "Sector", tab_sector)
addWorksheet(wb, "Calificacion"); writeData(wb, "Calificacion", tab_calif)
addWorksheet(wb, "Rama");         writeData(wb, "Rama", tab_rama)
addWorksheet(wb, "TamEst");       writeData(wb, "TamEst", tab_tamest)

addWorksheet(wb, "InsufHoraria"); writeData(wb, "InsufHoraria", tab_intensi)
addWorksheet(wb, "Tiempo");       writeData(wb, "Tiempo", tab_tiempo)
addWorksheet(wb, "Sobreocup");    writeData(wb, "Sobreocup", tab_sobre)
addWorksheet(wb, "Antiguedad");   writeData(wb, "Antiguedad", tab_antig)

saveWorkbook(wb, "Tablas_ocupados_dimensiones.xlsx", overwrite = TRUE)
