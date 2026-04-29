asalariados_proc <- readRDS("data/procesada/asalariados_proc.rds")

cuadro_perfiles_asalariados <- function(base) {
  base %>%
    filter(!is.na(grupos.calif), !is.na(tam_estab)) %>%
    mutate(
      tamano_establecimiento = case_when(
        tam_estab == "1-5 personas" ~ "Pequeño (1-5)",
        tam_estab == "6-40 personas" ~ "Mediano (6-40)",
        tam_estab %in% c("41-200 personas", "201 o más") ~ "Grande (41+)",
        TRUE ~ NA_character_
      ),
      perfil = paste(grupos.calif, "-", tamano_establecimiento)
    ) %>%
    filter(!is.na(perfil)) %>%
    count(anio_trim, perfil, name = "n") %>%
    tidyr::complete(anio_trim, perfil, fill = list(n = 0)) %>%
    pivot_wider(names_from = perfil, values_from = n, values_fill = 0) %>%
    arrange(anio_trim)
}

cuadro_asalariados <- cuadro_perfiles_asalariados(asalariados_proc)

# Limpieza
rm(asalariados_proc, cuadro_perfiles_asalariados)
