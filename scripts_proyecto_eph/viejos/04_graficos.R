cuadro_long <- cuadro_asalariados %>%
  pivot_longer(cols = -anio_trim, names_to = "perfil", values_to = "n") %>%
  mutate(
    tamano = case_when(
      str_detect(perfil, "Pequeño") ~ "Pequeño (1-5)",
      str_detect(perfil, "Mediano") ~ "Mediano (6-40)",
      str_detect(perfil, "Grande")  ~ "Grande (41+)",
      TRUE ~ "Otro"
    )
  )

# Limpieza
rm(cuadro_asalariados)
