#CONFIG
# Configuración del proyecto

## Objetivo

La carpeta `config/` concentra toda la información de configuración compartida por el pipeline de armonización.

Actualmente contiene archivos YAML utilizados por `common_pipeline.py`.

A futuro se evaluará reemplazar parte de esta configuración por documentación Markdown más extensa y archivos YAML mínimos utilizados únicamente por el código.

---

# Archivos actuales

config/

country_mappings.yaml

variables.yaml

methodology.yaml

---

# country_mappings.yaml

Contiene la información necesaria para identificar cada país dentro del pipeline.

Incluye, entre otros:

- nombre interno del país
- códigos utilizados por el pipeline
- convenciones comunes
- posibles equivalencias de nombres

Este archivo NO contiene lógica.

Debe limitarse únicamente a configuración.

---

# variables.yaml

Define el conjunto de variables armonizadas utilizadas por todos los países.

Debe contener únicamente variables finales.

Nunca debe documentar variables propias de una encuesta.

Las variables específicas de cada país pertenecen a la documentación nacional correspondiente.

---

# methodology.yaml

Resume la metodología común del proyecto.

No reemplaza la documentación.

Su función es proveer parámetros que puedan ser utilizados automáticamente por el pipeline.

---

# Principios

Toda la lógica pertenece a:

scripts/common_pipeline.py

Los archivos YAML únicamente contienen configuración.

Nunca deben contener reglas complejas.

Nunca deben contener código.

---

# Cambios previstos

Es probable que parte de la documentación actualmente resumida en YAML migre hacia archivos Markdown.

La documentación completa quedará en:

11_METODOLOGIA.md

mientras que los YAML permanecerán únicamente como archivos de configuración consumidos por Python.

---

# Convenciones

Toda nueva variable armonizada debe documentarse en:

10_VARIABLES_ARMONIZADAS.md

Toda decisión metodológica debe documentarse en:

11_METODOLOGIA.md

Nunca solamente dentro de un YAML.
