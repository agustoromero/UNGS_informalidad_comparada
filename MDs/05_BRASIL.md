# BRASIL
# Brasil

## Objetivo

Este documento describe la implementación específica de Brasil dentro del proyecto de armonización de estructura ocupacional e informalidad para América Latina.

Brasil presenta una de las encuestas más complejas del proyecto debido a los cambios metodológicos ocurridos entre distintos períodos y a la existencia de múltiples bases oficiales.

---

# Fuente oficial

Instituto Brasileiro de Geografia e Estatística (IBGE)

Encuesta principal:

- PNAD (2007)
- PNADC Continua (2018 y 2023)

https://www.ibge.gov.br/

---

# Cobertura temporal

Objetivo final

- 2007
- 2018
- 2023

Actualmente implementado

- 2018
- 2023

Pendiente

- Incorporación de 2007 utilizando la PNAD clásica.

---

# Cobertura geográfica

Brasil posee cobertura nacional.

El proyecto buscará construir:

- Total urbano
- Total rural
- Urbano + Rural

y sus respectivos desagregados siempre que las variables lo permitan.

---

# Unidad de análisis

Personas.

Siempre se utiliza la ocupación principal.

---

# Rango etario

Se consideran personas entre

15 y 65 años.

---

# Denominadores

Los indicadores podrán calcularse sobre:

- PET
- PEA
- Ocupados

según corresponda.

---

# Estructura ocupacional

Se armonizarán los siguientes grupos.

## Total

- Ocupados

## Sector formal

- Asalariados privados
- Asalariados públicos
- Autónomos profesionales
- Patrones

## Sector informal

- Patrones micro
- Asalariados privados micro
- Autónomos no profesionales
- Trabajo familiar
- Empleo doméstico

Además se conservarán todos los agregados necesarios.

---

# Definición de informalidad

El proyecto utiliza una definición productivista.

No depende únicamente del registro laboral o de la seguridad social.

La clasificación combina múltiples dimensiones:

- categoría ocupacional
- tamaño del establecimiento
- educación
- características del vínculo laboral

La metodología completa se documenta en:

11_METODOLOGIA.md

---

# Cambios metodológicos

## Tamaño del establecimiento

Versión anterior

Menor a 5 personas.

Versión actual

Menor a 10 personas.

---

## Autónomos

Versión anterior

Clasificación basada en calificación ocupacional.

Versión actual

Clasificación según educación terciaria o universitaria completa.

---

# Indicadores adicionales

Siempre que la encuesta lo permita se construirán:

## Subocupación

- Demandante
- No demandante

## Contratos

- Contrato escrito
- Contrato verbal

## Temporalidad

- Permanente
- Temporal

---

# Sector público

Se buscará identificar la composición del empleo público en:

- Administración pública
- Educación
- Salud

Cuando existan variables compatibles.

---

# Salarios

Posteriormente se incorporarán los salarios reales de la ocupación principal utilizando un índice de precios compatible.

Esta etapa todavía no forma parte del pipeline.

---

# Particularidades de Brasil

Brasil constituye el país con mayor complejidad técnica del proyecto.

Durante el desarrollo se implementaron scripts específicos para resolver inconsistencias observadas en la PNADC.

La incorporación de nuevos años deberá procurar reutilizar esas soluciones antes de crear nuevas reglas.

---

# Scripts

Actualmente existen:

scripts/brasil/

- brasil_2018.py
- brasil_2023.py
- corrije_brasil.py

En el futuro se agregará:

- brasil_2007.py

---

# Datos

Los datos originales se almacenan en:

data/brasil/

También existen directorios auxiliares utilizados durante el desarrollo:

- data/brasil_clean/

Estos últimos no forman parte del pipeline definitivo y podrán desaparecer cuando la implementación quede consolidada.

---

# Estado actual

Brasil ya produce archivos armonizados para:

- 2018
- 2023

La siguiente etapa consiste en incorporar 2007 utilizando la PNAD clásica y mantener compatibilidad con el pipeline común.

---

# Observaciones

Brasil será probablemente el país con mayor cantidad de excepciones documentadas.

Siempre que una variable no exista deberá buscarse una variable equivalente o una proxy metodológicamente justificable antes de reemplazarla por valores faltantes.

Toda excepción deberá documentarse explícitamente.