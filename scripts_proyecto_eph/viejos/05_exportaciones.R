# ===============================================
# 05_exportaciones.R
# Exportación de cuadros clave a Excel
# ===============================================

library(openxlsx)

# Crear workbook
wb <- createWorkbook()

# Leer los objetos a exportar
tasas            <- readRDS("data/procesada/tasas_final.rds")
tasas_sexo       <- readRDS("data/procesada/tasas_sexo_final.rds")
tasas_sexo_educ  <- readRDS("data/procesada/tasas_sexo_educ.rds")
perfiles_asal    <- readRDS("data/procesada/perfiles_asalariados.rds")

# Agregar hojas
addWorksheet(wb, "Tasas_totales")
addWorksheet(wb, "Tasas_por_sexo")
addWorksheet(wb, "Tasas_sexo_nivel_ed")
addWorksheet(wb, "Perfiles_asalariados")

# Escribir en cada hoja
writeData(wb, "Tasas_totales", tasas)
writeData(wb, "Tasas_por_sexo", tasas_sexo)
writeData(wb, "Tasas_sexo_nivel_ed", tasas_sexo_educ)
writeData(wb, "Perfiles_asalariados", perfiles_asal)

# Guardar archivo
saveWorkbook(wb, file = "output/cuadros_resultados.xlsx", overwrite = TRUE)
