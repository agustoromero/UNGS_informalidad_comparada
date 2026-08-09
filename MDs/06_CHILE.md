# CHILE
# Chile

## Objetivo

Este documento describe la implementación específica de Chile dentro del proyecto de armonización de estructura ocupacional e informalidad para América Latina.

Chile constituye una incorporación nueva al proyecto y deberá integrarse respetando la estructura metodológica común utilizada para el resto de los países.

---

# Fuente oficial

Instituto Nacional de Estadísticas (INE)

Encuesta principal

- Encuesta Nacional de Empleo (ENE)

Sitio oficial

https://www.ine.gob.cl/

---

# Cobertura temporal

Objetivo final

- 2007
- 2023

Actualmente

- En proceso de incorporación.

---

# Cobertura geográfica

Siempre que la información esté disponible se construirán indicadores para:

- Total urbano
- Total rural
- Urbano + Rural

junto con sus respectivos desagregados.

Si alguna desagregación no existe en la encuesta deberá documentarse.

---

# Unidad de análisis

Personas.

Siempre se trabaja sobre la ocupación principal.

---

# Rango etario

Se consideran personas entre

15 y 65 años.

---

# Denominadores

Los indicadores podrán calcularse utilizando:

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

Además se conservarán todos los agregados necesarios para construir indicadores generales.

---

# Definición de informalidad

El proyecto utiliza una definición productivista.

La clasificación no depende exclusivamente del registro laboral ni del acceso a la seguridad social.

Se construye utilizando simultáneamente:

- categoría ocupacional
- tamaño del establecimiento
- educación
- características del vínculo laboral

La definición metodológica general se encuentra documentada en:

11_METODOLOGIA.md

---

# Cambios metodológicos

## Tamaño del establecimiento

Versión anterior

Menor a 5 trabajadores.

Versión actual

Menor a 10 trabajadores.

---

## Autónomos

Versión anterior

Clasificación según calificación ocupacional.

Versión actual

Clasificación según educación terciaria o universitaria completa.

---

# Indicadores adicionales

Siempre que las variables existan se construirán:

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

Cuando la información lo permita se identificará el empleo público en:

- Administración pública
- Educación
- Salud

---

# Salarios

En una etapa posterior se incorporarán salarios reales de la ocupación principal utilizando índices de precios compatibles.

Esta etapa todavía no forma parte del pipeline.

---

# Variables faltantes

Si alguna variable utilizada en el esquema armonizado no existe en Chile:

1. Buscar una variable equivalente.
2. Buscar una proxy metodológicamente consistente.
3. Consultar antes de utilizar valores faltantes.

Nunca reemplazar automáticamente una variable inexistente por missing.

---

# Scripts

Actualmente no existe una implementación definitiva.

Se prevé incorporar:

scripts/chile/

- chile_2007.py
- chile_2023.py

siguiendo la misma arquitectura utilizada para el resto de los países.

---

# Datos

Los datos originales se almacenarán en:

data/chile/

Toda limpieza o transformación deberá realizarse mediante scripts reproducibles.

---

# Estado actual

Chile es una incorporación nueva al proyecto.

Las tareas principales son:

- identificar las variables equivalentes de la ENE;
- construir los parquets armonizados para 2007 y 2023;
- integrar ambos años al pipeline común.

---

# Observaciones

La armonización tiene prioridad sobre la comparabilidad exacta de las variables originales.

Cuando una variable no exista exactamente igual que en los demás países deberá privilegiarse la construcción de una proxy conceptualmente equivalente, siempre documentando la decisión adoptada.