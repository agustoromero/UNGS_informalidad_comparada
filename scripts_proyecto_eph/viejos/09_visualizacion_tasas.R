# Visualización de tasas laborales
# -------------------------------

# Configuración de temas y colores
theme_set(theme_minimal(base_size = 11) +
            theme(legend.position = "bottom",
                  axis.text.x = element_text(angle = 45, hjust = 1)))

colores_sexo <- c("1" = "#1f77b4", "2" = "#2ca02c", "Total" = "#7f7f7f")

# Función para generar gráficos de tasas
generar_grafico_tasa <- function(tasa, datos = tasas_resultados) {
  datos %>%
    mutate(CH04 = factor(CH04, levels = c("1", "2", "Total"))) %>%
    ggplot(aes(x = anio_trim, y = .data[[tasa]], color = CH04, group = CH04)) +
    geom_line(linewidth = 0.8) +
    geom_point(size = 1.5) +
    scale_color_manual(values = colores_sexo,
                       labels = c("Varones", "Mujeres", "Total"),
                       name = NULL) +
    scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +
    labs(title = str_replace_all(tasa, "_", " "),
         x = NULL, y = NULL) +
    facet_wrap(~rango_etario, ncol = 5, scales = "free_y")
}

# Generar todos los gráficos
tasas_a_graficar <- c("Tasa_Actividad", "Tasa_Empleo", "Tasa_Desocupacion")
graficos_tasas <- map(tasas_a_graficar, generar_grafico_tasa)

# Combinar en un panel
panel_tasas <- wrap_plots(graficos_tasas, ncol = 1) +
  plot_annotation(title = "Evolución de Tasas Laborales por Sexo y Edad",
                  theme = theme(plot.title = element_text(hjust = 0.5, face = "bold")))

# Exportar
ggsave("output/graficos/panel_tasas.png", panel_tasas, 
       width = 16, height = 12, dpi = 300)